#ifndef LOADING_H
#define LOADING_H
/* W1L1 source frames 3211..3305 at 30 fps, resampled to GBA refresh. */
#define LOADING_BLACK_BEFORE 10u
#define LOADING_TEXT_FRAMES 171u
#define LOADING_BLACK_AFTER 8u
#define LOADING_TOTAL_FRAMES (LOADING_BLACK_BEFORE+LOADING_TEXT_FRAMES+LOADING_BLACK_AFTER)
static inline int loading_text_visible(unsigned age){
 return age>=LOADING_BLACK_BEFORE&&age<LOADING_BLACK_BEFORE+LOADING_TEXT_FRAMES;
}
#endif
