#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void place(Game *g,int area,int x,int y,int vy){
 game_reset(g);g->area=area;g->progress.area=(unsigned)area;
 g->x=x;g->y=y;g->vy=vy;g->grounded=0;
}
int main(void){
 Game g;
 /* Miss the third area's ledge: body must remain outside its solid face. */
 place(&g,2,81*FP,90*FP,FP);game_step(&g,RIGHT);
 assert(g.x==82*FP&&g.vx==0&&!g.grounded);
 for(int i=0;i<7;i++){game_step(&g,RIGHT);assert(g.x==82*FP&&!g.grounded);}
 /* Above the ledge the same horizontal crossing remains open. */
 place(&g,2,81*FP,70*FP,0);game_step(&g,RIGHT);
 assert(g.x>82*FP&&!g.grounded);
 /* Landing from above must catch the top even at maximum fall speed. */
 place(&g,2,110*FP,74*FP,6*FP);game_step(&g,0);
 assert(g.y==75*FP&&g.grounded&&g.vy==0);
 /* Exact edge contact is not overlap; one subpixel of overlap is. */
 place(&g,2,82*FP,74*FP,6*FP);game_step(&g,0);assert(!g.grounded);
 place(&g,2,82*FP+1,74*FP,6*FP);game_step(&g,0);assert(g.grounded);
 /* Both directions at the fifth area's gap. */
 place(&g,4,157*FP,80*FP,FP);game_step(&g,RIGHT);assert(g.x==158*FP&&g.vx==0);
 place(&g,4,99*FP,90*FP,FP);game_step(&g,LEFT);assert(g.x==98*FP&&g.vx==0);
 /* Undersides stop upward movement but never grant a midair jump. */
 for(int area=2;area<=4;area+=2){
  place(&g,area,180*FP,161*FP,-960);game_step(&g,0);
  assert(g.y==160*FP&&g.vy==0&&!g.grounded);
  game_step(&g,JUMP);assert(g.vy>0&&!g.grounded);
 }
 /* Below the rock, horizontal movement is free; a fall still costs one life. */
 place(&g,2,81*FP,161*FP,FP);game_step(&g,RIGHT);assert(g.x>82*FP);
 for(int i=0;i<60&&!g.falls;i++)game_step(&g,0);
 assert(g.falls==1&&g.lives==2&&!g.game_over&&g.area==2);
 puts("PASS collision volumes: side faces, clear jumps, swept landing, exact edges, undersides and fall respawn");
}
