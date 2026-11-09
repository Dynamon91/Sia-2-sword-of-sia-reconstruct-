#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void lower(Game *g){game_reset(g);g->area=15;g->progress.area=15;g->x=164*FP;g->y=78*FP;g->grounded=1;}
int main(void){
 Game g;lower(&g);int feet=g.y+PLAYER_H*FP;
 game_step(&g,LEFT);assert(g.x==164*FP&&!g.crawling);
 game_step(&g,DOWN|LEFT);assert(g.crawling&&g.x==164*FP-CRAWL_SPEED&&g.vx==-CRAWL_SPEED);
 assert(g.y+PLAYER_H*FP==feet&&game_body_top(&g)==98*FP&&g.grounded);
 unsigned poses=0;
 for(int i=0;i<80;i++){game_step(&g,LEFT);assert(g.crawling&&g.grounded&&g.y+PLAYER_H*FP==feet);poses|=1u<<game_crawl_frame(&g);}
 assert(poses==3);
 int x=g.x;game_step(&g,JUMP|ATTACK|UP);assert(g.crawling&&g.grounded&&!g.vy&&!g.attack&&g.x==x);
 unsigned phase=g.crawl_ticks;for(int i=0;i<20;i++)game_step(&g,0);assert(g.crawling&&g.crawl_ticks==phase);
 for(int i=0;i<200&&g.crawling;i++)game_step(&g,RIGHT);
 assert(!g.crawling&&g.x>=164*FP&&g.grounded&&g.y+PLAYER_H*FP==feet);
 game_step(&g,DOWN);assert(g.crawling);game_step(&g,0);assert(!g.crawling);
 lower(&g);unsigned crossings=0;
 for(int i=0;i<400&&(g.area!=16||g.crawling);i++){
  int area=g.area,wx=g.x-(area==15?-873:-790)*FP,wy=g.y-(area==15?267:204)*FP;
  game_step(&g,i==0?DOWN|LEFT:LEFT);
  if(area==15&&g.area==16){assert(g.x+790*FP==wx-CRAWL_SPEED&&g.y-204*FP==wy);crossings++;}
 }
 assert(crossings==1&&g.area==16&&!g.crawling&&g.grounded&&g.x+PLAYER_W*FP<=83*FP&&g.y==15*FP);
 /* Release DOWN only after returning to the open right-hand landing. */
 for(int i=0;i<400&&(g.area!=15||g.x<164*FP);i++)game_step(&g,RIGHT|DOWN);
 game_step(&g,0);assert(g.area==15&&!g.crawling&&g.grounded&&g.y==78*FP&&g.lives==3);
 lower(&g);g.x=191*FP;game_step(&g,DOWN|RIGHT);
 for(int i=0;i<100&&!g.falls;i++)game_step(&g,RIGHT|DOWN);
 assert(g.falls==1&&g.area==15&&g.lives==2&&!g.crawling&&g.x==172*FP&&g.y==78*FP);
 lower(&g);game_step(&g,DOWN|LEFT);assert(g.crawling);game_step(&g,RESET);assert(!g.crawling&&!g.crawl_ticks&&g.area==0);
 game_step(&g,DOWN);assert(!g.crawling);
 lower(&g);g.grounded=0;g.y=20*FP;game_step(&g,DOWN);assert(!g.crawling);
 puts("PASS crawl: safe low-rock entry, fixed feet, two distance-driven poses, forced crouch, suppressed jump/attack, safe stand-up, pit respawn, reset and area/air gating");
}
