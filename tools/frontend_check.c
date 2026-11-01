#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "../src/game.h"
#include "../src/alignment.h"
#include "../assets/ui.h"
static uint64_t energy;
static unsigned samples;
static FILE *audio_file;
static unsigned audio_frames;
static void run(struct mCore *c,unsigned count){
 for(unsigned i=0;i<count;i++){
  c->runFrame(c);
  short left[2048],right[2048];
  int n=blip_read_samples(c->getAudioChannel(c,0),left,2048,0);
  int m=blip_read_samples(c->getAudioChannel(c,1),right,2048,0);
  assert(n==m);
  for(int j=0;j<n;j++){energy+=(uint64_t)abs(left[j]);samples++;}
  if(audio_file&&audio_frames<180){
   for(int j=0;j<n;j++){fwrite(&left[j],2,1,audio_file);fwrite(&right[j],2,1,audio_file);}
   audio_frames++;
  }
 }
}
static unsigned value(struct mCore *c,int offset){return c->busRead32(c,0x0203F000+offset*4);}
static void state(struct mCore *c,unsigned expected){
 if(value(c,0)!=expected)fprintf(stderr,"Expected state %u, got %u at frame %u\n",expected,value(c,0),c->frameCounter(c));
 assert(value(c,0)==expected);
}
static void tap(struct mCore *c,unsigned key){c->setKeys(c,key);run(c,8);c->setKeys(c,0);run(c,8);}
static void capture(struct mCore *c,const char *name){
 const void *pixels;size_t stride;c->getPixels(c,&pixels,&stride);
 FILE *f=fopen(name,"wb");assert(f);fprintf(f,"P6\n240 160\n255\n");
 for(int y=0;y<160;y++)for(int x=0;x<240;x++){
  color_t p=((const color_t*)pixels)[y*stride+x];
  unsigned char rgb[3]={p&255,(p>>8)&255,(p>>16)&255};fwrite(rgb,1,3,f);
 }fclose(f);
}
static void player(struct mCore *c,int *x,int *y){
 *x=(int)value(c,8)/256;*y=(int)value(c,9)/256;
}
static void move_to(struct mCore *c,unsigned key,int target){
 c->setKeys(c,key);
 for(int i=0;i<400;i++){
  int x=(int)value(c,8)/256;
  if((key==16&&x>=target)||(key==32&&x<=target))break;
  run(c,1);
 }
 c->setKeys(c,0);run(c,4);
}
static void check_rest_background(struct mCore *c,const char *path,int gem_x,int gem_y){
 assert((int)value(c,15)==0);
 FILE *f=fopen(path,"rb");assert(f);assert(fseek(f,512,SEEK_SET)==0);
 int sx=(int)value(c,8)/256+PLAYER_W/2-SIA_ANCHOR_X;
 int sy=(int)value(c,9)/256+PLAYER_H-SIA_ANCHOR_Y;
 unsigned base=(c->busRead16(c,0x04000000)&16)?0x0600A000:0x06000000;
 for(int y=0;y<160;y++)for(int x=0;x<240;x++){
  int expected=fgetc(f);assert(expected>=0);
  if(x>=3&&x<55&&y>=3&&y<13)continue; /* Live HP/lives HUD replaces these background pixels. */
  if(x>=sx&&x<sx+48&&y>=sy&&y<sy+56)continue;
  if(x>=gem_x&&x<gem_x+16&&y>=gem_y&&y<gem_y+16)continue;
  assert(c->busRead8(c,base+(unsigned)y*240+(unsigned)x)==(unsigned)expected);
 }
 assert(fgetc(f)==EOF);fclose(f);
}

