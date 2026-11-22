#include "../src/game.h"
#include "../src/ladder.h"
#include "../src/view_camera.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void start(Game *g){
 game_reset(g);g->area=18;g->progress.area=18;g->x=153*FP;g->y=72*FP;
 g->enemy5_hp=0;g->enemy6_hp=0;g->grounded=1;level_set_lever_state(&g->progress,1);
}
int main(void){
 Game g;start(&g);ViewCamera camera;view_camera_reset(&camera,&g);unsigned poses=0,crossed=0;
 for(int i=0;i<100&&(i==0||g.climbing);i++){
  int area=g.area,wx=g.x-view_origin[area][0]*FP,wy=g.y-view_origin[area][1]*FP;
  int cx=camera.x,cy=camera.y;game_step(&g,UP);view_camera_step(&camera,&g);
  assert(g.x-view_origin[g.area][0]*FP==wx);
  assert(g.y-view_origin[g.area][1]*FP==wy-LADDER_SPEED);
  assert(abs(camera.x-cx)<=6*FP&&abs(camera.y-cy)<=6*FP);
  if(g.climbing)poses|=1u<<game_ladder_frame(&g);
  if(g.area!=area)crossed++;
 }
 assert(poses==15&&crossed==1&&g.area==19&&!g.climbing&&g.grounded&&g.y==40*FP);
 game_step(&g,DOWN);assert(g.climbing==CLIMB_LADDER);
 for(int i=0;i<100&&g.climbing;i++)game_step(&g,DOWN);
 assert(g.area==18&&g.grounded&&!g.climbing&&g.y==72*FP&&g.x==153*FP);
 start(&g);for(int i=0;i<10;i++)game_step(&g,UP);
 int y=g.y;unsigned phase=g.ladder_ticks;
 for(int i=0;i<15;i++)game_step(&g,0);
 assert(g.y==y&&g.ladder_ticks==phase&&g.climbing==CLIMB_LADDER);
 game_step(&g,UP|DOWN);assert(g.y==y&&g.ladder_ticks==phase);
 game_step(&g,JUMP|RIGHT);assert(!g.climbing&&g.vy<0&&g.x>153*FP&&g.ledge_cooldown);
 for(int i=0;i<100&&!g.grounded;i++)game_step(&g,0);
 assert(g.area==18&&g.grounded&&g.y==72*FP);
 start(&g);for(int i=0;i<20;i++)game_step(&g,UP);
 game_step(&g,DOWN|JUMP);assert(!g.climbing&&g.vy>0&&g.ledge_cooldown);
 for(int i=0;i<100&&!g.grounded;i++)game_step(&g,0);
 assert(g.area==18&&g.grounded&&g.y==72*FP);
 start(&g);g.area=20;g.progress.area=20;g.x=111*FP;g.y=71*FP;
 game_step(&g,DOWN);
 assert(g.area==19&&g.climbing==CLIMB_LADDER&&g.x==123*FP&&g.y==41*FP);
 start(&g);g.area=19;g.progress.area=19;g.x=123*FP;g.y=81*FP;g.grounded=0;g.climbing=CLIMB_LADDER;g.facing=-1;
 g.enemy6_hp=2;g.enemy6_x=94*FP;g.enemy6_dir=-1;y=g.y;
 for(int i=0;i<16;i++)game_step(&g,i==0?ATTACK|LEFT:0);
 assert(g.enemy6_hp==1&&g.climbing==CLIMB_LADDER&&g.y==y);
 for(int i=0;i<16;i++)game_step(&g,i==0?ATTACK|LEFT:0);
 assert(!g.enemy6_hp&&g.progress.defeated==1&&(g.progress.enemies_defeated[0]&32));
 for(int i=0;i<100&&g.climbing;i++)game_step(&g,UP);
 assert(g.area==19&&g.grounded&&!g.climbing);
 for(int i=0;i<40&&g.area!=20;i++)game_step(&g,RIGHT);
 assert(g.area==20&&g.grounded&&!g.enemy6_hp);
 for(int i=0;i<50&&g.area!=19;i++)game_step(&g,LEFT);
 assert(g.area==19&&g.grounded&&!g.enemy6_hp&&g.progress.defeated==1);
 start(&g);for(int i=0;i<55;i++)game_step(&g,UP);
 assert(g.area==19&&g.climbing==CLIMB_LADDER);g.progress.health=1;g.hurt_timer=0;
 assert(game_damage(&g,1));assert(g.area==19&&g.grounded&&!g.climbing&&g.lives==2&&!g.ladder_ticks);
 game_step(&g,RESET);assert(g.area==0&&g.enemy6_hp==2&&!g.ladder_ticks);
 puts("PASS ladder: up/down, four poses, fixed world anchor, bounded camera, idle, opposing input, jump/landing, mounted sword, sixth-guard persistence, portals, death and reset");
}
