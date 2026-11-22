#ifndef LADDER_H
#define LADDER_H
#include "game.h"
#define LADDER_SPEED FP
#define LADDER_SPRITE_W 40
#define LADDER_SPRITE_H 64
#define LADDER_SPRITE_ANCHOR_X 20
#define LADDER_ATTACK_W 112
#define LADDER_ATTACK_H 96
#define LADDER_ATTACK_ANCHOR_X 64
#define LADDER_POSES 4
/* Native registrations: foot -> upper (-30,+60), upper -> exit (-12,+31). */
int game_ladder_step(Game *g,unsigned input,unsigned pressed);
unsigned game_ladder_frame(const Game *g);
int game_ladder_base_feet(const Game *g);
#endif
