#ifndef LEVEL_PROGRESS_H
#define LEVEL_PROGRESS_H
/* Persistent run state shared by every future viewport. Capacity, not content counts. */
#define LEVEL_ENTITY_CAPACITY 128
#define LEVEL_ENTITY_BYTES (LEVEL_ENTITY_CAPACITY/8)
typedef struct {
 unsigned char gems_taken[LEVEL_ENTITY_BYTES], enemies_defeated[LEVEL_ENTITY_BYTES];
 unsigned gems, defeated, health, max_health, elapsed_frames;
 unsigned area, checkpoint_area; int checkpoint_x,checkpoint_y;
 unsigned completed;
} LevelProgress;
void level_progress_reset(LevelProgress *p,unsigned health);
int level_collect_gem(LevelProgress *p,unsigned id);
int level_defeat_enemy(LevelProgress *p,unsigned id);
void level_progress_tick(LevelProgress *p,int paused);
int level_take_damage(LevelProgress *p,unsigned damage);
void level_set_checkpoint(LevelProgress *p,unsigned area,int x,int y);
void level_finish(LevelProgress *p);
#endif
