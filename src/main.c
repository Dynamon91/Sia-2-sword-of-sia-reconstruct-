#include "game.h"
#include "settings.h"
/* Standard emulator SRAM detection marker. */
static const char save_type[] __attribute__((used))="SRAM_V113";
#define SETTINGS_SRAM ((volatile unsigned char *)0x0E000000)
#include "alignment.h"
#include "story.h"
#include "../assets/assets.h"
#include "../assets/room.h"
#include "../assets/ui.h"
extern const unsigned char bridge_background[],bridge_sky[],bridge_run[];
extern const unsigned char room_backdrop[],room_spans[],bridge_backdrop[],bridge_spans[];
typedef unsigned short u16;
#define REG16(a) (*(volatile u16 *)(a))
#define REG32(a) (*(volatile unsigned *)(a))
#define RGB(r,g,b) ((r)|((g)<<5)|((b)<<10))
enum { TITLE,MENU,INTRO,STORY,OPTIONS,CREDITS,ARRIVAL,LAB,PAUSE,TUTORIAL };
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
static void start_intro(void){
 paused=0;intro_frame=0;clock_start();audio_play(audio_intro,AUDIO_INTRO_LEN);enter(INTRO);
}
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
static void draw_level(void){
 const unsigned char *background=game.area?bridge_backdrop:room_backdrop;
 const unsigned char *spans=game.area?bridge_spans:room_spans;
 int shift=-game.camera_y;
 image(background);
 for(int row=0;row<160-shift;row++){
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
 if(!(game.collected&(1<<game.area)))sprite(game.area?133:109,(game.area?74:62)-game.camera_y,16,16,room_sprites+ROOM_GEM_OFFSET,0);
 unsigned pose=game.climbing?2:game.attack?3:!game.grounded?1:0;
 const unsigned char *actor=room_sprites+pose*ROOM_SPRITE_SIZE;
 if(!pose&&game.vx&&((game.ticks>>3)&1))actor=bridge_run;
 sprite(aligned_sprite_x(game.x/FP+PLAYER_W/2,ROOM_SPRITE_W,SIA_ANCHOR_X,game.facing<0),game.y/FP+PLAYER_H-SIA_ANCHOR_Y-game.camera_y,
        ROOM_SPRITE_W,ROOM_SPRITE_H,actor,game.facing<0);
 if(game.pickup_timer>0){
  ui_object(0,95,11,2,UI_GEM_TILE);
  ui_object(1,129,29,1,game.gems>=2?UI_DIGIT2_TILE:game.gems?UI_DIGIT1_TILE:UI_DIGIT0_TILE);
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
  ui_object(0,16,44+selection*24,1,UI_CURSOR_TILE);break;
 case INTRO:
  blit(INTRO_FIRST+intro_frame);
  rect(0,0,211,12,240);text(3,2,paused?"A RESUME  START SKIP":"A PAUSE   START SKIP",241);break;
 case STORY:
  dialog(story_index);footer("A NEXT B BACK START MENU");
  number(148,83,story_index+1,243);break;
 case ARRIVAL:
  draw_arrival();break;
 case OPTIONS:
  clear();text(18,20,"OPTIONS",242);
  text(24,50,sound_enabled?"SOUND       ON":"SOUND       OFF",241);
  text(24,72,intro_enabled?"INTRO       ON":"INTRO       OFF",241);
  text(24,94,"BACK",241);ui_object(0,3,46+option_index*22,1,UI_CURSOR_TILE);
  footer("A CHANGE  B MENU");break;
 case CREDITS:
  clear();text(15,20,"RECONSTRUCTION CREDITS",242);
  wrapped(15,44,"Unofficial recreation.\nLady Sia 2: RFX Interactive\nOriginal publisher: TDK\nVideo reference: Papacube\nNative frontend: v0.6\nOriginal staff roll not shown\nin this supplied level video.",241);
  footer("A/B RETURN TO MENU");break;
 case LAB:draw_level();break;
 case PAUSE:
  draw_level();rect(35,53,170,59,244);text(52,62,"PAUSED",242);
  text(48,80,"A RESUME",241);text(48,95,"B MAIN MENU",241);break;
 case TUTORIAL:
  draw_level();rect(5,87,230,69,244);text(12,94,"CONTROLS",242);
  wrapped(12,108,"UP / DOWN: climb the ladder.\nA: jump. B: attack.\nSTART: pause. SELECT: menu.",241);
  text(12,143,"A / B: CONTINUE",243);break;
 }
 present();dirty=0;
}
int main(void){
 REG16(0x04000204)=0x4317;REG16(0x04000000)=0x0404;
 REG16(0x04000088)=0x200;ui_init();
 settings_load(SETTINGS_SRAM,&sound_enabled,&intro_enabled);dirty=1;game_reset(&game);
 clock_start();audio_play(audio_title,AUDIO_TITLE_LEN);
 for(;;){
  clock_update();
  if(audio_active&&clock_ticks>=audio_end)audio_stop();
  unsigned keys=(~REG16(0x04000130))&1023;
  unsigned pressed=keys&~previous_keys;previous_keys=keys;
  switch(state){
  case TITLE:if(pressed&9)enter(MENU);break;
  case MENU:
   if(pressed&64){selection=(selection+2)%3;dirty=1;}
   if(pressed&128){selection=(selection+1)%3;dirty=1;}
   if(pressed&2)enter(TITLE);
   if(pressed&4){audio_stop();story_index=0;enter(STORY);}
   else if(pressed&9){
    audio_stop();
    if(selection==0){if(intro_enabled)start_intro();else arrival();}
    if(selection==1){option_index=0;enter(OPTIONS);}
    if(selection==2)enter(CREDITS);
   }break;
  case INTRO:
   if(pressed&8){arrival();break;}
   if(pressed&1){
    paused^=1;dirty=1;
    if(paused)audio_stop();else{
     unsigned offset=clock_ticks&~3u;
     if(offset<AUDIO_INTRO_LEN)audio_play(audio_intro+offset,AUDIO_INTRO_LEN-offset);
    }
   }
   if(clock_ticks>=INTRO_TICKS){arrival();break;}
   {unsigned next=(clock_ticks*INTRO_FPS)>>14;
    if(next>=INTRO_COUNT)next=INTRO_COUNT-1;
    if(next!=intro_frame){intro_frame=next;dirty=1;}}
   break;
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
   if(pressed&64){option_index=(option_index+2)%3;dirty=1;}
   if(pressed&128){option_index=(option_index+1)%3;dirty=1;}
   if(pressed&2)enter(MENU);
   if(pressed&(1|16|32)){
    if(option_index==0){sound_enabled^=1;audio_stop();}
    if(option_index==1)intro_enabled^=1;
    if(option_index<2)settings_store(SETTINGS_SRAM,sound_enabled,intro_enabled);
    if(option_index==2)enter(MENU);
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
    if(game.sign_open){paused=1;audio_stop();enter(TUTORIAL);}
   }break;
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
  if(dirty)render();else wait_frame();
 }
}
