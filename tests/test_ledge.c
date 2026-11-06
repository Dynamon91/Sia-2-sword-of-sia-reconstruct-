#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void steps(Game *g,unsigned key,int n){while(n--)game_step(g,key);}
static void catch_first(Game *g){
 game_reset(g);steps(g,RIGHT,54);steps(g,UP,30);
 assert(g->grounded&&!g->climbing); /* No ground-to-top teleport. */
 game_step(g,JUMP);
 for(int i=0;i<100&&!g->climbing;i++)game_step(g,0);
 assert(g->climbing==LEDGE_HANG&&g->y==98*FP&&g->ledge_y==88);
 assert(!g->grounded&&!g->vx&&!g->vy&&!g->attack);
}
int main(void){
 Game g;catch_first(&g);int x=g.x,y=g.y;
 steps(&g,0,80);assert(g.x==x&&g.y==y&&game_ledge_frame(&g)==0);
 steps(&g,ATTACK,20);assert(!g.attack&&g.y==y&&g.climbing==LEDGE_HANG);
 game_step(&g,UP);assert(g.climbing==LEDGE_PULL&&game_ledge_frame(&g)==1);
 unsigned seen=0;int last=g.y;
 for(int i=0;i<LEDGE_PULL_TICKS;i++){
  seen|=1u<<game_ledge_frame(&g);game_step(&g,RIGHT|ATTACK);
  assert(g.x==x&&g.y<=last&&!g.attack);last=g.y;
 }
 assert(seen==14&&g.grounded&&!g.climbing&&g.y==48*FP&&g.gems==1);
 steps(&g,UP|DOWN,90);assert(g.grounded&&g.y==48*FP&&g.gems==1);
 catch_first(&g);game_step(&g,DOWN);assert(!g.climbing&&g.vy>0&&g.ledge_cooldown);
 steps(&g,0,100);assert(!g.climbing&&g.grounded&&g.y+PLAYER_H*FP==game_floor(g.x/FP+7)*FP);
 catch_first(&g);game_step(&g,JUMP);assert(g.climbing==LEDGE_PULL);
 assert(game_damage(&g,1)&&!g.climbing&&g.ledge_cooldown);steps(&g,0,100);assert(g.grounded);
 catch_first(&g);game_step(&g,LEFT);assert(!g.climbing&&g.x<x&&g.vy>0);
 /* Rising through the grab band must not catch until the descent. */
 game_reset(&g);g.x=108*FP;g.y=100*FP;g.vy=-3*FP;g.grounded=0;
 game_step(&g,0);assert(!g.climbing&&g.y<100*FP);
 /* Swept hand crossing can catch even at maximum fall speed. */
 g.y=94*FP;g.vy=6*FP;game_step(&g,0);assert(g.climbing==LEDGE_HANG&&g.y==98*FP);
 /* Insufficient reach, outside edge margin, and intentional DOWN never catch. */
 game_reset(&g);g.x=108*FP;g.y=99*FP;g.vy=FP;g.grounded=0;game_step(&g,0);assert(!g.climbing);
 g.x=80*FP;g.y=94*FP;g.vy=6*FP;g.grounded=0;game_step(&g,0);assert(!g.climbing);
 g.x=108*FP;g.y=94*FP;g.vy=6*FP;g.grounded=0;game_step(&g,DOWN);assert(!g.climbing);
 /* A normal top landing wins over a grab. */
 g.y=45*FP;g.vy=6*FP;g.grounded=0;game_step(&g,0);assert(g.grounded&&!g.climbing&&g.y==48*FP);
 /* The upper authored ledge also catches, and its camera remains bounded. */
 g.x=205*FP;g.y=46*FP;g.vy=6*FP;g.grounded=0;game_step(&g,0);
 assert(g.climbing==LEDGE_HANG&&g.ledge_y==40);
 steps(&g,UP,LEDGE_PULL_TICKS+1);assert(g.grounded&&g.y==0&&g.camera_y==-40);
 game_step(&g,RESET);assert(!g.climbing&&!g.ledge_ticks&&!g.ledge_cooldown);
 puts("PASS ledges: jump reach, swept catch, idle hold, recorded pull-up phases, release/regrab prevention, damage, top landing and upper ledge");
}
