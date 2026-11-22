#ifndef CRAWL_SKY_H
#define CRAWL_SKY_H
/* Sparse opaque runs; even/odd source banks permit aligned DMA at any x. */
#define CRAWL_SKY_WIDTH 240
#define CRAWL_SKY_HEIGHT 55
/* Registered later views expose the former repair pixels. In passage-local
   coordinates the foot view ends at x=32; the hall ends at x=148, with its
   first 14 rows and avatar (x>=112,y<45) still covered by the recording. */
static inline int crawl_patch_first_column(int y){return y<14?32:y<45?112:148;}
#endif
