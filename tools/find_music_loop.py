"""Find a waveform-repeat candidate; correlation is not a listening approval."""
from pathlib import Path
import argparse,json
import numpy as np
from scipy import signal
from scipy.io import wavfile
p=argparse.ArgumentParser();p.add_argument('wav',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
sr,x=wavfile.read(a.wav)
assert x.dtype==np.int16 and x.ndim==1
# Match a two-second phrase against later occurrences, avoiding adjacent frames.
y=signal.resample_poly(x.astype(float),1,16);rate=sr/16;window=round(2*rate)
best=None
for seconds in range(4,min(40,int(len(x)/sr)-20),2):
 start=round(seconds*rate);q=y[start:start+window];q=q-q.mean()
 lo=start+round(8*rate);hi=min(len(y)-window,start+round(100*rate))
 if hi<=lo:continue
 section=y[lo:hi+window];corr=signal.correlate(section,q,mode='valid',method='fft')
 sums=np.r_[0,np.cumsum(section)];sq=np.r_[0,np.cumsum(section*section)]
 energy=np.maximum(1e-12,sq[window:]-sq[:-window]-(sums[window:]-sums[:-window])**2/window)
 scores=corr/np.sqrt(energy*np.dot(q,q));i=int(np.argmax(scores));score=float(scores[i])
 if best is None or score>best[0]:best=(score,start,lo+i)
assert best is not None
score,b,e=best;b*=16;e*=16
loop=x[b:e];assert len(loop)>sr*8
fade=min(round(.02*sr),len(loop)//4)
# Export the exact candidate plus a separate audition with a short crossfade.
wavfile.write(a.out/'loop_candidate_raw.wav',sr,loop)
f=np.linspace(0,1,fade);join=np.rint(loop[-fade:]*(1-f)+loop[:fade]*f).astype(np.int16)
audio=np.concatenate([loop[:-fade],join,loop[fade:]])
wavfile.write(a.out/'loop_twice_crossfade_preview.wav',sr,audio)
report={'source':a.wav.name,'sample_rate':sr,'start_seconds':b/sr,'end_seconds':e/sr,'duration_seconds':len(loop)/sr,'phrase_correlation':score,'raw_seam_jump_pcm16':abs(int(loop[-1])-int(loop[0])),'preview_crossfade_seconds':fade/sr,'approved_by_listening':False,'integrated_in_rom':False,'limits':['Waveform match may follow repeated effects as well as music.','A two-second match does not prove complete musical phrase alignment.','Crossfade preview changes the boundary; raw candidate remains available.','Music/effects isolation remains experimental.']}
(a.out/'loop_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
