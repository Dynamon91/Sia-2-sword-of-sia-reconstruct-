#include "game.h"
#include "alignment.h"
/* Approximate first viewport from the supplied recording, not a recovered ROM map. */
const Platform platforms[PLATFORM_COUNT]={{81,88,70,8},{186,40,54,8}};
static const Platform bridge_platforms[3]={{33,BRIDGE_SURFACE_Y,48,8},{81,BRIDGE_SURFACE_Y,125,8},{206,BRIDGE_SURFACE_Y,34,8}};
static const Platform cliff_platforms[2]={{0,60,89,8},{140,115,100,8}};
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
void game_reset(Game *g){
 level_progress_reset(&g->progress,0);
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
 g->x=(g->area==2?20:g->area?60:40)*FP;g->y=(g->area==2?20:g->area?BRIDGE_SURFACE_Y-PLAYER_H:118)*FP;
 g->vx=0;g->vy=0;g->grounded=1;g->climbing=0;g->sign_open=0;
 g->camera=0;camera(g);
}
static void camera(Game *g){
 if(g->area==2){g->camera_y=0;return;}
 g->camera_y=g->y/FP-48;
 if(g->camera_y>0)g->camera_y=0;
 if(g->camera_y<-40)g->camera_y=-40;
}
static void collect(Game *g){
 if(g->area>=2)return;
 int bit=1<<g->area,left=g->area?133:110,top=g->area?74:62;
 if(!(g->collected&bit)&&g->x+PLAYER_W*FP>left*FP&&g->x<(left+16)*FP&&
    g->y<(top+16)*FP&&g->y+PLAYER_H*FP>top*FP){if(level_collect_gem(&g->progress,(unsigned)g->area)){g->collected|=bit;g->gems=(int)g->progress.gems;g->pickup_timer=150;}}
}
void game_step(Game *g,unsigned input){
 if(input&RESET){game_reset(g);return;}
 unsigned pressed=input&~(unsigned)g->previous;g->previous=(int)input;g->ticks++;level_progress_tick(&g->progress,0);
 if(g->pickup_timer>0)g->pickup_timer--;
 if((pressed&ATTACK)&&!g->attack)g->attack=12;
 else if(g->attack)--g->attack;
 int old_floor=(g->area?4096:game_floor(g->x/FP+PLAYER_W/2))*FP;
 int was_floor=g->grounded&&g->y+PLAYER_H*FP==old_floor;
 g->vx=((input&RIGHT)!=0)*320-((input&LEFT)!=0)*320;
 if(g->vx)g->facing=g->vx>0?1:-1;
 g->x+=g->vx;
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
 const Platform *list=g->area==2?cliff_platforms:g->area?bridge_platforms:platforms;
 int count=g->area==2?2:g->area?3:PLATFORM_COUNT;
 for(int i=0;i<count;i++){
  const Platform *p=&list[i];
  if(g->vy>=0&&g->x+PLAYER_W*FP>p->x*FP&&g->x<(p->x+p->w)*FP&&
     old_bottom<=p->y*FP&&next+PLAYER_H*FP>=p->y*FP&&p->y*FP<landing)
   landing=p->y*FP;
 }
 int floor=(g->area?4096:game_floor(center))*FP;
 if((next+PLAYER_H*FP>=floor||(was_floor&&g->vy>=0))&&floor<landing)landing=floor;
 if(landing!=0x7fffffff){next=landing-PLAYER_H*FP;g->vy=0;g->grounded=1;}
 g->y=next;g->camera=0;collect(g);camera(g);
 if(!g->area&&(pressed&DOWN)&&center>=158&&center<=190&&g->grounded)g->sign_open=1;
 if(!g->area&&(input&RIGHT)&&g->x>=225*FP&&g->grounded&&g->y==0)transition_area(g,1);
 else if(g->area==1&&(input&LEFT)&&g->x<=32*FP&&g->grounded)transition_area(g,0);
 else if(g->area==1&&(input&RIGHT)&&g->x>=225*FP&&g->grounded){g->area=2;g->progress.area=2;g->x=20*FP;g->y=20*FP;g->vy=0;camera(g);}
 else if(g->area==2&&(input&LEFT)&&g->x<=8*FP&&g->grounded){g->area=1;g->progress.area=1;g->x=224*FP;g->y=60*FP;g->vy=0;camera(g);}
 else if(g->y>210*FP){g->falls++;respawn_area(g);}
}
