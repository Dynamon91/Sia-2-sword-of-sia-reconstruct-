import unittest
from PIL import Image
from tools.clean_frontend import clean_frame

class FrontendCleanupTest(unittest.TestCase):
    def test_preserves_observed_rows_and_native_geometry(self):
        original=Image.new('L',(240,160))
        for y in range(160):
            for x in range(240):
                original.putpixel((x,y),(x*3+y*7)%240+1)
        captured=original.copy()
        for y in range(12):
            for x in range(240):
                captured.putpixel((x,y),0)
        for y in range(12,30):
            for x in range(209,240):
                captured.putpixel((x,y),255)
        repaired=clean_frame(captured)
        self.assertEqual(repaired.size,(240,160))
        for y in range(12,160):
            for x in range(240):
                expected=original.getpixel((x,30)) if 209<=x<240 and 12<=y<30 else original.getpixel((x,y))
                self.assertEqual(repaired.getpixel((x,y)),expected,(x,y))
        for y in range(12):
            for x in range(240):
                self.assertEqual(repaired.getpixel((x,y)),repaired.getpixel((x,12)),(x,y))

if __name__=='__main__':
    unittest.main()
