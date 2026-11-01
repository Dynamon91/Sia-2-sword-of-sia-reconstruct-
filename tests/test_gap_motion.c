#include "../src/game.h"
#include <assert.h>
#include <stdio.h>
static void steps(Game *g,unsigned key,int n){while(n--)game_step(g,key);}
int main(void){
 Game g;game_reset(&g);
 /* Walking advances only while moving on a surface, and all three poses occur. */
 unsigned seen=0;for(int i=0;i<24;i++){game_step(&g,RIGHT);seen|=1u<<game_walk_frame(&g);}
 assert(seen==7);game_step(&g,0);assert(g.walk_ticks==0);
 game_step(&g,JUMP);assert(!g.grounded&&g.walk_ticks==0);
 /* Attack phases and hit window are driven by the same state counter. */
 game_reset(&g);g.area=3;g.x=125*FP;g.y=48*FP;g.grounded=1;
 game_step(&g,ATTACK);assert(game_attack_frame(&g)==0&&g.enemy_hp==2);
 steps(&g,ATTACK,3);assert(g.enemy_hp==2);
 game_step(&g,ATTACK);assert(game_attack_frame(&g)==1&&g.enemy_hp==1);
 steps(&g,ATTACK,5);assert(game_attack_frame(&g)==2&&g.enemy_hp==1);
 steps(&g,ATTACK,10);assert(g.attack==0&&g.enemy_hp==1);
 /* Exact registered portal transform in both directions; no velocity reset. */
 game_reset(&g);g.area=3;g.progress.area=3;g.x=224*FP;g.y=48*FP;g.grounded=1;g.enemy_hp=0;
 int x=g.x,y=g.y;game_step(&g,RIGHT);
 assert(g.area==4&&g.x+158*FP-x==320&&g.y-18*FP==y&&g.vx==320);
 g.x=33*FP;g.y=66*FP;g.grounded=1;x=g.x;y=g.y;game_step(&g,LEFT);
 assert(g.area==3&&g.x-158*FP-x==-320&&g.y+18*FP==y&&g.vx==-320);
 /* Real gap: edge launch reaches the far island and its suspended gem. */
 game_reset(&g);g.area=4;g.progress.area=4;g.x=94*FP;g.y=66*FP;g.grounded=1;g.enemy2_hp=0;
 steps(&g,JUMP|RIGHT,60);steps(&g,0,10);
 assert(g.grounded&&g.y==58*FP&&g.falls==0);
 assert(g.gems==1&&(g.collected&8)&&g.progress.gems_taken[0]==8);
 /* Revisiting cannot award the same gem twice. */
 g.x=126*FP;g.y=40*FP;g.vy=0;game_step(&g,0);assert(g.gems==1);
 /* Missed jump stops at the cliff's side and falls, never snaps onto its top. */
 g.x=157*FP;g.y=80*FP;g.vy=FP;g.grounded=0;game_step(&g,RIGHT);
 assert(g.x==158*FP&&!g.grounded&&g.y>80*FP&&g.vx==0);
 steps(&g,RIGHT,70);assert(g.falls==1&&g.progress.health==2&&g.gems==1);
 /* Independent second guard, with persistent entity ID and reset behavior. */
 game_reset(&g);g.area=4;g.x=180*FP;g.y=58*FP;g.grounded=1;
 game_step(&g,ATTACK);steps(&g,0,4);assert(g.enemy2_hp==1&&g.enemy_hp==2);
 steps(&g,0,12);game_step(&g,ATTACK);steps(&g,0,4);
 assert(g.enemy2_hp==0&&g.progress.defeated==1&&g.progress.enemies_defeated[0]==2);
 game_reset(&g);assert(g.enemy2_hp==2&&g.collected==0&&g.walk_ticks==0);
 puts("PASS gap/motion: three walk poses, synchronized sword hit window, registered portals, reachable gap/gem, solid cliff sides, independent guard persistence");
}
