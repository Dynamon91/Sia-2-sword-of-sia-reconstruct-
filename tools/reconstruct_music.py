"""Approximate transcription from the supplied mixed recording, not recovered music data.
Requires numpy/scipy. No original music driver, samples or score are claimed.
"""
from pathlib import Path
import argparse, json, hashlib, struct
import numpy as np
from scipy import signal, ndimage
from scipy.io import wavfile

SR=16384
HOP=256
NFFT=2048

def vlq(n):
    out=[n&127];n>>=7
    while n:out.insert(0,(n&127)|128);n>>=7
    return bytes(out)

def midi(path,notes):
    # Fixed 120 BPM is a timebase, not an asserted original tempo.
    events=[]
    for start,end,pitch,amp in notes:
        ch=1 if pitch<60 else 0
        velocity=max(24,min(110,round(amp*100)))
        events.extend([(round(start*960),bytes([0x90|ch,pitch,velocity])),
                       (round(end*960),bytes([0x80|ch,pitch,0]))])
    events.sort(key=lambda e:(e[0],e[1][0]&0xf0))
    track=b'\x00\xff\x51\x03\x07\xa1\x20'+b'\x00\xc0\x50\x00\xc1\x26'
    previous=0
    for tick,event in events:track+=vlq(tick-previous)+event;previous=tick
    track+=b'\x00\xff\x2f\x00'
    path.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pcm',type=Path);ap.add_argument('--seconds',type=float,default=251)
    ap.add_argument('--out',type=Path,default=Path('music'));a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    raw=a.pcm.read_bytes();x=np.frombuffer(raw,dtype=np.int8).astype(np.float64)/128
    x=x[:min(len(x),round(a.seconds*SR))];duration=len(x)/SR
    freq,t,z=signal.stft(x,SR,nperseg=NFFT,noverlap=NFFT-HOP,boundary='zeros')
    mag=np.abs(z)
    harmonic=ndimage.median_filter(mag,size=(1,21))
    percussive=ndimage.median_filter(mag,size=(21,1))
    mask=harmonic**2/(harmonic**2+percussive**2+1e-12)
    _,clean=signal.istft(z*mask,SR,nperseg=NFFT,noverlap=NFFT-HOP)
    clean=clean[:len(x)]
    # Harmonic templates with a smooth spectral envelope. They cannot identify instruments.
    pitches=np.arange(36,97);dictionary=np.zeros((len(freq),len(pitches)))
    for j,p in enumerate(pitches):
        fundamental=440*2**((int(p)-69)/12)
        for h in range(1,7):
            if fundamental*h>=SR/2:break
            dictionary[:,j]+=np.exp(-0.5*((freq-fundamental*h)/(SR/NFFT*0.8))**2)/h**1.3
    whitening=1/np.maximum(np.mean(mag*mask,axis=1),0.00008)**0.55
    dictionary*=whitening[:,None]
    dictionary/=np.maximum(np.linalg.norm(dictionary,axis=0),1e-12)
    residual=(mag*mask)*whitening[:,None]
    activations=np.zeros((len(pitches),len(t)))
    cols=np.arange(len(t))
    for _ in range(4):
        scores=dictionary.T@residual
        idx=np.argmax(scores,axis=0);strength=scores[idx,cols]
        activations[idx,cols]+=strength
        residual=np.maximum(0,residual-dictionary[:,idx]*strength)
    activations=ndimage.median_filter(activations,size=(1,3))
    global_peak=float(np.max(activations));notes=[]
    for j,p in enumerate(pitches):
        row=activations[j];threshold=max(global_peak*0.11,float(np.max(row))*0.24)
        active=row>threshold
        # Fill only one-frame holes; avoid extending notes into adjacent phrases.
        active[1:-1]|=active[:-2]&active[2:]
        edges=np.diff(np.r_[False,active,False].astype(int));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
        for b,e in zip(starts,ends):
            start=max(0,float(t[b]-HOP/SR/2));end=min(duration,float(t[min(e,len(t)-1)]-HOP/SR/2))
            if end-start<0.095:continue
            amp=float(np.mean(row[b:e])/max(global_peak,1e-12))
            notes.append((round(start,5),round(end,5),int(p),amp))
    notes.sort();midi(a.out/'level1_transcription_draft.mid',notes)
    synth=np.zeros(len(x),dtype=np.float64)
    for start,end,p,amp in notes:
        b=round(start*SR);e=min(len(x),round(end*SR)+round(.07*SR));n=e-b
        if n<=0:continue
        time=np.arange(n)/SR;f=440*2**((p-69)/12)
        # New neutral additive timbres, unrelated to the original sample bank.
        tone=np.sin(2*np.pi*f*time)+.22*np.sin(2*np.pi*2*f*time)+.08*np.sin(2*np.pi*3*f*time)
        env=np.minimum(time/.012,1)*np.minimum(np.maximum((n/SR-time)/.07,0),1)
        synth[b:e]+=tone*env*amp*(.22 if p<60 else .15)
    synth=np.tanh(synth)
    def wav(name,y):
        wavfile.write(a.out/name,SR,(np.clip(y,-1,1)*30000).astype(np.int16))
    wav('level1_resynthesis_draft.wav',synth)
    wav('level1_harmonic_reference.wav',clean)
    wav('preview_reconstruction_30s.wav',synth[:30*SR])
    wav('preview_source_30s.wav',x[:30*SR])
    wav('preview_harmonic_30s.wav',clean[:30*SR])
    report={'source_sha256':hashlib.sha256(raw).hexdigest(),'source_pcm':'signed 8-bit mono 16384 Hz',
            'duration_seconds':duration,'method':'median harmonic/percussive mask; four-component harmonic-template matching; unquantized note segmentation; neutral additive synthesis',
            'notes':len(notes),'pitch_range_considered':[36,96],'midi_timebase_bpm':120,
            'tempo_estimated':False,'original_samples_recovered':False,'original_score_recovered':False,
            'integrated_in_rom':False,'limitations':['Effects with stable pitch can remain in the harmonic reference and transcription.','Missed notes, false notes and octave errors require listening and manual correction.','No original instruments or percussion reconstructed.','No loop point or original tempo confirmed.'],
            'note_events':[{'start':s,'end':e,'midi_pitch':p,'strength':round(v,5)} for s,e,p,v in notes]}
    (a.out/'reconstruction_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='note_events'},indent=2))
if __name__=='__main__':main()
