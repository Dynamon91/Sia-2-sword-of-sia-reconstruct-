#include "level_progress.h"
#include <limits.h>
void level_progress_reset(LevelProgress *p,unsigned health){
 for(unsigned i=0;i<LEVEL_ENTITY_BYTES;i++){p->gems_taken[i]=0;p->enemies_defeated[i]=0;}
 p->gems=0;p->defeated=0;p->elapsed_frames=0;p->completed=0;
 p->max_health=health;p->health=health;p->area=0;p->checkpoint_area=0;p->checkpoint_x=0;p->checkpoint_y=0;
}
static int mark(unsigned char *bits,unsigned id){
 if(id>=LEVEL_ENTITY_CAPACITY)return 0;
 unsigned byte=id>>3,mask=1u<<(id&7);
 if(bits[byte]&mask)return 0;
 bits[byte]|=mask;return 1;
}
int level_collect_gem(LevelProgress *p,unsigned id){
 if(p->completed||!mark(p->gems_taken,id))return 0;
 p->gems++;return 1;
}
int level_defeat_enemy(LevelProgress *p,unsigned id){
 if(p->completed||!mark(p->enemies_defeated,id))return 0;
 p->defeated++;return 1;
}
void level_progress_tick(LevelProgress *p,int paused){
 if(!paused&&!p->completed&&p->elapsed_frames<UINT_MAX)p->elapsed_frames++;
}
int level_take_damage(LevelProgress *p,unsigned damage){
 if(p->completed||!p->health||!damage)return 0;
 p->health=damage>=p->health?0:p->health-damage;return 1;
}
void level_set_checkpoint(LevelProgress *p,unsigned area,int x,int y){
 if(p->completed)return;
 p->checkpoint_area=area;p->checkpoint_x=x;p->checkpoint_y=y;
}
void level_finish(LevelProgress *p){if(p->health)p->completed=1;}
