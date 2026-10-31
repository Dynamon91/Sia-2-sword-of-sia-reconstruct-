"""Non-local repetition-based background estimate from a mono game recording.
No neural model, original stems, semantic sound labels, or perfect separation.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from scipy import signal,ndimage
from scipy.io import wavfile
SR=16384;NFFT=2048;HOP=512

def main():
 ap=argparse.ArgumentParser();ap.add_argument('pcm',type=Path);ap.add_argument('--out',type=Path,default=Path('music/separation_trial'));a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 raw=a.pcm.read_bytes();x=np.frombuffer(raw,dtype=np.int8).astype(float)[:251*SR]/128
 f,t,z=signal.stft(x,SR,nperseg=NFFT,noverlap=NFFT-HOP);mag=np.abs(z)
 # Compare broad spectral shape plus neighboring context, excluding nearby time.
 edges=np.unique(np.round(np.geomspace(1,len(f),97)).astype(int));features=[]
 for lo,hi in zip(edges[:-1],edges[1:]):features.append(np.log1p(1000*np.mean(mag[lo:hi],axis=0)))
 feat=np.array(features);feat=ndimage.uniform_filter1d(feat,size=9,axis=1)
 feat-=np.mean(feat,axis=1,keepdims=True)
 feat=np.maximum(feat,0);feat/=np.maximum(np.linalg.norm(feat,axis=0,keepdims=True),1e-12)
 background=np.zeros_like(mag);quality=np.zeros(len(t));exclude=round(5*SR/HOP);k=12
 for begin in range(0,len(t),96):
  end=min(len(t),begin+96);sim=feat[:,begin:end].T@feat
  for row,col in enumerate(range(begin,end)):
   sim[row,max(0,col-exclude):min(len(t),col+exclude+1)]=-1
   idx=np.argpartition(sim[row],-k)[-k:];idx=idx[sim[row,idx]>=.72]
   quality[col]=len(idx)/k
   if len(idx)>=4:background[:,col]=np.minimum(mag[:,col],np.median(mag[:,idx],axis=1))
   else:background[:,col]=mag[:,col] # Do not suppress uncertain non-repeating material.
 residual=np.maximum(mag-background,0)
 mask=background**2/(background**2+(1.7*residual)**2+1e-15)
 mask=ndimage.median_filter(mask,size=(3,3))
 _,music=signal.istft(z*mask,SR,nperseg=NFFT,noverlap=NFFT-HOP)
 music=music[:len(x)];effects=x-music
 assert len(music)==len(x) and np.all(np.isfinite(music))
 assert np.max(np.abs((music+effects)-x))<1e-12
 def write(name,y):
  # Same gain for all comparison files, preserving relative level.
  wavfile.write(a.out/name,SR,(np.clip(y,-1,1)*30000).astype(np.int16))
 write('music_background_trial.wav',music)
 for name,y in [('source',x),('music',music),('residual',effects)]:write('preview_'+name+'_30s.wav',y[:30*SR])
 # Strong residual transients are candidates only: they can include percussion.
 rms=np.sqrt(np.maximum(0,ndimage.uniform_filter1d(effects**2,size=round(.06*SR))[::HOP]))
 peaks,_=signal.find_peaks(rms,distance=round(3*SR/HOP),prominence=.012)
 peaks=sorted(peaks,key=lambda i:rms[i],reverse=True)[:6];candidates=[]
 for num,i in enumerate(sorted(peaks),1):
  start=max(0,i*HOP/SR-.15);end=min(len(x)/SR,start+.9);b=round(start*SR);e=round(end*SR)
  name=f'candidate_{num:02d}_residual.wav';write(name,effects[b:e]);write(f'candidate_{num:02d}_source.wav',x[b:e])
  candidates.append({'file':name,'start_in_level_seconds':round(start,4),'video_seconds':round(start+114,4),'duration_seconds':round(end-start,4),'identified_effect':None,'ready_for_game':False})
 # A matching preview around the strongest residual event makes losses audible.
 if len(peaks):
  start=max(0,min(peaks[0]*HOP/SR-5,len(x)/SR-15));b=round(start*SR);e=b+15*SR
  for name,y in [('source',x),('music',music),('residual',effects)]:write('event_comparison_'+name+'_15s.wav',y[b:e])
 else:start=None
 report={'source_sha256':hashlib.sha256(raw).hexdigest(),'duration_seconds':len(x)/SR,'sample_rate':SR,'method':'non-local repetition estimate, 12 spectral neighbors at least 5 seconds apart; conservative fallback for unmatched material; soft magnitude mask with original phase',
 'frame_fraction_with_at_least_four_matches':float(np.mean(quality>=4/k)),'waveform_additivity_max_error':float(np.max(np.abs(music+effects-x))),
 'source_rms':float(np.sqrt(np.mean(x*x))),'music_rms':float(np.sqrt(np.mean(music*music))),'residual_rms':float(np.sqrt(np.mean(effects*effects))),
 'event_comparison_start_seconds':start,'candidates':candidates,'integrated_in_rom':False,
 'limitations':['Background and residual are estimates, not isolated stems.','Repeated sound effects may remain in background.','Unique music and drums can leak into residual.','No candidate has been identified or verified as a reusable effect.','No automatic quality or fidelity claim; compare by listening.']}
 (a.out/'separation_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
