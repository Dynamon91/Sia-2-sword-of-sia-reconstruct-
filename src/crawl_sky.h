#ifndef CRAWL_SKY_H
#define CRAWL_SKY_H
/* Sparse opaque runs; even/odd source banks permit aligned DMA at any x. */
#define CRAWL_SKY_WIDTH 240
#define CRAWL_SKY_HEIGHT 55
/* Registered later views expose the former repair pixels. In passage-local
   coordinates the upper views expose columns through x=74/62 in the first
   14 rows; the hall exposes x<148 below the avatar (x>=112,y<45). */
static inline int crawl_patch_first_column(int y){return y<13?74:y<14?62:y<45?112:148;}
#endif
