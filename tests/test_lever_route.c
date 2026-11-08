#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void at(Game *g,int area,int x,int y){game_reset(g);g->area=area;g->progress.area=(unsigned)area;g->x=x*FP;g->y=y*FP;}
static void test_lever_input_edges(void){
 Game g;at(&g,13,73,109);g.grounded=1;g.previous=ATTACK;
 game_step(&g,ATTACK);assert(!g.progress.lever_activated);
 game_step(&g,0);game_step(&g,UP);assert(!g.progress.lever_activated);
 game_step(&g,0);game_step(&g,JUMP);assert(!g.progress.lever_activated);
 at(&g,13,130,109);g.grounded=1;game_step(&g,ATTACK);assert(!g.progress.lever_activated);
 at(&g,13,73,70);game_step(&g,ATTACK);assert(!g.progress.lever_activated);
 /* The former invisible entry trigger must no longer activate anything. */
 at(&g,12,142,23);g.grounded=1;game_step(&g,ATTACK);assert(!g.progress.lever_activated);
 at(&g,13,73,109);g.grounded=1;game_step(&g,ATTACK);assert(g.progress.lever_activated);
 game_step(&g,ATTACK);assert(g.progress.lever_activated);
 /* Both captured projections identify the same switch in shared coordinates. */
 at(&g,12,29,23);g.grounded=1;game_step(&g,ATTACK);assert(g.progress.lever_activated);
}
static void test_lever_barrier(void){
 Game g;at(&g,12,142,23);
 assert(!g.progress.lever_activated&&!g.progress.barrier_open);
 /* Reach the original switch before opening anything; no invented entry gate. */
 for(int i=0;i<40&&g.area!=13;i++)game_step(&g,LEFT);
 assert(g.area==13&&!g.progress.lever_activated);
 /* Neutralize only the guard in this interaction fixture; combat is checked below. */
 g.enemy4_hp=0;
 while(g.x>80*FP)game_step(&g,LEFT);
 game_step(&g,0);game_step(&g,ATTACK);
 assert(g.progress.lever_activated&&g.progress.barrier_open);
 for(int i=0;i<100&&g.area!=12;i++)game_step(&g,RIGHT);
 assert(g.area==12&&g.progress.lever_activated&&g.progress.barrier_open);
 for(int i=0;i<40&&g.area!=13;i++)game_step(&g,LEFT);
 assert(g.area==13&&g.progress.lever_activated);
 g.x=210*FP;g.y=(game_extension_floor(13,210)-PLAYER_H)*FP;g.grounded=1;game_step(&g,0);game_step(&g,RIGHT|JUMP);
 for(int i=0;i<200&&!g.falls;i++)game_step(&g,RIGHT);
 assert(g.falls==1&&g.area==14&&g.lives==2);
 assert(g.progress.lever_activated&&g.progress.barrier_open);
 game_step(&g,RESET);
 assert(!g.progress.lever_activated&&!g.progress.barrier_open);
}
int main(void){
 test_lever_input_edges();
 test_lever_barrier();
 Game g;at(&g,11,30,20);assert(level_set_lever_state(&g.progress,1));
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
 assert(g.area==14&&g.falls==1&&g.lives==2&&g.x==42*FP&&g.y==(game_extension_floor(14,42)-PLAYER_H)*FP);
 assert(!g.enemy4_hp&&g.progress.defeated==1&&g.gems==1&&g.progress.health==3);
 at(&g,11,23,20);game_step(&g,LEFT|RIGHT);assert(g.area==11);
 at(&g,12,129,23);game_step(&g,LEFT|RIGHT);assert(g.area==12);
 at(&g,12,151,23);game_step(&g,LEFT|RIGHT);assert(g.area==12);
 at(&g,13,177,109);game_step(&g,LEFT|RIGHT);assert(g.area==13);
 game_step(&g,RESET);assert(g.area==0&&g.enemy4_hp==2&&g.progress.defeated==0);
 puts("PASS lever route and barrier: reference-aligned switch, accessible approach, logical gate state, revisits, death persistence, reset, fourth guard and gem persistence");
}
