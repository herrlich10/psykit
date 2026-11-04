import unittest

import sys
import numpy as np
from psychopy import visual
from psykit.stereomode import StereoWindow


def workaround_macOS_DisplayLink_hang(win):
    # This is probably a bug of PsychoPy 2026.2.5 on older macOS (before macOS 14, tested on macOS 12.6.5)
    # Cause: macOS 14 Sonoma introduced the new CADisplayLink API
    # Workaround for PsychoPy macOS DisplayLink hang.
    if sys.platform == "darwin":
        backend = win.backend
        if hasattr(backend, "refreshEventHandlerMacOS"):
            del backend.refreshEventHandlerMacOS


def capture_frame(win):
    """Capture the displayed frame as an RGB array."""
    # self._getPixels(buffer="front") returns ndarray directly, but is not public API
    return np.asarray(win.getMovieFrame(buffer="front").convert("RGB"))


def center_lum(frame, mode="none"):
    """Measure the center brightness."""
    h, w = frame.shape[:2]
    if mode == 'none':
        return frame[h//2,w//2].mean()
    elif mode == 'left/right':
        return {"left": frame[h//2,w//4].mean(), 
                "right": frame[h//2,w*3//4].mean()}


class TestWindowFlip(unittest.TestCase):

    def setUp(self):
        # Only support winType='pyglet', but not 'glfw' nor 'pygame'
        self.win = visual.Window(monitor="testMonitor", units="pix", size=(400,300),             
            color="black", checkTiming=False)
        workaround_macOS_DisplayLink_hang(self.win)
        self.stim = visual.Rect(self.win, size=100, fillColor="white")

    def tearDown(self):
        self.win.close()

    def test_flip_clear_buffer(self):
        # Draw a white rectangle
        self.stim.draw()

        # First flip: the rectangle should be visible, back buffer is not cleared
        print("Before first flip", flush=True)
        self.win.flip(clearBuffer=True)
        print("After first flip", flush=True)
        first = center_lum(capture_frame(self.win))
        with self.subTest(frame=1):
            self.assertAlmostEqual(first, 255, msg=f"first frame should be white")

        # Second flip: no new drawing, no setBuffer calls, back buffer is now cleared
        self.win.flip()
        second = center_lum(capture_frame(self.win))
        with self.subTest(frame=2):
            self.assertAlmostEqual(second, 0, msg=f"back buffer was not cleared after flip")


class TestStereoWindowFlip(unittest.TestCase):

    def setUp(self):
        self.win = StereoWindow(monitor="testMonitor", units="pix", size=(400,300),             
            stereoMode="left/right", color="black", checkTiming=False)
        workaround_macOS_DisplayLink_hang(self.win)
        self.stim = visual.Rect(self.win, size=100, fillColor="white")

    def tearDown(self):
        self.win.close()

    def test_flip_clear_both_eye_buffers(self):
        # Draw a white rectangle into each eye's buffer.
        for eye in ("left", "right"):
            self.win.setBuffer(eye, clear=True)
            self.stim.draw()

        # First flip: both rectangles should be visible, eye buffers are not cleared
        print("Before first flip", flush=True)
        self.win.flip(clearBuffer=False)
        print("After first flip", flush=True)
        first = center_lum(capture_frame(self.win), mode="left/right")
        for eye in ("left", "right"):
            with self.subTest(eye=eye, frame=1):
                self.assertAlmostEqual(first[eye], 255, msg=f"{eye} eye: first frame should be white")

        # Second flip: no new drawing, no setBuffer calls, eye buffers are now cleared
        self.win.flip(clearBuffer=True)
        second = center_lum(capture_frame(self.win), mode="left/right")
        for eye in ("left", "right"):
            with self.subTest(eye=eye, frame=2):
                self.assertAlmostEqual(second[eye], 255, msg=f"{eye} eye: second frame should still be white")

        # Third flip: no new drawing, no setBuffer calls, eye buffers are previously cleared
        self.win.flip(clearBuffer=False)
        third = center_lum(capture_frame(self.win), mode="left/right")
        for eye in ("left", "right"):
            with self.subTest(eye=eye, frame=3):
                self.assertAlmostEqual(third[eye], 0, msg=f"{eye} eye: buffer was not cleared after flip")


class TestStereoWindowCheckTiming(unittest.TestCase):

    def setUp(self):
        self.win = StereoWindow(monitor="testMonitor", units="pix", size=(400,300),             
            stereoMode="left/right", color="black", checkTiming=True)
        workaround_macOS_DisplayLink_hang(self.win)

    def tearDown(self):
        self.win.close()

    def test_check_timing(self):
        self.win.flip()


if __name__ == "__main__":
    unittest.main()
