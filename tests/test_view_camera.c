#include "../src/view_camera.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
int main(void){
 Game g;game_reset(&g);ViewCamera v;view_camera_reset(&v,&g);
 assert(!v.x&&!v.y);
 for(int i=0;i<200;i++){g.x+=320;int x=v.x,y=v.y;view_camera_step(&v,&g);assert(abs(v.x-x)<=6*FP&&abs(v.y-y)<=6*FP);}
 /* All registered late-route portals preserve the projected player at a fixed camera. */
 const int pairs[][4]={{0,1,-152,60},{1,2,-206,-46},{2,3,-216,15},{3,4,-158,18},{4,5,-188,25},{5,6,-170,9},{6,7,-168,7},{7,8,35,81},{8,9,58,-15},{9,10,108,93},{10,11,76,44},{11,12,118,3},{12,13,44,86},{13,14,-144,-8}};
 for(unsigned i=0;i<sizeof(pairs)/sizeof(pairs[0]);i++){
  int a=pairs[i][0],b=pairs[i][1],dx=pairs[i][2],dy=pairs[i][3];
  assert(view_origin[b][0]-view_origin[a][0]==dx);
  assert(view_origin[b][1]-view_origin[a][1]==dy);
  int oldx=75-view_origin[a][0],oldy=40-view_origin[a][1];
  assert(75+dx-view_origin[b][0]==oldx&&40+dy-view_origin[b][1]==oldy);
 }
 /* Early cliff portals retain their subpixel position in both directions. */
 const int early[][6]={{1,224,60,RIGHT,2,320},{2,8,14,LEFT,1,-320},{2,224,75,RIGHT,3,320},{3,0,90,LEFT,2,0}};
 for(unsigned i=0;i<4;i++){
  game_reset(&g);g.area=early[i][0];g.progress.area=(unsigned)g.area;g.x=early[i][1]*FP;g.y=early[i][2]*FP;g.grounded=1;
  int wx=g.x-view_origin[g.area][0]*FP,wy=g.y-view_origin[g.area][1]*FP;
  game_step(&g,(unsigned)early[i][3]);assert(g.area==early[i][4]);
  assert(g.x-view_origin[g.area][0]*FP==wx+early[i][5]);assert(g.y-view_origin[g.area][1]*FP==wy);
 }
 /* Area identity itself cannot move the camera; only the common world position follows. */
 game_reset(&g);g.area=11;g.x=24*FP;g.y=20*FP;view_camera_reset(&v,&g);view_camera_step(&v,&g);
 ViewCamera same=v;int px=g.x-view_origin[11][0]*FP,py=g.y-view_origin[11][1]*FP;
 g.area=12;g.x+=118*FP;g.y+=3*FP;assert(g.x-view_origin[12][0]*FP==px&&g.y-view_origin[12][1]*FP==py);
 Game old=g;old.area=11;old.x-=118*FP;old.y-=3*FP;view_camera_step(&same,&old);view_camera_step(&v,&g);assert(v.x==same.x&&v.y==same.y);
 puts("PASS world camera: bounded follow, fourteen portal transforms (early cliff geometry provisional), area-independent projection and no portal camera reset");
}
