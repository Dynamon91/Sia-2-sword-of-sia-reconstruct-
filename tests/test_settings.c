#include "../src/settings.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 unsigned char memory[SETTINGS_BYTES];unsigned sound,intro;
 for(unsigned erased=0;erased<2;erased++){
  for(unsigned i=0;i<SETTINGS_BYTES;i++)memory[i]=erased?255:0;
  settings_load(memory,&sound,&intro);assert(sound==1&&intro==1);
 }
 for(unsigned a=0;a<2;a++)for(unsigned b=0;b<2;b++){
  settings_store(memory,a,b);settings_load(memory,&sound,&intro);
  assert(sound==a&&intro==b);
  for(unsigned i=0;i<SETTINGS_BYTES;i++)for(unsigned bit=0;bit<8;bit++){
   memory[i]^=1u<<bit;settings_load(memory,&sound,&intro);
   assert(sound==1&&intro==1);memory[i]^=1u<<bit;
  }
 }
 settings_store(memory,0,0);memory[0]=0;
 settings_load(memory,&sound,&intro);assert(sound==1&&intro==1);
 puts("PASS settings: four combinations, erased SRAM, all single-bit corruptions, invalid commit marker");
}
