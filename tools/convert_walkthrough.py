"""Build GBA mode-4 visual/audio references from the user-supplied recording.

This is sampled video playback, not recovery of the original scene engine.
Requires ffmpeg, Pillow and the supplied MP4. Output fits in a 32 MiB GBA ROM.
"""
from pathlib import Path
import argparse, subprocess, tempfile, struct, json
from PIL import Image, ImageFont, ImageDraw

FRAME_BYTES=512+240*160
UI=[(0,0,0),(255,255,255),(255,210,80),(80,220,240),(15,25,50),(220,100,140)]
UI += [(0,0,0)]*(16-len(UI))
STILLS=[('TITLE',5),('MENU',8),('SEA',24),('ELDERS',36),('CHAMBER',60),
        ('SCOPE',72),('BIRD',92),('ARRIVAL',112),('ROOM',114)]
def run(*args):return subprocess.run(args,check=True,stdout=subprocess.PIPE).stdout
def encode(im):
    im=im.convert('RGB').resize((240,160),Image.Resampling.LANCZOS)
    q=im.quantize(colors=240,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    palette=q.getpalette()[:720]
    palette += [0]*(720-len(palette))
    colors=[tuple(palette[i:i+3]) for i in range(0,720,3)]+UI
    return b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in colors)+q.tobytes()
def main():
    p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',default='assets');a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    meta={'source':Path(a.video).name,'stills':dict(STILLS),'intro_start':10,'intro_end':108,
          'intro_fps':6,'audio_rate':16384,'source_overlays_retained':True,
          'method':'240x160 indexed frames; sampled playback; mixed recording audio'}
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        with (out/'visuals.bin').open('wb') as f:
            for name,t in STILLS:
                data=run('ffmpeg','-loglevel','error','-ss',str(t),'-i',a.video,'-map','0:v:0',
                         '-frames:v','1','-f','image2pipe','-vcodec','png','-')
                from io import BytesIO
                im=Image.open(BytesIO(data)).convert('RGB').resize((240,160),Image.Resampling.LANCZOS)
                if name=='MENU':
                    # Remove only the recorded selection arrow; native cursor replaces it.
                    im.paste(im.crop((34,44,53,63)),(15,44))
                f.write(encode(im))
            subprocess.run(['ffmpeg','-loglevel','error','-ss','10','-t','98','-i',a.video,
                            '-map','0:v:0','-vf','fps=6,scale=240:160','-vsync','0',str(tmp/'%04d.png')],check=True)
            frames=sorted(tmp.glob('*.png'));assert len(frames)==588,len(frames)
            for image in frames:f.write(encode(Image.open(image)))
    lengths={}
    for name,start,duration in [('title',2,8),('intro',10,98),('level',114,251)]:
        pcm=run('ffmpeg','-loglevel','error','-ss',str(start),'-t',str(duration),'-i',a.video,
                '-map','0:a:0','-ac','1','-ar','16384','-f','s8','-')
        lengths[name]=len(pcm);assert len(pcm)==duration*16384
        (out/f'audio_{name}.pcm').write_bytes(pcm+bytes(2048))
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',8)
    glyphs=bytearray()
    for c in range(32,128):
        im=Image.new('L',(6,8));ImageDraw.Draw(im).text((0,-2),chr(c),font=font,fill=255)
        for y in range(8):glyphs.append(sum(1<<x for x in range(6) if im.getpixel((x,y))>=80))
    (out/'font.bin').write_bytes(glyphs)
    header=['#ifndef ASSETS_H','#define ASSETS_H',f'#define ASSET_FRAME_BYTES {FRAME_BYTES}',
            f'#define INTRO_FIRST {len(STILLS)}','#define INTRO_COUNT 588','#define INTRO_FPS 6','#define INTRO_TICKS (98u*16384u)']
    header += [f'#define FRAME_{n} {i}' for i,(n,_) in enumerate(STILLS)]
    header += [f'#define AUDIO_{n.upper()}_LEN {v}u' for n,v in lengths.items()]
    header += ['extern const unsigned char assets_visuals[],audio_title[],audio_intro[],audio_level[],asset_font[];','#endif']
    (out/'assets.h').write_text('\n'.join(header)+'\n')
    meta['audio_lengths']=lengths;meta['intro_frames']=588
    (out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Built',len(STILLS)+392,'indexed frames,',sum(lengths.values()),'PCM bytes')
if __name__=='__main__':main()
