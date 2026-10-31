#ifndef SETTINGS_H
#define SETTINGS_H
/* Versioned reconstruction settings; not an original-game save format.
 * Cartridge SRAM is accessed one byte at a time. */
#define SETTINGS_BYTES 8
static inline void settings_load(const volatile unsigned char *p,unsigned *sound,unsigned *intro){
 unsigned char b[SETTINGS_BYTES];
 for(unsigned i=0;i<SETTINGS_BYTES;i++)b[i]=p[i];
 *sound=1;*intro=1;
 if(b[0]!='L'||b[1]!='S'||b[2]!='2'||b[3]!='O'||b[4]!=1||b[5]>3||
    b[6]!=(unsigned char)(b[5]^0xA5)||b[7]!=(unsigned char)(b[6]^0xFF))return;
 *sound=b[5]&1;*intro=(b[5]>>1)&1;
}
static inline void settings_store(volatile unsigned char *p,unsigned sound,unsigned intro){
 unsigned char flags=(sound?1:0)|(intro?2:0);
 p[0]=0; /* Invalidate until the complete new record has been written. */
 p[1]='S';p[2]='2';p[3]='O';p[4]=1;p[5]=flags;
 p[6]=flags^0xA5;p[7]=(unsigned char)((flags^0xA5)^0xFF);
 p[0]='L';
}
#endif
