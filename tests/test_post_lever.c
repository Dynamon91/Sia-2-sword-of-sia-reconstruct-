#include "../src/view_camera.h"
#include <assert.h>
#include <stdio.h>
static void at(Game *g,int area,int x,int y){
 game_reset(g);g->area=area;g->progress.area=(unsigned)area;g->x=x*FP;g->y=y*FP;
}
int main(void){
 Game g;int start_y=game_extension_floor(13,209)-PLAYER_H;
 at(&g,13,209,start_y);g.grounded=1;
 for(int x=0;x<76;x++)assert(game_extension_floor(14,x)==game_extension_floor(13,x+144)-8);
 ViewCamera v;view_camera_reset(&v,&g);int camera_x=v.x,camera_y=v.y;
 int world_x=g.x-view_origin[13][0]*FP;
 game_step(&g,RIGHT|JUMP);
 assert(g.area==14&&g.progress.area==14);
 assert(g.x-view_origin[14][0]*FP==world_x+320);
 assert(g.y==start_y*FP-928-8*FP);
 view_camera_step(&v,&g);
 assert(v.x-camera_x<=6*FP&&v.x-camera_x>=-6*FP);
 assert(v.y-camera_y<=6*FP&&v.y-camera_y>=-6*FP);
 for(int i=0;i<100;i++)game_step(&g,0);
 assert(g.area==14&&g.grounded&&g.y==(game_extension_floor(14,g.x/FP)-PLAYER_H)*FP&&!g.falls&&g.lives==3);
 for(int i=0;i<80&&g.area==14;i++)game_step(&g,LEFT);
 assert(g.area==13&&g.grounded&&g.y==109*FP&&g.lives==3);
 /* Rock side and underside block passage, without snapping onto the roof. */
 at(&g,14,113,25);game_step(&g,RIGHT);
 assert(g.x==114*FP&&!g.vx&&!g.grounded);
 at(&g,14,150,65);g.vy=-4*FP;
 game_step(&g,0);game_step(&g,0);assert(g.y==60*FP&&!g.vy&&!g.grounded);
 /* Opposing directions cannot trigger the return portal. */
 at(&g,14,31,101);g.grounded=1;game_step(&g,LEFT|RIGHT);assert(g.area==14);
 at(&g,15,165,78);g.grounded=1;
 game_step(&g,LEFT);assert(g.x==164*FP&&!g.vx&&g.grounded);
 /* The lower portal translates subpixels exactly, preserving downward velocity. */
 at(&g,14,95,169);g.x+=17;g.y+=128;g.vy=2*FP;g.grounded=0;
 int wx=g.x-view_origin[14][0]*FP,wy=g.y-view_origin[14][1]*FP;
 game_step(&g,0);assert(g.area==15&&g.vy==2*FP+32);
 assert(g.x-view_origin[15][0]*FP==wx&&g.y-view_origin[15][1]*FP==wy+g.vy);
 assert(game_extension_floor(15,191)==118&&game_extension_floor(15,192)==4096);
 /* A deep drop reaches the registered lower landing and preserves the run. */
 at(&g,14,90,101);assert(level_collect_gem(&g.progress,4));g.gems=1;g.collected=16;
 assert(level_defeat_enemy(&g.progress,3));g.enemy4_hp=0;
 assert(level_set_lever_state(&g.progress,1));
 for(int i=0;i<100&&!g.grounded;i++)game_step(&g,0);
 for(int i=0;i<100&&g.area==14;i++)game_step(&g,0);
 for(int i=0;i<100&&!g.grounded;i++)game_step(&g,0);
 assert(g.area==15&&g.grounded&&g.y==78*FP&&g.lives==3&&!g.falls);
 for(int i=0;i<160&&!g.falls;i++)game_step(&g,RIGHT);
 assert(g.falls==1&&g.lives==2&&g.area==15&&g.x==172*FP&&g.y==78*FP);
 assert(g.gems==1&&g.collected==16&&!g.enemy4_hp&&g.progress.defeated==1);
 assert(g.progress.lever_activated&&g.progress.barrier_open);
 game_step(&g,RESET);assert(g.area==0&&!g.progress.lever_activated&&g.lives==3);
 puts("PASS post-lever edge: airborne registered entry, landing, return, roof side/underside, lower landing, pit respawn and persistent run state");
}
