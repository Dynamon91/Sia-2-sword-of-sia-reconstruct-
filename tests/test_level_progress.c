#include "../src/level_progress.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
int main(void){
 LevelProgress p;level_progress_reset(&p,5);
 for(unsigned i=0;i<128;i++){assert(level_collect_gem(&p,i));assert(level_defeat_enemy(&p,i));}
 for(unsigned i=0;i<128;i++){assert(!level_collect_gem(&p,i));assert(!level_defeat_enemy(&p,i));}
 assert(p.gems==128&&p.defeated==128);assert(!level_collect_gem(&p,128));assert(!level_defeat_enemy(&p,UINT_MAX));
 p.area=12;assert(!level_collect_gem(&p,0));
 level_set_checkpoint(&p,12,140,-40);assert(p.checkpoint_area==12&&p.checkpoint_y==-40);
 level_progress_tick(&p,0);level_progress_tick(&p,1);assert(p.elapsed_frames==1);
 assert(level_take_damage(&p,UINT_MAX));assert(p.health==0);level_progress_tick(&p,1);assert(p.elapsed_frames==1);
 level_finish(&p);assert(!p.completed);
 level_progress_reset(&p,5);assert(level_collect_gem(&p,0));level_finish(&p);
 assert(!level_take_damage(&p,1));assert(!level_collect_gem(&p,1));level_progress_tick(&p,0);assert(p.elapsed_frames==0);
 level_progress_reset(&p,5);p.elapsed_frames=UINT_MAX;level_progress_tick(&p,0);assert(p.elapsed_frames==UINT_MAX);
 puts("PASS whole-level progress: stable entity IDs, revisit persistence, bounds, pause, health saturation, completion and reset");
}
