#ifndef GAME_H
#define GAME_H
#include "level_progress.h"
#define FP 256
#define PLAYER_W 14
#define PLAYER_H 40
#define WORLD_W 240
#define PLATFORM_COUNT 2
#define GEM_COUNT 4
enum { LEDGE_NONE, LEDGE_HANG, LEDGE_PULL };
enum { AIR_RISE, AIR_APEX, AIR_FALL, AIR_NONE };
#define LEDGE_PULL_TICKS 12
enum { LEFT=1, RIGHT=2, JUMP=4, ATTACK=8, RESET=16, UP=32, DOWN=64 };
typedef struct { int x,y,w,h; } Platform;
typedef struct { int area,x,y; unsigned id; } Gem;
extern const Gem level_gems[GEM_COUNT];
typedef struct { int x,y,vx,vy,grounded,facing,attack,camera,previous;
    int climbing,gems,collected,sign_open,camera_y,area,falls,pickup_timer; int hurt_timer,game_over,enemy_x,enemy_dir,enemy_hp,enemy_flash; int enemy2_x,enemy2_dir,enemy2_hp,enemy2_flash; unsigned enemy2_last_swing,walk_ticks; unsigned swing_id,enemy_last_swing; unsigned ticks,lives; int ledge_y; unsigned ledge_ticks,ledge_cooldown; LevelProgress progress; } Game;
extern const Platform platforms[PLATFORM_COUNT];
int game_floor(int x);
/* Provisional sixth-view walk plane, using character overlap at the edges. */
int game_continuation_floor(int player_x);
void game_reset(Game *g);
void game_step(Game *g, unsigned input);
int game_damage(Game *g,unsigned amount);
unsigned game_attack_frame(const Game *g);
/* walk_ticks stores subpixel distance modulo one three-pose stride. */
unsigned game_walk_frame(const Game *g);
unsigned game_ledge_frame(const Game *g);
/* Pose follows vertical motion; AIR_NONE is never a sprite-buffer offset. */
unsigned game_air_frame(const Game *g);
#endif
