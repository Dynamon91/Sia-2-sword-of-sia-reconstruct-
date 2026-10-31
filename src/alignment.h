#ifndef ALIGNMENT_H
#define ALIGNMENT_H
/* Foreground registration of the shared island: first -> bridge (-152,+60).
   Measured from the supplied video; not recovered original world coordinates. */
#define AREA_OFFSET_X 152
#define AREA_OFFSET_Y 60
#define BRIDGE_SURFACE_Y 100
#define SIA_ANCHOR_X 24
#define SIA_ANCHOR_Y 56
static inline int aligned_sprite_x(int center,int width,int anchor,int flip){
 return center-(flip?width-1-anchor:anchor);
}
#endif
