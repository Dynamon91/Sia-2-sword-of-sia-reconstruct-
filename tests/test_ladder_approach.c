#include "../src/game.h"
#include "../src/view_camera.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

static void corridor(Game *g){
 game_reset(g);g->area=16;g->progress.area=16;g->x=55*FP;g->y=15*FP;
 g->enemy_hp=g->enemy2_hp=g->enemy3_hp=g->enemy4_hp=0;
 for(unsigned i=0;i<4;i++)assert(level_defeat_enemy(&g->progress,i));
 for(unsigned i=0;i<GEM_COUNT;i++)assert(level_collect_gem(&g->progress,i));
 g->gems=GEM_COUNT;g->collected=(1u<<GEM_COUNT)-1;level_set_lever_state(&g->progress,1);
}

int main(void){
 Game g;corridor(&g);ViewCamera camera;view_camera_reset(&camera,&g);
 unsigned crossed=0;
 for(int i=0;i<160&&g.area!=18;i++){
  int area=g.area,wx=g.x-view_origin[area][0]*FP,wy=g.y-view_origin[area][1]*FP;
  int cx=camera.x,cy=camera.y;
  game_step(&g,LEFT);view_camera_step(&camera,&g);
  assert(g.grounded&&!g.crawling&&g.lives==3);
  assert(g.x-view_origin[g.area][0]*FP==wx-320);
  assert(g.y-view_origin[g.area][1]*FP==wy);
  assert(abs(camera.x-cx)<=6*FP&&abs(camera.y-cy)<=6*FP);
  if(area!=g.area)crossed++;
 }
 assert(g.area==18&&crossed==2&&g.y==72*FP&&g.progress.area==18);
 /* Same guard in both views; two separate sword contacts, one hit per swing. */
 g.enemy5_x=54*FP;g.enemy5_dir=1;g.x=196*FP;g.facing=-1;
 for(int i=0;i<16;i++)game_step(&g,i==0?ATTACK:0);
 assert(g.enemy5_hp==1&&g.progress.defeated==4);
 for(int i=0;i<16;i++)game_step(&g,i==0?ATTACK:0);
 assert(!g.enemy5_hp&&g.progress.defeated==5&&(g.progress.enemies_defeated[0]&16));
 for(int i=0;i<100;i++)game_step(&g,LEFT);
 assert(g.area==18&&g.x==132*FP&&g.grounded&&g.y==72*FP);
 game_step(&g,UP|DOWN);assert(!g.crawling&&g.grounded);
 for(int i=0;i<200&&(g.area!=16||g.x<55*FP);i++){
  int cx=camera.x,cy=camera.y;
  game_step(&g,RIGHT);view_camera_step(&camera,&g);
  assert(abs(camera.x-cx)<=6*FP&&abs(camera.y-cy)<=6*FP);
 }
 assert(g.area==16&&g.x>=55*FP&&g.grounded&&g.y==15*FP);
 assert(g.progress.defeated==5&&g.gems==5&&g.progress.barrier_open&&g.lives==3);
 for(int i=0;i<180&&g.area!=18;i++)game_step(&g,LEFT);
 assert(g.area==18&&!g.enemy5_hp&&g.progress.defeated==5);
 g.progress.health=1;g.hurt_timer=0;assert(game_damage(&g,1));
 assert(g.lives==2&&g.area==18&&g.x==198*FP&&g.y==72*FP&&g.grounded);
 assert(!g.enemy5_hp&&g.gems==5&&g.progress.defeated==5&&g.progress.barrier_open);
 game_step(&g,RESET);assert(g.area==0&&g.enemy5_hp==2&&!g.progress.defeated&&!g.progress.barrier_open);
 corridor(&g);int enemy=g.enemy5_x;for(int i=0;i<5;i++)game_step(&g,0);
 assert(g.enemy5_x==enemy);
 puts("PASS ladder approach: two reversible world-preserving portals, five-guard persistence, sword contacts, camera bounds, wall, respawn and reset; upper ladder route checked separately");
}
