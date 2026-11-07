#include "../src/game.h"
#include <assert.h>
#include <stdio.h>

int main(void){
 Game g;game_reset(&g);assert(game_air_frame(&g)==AIR_NONE);
 for(int direction=-1;direction<=1;direction+=2){
  game_reset(&g);g.facing=direction;
  game_step(&g,JUMP);assert(game_air_frame(&g)==AIR_RISE);
  unsigned seen=0,last=AIR_RISE;int apex_y=1000*FP,air_ticks=0;
  while(!g.grounded&&air_ticks++<100){
   unsigned frame=game_air_frame(&g);
   assert(frame<3&&frame>=last);last=frame;seen|=1u<<frame;
   if(g.y<apex_y)apex_y=g.y;
   if(frame==AIR_RISE)assert(g.vy < -FP/2);
   if(frame==AIR_APEX)assert(g.vy>=-FP/2&&g.vy<=0);
   if(frame==AIR_FALL)assert(g.vy>0);
   game_step(&g,0);
  }
  assert(seen==7&&g.grounded&&air_ticks<100&&apex_y<80*FP);
  assert(game_air_frame(&g)==AIR_NONE&&g.facing==direction);
 }
 /* Stepping off an edge is a fall even at the first small positive velocity. */
 game_reset(&g);g.area=4;g.x=97*FP;g.y=66*FP;g.grounded=1;
 game_step(&g,RIGHT);assert(!g.grounded&&g.vy==32&&game_air_frame(&g)==AIR_FALL);
 /* Holding a ledge, pulling up and game over never index an airborne sprite. */
 g.climbing=LEDGE_HANG;assert(game_air_frame(&g)==AIR_NONE);
 g.climbing=LEDGE_PULL;assert(game_air_frame(&g)==AIR_NONE);
 g.climbing=LEDGE_HANG;game_step(&g,DOWN);
 assert(!g.climbing&&game_air_frame(&g)==AIR_FALL);
 g.game_over=1;assert(game_air_frame(&g)==AIR_NONE);
 game_reset(&g);assert(game_air_frame(&g)==AIR_NONE);
 puts("PASS airborne motion: ordered rise/apex/fall in real jumps, both facings, landing/reset, immediate edge fall, ledge release and inactive-state guards");
}
