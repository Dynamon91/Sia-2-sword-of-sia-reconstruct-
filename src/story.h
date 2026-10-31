#ifndef STORY_H
#define STORY_H
typedef struct { const char *speaker,*text; unsigned frame; const char *time; } StoryPage;
extern const StoryPage story[];
extern const unsigned story_count;
#endif