int main(int argc,char **argv){
 assert(argc==2);struct mCore *c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
 color_t *pixels=calloc(240*160,sizeof(color_t));assert(pixels);c->setVideoBuffer(c,pixels,240);
 blip_set_rates(c->getAudioChannel(c,0),c->frequency(c),32768);
 blip_set_rates(c->getAudioChannel(c,1),c->frequency(c),32768);
 assert(mCoreLoadFile(c,argv[1]));c->reset(c);run(c,90);state(c,0);
 FILE *tile_file=fopen("assets/ui_tiles.bin","rb");assert(tile_file);
 for(unsigned i=0;i<UI_TILE_BYTES;i++){
  int expected=fgetc(tile_file);assert(expected>=0);
  assert(c->busRead8(c,0x06014000+i)==(unsigned)expected);
 }
 assert(fgetc(tile_file)==EOF);fclose(tile_file);
 capture(c,"build/title_v06.ppm");assert(energy>10000&&samples>1000);
 tap(c,8);state(c,1);capture(c,"build/menu_v06.ppm");
 assert((c->busRead16(c,0x04000000)&0x1040)==0x1040);
 assert((c->busRead16(c,0x07000004)&1023)==UI_CURSOR_TILE);
 assert((c->busRead16(c,0x07000000)&255)==34);
 tap(c,4);state(c,3);capture(c,"build/story_v06.ppm");
 for(int i=1;i<8;i++){tap(c,1);state(c,3);assert(value(c,2)==(unsigned)i);}
 tap(c,2);assert(value(c,2)==6);tap(c,8);state(c,1);
 tap(c,128);tap(c,1);state(c,4);tap(c,1);assert(value(c,3)==0);
 capture(c,"build/options_v06.ppm");
 tap(c,1);assert(value(c,3)==1);tap(c,128);assert(value(c,4)==0);
 tap(c,2);state(c,1);tap(c,64);tap(c,1);state(c,6);
 capture(c,"build/arrival_v06.ppm");
 assert((c->busRead16(c,0x07000004)&1023)==UI_PORTRAIT_TILE);
 assert((c->busRead16(c,0x07000000)&255)==102);
 tap(c,1);state(c,6);assert(value(c,13)==1);
 capture(c,"build/arrival2_v06.ppm");tap(c,1);state(c,7);
 int x,y;player(c,&x,&y);assert(x==40&&y==118);
 capture(c,"build/room_idle_v06.ppm");
 check_rest_background(c,"assets/room.bin",109,62);
 audio_file=fopen("build/level_emulated_s16le.pcm","wb");assert(audio_file);audio_frames=0;
 unsigned logic_start=value(c,16);run(c,180);
 fprintf(stderr,"Level performance: %u logic updates in 180 emulated display frames\n",value(c,16)-logic_start);
 fclose(audio_file);audio_file=NULL;
 c->setKeys(c,16);run(c,20);c->setKeys(c,1);run(c,8);c->setKeys(c,0);
 player(c,&x,&y);assert(x>40&&y<118);capture(c,"build/room_jump_v06.ppm");run(c,160);
 player(c,&x,&y);assert(y+40==game_floor(x+7));
 move_to(c,16,107);c->setKeys(c,64);run(c,25);c->setKeys(c,0);run(c,3);
 assert(value(c,11)==1);capture(c,"build/room_climb_v06.ppm");
 c->setKeys(c,64);for(int i=0;i<100&&value(c,10)==0;i++)run(c,1);
 run(c,3);assert(value(c,19)>0);
 assert((c->busRead16(c,0x07000004)&1023)==UI_GEM_TILE);
 assert((c->busRead16(c,0x0700000c)&1023)==UI_DIGIT1_TILE);
 capture(c,"build/pickup_hud_v06.ppm");
 run(c,200);c->setKeys(c,0);run(c,4);
 assert(value(c,19)==0&&(c->busRead16(c,0x07000000)&0x200));
 assert(value(c,10)==1&&value(c,12)==1&&value(c,11)==0);player(c,&x,&y);assert(y==48);
 capture(c,"build/room_gem_v06.ppm");
 move_to(c,16,139);c->setKeys(c,17);run(c,10);
 for(int i=0;i<100;i++){
  if(value(c,14)==1&&(int)value(c,9)==0)break;
  run(c,1);
 }
 c->setKeys(c,0);run(c,10);
 player(c,&x,&y);assert(y==0&&value(c,14)==1);assert((int)value(c,15)==-40);
 capture(c,"build/room_upper_v06.ppm");
 c->setKeys(c,16);
 for(int i=0;i<200&&value(c,17)==0;i++){
  int before_x=(int)value(c,8),before_y=(int)value(c,9);
  run(c,1);
  if(value(c,17)==1){
   assert((int)value(c,8)+AREA_OFFSET_X*256-before_x==320);
   assert((int)value(c,9)-AREA_OFFSET_Y*256==before_y);
  }
 }
 c->setKeys(c,0);run(c,5);assert(value(c,17)==1);state(c,7);
 capture(c,"build/bridge_entry_v06.ppm");
 check_rest_background(c,"assets/bridge.bin",133,74);
 c->setKeys(c,33);for(int i=0;i<300&&value(c,18)==0;i++)run(c,1);
 c->setKeys(c,0);run(c,5);assert(value(c,17)==1&&value(c,18)==1&&value(c,10)==1);
 capture(c,"build/bridge_respawn_v06.ppm");
 move_to(c,16,141);assert(value(c,10)==2&&value(c,12)==3);
 capture(c,"build/bridge_gem_v06.ppm");
 assert(value(c,19)>0&&(c->busRead16(c,0x0700000c)&1023)==UI_DIGIT2_TILE);
 c->setKeys(c,16);run(c,1);
 for(int i=0;i<16&&!((value(c,16)>>3)&1);i++)run(c,1);
 capture(c,"build/bridge_walk_v06.ppm");c->setKeys(c,0);run(c,4);
 c->setKeys(c,1);run(c,12);c->setKeys(c,0);run(c,2);
 capture(c,"build/bridge_jump_v06.ppm");run(c,100);
 c->setKeys(c,16);
 for(int i=0;i<180&&value(c,17)==1;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==2);
 capture(c,"build/cliff_entry.ppm");
 c->setKeys(c,16);run(c,5);c->setKeys(c,17);run(c,90);c->setKeys(c,0);run(c,60);
 assert(value(c,17)==2&&value(c,14)==1&&(int)value(c,9)==75*256);
 capture(c,"build/cliff_landing.ppm");
 unsigned old_falls=value(c,18);c->setKeys(c,32);
 for(int i=0;i<300&&value(c,18)==old_falls;i++)run(c,1);
 assert(value(c,18)==old_falls+1);c->setKeys(c,0);run(c,4);
 c->setKeys(c,32);for(int i=0;i<60&&value(c,17)==2;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==1&&value(c,10)==2);
 c->setKeys(c,32);
 for(int i=0;i<200&&value(c,17)==1;i++){
  int before_x=(int)value(c,8)+AREA_OFFSET_X*256,before_y=(int)value(c,9)-AREA_OFFSET_Y*256;
  run(c,1);
  if(value(c,17)==0){assert((int)value(c,8)-before_x==-320);assert((int)value(c,9)==before_y);}
 }
 c->setKeys(c,0);run(c,5);assert(value(c,17)==0&&value(c,10)==2);
 assert(value(c,21)==2&&value(c,20)==value(c,16));
 capture(c,"build/return_ridge_v06.ppm");
 tap(c,8);state(c,8);unsigned ticks=value(c,6);run(c,60);assert(value(c,6)==ticks);
 unsigned run_ticks=value(c,20);run(c,60);assert(value(c,20)==run_ticks);
 capture(c,"build/pause_v06.ppm");tap(c,1);state(c,7);
 tap(c,256);state(c,7);assert(value(c,10)==0);player(c,&x,&y);assert(x==40&&y==118);
 run(c,15200);state(c,7);assert(value(c,7)==0);
 move_to(c,16,166);tap(c,128);state(c,9);capture(c,"build/sign_v06.ppm");tap(c,1);state(c,7);
 tap(c,4);state(c,1);assert(value(c,7)==0);
 tap(c,64);tap(c,1);state(c,5);capture(c,"build/credits_v06.ppm");tap(c,2);state(c,1);
 tap(c,64);tap(c,1);state(c,4);assert(value(c,4)==0);
 tap(c,2);tap(c,64);tap(c,1);state(c,6);assert(value(c,1)==0);
 printf("PASS frontend no-intro: %u emulated frames; linked areas, camera, pickups, pause, menus, direct arrival without intro\n",c->frameCounter(c));
 /* Exercise settings through the actual menu before resetting the CPU. */
 tap(c,2);state(c,1);tap(c,128);tap(c,1);state(c,4);
 /* Entering OPTIONS always selects SOUND. */
 tap(c,1);assert(value(c,3)==0);
 tap(c,128);assert(value(c,4)==0);
 assert(c->busRead8(c,0x0E000000)=='L');
 assert(c->busRead8(c,0x0E000005)==0);
 c->setKeys(c,0);c->reset(c);run(c,90);state(c,0);
 assert(value(c,3)==0&&value(c,4)==0&&value(c,7)==0);
 tap(c,8);tap(c,128);tap(c,1);state(c,4);
 capture(c,"build/options_saved.ppm");
 /* A damaged checksum must select documented defaults on the next boot. */
 c->busWrite8(c,0x0E000006,c->busRead8(c,0x0E000006)^1);
 c->setKeys(c,0);c->reset(c);run(c,90);state(c,0);
 assert(value(c,3)==1&&value(c,4)==0);
 puts("PASS settings integration: menu writes SRAM, soft-reset reload, corrupt-record defaults. Disk save reload and real hardware are not tested.");
 /* Verify actual fall damage, Game Over, frozen state and retry. */
 tap(c,8);tap(c,128);tap(c,1);state(c,4);
 tap(c,2);tap(c,64);tap(c,1);state(c,6);
 tap(c,1);tap(c,1);state(c,7);assert(value(c,22)==3);
 move_to(c,16,107);c->setKeys(c,64);run(c,100);c->setKeys(c,0);run(c,4);
 move_to(c,16,139);c->setKeys(c,17);run(c,45);c->setKeys(c,0);run(c,40);
 c->setKeys(c,16);for(int i=0;i<160&&value(c,17)==0;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==1);
 for(unsigned death=0;death<3;death++){
  c->setKeys(c,33);for(int i=0;i<300&&value(c,18)==death;i++)run(c,1);
  c->setKeys(c,0);run(c,4);assert(value(c,18)==death+1&&value(c,31)==2-death&&value(c,22)==(death==2?0u:3u));
 }
 state(c,10);assert(value(c,23)==1&&value(c,7)==0);
 capture(c,"build/game_over.ppm");unsigned stopped=value(c,16);run(c,90);assert(value(c,16)==stopped);
 tap(c,1);state(c,7);assert(value(c,22)==3&&value(c,31)==3&&value(c,18)==0&&value(c,10)==0);
 capture(c,"build/retry_after_game_over.ppm");
 puts("PASS defeat integration: three life-consuming falls, restored HP, Game Over, frozen simulation, retry resets run");
 /* Reach the new native guard area and exercise contact and sword damage. */
 move_to(c,16,107);c->setKeys(c,64);run(c,100);c->setKeys(c,0);run(c,4);
 move_to(c,16,139);c->setKeys(c,17);run(c,45);c->setKeys(c,0);run(c,40);
 c->setKeys(c,16);for(int i=0;i<160&&value(c,17)==0;i++)run(c,1);
 for(int i=0;i<180&&value(c,17)==1;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==2);
 c->setKeys(c,16);run(c,5);c->setKeys(c,17);run(c,90);c->setKeys(c,0);run(c,60);
 c->setKeys(c,16);for(int i=0;i<160&&value(c,17)==2;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==3);
 capture(c,"build/guard_entry.ppm");
 move_to(c,16,160);for(int i=0;i<240&&value(c,22)==3;i++)run(c,1);
 assert(value(c,22)==2&&value(c,24)>0);capture(c,"build/guard_contact.ppm");
 /* Keep contact until a lethal enemy hit; respawn must preserve the run. */
 unsigned lives_before_combat=value(c,31),gems_before_combat=value(c,10);
 c->setKeys(c,0);
 for(int i=0;i<1400&&value(c,31)==lives_before_combat;i++)run(c,1);
 assert(value(c,31)==lives_before_combat-1&&value(c,22)==3&&value(c,24)>0);
 assert(value(c,17)==3&&value(c,10)==gems_before_combat&&value(c,25)==2);state(c,7);
 capture(c,"build/combat_respawn.ppm");
 puts("PASS lethal combat integration: one life consumed, HP restored, same area and gems preserved");
 move_to(c,16,120);c->setKeys(c,16);run(c,1);c->setKeys(c,0);run(c,1);
 for(int i=0;i<40&&value(c,25)>0;i++){tap(c,2);run(c,8);}
 assert(value(c,25)==0&&value(c,26)==1);state(c,7);
 capture(c,"build/guard_defeated.ppm");
 puts("PASS combat integration: guard area, contact damage, sword defeat and persistent defeat counter");
 /* Actual-ROM validation of recorded animation, new gap, pickups and UI. */
 unsigned motion_seen=0,previous_motion=3;
 c->setKeys(c,16);
 for(int i=0;i<24;i++){
  run(c,1);unsigned f=value(c,28);
  if(previous_motion==f&&!(motion_seen&(1u<<f))){char path[64];snprintf(path,sizeof(path),"build/walk_frame_%u.ppm",f);capture(c,path);}
  if(previous_motion==f)motion_seen|=1u<<f;
  previous_motion=f;
 }
 c->setKeys(c,0);run(c,4);assert(motion_seen==7);
 assert(value(c,10)==3&&(c->busRead16(c,0x0700000c)&1023)==704);
 capture(c,"build/pickup_three.ppm");
 c->setKeys(c,2);run(c,2);assert(value(c,29)==0);capture(c,"build/sword_windup.ppm");
 run(c,4);assert(value(c,29)==1);capture(c,"build/sword_active.ppm");
 run(c,5);assert(value(c,29)==2);capture(c,"build/sword_recovery.ppm");
 c->setKeys(c,0);run(c,8);
 c->setKeys(c,16);
 for(int i=0;i<180&&value(c,17)==3;i++){
  int bx=(int)value(c,8),by=(int)value(c,9);run(c,1);
  if(value(c,17)==4){assert((int)value(c,8)+158*256-bx==320);assert((int)value(c,9)-18*256==by);}
 }
 c->setKeys(c,0);run(c,4);assert(value(c,17)==4);capture(c,"build/gap_entry.ppm");
 move_to(c,16,94);c->setKeys(c,17);run(c,60);c->setKeys(c,0);run(c,4);
 assert(value(c,17)==4&&value(c,14)==1&&(int)value(c,9)==58*256);
 assert(value(c,10)==4&&value(c,12)==15);
 assert((c->busRead16(c,0x0700000c)&1023)==712);capture(c,"build/gap_pickup_four.ppm");
 for(int i=0;i<15&&value(c,30);i++){tap(c,2);run(c,8);}
 assert(value(c,30)==0&&value(c,26)==2);capture(c,"build/gap_guard_defeated.ppm");
 unsigned falls_before=value(c,18),lives_before=value(c,31);
 c->setKeys(c,32);for(int i=0;i<240&&value(c,18)==falls_before;i++)run(c,1);
 c->setKeys(c,0);run(c,4);
 assert(value(c,18)==falls_before+1&&value(c,31)==lives_before-1&&value(c,22)==3&&value(c,10)==4&&value(c,17)==4);
 capture(c,"build/gap_respawn.ppm");
 c->setKeys(c,32);for(int i=0;i<100&&value(c,17)==4;i++)run(c,1);
 c->setKeys(c,0);run(c,4);assert(value(c,17)==3&&value(c,10)==4&&value(c,26)==2);
 puts("PASS motion/gap integration: three recorded walk frames, three attack phases, registered fifth viewport, gap jump and fall, four persistent gems, OBJ digits 3/4, second guard defeat, return persistence");
 c->deinit(c);free(pixels);
}
