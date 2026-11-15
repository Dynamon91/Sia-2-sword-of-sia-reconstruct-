import unittest
import numpy as np
from PIL import Image
from tools.clean_frontend import clean_frame, encode_intro_video, decode_intro_video

class FrontendCleanupTest(unittest.TestCase):
    def test_preserves_observed_rows_and_native_geometry(self):
        yy,xx=np.indices((160,240))
        original=((xx*3+yy*7)%240+1).astype(np.uint8)
        covered=np.zeros(original.shape,dtype=bool)
        covered[:13]=True;covered[13:31,208:240]=True
        captured=original.copy();captured[covered]=255
        repaired=clean_frame(Image.fromarray(captured))
        self.assertEqual(repaired.size,(240,160))
        np.testing.assert_array_equal(np.asarray(repaired)[~covered],original[~covered])

    def test_black_intro_has_no_gray_banner_or_avatar_edge(self):
        captured=np.zeros((160,240),dtype=np.uint8)
        captured[130:140,20:190]=1 # visible story text remains in place
        captured[:13]=2;captured[13:31,208:240]=2
        palette=np.zeros(256,dtype='<u2');palette[1]=0x7FFF;palette[2]=0x6318
        repaired=np.asarray(clean_frame(Image.fromarray(captured),palette.tobytes()))
        self.assertFalse(np.any(repaired[:60]))
        np.testing.assert_array_equal(repaired[130:140],captured[130:140])

    def test_bright_sky_pixel_is_not_stretched_into_a_vertical_line(self):
        sky=np.zeros((160,240),dtype=np.uint8);sky[13,100]=255
        repaired=np.asarray(clean_frame(Image.fromarray(sky)))
        self.assertEqual(repaired[13,100],255)
        self.assertLess(repaired[0,100],50)
        self.assertLess(repaired[6,100],repaired[12,100])

    def test_lz77_intro_delta_blocks_round_trip(self):
        from tools.clean_frontend import FRAME_BYTES
        base=bytes((i*17+(i//127))&255 for i in range(FRAME_BYTES))
        changed=bytearray(base)
        for i in range(0,len(changed),997):changed[i]^=0x5A
        frames=[base,bytes(changed),bytes(changed)]
        blob=encode_intro_video(frames,expected_count=len(frames))
        self.assertEqual(decode_intro_video(blob,len(frames)),frames)

if __name__=="__main__":unittest.main()
