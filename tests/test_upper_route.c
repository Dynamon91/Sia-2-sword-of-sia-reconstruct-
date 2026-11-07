#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void place(Game *g){game_reset(g);g->area=7;g->progress.area=7;g->enemy3_hp=0;g->x=92*FP;g->y=59*FP;g->grounded=1;}
static void steps(Game *g,unsigned keys,int n){while(n--)game_step(g,keys);}
int main(void){
 Game g;place(&g);steps(&g,JUMP,90);assert(g.area==7&&g.grounded&&g.y==59*FP);
 place(&g);int crossed=0;
 for(int i=0;i<60;i++){
  int x=g.x;game_step(&g,LEFT|UP|JUMP);
  if(g.area==8&&!crossed){assert(g.x-x==35*FP-320&&g.vy<0);crossed=1;}
 }
 steps(&g,0,8);assert(crossed&&g.area==8&&g.grounded&&g.y==60*FP);
 while(g.x<58*FP)game_step(&g,RIGHT);
 steps(&g,RIGHT|JUMP,40);assert(g.gems==1&&g.collected==16);
 int returned=0;
 for(int i=0;i<160;i++){
  int x=g.x;game_step(&g,0);
  if(g.area==7&&!returned){assert(g.x==x-35*FP);returned=1;}
 }
 assert(returned&&g.area==7&&g.grounded&&g.lives==3&&g.falls==0&&g.gems==1);
 /* Revisit cannot duplicate the pickup; lethal damage respawns on upper island. */
 g.area=8;g.progress.area=8;g.x=106*FP;g.y=56*FP;g.grounded=0;game_step(&g,0);assert(g.gems==1);
 assert(game_damage(&g,99));assert(g.area==8&&g.lives==2&&g.x==50*FP&&g.y==60*FP&&g.grounded&&g.gems==1);
 game_step(&g,RESET);assert(g.area==0&&g.gems==0&&g.collected==0);
 puts("PASS upper route: normal jump retained, high-jump portal, upper landing, fifth stable gem ID, camera return without life loss, upper respawn and reset");
}
