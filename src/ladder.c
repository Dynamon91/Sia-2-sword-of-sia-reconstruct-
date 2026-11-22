#include "ladder.h"

static int shift_y(int area){return area==20?91:area==19?60:0;}
static int center_x(int area){return area==20?118:area==19?130:160;}
int game_ladder_base_feet(const Game *g){return g->y+PLAYER_H*FP-shift_y(g->area)*FP;}
unsigned game_ladder_frame(const Game *g){return g->ladder_ticks/(4u*FP);}

/* This small control routine runs from ROM so the active renderer keeps IWRAM. */
int __attribute__((section(".romtext"),noinline)) game_ladder_step(Game *g,unsigned input,unsigned pressed){
 if(g->area<18||g->area>20)return 0;
 int attached=g->climbing==CLIMB_LADDER;
 if(!attached){
  if(g->climbing||!g->grounded||g->ledge_cooldown)return 0;
  int center=g->x+PLAYER_W*FP/2,anchor=center_x(g->area)*FP;
  int feet=game_ladder_base_feet(g);
  if(center<anchor-12*FP||center>anchor+12*FP)return 0;
  int enter=g->area==18?(input&UP)&&!(input&DOWN)&&feet>=107*FP&&feet<=117*FP:
                        (input&DOWN)&&!(input&UP)&&feet>=15*FP&&feet<=25*FP;
  if(!enter)return 0;
  g->climbing=CLIMB_LADDER;g->ladder_ticks=0;g->attack=0;
 }
 g->x=(center_x(g->area)-PLAYER_W/2)*FP;
 g->vx=0;g->vy=0;g->grounded=0;g->walk_ticks=0;g->crawling=0;
 if((input&(LEFT|RIGHT))==LEFT)g->facing=-1;
 if((input&(LEFT|RIGHT))==RIGHT)g->facing=1;
 if(pressed&JUMP){
  g->climbing=LEDGE_NONE;g->ledge_cooldown=18;g->ladder_ticks=0;g->attack=0;
  g->vy=(input&DOWN)?FP:-960;return 0;
 }
 if((pressed&ATTACK)&&!g->attack){g->attack=12;g->swing_id++;}
 else if(g->attack)g->attack--;
 int dy=g->attack?0:(((input&DOWN)!=0)-((input&UP)!=0))*LADDER_SPEED;
 int feet=game_ladder_base_feet(g)+dy;
 if(feet<20*FP)feet=20*FP;
 if(feet>112*FP)feet=112*FP;
 int moved=feet-game_ladder_base_feet(g);
 g->y=feet+(shift_y(g->area)-PLAYER_H)*FP;
 if(moved)g->ladder_ticks=(g->ladder_ticks+(unsigned)(moved<0?-moved:moved))%(LADDER_POSES*4u*FP);
 if(g->area==20){g->area=19;g->x+=12*FP;g->y-=31*FP;}
 if(g->area==18&&feet<=72*FP){g->area=19;g->x-=30*FP;g->y+=60*FP;}
 else if(g->area==19&&feet>=76*FP){g->area=18;g->x+=30*FP;g->y-=60*FP;}
 g->progress.area=(unsigned)g->area;
 if((dy<0&&feet==20*FP)||(dy>0&&feet==112*FP)){
  g->climbing=LEDGE_NONE;g->grounded=1;g->ladder_ticks=0;
 }
 return 1;
}
