#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void at(Game *g,int area,int x,int y){game_reset(g);g->area=area;g->progress.area=(unsigned)area;g->x=x*FP;g->y=y*FP;}
int main(void){
 Game g;at(&g,11,30,20);
 assert(level_collect_gem(&g.progress,4));g.gems=1;g.collected=16;
 for(int i=0;i<40&&g.area!=13;i++){
  int area=g.area,x=g.x,y=g.y;game_step(&g,LEFT);
  if(g.area!=area){assert(g.x-x==(area==11?118:44)*FP-320);assert(g.y-y==(area==11?3:86)*FP);}
 }
 assert(g.area==13&&g.grounded&&g.y==109*FP&&g.lives==3&&!g.falls);
 while(g.x>150*FP)game_step(&g,LEFT);
 for(int i=0;i<240&&g.enemy4_hp;i++)game_step(&g,i%16==0?ATTACK:0);
 assert(!g.enemy4_hp&&g.progress.defeated==1&&g.progress.enemies_defeated[0]==8);
 assert(g.enemy_hp==2&&g.enemy2_hp==2&&g.enemy3_hp==2&&g.gems==1&&g.lives==3);
 for(int i=0;i<80&&g.area!=11;i++)game_step(&g,RIGHT);
 assert(g.area==11&&g.grounded&&g.y==20*FP&&!g.enemy4_hp&&g.progress.defeated==1);
 for(int i=0;i<80&&g.area!=13;i++)game_step(&g,LEFT);
 assert(g.area==13&&!g.enemy4_hp&&g.gems==1&&g.collected==16);
 /* The left wall blocks walking, without a floor snap or running in place. */
 for(int i=0;i<150;i++)game_step(&g,LEFT);
 assert(g.x==44*FP&&g.y==109*FP&&g.grounded&&!g.vx);
 /* An airborne miss to the right bypasses the ground portal and falls. */
 g.x=210*FP;game_step(&g,0);game_step(&g,RIGHT|JUMP);
 for(int i=0;i<200&&!g.falls;i++)game_step(&g,RIGHT);
 assert(g.area==13&&g.falls==1&&g.lives==2&&g.x==174*FP&&g.y==109*FP);
 assert(!g.enemy4_hp&&g.progress.defeated==1&&g.gems==1&&g.progress.health==3);
 at(&g,11,23,20);game_step(&g,LEFT|RIGHT);assert(g.area==11);
 at(&g,12,129,23);game_step(&g,LEFT|RIGHT);assert(g.area==12);
 at(&g,12,151,23);game_step(&g,LEFT|RIGHT);assert(g.area==12);
 at(&g,13,177,109);game_step(&g,LEFT|RIGHT);assert(g.area==13);
 game_step(&g,RESET);assert(g.area==0&&g.enemy4_hp==2&&g.progress.defeated==0);
 puts("PASS lever route: measured portals both ways, fourth independent guard, persistent defeat/gem, solid wall, pit respawn, opposing input and reset");
}
