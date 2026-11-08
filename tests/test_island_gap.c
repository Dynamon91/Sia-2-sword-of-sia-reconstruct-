#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void at(Game *g,int area,int x,int y){game_reset(g);g->area=area;g->progress.area=(unsigned)area;g->x=x*FP;g->y=y*FP;}
int main(void){
 Game g;at(&g,10,85,60);
 assert(level_collect_gem(&g.progress,4));g.gems=1;g.collected=16;
 for(int i=0;i<30&&g.area==10;i++){
  int x=g.x,y=g.y;game_step(&g,LEFT);
  if(g.area==11){assert(g.x-x==76*FP-320&&g.y-y==44*FP);}
 }
 assert(g.area==11&&g.grounded&&g.y==104*FP);
 while(g.x>140*FP)game_step(&g,LEFT);
 game_step(&g,0);game_step(&g,LEFT|JUMP);
 unsigned airborne=0;
 for(int i=0;i<100;i++){
  if(!g.grounded)airborne++;
  if(g.grounded&&g.x<84*FP)break;
  game_step(&g,LEFT);
 }
 assert(airborne>30&&g.grounded&&g.x<84*FP&&g.y==104*FP);
 assert(g.lives==3&&!g.falls&&g.gems==1&&g.collected==16);
 /* The observed upper-left ledge can be reached with the existing high jump. */
 game_step(&g,0);game_step(&g,UP|JUMP);
 for(int i=0;i<120&&!g.grounded;i++)game_step(&g,LEFT);
 assert(g.grounded&&g.y==20*FP&&g.lives==3);
 /* Return from the lower island across the same gap, without a forced teleport. */
 at(&g,11,65,104);game_step(&g,RIGHT|JUMP);
 for(int i=0;i<120&&g.area==11;i++)game_step(&g,RIGHT);
 assert(g.area==10&&g.grounded&&g.lives==3&&!g.falls);
 at(&g,11,154,104);
 for(int i=0;i<250&&!g.falls;i++)game_step(&g,LEFT);
 assert(g.area==11&&g.falls==1&&g.lives==2&&g.x==154*FP&&g.y==104*FP);
 assert(g.progress.health==3&&g.grounded);
 /* Both directions also cancel the new portal. */
 at(&g,10,77,60);game_step(&g,LEFT|RIGHT);assert(g.area==10);
 at(&g,11,161,104);game_step(&g,LEFT|RIGHT);assert(g.area==11);
 game_step(&g,RESET);assert(g.area==0&&g.lives==3&&!g.falls);
 puts("PASS island gap: registered portal, input-only jumps both ways, high ledge, cancelled directions, pit respawn and persistent progress");
}
