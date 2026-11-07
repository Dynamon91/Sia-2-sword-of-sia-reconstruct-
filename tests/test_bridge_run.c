#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void steps(Game *g,unsigned keys,int n){while(n--)game_step(g,keys);}
static void place(Game *g,int area,int x){
 game_reset(g);g->area=area;g->progress.area=(unsigned)area;g->enemy3_hp=0;
 g->x=x*FP;g->y=(game_extension_floor(area,x)-PLAYER_H)*FP;g->grounded=1;
}
int main(void){
 Game g;place(&g,5,224);g.enemy2_hp=0;int x=g.x,y=g.y;game_step(&g,RIGHT);
 assert(g.area==6&&g.x+170*FP-x==320&&g.y-9*FP==y&&g.grounded);
 /* Walk to the eighth view without artificial jump requirements. */
 while(g.area==6){x=g.x;y=g.y;game_step(&g,RIGHT);assert(g.grounded);
  if(g.area==7){assert(g.x+168*FP-x==320&&g.y-7*FP==y);}}
 while(g.x<119*FP)game_step(&g,RIGHT);
 steps(&g,RIGHT,60);assert(g.x==119*FP&&g.vx==0&&g.walk_ticks==0&&g.grounded);
 while(g.area==7){x=g.x;y=g.y;game_step(&g,LEFT);
  if(g.area==6){assert(g.x-168*FP-x==-320&&g.y+7*FP==y);}}
 while(g.area==6){x=g.x;y=g.y;game_step(&g,LEFT);assert(g.grounded);
  if(g.area==5){assert(g.x-170*FP-x==-320&&g.y+9*FP==y);}}
 /* Contact with the new guard damages once, then respects hit immunity. */
 place(&g,6,110);g.enemy3_hp=2;game_step(&g,0);
 assert(g.progress.health==2&&g.hurt_timer>0&&g.lives==3);
 game_step(&g,0);assert(g.progress.health==2&&g.lives==3);
 /* The new enemy has stable identity 2 and shares the attack clock. */
 place(&g,6,82);g.enemy3_hp=2;
 game_step(&g,ATTACK);steps(&g,0,4);assert(g.enemy3_hp==1);
 steps(&g,0,12);game_step(&g,ATTACK);steps(&g,0,4);
 assert(!g.enemy3_hp&&g.progress.defeated==1&&g.progress.enemies_defeated[0]==4);
 g.area=7;g.progress.area=7;steps(&g,0,4);assert(!g.enemy3_hp&&g.progress.defeated==1);
 assert(game_damage(&g,99));assert(g.area==7&&g.lives==2&&!g.enemy3_hp&&g.progress.defeated==1);
 /* Both new areas lose a life to a fall, preserving the current area. */
 for(int area=6;area<8;area++){
  place(&g,area,60);g.y=211*FP;g.grounded=0;g.vy=FP;game_step(&g,0);
  assert(g.falls==1&&g.lives==2&&g.area==area&&g.progress.health==3&&g.grounded);
 }
 game_step(&g,RESET);assert(g.area==0&&g.enemy3_hp==2&&!g.progress.defeated);
 puts("PASS bridge run: two registered portals both ways, connected slopes, solid wall, third guard contact/immunity/combat/persistence, eight-area respawn and reset");
}
