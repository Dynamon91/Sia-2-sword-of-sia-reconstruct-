#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void steps(Game *g,unsigned input,int n){while(n--)game_step(g,input);}
static void place(Game *g,int x){
 game_reset(g);g->area=5;g->progress.area=5;g->enemy2_hp=0;
 g->x=x*FP;g->y=(game_continuation_floor(x)-PLAYER_H)*FP;g->grounded=1;
}
int main(void){
 Game g;game_reset(&g);g.area=4;g.progress.area=4;g.enemy2_hp=0;
 g.x=224*FP;g.y=58*FP;g.grounded=1;
 int x=g.x,y=g.y;game_step(&g,RIGHT);
 assert(g.area==5&&g.progress.area==5&&g.x+188*FP-x==320&&g.y-25*FP==y&&g.vx==320);
 steps(&g,LEFT,6);assert(g.area==4&&g.y==58*FP&&g.vx==-320);
 /* Walk the full slope in both directions, without artificial airborne frames. */
 place(&g,40);
 while(g.x<120*FP){game_step(&g,RIGHT);assert(g.grounded&&g.y+PLAYER_H*FP==game_continuation_floor(g.x/FP)*FP);}
 while(g.x>40*FP){game_step(&g,LEFT);assert(g.grounded&&g.y+PLAYER_H*FP==game_continuation_floor(g.x/FP)*FP);}
 /* Launch at the edge and land on the narrow pillar/bridge. */
 place(&g,130);steps(&g,JUMP|RIGHT,70);steps(&g,0,5);
 assert(g.area==5&&g.grounded&&g.y==55*FP&&g.falls==0);
 while(g.x>200*FP)game_step(&g,LEFT);
 steps(&g,JUMP|LEFT,70);steps(&g,0,5);
 assert(g.area==5&&g.grounded&&g.y==61*FP&&g.falls==0);
 /* A missed jump hits the solid pillar face and then loses one life. */
 place(&g,130);g.x=187*FP;g.y=90*FP;g.grounded=0;g.vy=FP;
 game_step(&g,RIGHT);assert(g.x==188*FP&&!g.grounded&&!g.vx);
 steps(&g,RIGHT,70);assert(g.falls==1&&g.lives==2&&g.area==5&&g.progress.health==3);
 /* Falling onto the island from below its top cannot teleport up through it. */
 place(&g,80);g.y=145*FP;g.grounded=0;g.vy=FP;game_step(&g,0);
 assert(!g.grounded&&g.y>145*FP);
 /* Same second guard, same persistent entity and world position on both sides. */
 place(&g,40);g.enemy2_hp=2;g.enemy2_x=210*FP;game_step(&g,0);assert(g.enemy2_x<210*FP);
 g.progress.health=1;assert(game_damage(&g,99));assert(g.lives==2&&g.x==40*FP&&g.y==83*FP);
 puts("PASS continuation: registered round trip, grounded slopes both ways, reachable bridge, solid miss/fall, no upward teleport and six-area respawn");
}
