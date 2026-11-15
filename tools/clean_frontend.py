"""Clean all recorded frontend frames and pack intro deltas for the GBA."""
from pathlib import Path
import hashlib
import json
import struct
from functools import lru_cache
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FRAME_BYTES=38912
FRONTEND_COUNT=9
INTRO_COUNT=588
TOTAL_COUNT=FRONTEND_COUNT+INTRO_COUNT
WIDTH=240
HEIGHT=160


BANNER_ROWS=13
AVATAR_RECT=(208,13,32,18)
CLEANUP_REVISION=2

@lru_cache(maxsize=1)
def recording_repair_system():
    """Factor the fixed Laplace system once for all captured frames."""
    from scipy.sparse import csc_matrix
    from scipy.sparse.linalg import splu
    covered=np.zeros((HEIGHT,WIDTH),dtype=bool)
    covered[:BANNER_ROWS]=True
    left,top,width,height=AVATAR_RECT
    covered[top:top+height,left:left+width]=True
    yy,xx=np.nonzero(covered)
    ids=np.full(covered.shape,-1,dtype=np.int32)
    ids[yy,xx]=np.arange(len(yy))
    rows=[];columns=[];values=[];boundary_rows=[];boundary_y=[];boundary_x=[]
    for index,(y,x) in enumerate(zip(yy,xx)):
        degree=0
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny,nx=y+dy,x+dx
            if not (0<=ny<HEIGHT and 0<=nx<WIDTH):continue
            degree+=1
            neighbor=ids[ny,nx]
            if neighbor>=0:
                rows.append(index);columns.append(int(neighbor));values.append(-1.0)
            else:
                boundary_rows.append(index);boundary_y.append(ny);boundary_x.append(nx)
        rows.append(index);columns.append(index);values.append(float(degree))
    matrix=csc_matrix((values,(rows,columns)),shape=(len(yy),len(yy)))
    return yy,xx,np.asarray(boundary_rows),np.asarray(boundary_y),np.asarray(boundary_x),splu(matrix)

def clean_frame(im,palette=None):
    if im.size != (WIDTH,HEIGHT):
        raise ValueError("Expected a native 240x160 frontend still")
    if im.mode!="L":raise ValueError("Expected native indexed pixels in L mode")
    pixels=np.asarray(im).copy()
    yy,xx,rows,by,bx,system=recording_repair_system()
    colors=None
    if palette is not None:
        if len(palette)!=512:raise ValueError("Expected a 256-color GBA palette")
        words=np.frombuffer(palette,dtype='<u2')
        colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.int32)
        boundary=colors[pixels[by,bx]].astype(np.float64)
    else:
        boundary=pixels[by,bx,None].astype(np.float64)
    if np.all(boundary==boundary[0]):
        filled=np.broadcast_to(boundary[0],(len(yy),boundary.shape[1]))
    else:
        rhs=np.zeros((len(yy),boundary.shape[1]),dtype=np.float64)
        np.add.at(rhs,rows,boundary)
        filled=system.solve(rhs)
    # Only covered pixels are estimated. Diffusion avoids the former vertical
    # streaks from repeating a contaminated row; observed art never moves.
    filled=np.floor(filled+0.500001).clip(0,255).astype(np.int32)
    if colors is None:
        pixels[yy,xx]=filled[:,0].astype(np.uint8)
    else:
        unique,inverse=np.unique(filled,axis=0,return_inverse=True)
        nearest=np.empty(len(unique),dtype=np.uint8)
        for start in range(0,len(unique),1024):
            delta=unique[start:start+1024,None,:]-colors[None,:,:]
            nearest[start:start+1024]=np.sum(delta*delta,axis=2).argmin(1)
        pixels[yy,xx]=nearest[inverse]
    return Image.fromarray(pixels)

def compress_lz77(data):
    """Encode GBA BIOS 0x10 LZ77 data with a 4 KiB window and 18-byte matches."""
    length=len(data)
    if length>0xFFFFFF:
        raise ValueError("GBA LZ77 block is too large")
    out=bytearray((0x10,length&255,(length>>8)&255,(length>>16)&255))
    positions={}
    cursor=0
    while cursor<length:
        flag_index=len(out)
        out.append(0)
        flags=0
        for bit in range(7,-1,-1):
            if cursor>=length:
                break
            best_length=0
            best_distance=0
            if cursor+2<length:
                candidates=positions.get(data[cursor:cursor+3],())
                first=max(0,len(candidates)-64)
                limit=min(18,length-cursor)
                for n in range(len(candidates)-1,first-1,-1):
                    candidate=candidates[n]
                    distance=cursor-candidate
                    if distance>4096:
                        break
                    match=3
                    while match<limit and data[candidate+match]==data[cursor+match]:
                        match+=1
                    if match>best_length:
                        best_length=match
                        best_distance=distance
                        if match==limit:
                            break
            start=cursor
            if best_length>=3:
                flags|=1<<bit
                displacement=best_distance-1
                out.append(((best_length-3)<<4)|(displacement>>8))
                out.append(displacement&255)
                cursor+=best_length
            else:
                out.append(data[cursor])
                cursor+=1
            for position in range(start,cursor):
                if position+2<length:
                    key=data[position:position+3]
                    positions.setdefault(key,[]).append(position)
        out[flag_index]=flags
    return bytes(out)

