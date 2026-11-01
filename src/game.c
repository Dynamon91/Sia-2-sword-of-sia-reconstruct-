#include "game.h"
#include "alignment.h"
/* Approximate first viewport from the supplied recording, not a recovered ROM map. */
const Platform platforms[PLATFORM_COUNT]={{81,88,70,8},{186,40,54,8}};
static const Platform bridge_platforms[3]={{33,BRIDGE_SURFACE_Y,48,8},{81,BRIDGE_SURFACE_Y,125,8},{206,BRIDGE_SURFACE_Y,34,8}};
static const Platform cliff_platforms[2]={{0,54,43,8},{96,115,144,8}};
static const Platform gap_platforms[2]={{0,106,98,54},{172,98,68,62}};
const Gem level_gems[GEM_COUNT]={{0,109,62,0},{1,133,74,1},{3,151,47,2},{4,126,40,3}};
/* Animation and damage share the same attack clock: wind-up, contact, recovery. */
unsigned game_attack_frame(const Game *g){return g->attack>8?0:g->attack>=4?1:2;}
unsigned game_walk_frame(const Game *g){return (g->walk_ticks/6)%3;}
static const int guard_ground[][2]={{0,130},{24,130},{48,120},{72,115},{96,102},{120,94},{144,88},{239,88}};
static const int ground[][2]={{0,151},{24,153},{40,158},{56,158},{72,153},{84,153},
 {100,154},{120,153},{140,145},{156,146},{176,153},{192,157},{216,157},{239,153}};
