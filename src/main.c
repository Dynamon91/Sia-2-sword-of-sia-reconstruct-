#include "game.h"
#include "settings.h"
/* Standard emulator SRAM detection marker. */
static const char save_type[] __attribute__((used))="SRAM_V113";
#define SETTINGS_SRAM ((volatile unsigned char *)0x0E000000)
#include "alignment.h"
#include "scenery.h"
#include "story.h"
#include "../assets/assets.h"
#include "../assets/room.h"
#include "../assets/ui.h"
extern const unsigned char continuation_background[],bridge_run_background[],riser_background[],upper_background[],ui_digit5_tiles[];
extern const unsigned char cliff_background[],guard_background[],guard_sprite[];
extern const unsigned char ambient_gems[],ledge_cycle[],jump_cycle[],cloud_strip[];
extern const unsigned char gap_background[],guard2_sprite[],walk_cycle[],attack_cycle[],ui_more_tiles[];
extern const unsigned char bridge_background[],bridge_sky[],bridge_run[];
extern const unsigned char room_backdrop[],room_spans[],bridge_backdrop[],bridge_spans[];
typedef unsigned short u16;
#define REG16(a) (*(volatile u16 *)(a))
#define REG32(a) (*(volatile unsigned *)(a))
#define RGB(r,g,b) ((r)|((g)<<5)|((b)<<10))
enum { TITLE,MENU,INTRO,STORY,OPTIONS,CREDITS,ARRIVAL,LAB,PAUSE,TUTORIAL,GAME_OVER };
static volatile u16 *page;
static const u16 *pending_palette;
static unsigned front,state,selection,story_index,option_index,dirty;
static unsigned sound_enabled,intro_enabled,paused,previous_keys;
static unsigned clock_ticks,clock_last,audio_end,audio_active,intro_frame;
static unsigned arrival_index;
static u16 object_shadow[128*4];
static Game game;
static const u16 lab_palette[256]={
 RGB(3,5,10),RGB(8,12,18),RGB(10,18,19),RGB(25,21,12),RGB(23,10,15),RGB(30,29,24),
 [240]=0,[241]=RGB(31,31,31),[242]=RGB(31,26,10),[243]=RGB(10,27,30),[244]=RGB(1,3,6),[245]=RGB(27,12,17)
};
static inline __attribute__((always_inline)) void pixel(int x,int y,unsigned color){
 if((unsigned)x>=240||(unsigned)y>=160)return;
 volatile u16 *p=page+y*120+(x>>1);u16 v=*p;
 *p=(x&1)?(u16)((v&255)|(color<<8)):(u16)((v&65280)|color);
}
static void rect(int x,int y,int w,int h,unsigned color){
 int x2=x+w,y2=y+h;if(x<0)x=0;if(y<0)y=0;if(x2>240)x2=240;if(y2>160)y2=160;
 if(x>=x2||y>=y2)return;
 u16 pair=(u16)(color|(color<<8));
 for(int py=y;py<y2;py++){
  int px=x;volatile u16 *p=page+py*120+(px>>1);
  if(px&1){*p=(u16)((*p&255)|(color<<8));++p;++px;}
  for(;px+1<x2;px+=2)*p++=pair;
  if(px<x2)*p=(u16)((*p&65280)|color);
 }
}
static void text(int x,int y,const char *s,unsigned color){
 int origin=x;
 for(;*s;s++){
  if(*s=='\n'){x=origin;y+=10;continue;}
  unsigned c=(unsigned char)*s;if(c<32||c>127)c='?';
  const unsigned char *glyph=asset_font+(c-32)*8;
  for(int row=0;row<8;row++)for(int bit=0;bit<6;bit++)
   if(glyph[row]&(1u<<bit))pixel(x+bit,y+row,color);
  x+=6;
 }
}
static void wrapped(int x,int y,const char *s,unsigned color){
 int origin=x;
 while(*s){
  if(*s==' '){x+=6;s++;continue;}
  if(*s=='\n'){x=origin;y+=10;s++;continue;}
  int len=0;while(s[len]&&s[len]!=' '&&s[len]!='\n')len++;
  if(x+len*6>228){x=origin;y+=10;}
  for(int i=0;i<len;i++){
   char one[2];one[0]=*s++;one[1]=0;text(x,y,one,color);x+=6;
  }
 }
}
static void number(int x,int y,unsigned value,unsigned color){
 char b[11];unsigned n=0;
 do{b[n++]=(char)('0'+value%10);value/=10;}while(value);
 for(unsigned i=0;i<n/2;i++){char t=b[i];b[i]=b[n-i-1];b[n-i-1]=t;}
 b[n]=0;text(x,y,b,color);
}
static void image(const unsigned char *p){
 pending_palette=(const u16*)p;
 REG32(0x040000D4)=(unsigned)(p+512);REG32(0x040000D8)=(unsigned)page;
 REG32(0x040000DC)=0x84000000|9600;
}
static void blit(unsigned frame){image(assets_visuals+frame*ASSET_FRAME_BYTES);}
static void clear(void){
 const volatile unsigned zero=0;
 pending_palette=lab_palette;
 REG32(0x040000D4)=(unsigned)&zero;REG32(0x040000D8)=(unsigned)page;
 REG32(0x040000DC)=0x85000000|9600;
}
static void wait_frame(void){
 while(REG16(0x04000006)>=160){}
 while(REG16(0x04000006)<160){}
}
static void ui_init(void){
 REG32(0x040000D4)=(unsigned)ui_palette;REG32(0x040000D8)=0x05000200;
 REG32(0x040000DC)=0x84000000|128;
 REG32(0x040000D4)=(unsigned)ui_tiles;REG32(0x040000D8)=0x06014000;
 REG32(0x040000DC)=0x84000000|(UI_TILE_BYTES/4);
 REG32(0x040000D4)=(unsigned)ui_more_tiles;REG32(0x040000D8)=0x06014000+UI_TILE_BYTES;
 REG32(0x040000DC)=0x84000000|128;
 REG32(0x040000D4)=(unsigned)ui_digit5_tiles;REG32(0x040000D8)=0x06010000+720*32;
 REG32(0x040000DC)=0x84000000|64;
}
static void ui_hide(void){for(unsigned i=0;i<128;i++)object_shadow[i*4]=0x0200;}
static void ui_object(unsigned slot,unsigned x,unsigned y,unsigned size,unsigned tile){
 object_shadow[slot*4]=(u16)((y&255)|0x2000);
 object_shadow[slot*4+1]=(u16)((x&511)|(size<<14));
 object_shadow[slot*4+2]=(u16)tile;
}
static void present(void){
 wait_frame();
 REG32(0x040000D4)=(unsigned)pending_palette;REG32(0x040000D8)=0x05000000;
 REG32(0x040000DC)=0x84000000|128;
 REG32(0x040000D4)=(unsigned)object_shadow;REG32(0x040000D8)=0x07000000;
 REG32(0x040000DC)=0x84000000|256;
 front^=1;REG16(0x04000000)=(u16)(0x1444|(front?16:0));
}
static void clock_start(void){
 REG16(0x0400010A)=0;REG16(0x04000108)=0;
 clock_ticks=0;clock_last=0;REG16(0x0400010A)=0x83;
}
static void clock_update(void){
 unsigned now=REG16(0x04000108);
 if(!paused)clock_ticks+=(u16)(now-clock_last);
 clock_last=now;
}
static void audio_stop(void){
 REG32(0x040000C4)=0;REG16(0x04000102)=0;audio_active=0;
 REG16(0x04000082)=0x0B04;
}
static void audio_play(const unsigned char *p,unsigned length){
 audio_stop();audio_end=clock_ticks+length;
 if(!sound_enabled||!length)return;
 REG16(0x04000084)=0x80;REG16(0x04000082)=0x0B04;
 REG32(0x040000BC)=(unsigned)p;REG32(0x040000C0)=0x040000A0;
 REG32(0x040000C4)=0xB6400004;
 REG16(0x04000100)=0xFC00;REG16(0x04000102)=0x80;audio_active=1;
}
static void enter(unsigned next){state=next;dirty=1;}
static void arrival(void){audio_stop();paused=0;arrival_index=0;game_reset(&game);enter(ARRIVAL);}
static void return_menu(void){audio_stop();paused=0;enter(MENU);}
static void start_level(void){
 paused=0;game_reset(&game);game.previous=JUMP|ATTACK;
 clock_start();audio_play(audio_level,AUDIO_LEVEL_LEN);enter(LAB);
}
static void resume_level(void){
 paused=0;game.previous|=JUMP|ATTACK;
 unsigned offset=clock_ticks&~3u;
 if(offset<AUDIO_LEVEL_LEN)audio_play(audio_level+offset,AUDIO_LEVEL_LEN-offset);
 enter(LAB);
}
static void footer(const char *s){rect(0,149,240,11,240);text(4,151,s,241);}
static void dialog(unsigned index){
 const StoryPage *p=&story[index];blit(p->frame);
 rect(0,78,240,82,244);rect(0,78,240,1,242);
 text(10,83,p->speaker,242);text(188,83,p->time,243);
 wrapped(10,98,p->text,241);
}
static void sprite(int x,int y,int w,int h,const unsigned char *pixels,int flip){
 for(int row=0;row<h;row++)for(int col=0;col<w;col++){
  unsigned p=pixels[row*w+(flip?w-col-1:col)];
  if(p)pixel(x+col,y+row,p);
 }
}
static void draw_clouds(unsigned phase){
 const unsigned char *bank=cloud_strip+(phase&1u)*CLOUD_BANK_BYTES;
 unsigned offset=phase&~1u;
 unsigned first=CLOUD_WIDTH-offset;if(first>240)first=240;
 for(unsigned y=0;y<CLOUD_HEIGHT;y++){
  const unsigned char *row=bank+y*CLOUD_WIDTH;
  REG32(0x040000D4)=(unsigned)(row+offset);REG32(0x040000D8)=(unsigned)(page+y*120);
  REG32(0x040000DC)=0x80000000|(first/2);
  if(first<240){
   REG32(0x040000D4)=(unsigned)row;REG32(0x040000D8)=(unsigned)(page+y*120+first/2);
   REG32(0x040000DC)=0x80000000|((240-first)/2);
  }
 }
}
static void draw_level(void){
 const unsigned char *background=game.area?bridge_backdrop:room_backdrop;
 const unsigned char *spans=game.area?bridge_spans:room_spans;
 int shift=-game.camera_y;
 if(game.area==8)image(upper_background);else if(game.area==7)image(riser_background);else if(game.area==6)image(bridge_run_background);else if(game.area==5)image(continuation_background);else if(game.area==4)image(gap_background);else if(game.area==3)image(guard_background);else if(game.area==2)image(cliff_background);else image(background);
 if(game.area<2)draw_clouds(cloud_phase(game.ticks));
 for(int row=0;row<160-shift&&game.area<2;row++){
  unsigned count=spans[0]|((unsigned)spans[1]<<8);spans+=2;
  for(unsigned run=0;run<count;run++){
   int x=spans[0];unsigned length=spans[1];spans+=2;
   const unsigned char *pixels=spans;spans+=length+(length&1);
   int y=row+shift;unsigned n=length;
   if(x&1){pixel(x++,y,*pixels++);n--;}
   if(!((unsigned)pixels&1)&&n>=2){
    REG32(0x040000D4)=(unsigned)pixels;REG32(0x040000D8)=(unsigned)(page+y*120+x/2);
    REG32(0x040000DC)=0x80000000|(n/2);
    if(n&1)pixel(x+(int)n-1,y,pixels[n-1]);
   }else{
    volatile u16 *dst=page+y*120+x/2;
    while(n>=2){*dst++=(u16)(pixels[0]|((unsigned)pixels[1]<<8));pixels+=2;n-=2;x+=2;}
    if(n)pixel(x,y,*pixels);
   }
  }
 }
 for(unsigned i=0;i<GEM_COUNT;i++){
  const Gem *gem=&level_gems[i];
  if(gem->area==game.area&&!(game.collected&(1u<<gem->id)))
   sprite(gem->x,gem->y-game.camera_y,16,16,ambient_gems+((game.ticks/8)%4)*256,0);
 }
 if(game.area==3&&game.enemy_hp&&(!game.enemy_flash||(game.enemy_flash&2)))
  sprite(game.enemy_x/FP+9-20,88-55,41,60,guard_sprite,game.enemy_dir>0);
 if((game.area==4||game.area==5)&&game.enemy2_hp&&(!game.enemy2_flash||(game.enemy2_flash&2)))
  sprite(game.enemy2_x/FP+9-15-(game.area==5?188:0),98-51+(game.area==5?25:0),34,55,guard2_sprite,game.enemy2_dir>0);
 if((game.area==6||game.area==7)&&game.enemy3_hp&&(!game.enemy3_flash||(game.enemy3_flash&2)))
  sprite(game.enemy3_x/FP+9-20-(game.area==7?168:0),104-55+(game.area==7?7:0),41,60,guard_sprite,game.enemy3_dir>0);
 unsigned air=game_air_frame(&game);
 const unsigned char *actor=room_sprites;
 int width=48,height=56,anchor=24;
 if(game.attack&&!game.climbing){
  width=80;height=64;anchor=39;actor=attack_cycle+game_attack_frame(&game)*80*64;
 }else if(air!=AIR_NONE){
  width=56;anchor=28;actor=jump_cycle+air*56*56;
 }else if(game.grounded&&game.vx)actor=walk_cycle+game_walk_frame(&game)*ROOM_SPRITE_SIZE;
 if(game.climbing){
  sprite(game.x/FP+PLAYER_W/2-24,game.ledge_y-44-game.camera_y,
         48,104,ledge_cycle+game_ledge_frame(&game)*48*104,0);
 }else if(!game.hurt_timer||(game.hurt_timer&4))sprite(aligned_sprite_x(game.x/FP+PLAYER_W/2,width,anchor,game.facing<0),game.y/FP+PLAYER_H-height-game.camera_y,
        width,height,actor,game.facing<0);
 if(game.pickup_timer>0){
  ui_object(0,95,11,2,UI_GEM_TILE);
  ui_object(1,129,29,1,game.gems==5?720:game.gems==4?712:game.gems==3?704:game.gems==2?UI_DIGIT2_TILE:game.gems?UI_DIGIT1_TILE:UI_DIGIT0_TILE);
 }
}
static void draw_arrival(void){
 draw_level();ui_object(0,0,102,3,UI_PORTRAIT_TILE);
 const unsigned char *ink=ui_dialogs+arrival_index*(UI_DIALOG_W*UI_DIALOG_H);
 for(int y=0;y<UI_DIALOG_H;y++)for(int x=0;x<UI_DIALOG_W;x++){
  unsigned p=ink[y*UI_DIALOG_W+x];if(p)pixel(64+x,102+y,p==1?240:241);
 }
}
static void render(void){
 page=(volatile u16*)(front?0x06000000:0x0600A000);
 ui_hide();
 switch(state){
 case TITLE:blit(FRAME_TITLE);break;
 case MENU:
  blit(FRAME_MENU);
  ui_object(0,16,(44+(int)selection*24-12)*160/148,1,UI_CURSOR_TILE);break;
 case STORY:
  dialog(story_index);footer("A NEXT B BACK START MENU");
  number(148,83,story_index+1,243);break;
 case ARRIVAL:
  draw_arrival();break;
 case OPTIONS:
  clear();text(18,20,"OPTIONS",242);
  text(24,50,sound_enabled?"SOUND       ON":"SOUND       OFF",241);
  text(24,72,"BACK",241);ui_object(0,3,46+option_index*22,1,UI_CURSOR_TILE);
  footer("A CHANGE  B MENU");break;
 case CREDITS:
  clear();text(15,20,"RECONSTRUCTION CREDITS",242);
  wrapped(15,44,"Unofficial recreation.\nLady Sia 2: RFX Interactive\nOriginal publisher: TDK\nVideo reference: Papacube\nNative frontend: v0.6\nOriginal staff roll not shown\nin this supplied level video.",241);
  footer("A/B RETURN TO MENU");break;
 case LAB:draw_level();break;
 case GAME_OVER:
  draw_level();rect(24,43,192,86,244);text(66,53,"GAME OVER",242);
  text(40,77,"A / START: RETRY",241);text(40,96,"B: MAIN MENU",241);
  text(40,115,"RETRY RESETS THE RUN",243);break;
 case PAUSE:
  draw_level();rect(35,42,170,84,244);text(52,51,"PAUSED",242);
  text(48,69,"HP",241);number(66,69,game.progress.health,241);
  text(96,69,"LIVES",241);number(132,69,game.lives,241);
  text(48,90,"A RESUME",241);text(48,107,"B MAIN MENU",241);break;
 case TUTORIAL:
  draw_level();rect(5,87,230,69,244);text(12,94,"CONTROLS",242);
  wrapped(12,108,"A: jump / pull up. B: attack.\nUP: pull up. DOWN: let go.\nSTART: pause. SELECT: menu.",241);
  text(12,143,"A / B: CONTINUE",243);break;
 }
 present();dirty=0;
 /* Snapshot the displayed pose after the page flip, rather than the next
    physics update. Native-frame tests can then check a moving sprite exactly. */
 volatile unsigned *shown=(volatile unsigned*)0x0203F100;
 shown[0]=state;shown[1]=(unsigned)game.x;shown[2]=(unsigned)game.y;
 shown[3]=(unsigned)game.camera_y;shown[4]=game_air_frame(&game);
 shown[5]=(unsigned)game.facing;shown[6]=game.attack?game_attack_frame(&game):3;
 shown[7]=(unsigned)game.climbing;shown[8]=(unsigned)game.grounded;
 shown[9]=game.ticks;shown[10]=front;
 shown[11]=(unsigned)game.area;shown[12]=cloud_phase(game.ticks);
}
int main(void){
 REG16(0x04000204)=0x4317;REG16(0x04000000)=0x0404;
 REG16(0x04000088)=0x200;ui_init();
 settings_load(SETTINGS_SRAM,&sound_enabled,&intro_enabled);intro_enabled=0;dirty=1;game_reset(&game);
 clock_start();audio_play(audio_title,AUDIO_TITLE_LEN);
 for(;;){
  clock_update();
  if(audio_active&&clock_ticks>=audio_end)audio_stop();
  unsigned keys=(~REG16(0x04000130))&1023;
  unsigned pressed=keys&~previous_keys;previous_keys=keys;
  switch(state){
  case TITLE:if(pressed&9)enter(MENU);break;
  case MENU:
   if(pressed&2){enter(TITLE);break;}
   if(pressed&64){selection=(selection+2)%3;dirty=1;}
   if(pressed&128){selection=(selection+1)%3;dirty=1;}
   if(pressed&4){audio_stop();story_index=0;enter(STORY);}
   else if(pressed&9){
    audio_stop();
    if(selection==0)arrival();
    if(selection==1){option_index=0;enter(OPTIONS);}
    if(selection==2)enter(CREDITS);
   }break;
  case STORY:
   if(pressed&12){enter(MENU);break;}
   if(pressed&(2|32)){if(story_index)story_index--;else enter(MENU);dirty=1;}
   if(pressed&(1|16)){if(story_index+1<story_count)story_index++;else enter(MENU);dirty=1;}
   break;
  case ARRIVAL:
   if(pressed&2)return_menu();
   else if(pressed&9){if(arrival_index==0){arrival_index=1;dirty=1;}else start_level();}
   break;
  case OPTIONS:
   if(pressed&2){enter(MENU);break;}
   if(pressed&64){option_index=(option_index+1)%2;dirty=1;}
   if(pressed&128){option_index=(option_index+1)%2;dirty=1;}
   if(pressed&(1|16|32)){
    if(option_index==0){sound_enabled^=1;audio_stop();}
    if(option_index==0)settings_store(SETTINGS_SRAM,sound_enabled,0);
    if(option_index==1)enter(MENU);
    dirty=1;
   }break;
  case CREDITS:if(pressed&11)enter(MENU);break;
  case LAB:
   if(pressed&8){paused=1;audio_stop();enter(PAUSE);break;}
   if(pressed&4){return_menu();break;}
   {unsigned input=0;
    if(keys&32)input|=LEFT;
    if(keys&16)input|=RIGHT;
    if(keys&1)input|=JUMP;
    if(keys&2)input|=ATTACK;
    if(keys&64)input|=UP;
    if(keys&128)input|=DOWN;
    if(pressed&256)input|=RESET;
    game_step(&game,input);dirty=1;
    if(game.game_over){paused=1;audio_stop();enter(GAME_OVER);}
    else if(game.sign_open){paused=1;audio_stop();enter(TUTORIAL);}
   }break;
  case GAME_OVER:
   if(pressed&9)start_level();
   else if(pressed&6)return_menu();
   break;
  case PAUSE:
   if(pressed&9)resume_level();
   else if(pressed&6)return_menu();
   break;
  case TUTORIAL:
   if(pressed&3){game.sign_open=0;resume_level();}
   else if(pressed&12){game.sign_open=0;return_menu();}
   break;
  }
  /* Test telemetry in unused EWRAM; never read as gameplay input. */
  volatile unsigned *debug=(volatile unsigned*)0x0203F000;
  debug[0]=state;debug[1]=intro_frame;debug[2]=story_index;
  debug[3]=sound_enabled;debug[4]=intro_enabled;debug[5]=paused;
  debug[6]=clock_ticks;debug[7]=audio_active;
  debug[8]=game.x;debug[9]=game.y;debug[10]=(unsigned)game.gems;
  debug[11]=(unsigned)game.climbing;debug[12]=(unsigned)game.collected;
  debug[13]=arrival_index;debug[14]=(unsigned)game.grounded;
  debug[15]=(unsigned)game.camera_y;
  debug[16]=game.ticks;
  debug[17]=(unsigned)game.area;debug[18]=(unsigned)game.falls;
  debug[19]=(unsigned)game.pickup_timer;
  debug[20]=game.progress.elapsed_frames;debug[21]=game.progress.gems;
  debug[22]=game.progress.health;debug[23]=(unsigned)game.game_over;debug[24]=(unsigned)game.hurt_timer;
  debug[25]=(unsigned)game.enemy_hp;debug[26]=game.progress.defeated;debug[27]=(unsigned)game.enemy_x;
  debug[31]=game.lives;debug[32]=game_ledge_frame(&game);debug[33]=game.ledge_ticks;debug[34]=(unsigned)game.ledge_y;
  debug[28]=game_walk_frame(&game);debug[29]=game.attack?game_attack_frame(&game):3;debug[30]=(unsigned)game.enemy2_hp;
  debug[35]=game_air_frame(&game);debug[36]=(unsigned)game.vy;debug[37]=(unsigned)game.facing;
  debug[38]=(unsigned)game.enemy3_hp;debug[39]=(unsigned)game.enemy3_x;
  if(dirty)render();else wait_frame();
 }
}