def decompress_lz77(block):
    if len(block)<4 or block[0]!=0x10:
        raise ValueError("Invalid GBA LZ77 header")
    length=block[1]|(block[2]<<8)|(block[3]<<16)
    output=bytearray()
    cursor=4
    while len(output)<length:
        if cursor>=len(block):
            raise ValueError("Truncated GBA LZ77 flags")
        flags=block[cursor]
        cursor+=1
        for bit in range(7,-1,-1):
            if len(output)>=length:
                break
            if flags&(1<<bit):
                if cursor+2>len(block):
                    raise ValueError("Truncated GBA LZ77 match")
                a,b=block[cursor],block[cursor+1]
                cursor+=2
                count=(a>>4)+3
                distance=(((a&15)<<8)|b)+1
                if distance>len(output) or len(output)+count>length:
                    raise ValueError("Invalid GBA LZ77 match")
                for _ in range(count):
                    output.append(output[-distance])
            else:
                if cursor>=len(block):
                    raise ValueError("Truncated GBA LZ77 literal")
                output.append(block[cursor])
                cursor+=1
    return bytes(output)

def encode_intro_video(frames,expected_count=INTRO_COUNT):
    """Index independent LZ77 blocks; frame zero is absolute, later frames are XOR deltas."""
    offsets=[0]
    payload=bytearray()
    previous=None
    count=0
    for frame in frames:
        frame=bytes(frame)
        if len(frame)!=FRAME_BYTES:
            raise ValueError("Every intro frame must include a 240x160 image and palette")
        delta=frame if previous is None else bytes(a^b for a,b in zip(frame,previous))
        block=compress_lz77(delta)
        if decompress_lz77(block)!=delta:
            raise ValueError("GBA LZ77 verification failed")
        payload.extend(block)
        offsets.append(len(payload))
        previous=frame
        count+=1
    if count!=expected_count:
        raise ValueError("Expected "+str(expected_count)+" intro frames, got "+str(count))
    index=b"".join(struct.pack("<I",offset) for offset in offsets)
    return index+payload

def decode_intro_video(blob,count):
    index_bytes=4*(count+1)
    if len(blob)<index_bytes:
        raise ValueError("Truncated intro offset table")
    offsets=struct.unpack("<"+"I"*(count+1),blob[:index_bytes])
    payload=blob[index_bytes:]
    previous=None
    frames=[]
    for index in range(count):
        start,end=offsets[index],offsets[index+1]
        if end<=start or end>len(payload):
            raise ValueError("Invalid intro frame offset")
        delta=decompress_lz77(payload[start:end])
        if len(delta)!=FRAME_BYTES:
            raise ValueError("Invalid intro frame size")
        frame=delta if previous is None else bytes(a^b for a,b in zip(delta,previous))
        frames.append(frame)
        previous=frame
    return frames

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    asset_dir=ROOT/"assets"
    visuals=asset_dir/"visuals.bin"
    report_path=asset_dir/"frontend_cleanup.json"
    intro_path=asset_dir/"intro_video.bin"
    frontend_path=asset_dir/"frontend.bin"
    raw=visuals.read_bytes()
    archive=json.loads((asset_dir/"embedded_assets.json").read_text())
    expected=next(a["sha256"] for a in archive["assets"] if a["path"]=="assets/visuals.bin")
    if report_path.exists():
        report=json.loads(report_path.read_text())
        if (report.get("cleanup_revision")==CLEANUP_REVISION and
            report.get("input_sha256")==expected and
            report.get("cleaned_visuals_sha256")==hashlib.sha256(raw).hexdigest() and
            frontend_path.exists() and report.get("frontend_sha256")==sha(frontend_path) and
            intro_path.exists() and report.get("intro_video_sha256")==sha(intro_path)):
            print("Frontend frames already cleaned and intro stream verified")
            return
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise SystemExit("Restore original assets before cleanup")
    if len(raw)!=TOTAL_COUNT*FRAME_BYTES:
        raise SystemExit("Expected 597 indexed frames; got "+str(len(raw)//FRAME_BYTES))
    cleaned=bytearray()
    intro_frames=[]
    for index in range(TOTAL_COUNT):
        frame=raw[index*FRAME_BYTES:(index+1)*FRAME_BYTES]
        palette=frame[:512]
        image=Image.frombytes("L",(WIDTH,HEIGHT),frame[512:])
        image=clean_frame(image,palette)
        fixed=palette+image.tobytes()
        cleaned.extend(fixed)
        if index>=FRONTEND_COUNT:
            intro_frames.append(fixed)
    visuals.write_bytes(cleaned)
    frontend_path.write_bytes(cleaned[:FRONTEND_COUNT*FRAME_BYTES])
    intro_video=encode_intro_video(intro_frames)
    intro_path.write_bytes(intro_video)
    report={
        "cleanup_revision":CLEANUP_REVISION,
        "input_sha256":expected,
        "cleaned_visuals_sha256":hashlib.sha256(cleaned).hexdigest(),
        "frontend_sha256":sha(frontend_path),
        "intro_video_sha256":hashlib.sha256(intro_video).hexdigest(),
        "intro_video_bytes":len(intro_video),
        "intro_uncompressed_bytes":INTRO_COUNT*FRAME_BYTES,
        "intro_frame_count":INTRO_COUNT,
        "intro_fps":6,
        "intro_audio_length_samples":1605632,
        "recording_banner_removed_rows":BANNER_ROWS,
        "recording_avatar_removed_rect":list(AVATAR_RECT),
        "covered_pixels":"harmonic RGB continuation from unobscured boundary, mapped to the original GBA palette; not recovered original art",
        "observed_rows":"kept at their original y coordinates; no scaling",
        "video_encoding":"GBA LZ77 blocks; first frame absolute; later frames XOR deltas; little-endian uint32 offset table"
    }
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("PASS frontend cleanup: 597 frames, banner/avatar masked, intro encoded as verified GBA LZ77 delta stream")
if __name__=="__main__":
    main()
