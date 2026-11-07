/* Exercise cartridge SRAM through real files and fresh mGBA core instances. */
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

static void log_message(struct mLogger *logger,int category,enum mLogLevel level,const char *format,va_list args){
 (void)logger;
 if(level&(mLOG_FATAL|mLOG_ERROR|mLOG_WARN|mLOG_GAME_ERROR)){
  fprintf(stderr,"%s: ",mLogCategoryName(category));vfprintf(stderr,format,args);fputc('\n',stderr);
 }
}
static struct mLogger logger={.log=log_message,.filter=NULL};
static void frames(struct mCore *c,unsigned n){
 for(unsigned i=0;i<n;i++){
  short samples[2048];c->runFrame(c);
  blip_read_samples(c->getAudioChannel(c,0),samples,2048,0);
  blip_read_samples(c->getAudioChannel(c,1),samples,2048,0);
 }
}
static unsigned debug(struct mCore *c,unsigned i){return c->busRead32(c,0x0203F000+4*i);}
static void tap(struct mCore *c,unsigned key){c->setKeys(c,key);frames(c,8);c->setKeys(c,0);frames(c,8);}
static struct mCore *boot(const char *rom,const char *save,color_t *pixels){
 struct mCore *c=mCoreFind(rom);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
 c->setVideoBuffer(c,pixels,240);
 for(unsigned i=0;i<2;i++)blip_set_rates(c->getAudioChannel(c,i),c->frequency(c),32768);
 assert(mCoreLoadFile(c,rom));
 struct VFile *vf=VFileOpen(save,O_RDWR|O_CREAT);assert(vf&&c->loadSave(c,vf));
 c->reset(c);frames(c,90);assert(debug(c,0)==0);return c;
}
static void options(struct mCore *c){tap(c,8);tap(c,128);tap(c,1);assert(debug(c,0)==4);}
static void close_core(struct mCore *c){c->deinit(c);}
static void capture(struct mCore *c){
 const void *buffer;size_t stride;c->getPixels(c,&buffer,&stride);
 FILE *f=fopen("build/options_disk_reload.ppm","wb");assert(f);assert(fprintf(f,"P6\n240 160\n255\n")>0);
 for(unsigned y=0;y<160;y++)for(unsigned x=0;x<240;x++){
  color_t p=((const color_t*)buffer)[y*stride+x];unsigned char rgb[3]={p&255,(p>>8)&255,(p>>16)&255};
  assert(fwrite(rgb,1,3,f)==3);
 }
 assert(!fclose(f));
}
int main(int argc,char **argv){
 assert(argc==2);mLogSetDefaultLogger(&logger);
 /* A unique throwaway file never overwrites a player's adjacent .sav. */
 char save[]="build/settings-reload-XXXXXX";int fd=mkstemp(save);assert(fd>=0);assert(!close(fd));
 color_t *pixels=calloc(240*160,sizeof(*pixels));assert(pixels);
 struct mCore *c=boot(argv[1],save,pixels);assert(debug(c,3)==1&&debug(c,4)==0);
 options(c);tap(c,1);assert(debug(c,3)==0);frames(c,120);close_core(c);
 struct stat st;assert(!stat(save,&st)&&st.st_size==32768);
 c=boot(argv[1],save,pixels);assert(debug(c,3)==0&&debug(c,4)==0&&debug(c,7)==0);
 options(c);capture(c);tap(c,1);assert(debug(c,3)==1);frames(c,120);close_core(c);
 c=boot(argv[1],save,pixels);assert(debug(c,3)==1&&debug(c,4)==0);
 options(c);tap(c,1);assert(debug(c,3)==0);frames(c,120);close_core(c);
 FILE *f=fopen(save,"r+b");assert(f);assert(!fseek(f,6,SEEK_SET));int byte=fgetc(f);assert(byte!=EOF);
 assert(!fseek(f,6,SEEK_SET));assert(fputc(byte^1,f)!=EOF);assert(!fclose(f));
 c=boot(argv[1],save,pixels);assert(debug(c,3)==1&&debug(c,4)==0);close_core(c);
 free(pixels);assert(!unlink(save));
 puts("PASS disk save integration: fresh mGBA cores reload SOUND off/on from a 32 KiB SRAM file; intro stays disabled; corrupt checksum restores defaults");
}
