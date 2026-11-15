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
  settings_store(memory,a,b);assert(memory[4]==2);
  settings_load(memory,&sound,&intro);assert(sound==a&&intro==b);
  for(unsigned i=0;i<SETTINGS_BYTES;i++)for(unsigned bit=0;bit<8;bit++){
   memory[i]^=1u<<bit;settings_load(memory,&sound,&intro);
   assert(sound==1&&intro==1);memory[i]^=1u<<bit;
  }
 }
 for(unsigned sound_before=0;sound_before<2;sound_before++){
  unsigned char old[SETTINGS_BYTES]={'L','S','2','O',1,0,0,0};
  old[5]=(unsigned char)sound_before;
  old[6]=(unsigned char)(old[5]^0xA5);
  old[7]=(unsigned char)(old[6]^0xFF);
  settings_load(old,&sound,&intro);
  assert(sound==sound_before&&intro==1);
  assert(old[4]==2&&old[5]==(unsigned char)(sound_before|2));
 }
 settings_store(memory,0,0);memory[0]=0;
 settings_load(memory,&sound,&intro);assert(sound==1&&intro==1);
 puts("PASS settings: v2 combinations, erased SRAM, v1 intro migration, single-bit corruption and invalid commit marker");
}
