#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 Game g;
 for(int area=0;area<15;area++){
  game_reset(&g);g.area=area;g.progress.area=(unsigned)area;
  assert(level_collect_gem(&g.progress,0));g.gems=1;g.collected=1;
  assert(level_defeat_enemy(&g.progress,0));g.enemy_hp=0;
  g.attack=8;g.climbing=1;g.vx=320;g.vy=-960;g.pickup_timer=150;
  assert(game_damage(&g,99));
  assert(g.lives==2&&g.progress.health==3&&!g.game_over);
  assert(g.area==area&&g.progress.area==(unsigned)area);
  assert(!g.attack&&!g.climbing&&!g.vx&&!g.vy&&g.hurt_timer==90);
  assert(g.gems==1&&g.collected==1&&g.progress.gems==1);
  assert(!g.pickup_timer);
  assert(g.enemy_hp==0&&g.progress.defeated==1);
  assert(!game_damage(&g,1));
 }
 /* Pits remain fatal even during post-hit immunity; exactly one life per fall. */
 game_reset(&g);assert(game_damage(&g,2));assert(g.progress.health==1&&g.lives==3);
 g.area=4;g.x=120*FP;g.y=211*FP;g.grounded=0;g.attack=8;g.pickup_timer=150;
 game_step(&g,0);assert(g.lives==2&&g.progress.health==3&&g.falls==1&&!g.attack);
 assert(!g.pickup_timer);
 game_step(&g,0);assert(g.lives==2&&g.falls==1);
 for(int n=0;n<2;n++){
  g.x=120*FP;g.y=211*FP;g.grounded=0;g.pickup_timer=150;game_step(&g,0);
 }
 assert(g.game_over&&g.lives==0&&g.progress.health==0);
 assert(!g.pickup_timer);
 unsigned tick=g.ticks;int falls=g.falls;
 for(int n=0;n<200;n++)game_step(&g,RIGHT|ATTACK);
 assert(g.ticks==tick&&g.falls==falls&&!game_damage(&g,99));
 game_step(&g,RESET);assert(g.lives==3&&g.progress.health==3&&!g.game_over&&!g.falls);
 puts("PASS lives: lethal-hit respawn in fifteen areas, progress preservation, immunity, pit override, frozen defeat and full retry");
}
