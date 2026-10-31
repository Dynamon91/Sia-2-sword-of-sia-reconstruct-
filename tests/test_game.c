#include "../src/game.h"
#include "../src/alignment.h"
#include <assert.h>
#include <stdio.h>
static void step(Game *g,unsigned keys,int count){for(int i=0;i<count;i++)game_step(g,keys);}
int main(void){
 Game g;game_reset(&g);step(&g,0,120);
 assert(g.x==40*FP&&g.y==118*FP&&g.grounded);
 game_step(&g,JUMP);assert(g.vy<0&&!g.grounded);
 int previous=g.vy;game_step(&g,JUMP);assert(g.vy>previous);
 step(&g,0,120);assert(g.y==118*FP&&g.grounded);
 step(&g,RIGHT,54);assert(g.x/FP>=107&&g.x/FP<=108);
 step(&g,UP,20);assert(g.climbing&&g.y<100*FP&&g.gems==0);
 int y=g.y;step(&g,DOWN,10);assert(g.y>y&&g.climbing);
 game_step(&g,JUMP);assert(!g.climbing&&g.vy<0);
 step(&g,0,120);assert(g.grounded);
 game_reset(&g);step(&g,RIGHT,54);step(&g,UP,90);
 assert(!g.climbing&&g.grounded&&g.y==48*FP&&g.x==108*FP);
 assert(g.gems==1&&g.collected&&g.pickup_timer>0);step(&g,0,200);assert(g.gems==1&&g.pickup_timer==0);
 step(&g,DOWN,90);assert(g.grounded&&g.y+PLAYER_H*FP==game_floor(115)*FP);
 game_reset(&g);step(&g,RIGHT,54);step(&g,UP,90);step(&g,RIGHT,25);
 step(&g,JUMP|RIGHT,45);step(&g,0,40);
 assert(g.grounded&&g.y==0&&g.camera_y==-40);
 for(int i=0;i<50&&g.area==0;i++){
  int before_x=g.x+g.area*AREA_OFFSET_X*FP,before_y=g.y-g.area*AREA_OFFSET_Y*FP;
  game_step(&g,RIGHT);
  if(g.area==1){assert(g.x+AREA_OFFSET_X*FP-before_x==320);assert(g.y-AREA_OFFSET_Y*FP==before_y);assert(g.vx==320);}
 }
 assert(g.area==1&&g.y==(BRIDGE_SURFACE_Y-PLAYER_H)*FP);
 step(&g,RIGHT,70);assert(g.gems==2&&g.collected==3);
 for(int i=0;i<200&&g.area==1;i++){
  int before_x=g.x+AREA_OFFSET_X*FP,before_y=g.y-AREA_OFFSET_Y*FP;
  game_step(&g,LEFT);
  if(g.area==0){assert(g.x-before_x==-320);assert(g.y==before_y);assert(g.vx==-320);}
 }
 assert(g.area==0&&g.gems==2&&g.collected==3);
 g.area=1;g.x=0;g.y=160*FP;g.vy=6*FP;g.grounded=0;
 step(&g,0,80);assert(g.area==1&&g.falls==1&&g.x==60*FP&&g.y==(BRIDGE_SURFACE_Y-PLAYER_H)*FP&&g.gems==2);
 game_reset(&g);step(&g,RIGHT,102);game_step(&g,DOWN);assert(g.sign_open);
 game_reset(&g);step(&g,RIGHT,1000);assert(g.x==(WORLD_W-PLAYER_W)*FP&&g.camera==0);
 assert(g.y+PLAYER_H*FP==game_floor(g.x/FP+PLAYER_W/2)*FP);
 step(&g,LEFT,1000);assert(g.x==0);
 game_step(&g,ATTACK);assert(g.attack==12&&g.facing==-1);
 step(&g,ATTACK,20);assert(g.attack==0);
 game_step(&g,0);game_step(&g,ATTACK);assert(g.attack==12);
 game_step(&g,RESET);assert(g.x==40*FP&&g.y==118*FP&&!g.collected&&!g.sign_open);
 for(int x=-1;x<=240;x++)assert(game_floor(x)>=145&&game_floor(x)<=158);
 for(int center=0;center<240;center++){
  assert(aligned_sprite_x(center,48,SIA_ANCHOR_X,0)+SIA_ANCHOR_X==center);
  assert(aligned_sprite_x(center,48,SIA_ANCHOR_X,1)+(47-SIA_ANCHOR_X)==center);
 }
 puts("PASS v0.6: terrain, jump, ladder, platforms/camera, registered area position/velocity continuity, flip anchors, bridge surface, two gems, round-trip persistence, fall respawn, reset, sign and attack");
}
