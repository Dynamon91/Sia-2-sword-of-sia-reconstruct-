#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 Game g;game_reset(&g);g.area=8;g.progress.area=8;g.x=50*FP;g.y=60*FP;g.enemy3_hp=0;
 assert(level_collect_gem(&g.progress,4));g.gems=1;g.collected=16;
 /* Opposite directions cancel movement and must not cross either ramp portal. */
 for(int area=8;area<=10;area++){
  Game idle;game_reset(&idle);idle.area=area;idle.progress.area=(unsigned)area;
  int positions[2]={area==8?10:area==9?40:85,area==8?50:area==9?76:152};
  for(int side=0;side<2;side++){
   idle.x=positions[side]*FP;idle.y=(game_extension_floor(area,positions[side])-PLAYER_H)*FP;
   idle.grounded=1;idle.vy=0;
   int x=idle.x,y=idle.y;
   for(int tick=0;tick<10;tick++)game_step(&idle,LEFT|RIGHT);
   assert(idle.area==area&&idle.progress.area==(unsigned)area);
   assert(idle.x==x&&idle.y==y&&idle.grounded&&!idle.vx);
  }
 }
 unsigned crossed=0;
 for(int i=0;i<200&&g.area!=10;i++){
  int a=g.area,x=g.x,y=g.y;game_step(&g,LEFT);
  if(g.area!=a){
   int dx=a==8?58:108,dy=a==8?-15:93;
   assert(g.x-x==dx*FP-320);
   assert(g.y+PLAYER_H*FP==game_extension_floor(g.area,g.x/FP)*FP);
   assert(g.y-y>=(dy-2)*FP&&g.y-y<=(dy+2)*FP);
   assert(g.grounded&&!g.vy);crossed++;
  }
 }
 assert(g.area==10&&crossed==2);
 while(g.x>85*FP)game_step(&g,LEFT);
 assert(g.grounded&&g.y==60*FP&&g.gems==1&&g.lives==3&&!g.falls);
 game_step(&g,JUMP);assert(!g.grounded&&g.vy<0);
 for(int i=0;i<120;i++)game_step(&g,0);
 assert(g.grounded&&g.area==10&&g.y==60*FP);
 for(int i=0;i<240&&g.area!=8;i++)game_step(&g,RIGHT);
 assert(g.area==8&&g.grounded&&g.gems==1&&g.collected==16&&g.lives==3&&!g.falls);
 for(int i=0;i<300&&!g.falls;i++)game_step(&g,LEFT);
 assert(g.area==11&&g.falls==1&&g.lives==2&&g.x==154*FP&&g.y==104*FP&&g.grounded);
 assert(g.gems==1&&g.collected==16&&g.progress.gems==1);
 game_step(&g,RESET);assert(g.area==0&&g.gems==0&&g.lives==3);
 puts("PASS ramp route: opposite directions never trigger portals, two registered slope portals each way, upper landing and jump, persistent gem, pit life loss and upper respawn, reset");
}