int game_floor(int x){
 if(x<0)x=0;
 if(x>239)x=239;
 for(unsigned i=1;i<sizeof(ground)/sizeof(ground[0]);i++)if(x<=ground[i][0]){
  int x0=ground[i-1][0],y0=ground[i-1][1];
  return y0+(ground[i][1]-y0)*(x-x0)/(ground[i][0]-x0);
 }
 return 153;
}
static int guard_floor(int x){
 for(unsigned i=1;i<sizeof(guard_ground)/sizeof(guard_ground[0]);i++)if(x<=guard_ground[i][0]){
 int x0=guard_ground[i-1][0],y0=guard_ground[i-1][1];return y0+(guard_ground[i][1]-y0)*(x-x0)/(guard_ground[i][0]-x0);}
 return 88;
}
void game_reset(Game *g){
 level_progress_reset(&g->progress,3);
 g->hurt_timer=0;g->game_over=0;g->walk_ticks=0;g->lives=3;
 g->enemy2_x=210*FP;g->enemy2_dir=-1;g->enemy2_hp=2;g->enemy2_flash=0;g->enemy2_last_swing=0;
 g->enemy_x=155*FP;g->enemy_dir=-1;g->enemy_hp=2;g->enemy_flash=0;g->swing_id=0;g->enemy_last_swing=0;
 level_set_checkpoint(&g->progress,0,40*FP,118*FP);
 g->x=40*FP;g->y=118*FP;g->vx=0;g->vy=0;
 g->grounded=1;g->facing=1;g->attack=0;g->camera=0;g->previous=0;
 g->climbing=0;g->gems=0;g->collected=0;g->sign_open=0;g->camera_y=0;
 g->area=0;g->falls=0;g->pickup_timer=0;g->ticks=0;
}
static void camera(Game *g);
static void transition_area(Game *g,int area){
 int delta=area-g->area;
 g->x-=delta*AREA_OFFSET_X*FP;
 g->y+=delta*AREA_OFFSET_Y*FP;
 g->area=area;g->progress.area=(unsigned)area;g->climbing=0;g->sign_open=0;g->camera=0;
 camera(g);
}
static void respawn_area(Game *g){
 g->x=(g->area==4?60:g->area==3?10:g->area==2?20:g->area?60:40)*FP;g->y=(g->area==4?66:g->area==3?90:g->area==2?14:g->area?BRIDGE_SURFACE_Y-PLAYER_H:118)*FP;
 g->vx=0;g->vy=0;g->grounded=1;g->climbing=0;g->sign_open=0;
 g->camera=0;camera(g);
}
/* A fall or lethal hit consumes one life; run progress survives respawn. */
static void lose_life(Game *g){
 if(g->game_over)return;
 if(g->lives)g->lives--;
 g->attack=0;g->walk_ticks=0;g->vx=0;g->vy=0;g->climbing=0;
 if(!g->lives){g->progress.health=0;g->game_over=1;return;}
 g->progress.health=g->progress.max_health;
 respawn_area(g);g->hurt_timer=90;
}
static void camera(Game *g){
 if(g->area>=2){g->camera_y=0;return;}
 g->camera_y=g->y/FP-48;
 if(g->camera_y>0)g->camera_y=0;
 if(g->camera_y<-40)g->camera_y=-40;
}
static void collect(Game *g){
 for(unsigned i=0;i<GEM_COUNT;i++){
  const Gem *item=&level_gems[i];
  if(item->area!=g->area)continue;
  unsigned bit=1u<<item->id;
  if(!((unsigned)g->collected&bit)&&g->x+PLAYER_W*FP>item->x*FP&&g->x<(item->x+16)*FP&&
     g->y<(item->y+16)*FP&&g->y+PLAYER_H*FP>item->y*FP&&level_collect_gem(&g->progress,item->id)){
   g->collected|=(int)bit;g->gems=(int)g->progress.gems;g->pickup_timer=150;
  }
 }
}
int game_damage(Game *g,unsigned amount){
 if(g->game_over||g->hurt_timer||!amount)return 0;
 if(!level_take_damage(&g->progress,amount))return 0;
 g->climbing=0;g->attack=0;g->hurt_timer=60;
 if(!g->progress.health)lose_life(g);
 return 1;
}
static void guard_step(Game *g){
 if(g->area!=3&&g->area!=4)return;
 int second=g->area==4;
 int *hp=second?&g->enemy2_hp:&g->enemy_hp;
 int *position=second?&g->enemy2_x:&g->enemy_x;
 int *direction=second?&g->enemy2_dir:&g->enemy_dir;
 int *flash=second?&g->enemy2_flash:&g->enemy_flash;
 unsigned *last=second?&g->enemy2_last_swing:&g->enemy_last_swing;
 if(!*hp)return;
 if(*flash>0)--*flash;
 *position+=*direction*64;
 int left=second?188:140,right=second?218:210;
 if(*position<left*FP){*position=left*FP;*direction=1;}
 if(*position>right*FP){*position=right*FP;*direction=-1;}
 int ex=*position/FP,ey=(second?98:guard_floor(ex+7))-40;
 int px=g->x/FP,py=g->y/FP;
 int vertical=py+PLAYER_H>ey&&py<ey+40;
 int sword_left=g->facing>0?px+PLAYER_W:px-30;
 if(g->attack&&game_attack_frame(g)==1&&*last!=g->swing_id&&vertical&&sword_left+30>ex&&sword_left<ex+18){
  *last=g->swing_id;--*hp;*flash=12;
  if(!*hp){level_defeat_enemy(&g->progress,(unsigned)second);return;}
 }
 if(vertical&&px+PLAYER_W>ex&&px<ex+18)game_damage(g,1);
}
void game_step(Game *g,unsigned input){
 if(input&RESET){game_reset(g);return;}
 if(g->game_over)return;
 if(g->hurt_timer>0)g->hurt_timer--;
 unsigned pressed=input&~(unsigned)g->previous;g->previous=(int)input;g->ticks++;level_progress_tick(&g->progress,0);
 if(g->pickup_timer>0)g->pickup_timer--;
 if((pressed&ATTACK)&&!g->attack){g->attack=12;g->swing_id++;}
 else if(g->attack)--g->attack;
 int old_floor=(g->area==3?guard_floor(g->x/FP+PLAYER_W/2):g->area?4096:game_floor(g->x/FP+PLAYER_W/2))*FP;
 int was_floor=g->grounded&&g->y+PLAYER_H*FP==old_floor;
 g->vx=((input&RIGHT)!=0)*320-((input&LEFT)!=0)*320;
 if(g->vx&&!g->attack)g->facing=g->vx>0?1:-1;
 int old_x=g->x;
 g->x+=g->vx;
 /* Solid cliff sides: a missed jump cannot enter the rock below its top. */
 if(g->area==4&&g->y<160*FP){
  int feet=g->y+PLAYER_H*FP;
  if(g->vx>0&&old_x+PLAYER_W*FP<=172*FP&&g->x+PLAYER_W*FP>172*FP&&feet>98*FP){g->x=(172-PLAYER_W)*FP;g->vx=0;}
  if(g->vx<0&&old_x>=98*FP&&g->x<98*FP&&feet>106*FP){g->x=98*FP;g->vx=0;}
 }
 if(g->x<0)g->x=0;
 if(g->x>(WORLD_W-PLAYER_W)*FP)g->x=(WORLD_W-PLAYER_W)*FP;
 int center=g->x/FP+PLAYER_W/2;
 int bottom=g->y+PLAYER_H*FP;
 if(!g->area&&!g->climbing&&(input&(UP|DOWN))&&center>=104&&center<=126&&
    bottom>=88*FP&&g->y<158*FP&&((input&DOWN)||bottom>88*FP)){
  g->climbing=1;g->grounded=0;g->vy=0;
  if(g->y>114*FP)g->y=114*FP;
 }
 if(g->climbing){
  if(pressed&JUMP){g->climbing=0;g->vy=-960;g->grounded=0;}
  else if(input&(LEFT|RIGHT)){g->climbing=0;g->vy=0;}
  else{
   g->x=108*FP;g->vx=0;g->vy=0;
   g->y+=((input&DOWN)!=0)*FP-((input&UP)!=0)*FP;
   if(g->y<=48*FP){g->y=48*FP;g->climbing=0;g->grounded=1;}
   if(g->y>=114*FP){g->y=114*FP;g->climbing=0;g->grounded=1;}
   collect(g);camera(g);return;
  }
 }else if((pressed&JUMP)&&g->grounded){g->vy=-960;g->grounded=0;}
 int old_bottom=g->y+PLAYER_H*FP;
 g->vy+=32;if(g->vy>6*FP)g->vy=6*FP;
 int next=g->y+g->vy,landing=0x7fffffff;
 g->grounded=0;
 const Platform *list=g->area==4?gap_platforms:g->area==2?cliff_platforms:g->area?bridge_platforms:platforms;
 int count=g->area==4?2:g->area==3?0:g->area==2?2:g->area?3:PLATFORM_COUNT;
 for(int i=0;i<count;i++){
  const Platform *p=&list[i];
  if(g->vy>=0&&g->x+PLAYER_W*FP>p->x*FP&&g->x<(p->x+p->w)*FP&&
     old_bottom<=p->y*FP&&next+PLAYER_H*FP>=p->y*FP&&p->y*FP<landing)
   landing=p->y*FP;
 }
 int floor=(g->area==3?guard_floor(center):g->area?4096:game_floor(center))*FP;
 if((next+PLAYER_H*FP>=floor||(was_floor&&g->vy>=0))&&floor<landing)landing=floor;
 if(landing!=0x7fffffff){next=landing-PLAYER_H*FP;g->vy=0;g->grounded=1;}
 g->y=next;g->camera=0;collect(g);camera(g);
 if(g->grounded&&g->vx&&!g->attack)g->walk_ticks++;else g->walk_ticks=0;
 if(!g->area&&(pressed&DOWN)&&center>=158&&center<=190&&g->grounded)g->sign_open=1;
 if(!g->area&&(input&RIGHT)&&g->x>=225*FP&&g->grounded&&g->y==0)transition_area(g,1);
 else if(g->area==1&&(input&LEFT)&&g->x<=32*FP&&g->grounded)transition_area(g,0);
 else if(g->area==1&&(input&RIGHT)&&g->x>=225*FP&&g->grounded){g->area=2;g->progress.area=2;g->x=20*FP;g->y=14*FP;g->vy=0;camera(g);}
 else if(g->area==2&&(input&LEFT)&&g->x<=8*FP&&g->grounded){g->area=1;g->progress.area=1;g->x=224*FP;g->y=60*FP;g->vy=0;camera(g);}
 else if(g->area==2&&(input&RIGHT)&&g->x>=225*FP&&g->grounded){g->area=3;g->progress.area=3;g->x=10*FP;g->y=90*FP;g->vy=0;camera(g);}
 else if(g->area==3&&(input&LEFT)&&g->x<=1*FP&&g->grounded){g->area=2;g->progress.area=2;g->x=224*FP;g->y=75*FP;g->vy=0;camera(g);}
 else if(g->area==3&&(input&RIGHT)&&g->x>=225*FP&&g->grounded){
  g->area=4;g->progress.area=4;g->x-=158*FP;g->y+=18*FP;camera(g);
 }else if(g->area==4&&(input&LEFT)&&g->x<=32*FP&&g->grounded){
  g->area=3;g->progress.area=3;g->x+=158*FP;g->y-=18*FP;camera(g);
 }
 else if(g->y>210*FP){g->falls++;lose_life(g);return;}
 guard_step(g);
}
