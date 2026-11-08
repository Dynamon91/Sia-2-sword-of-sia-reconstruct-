#ifndef VIEW_CAMERA_H
#define VIEW_CAMERA_H
#include "game.h"
#define VIEW_COUNT 15
/* Screen translations compose into a shared world; early cliff offsets provisional. */
static const int view_origin[VIEW_COUNT][2]={{0,0},{-152,60},{-358,14},{-574,29},
 {-732,47},{-920,72},{-1090,81},{-1258,88},{-1223,169},{-1165,154},
 {-1057,247},{-981,291},{-863,294},{-819,380},{-963,372}};
typedef struct { int x,y; } ViewCamera;
static inline void view_camera_reset(ViewCamera *v,const Game *g){
 v->x=view_origin[g->area][0]*FP;v->y=(view_origin[g->area][1]-g->camera_y)*FP;
}
static inline int view_limit(int n,int lo,int hi){return n<lo?lo:n>hi?hi:n;}
static inline void view_camera_step(ViewCamera *v,const Game *g){
 int px=g->x+PLAYER_W*FP/2-view_origin[g->area][0]*FP+v->x;
 int py=g->y+PLAYER_H*FP/2-view_origin[g->area][1]*FP+v->y;
 /* Directional framing: leave room ahead of actual movement. Idle and blocked
    movement do not swing the camera just because facing/input changed. */
 int dx=g->vx>0?80*FP-px:g->vx<0?128*FP-px:0;
 if(!g->vx)dx=px<16*FP?16*FP-px:px>224*FP?224*FP-px:0;
 int dy=py<48*FP?48*FP-py:py>136*FP?136*FP-py:0;
 v->x=view_limit(v->x+view_limit(dx,-6*FP,6*FP),-1258*FP,0);
 v->y=view_limit(v->y+view_limit(dy,-6*FP,6*FP),0,380*FP);
}
#endif
