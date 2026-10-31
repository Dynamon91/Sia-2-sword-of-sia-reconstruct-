#ifndef GAME_H
#define GAME_H
#define FP 256
#define PLAYER_W 14
#define PLAYER_H 40
#define WORLD_W 240
#define PLATFORM_COUNT 2
enum { LEFT=1, RIGHT=2, JUMP=4, ATTACK=8, RESET=16, UP=32, DOWN=64 };
typedef struct { int x,y,w,h; } Platform;
typedef struct { int x,y,vx,vy,grounded,facing,attack,camera,previous;
    int climbing,gems,collected,sign_open,camera_y,area,falls,pickup_timer; unsigned ticks; } Game;
extern const Platform platforms[PLATFORM_COUNT];
int game_floor(int x);
void game_reset(Game *g);
void game_step(Game *g, unsigned input);
#endif
