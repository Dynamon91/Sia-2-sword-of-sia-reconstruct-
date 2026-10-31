#ifndef ASSETS_H
#define ASSETS_H
#define ASSET_FRAME_BYTES 38912
#define INTRO_FIRST 9
#define INTRO_COUNT 588
#define INTRO_FPS 6
#define INTRO_TICKS (98u*16384u)
#define FRAME_TITLE 0
#define FRAME_MENU 1
#define FRAME_SEA 2
#define FRAME_ELDERS 3
#define FRAME_CHAMBER 4
#define FRAME_SCOPE 5
#define FRAME_BIRD 6
#define FRAME_ARRIVAL 7
#define FRAME_ROOM 8
#define AUDIO_TITLE_LEN 131072u
#define AUDIO_INTRO_LEN 1605632u
#define AUDIO_LEVEL_LEN 4112384u
extern const unsigned char assets_visuals[],audio_title[],audio_intro[],audio_level[],asset_font[];
#endif
