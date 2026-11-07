#ifndef SCENERY_H
#define SCENERY_H
#define CLOUD_WIDTH 320u
#define CLOUD_HEIGHT 80u
#define CLOUD_BANK_BYTES (CLOUD_WIDTH*CLOUD_HEIGHT)
/* Active simulation ticks stop during dialogues, pause and game over. Keep
   the phase shared across viewports, rather than restarting at each portal. */
static inline unsigned cloud_phase(unsigned active_ticks){return (active_ticks/2u)%CLOUD_WIDTH;}
#endif
