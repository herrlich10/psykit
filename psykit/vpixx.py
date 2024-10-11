#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, warnings
# from pypixxlib.propixx import PROPixx
# from pypixxlib import _libdpx


def reset_propixx(pixx, config=None):
    '''
    Reset ProPixx to its ordinary operating modes: rear, non-ceiling, RGB, C24

    Note that for fMRI, the mirror in the head coil will cause a left-right flip.
    'RearProjectionMode' should be False for rear projection in this scenario.

    Parameters
    ----------
    pixx : pypixxlib.propixx.PROPixx
        An initialized PROPixx object, e.g., ``pixx = pypixxlib.propixx.PROPixx()``.
    config : str or dict
        If provided, reset ProPixx to the modes defined by a config file (*.json)
        or a dict, e.g., for fMRI experiments with one mirror in the light path, 
        ``config=dict(RearProjectionMode=False)``.
    '''
    # Default configuration
    cfg = {
        'RearProjectionMode': True,
        'CeilingMountMode': False,
        'DlpSequencerProgram': 'RGB',
        'VideoMode': 'C24',
        'VideoVesaBlueline': False,
        'VesaFreeRun': False,
    }
    # Load and update configuration from the file/dict
    if config is not None:
        if isinstance(config, str):
            with open(config, 'r') as fi:
                config = json.load(fi)
        cfg.update(config)
    # Image orientation
    pixx.setRearProjectionMode(cfg['RearProjectionMode']) # Set rear-projection mode (flip-left-right; instant)
    pixx.setCeilingMountMode(cfg['CeilingMountMode']) # Set ceiling-mount mode (flip-up-down; instant)
    # DLP sequencer (timing)
    pixx.setDlpSequencerProgram(cfg['DlpSequencerProgram']) # Set DLP sequencer program (RGB|RB3D|RGB240|QUAD4X|QUAD12X; instant)
    # Video mode (color)
    pixx.setVideoMode(cfg['VideoMode']) # Set color 24-bit video color translation mode (C24|L48|M16|C48; cached)
    # 3D VESA port (polarizer or shutter glasses)
    pixx.setVideoVesaBlueline(cfg['VideoVesaBlueline']) # Disable polarizer switching (VESA port output) synchronized by blue lines (cached)
    pixx.setVesaFreeRun(cfg['VesaFreeRun']) # Disable polarizer switching (VESA port output) in free run mode (non-sync; cached)
    # Apply cached changes
    pixx.updateRegisterCache() # Update the new modes to the device (apply cached changes)
    # pixx.setCustomStartupConfig() # The projector will remember this configuration
    

def set_polarizer_mode(win, pixx, mode):
    '''
    Config the StereoWindow and DepthQ polarizer to realize specific stereo mode.

    Pros and cons of different stereo modes
    ---------------------------------------
    | Mode          | Binocular <br>frame rate | Support <br>color image | Robust to <br>frame drops |
    | ------------- | ------------------------ | ----------------------- | ------------------------- |
    | blueline      | 60 Hz                    | Yes                     | No                        |
    | RB3D          | 120 Hz                   | No                      | Yes                       |
    | double-height | 60 Hz                    | Yes                     | Yes                       |

    Parameters
    ----------
    win : psykit.stereomode.StereoWindow
        An initialized StereoWindow object.
    pixx : pypixxlib.propixx.PROPixx
        An initialized PROPixx object, e.g., ``pixx = pypixxlib.propixx.PROPixx()``.
    mode : str
        Stereo mode for using ProPixx with the DepthQ polarizer.
        - 'none': no stereo.
        - 'blueline': temporally interleaved stereo mode, synchronized by an 
            automatically drawn blue line at the bottom of the image. This mode
            is susceptible to frame drops and thus is **not recommended**. 
        - 'freerun': not really useable. Listed here only for completeness.
        - 'RB3D': display the image in 'red/blue' mode at 120 Hz, and ProPixx
            will decompose each frame and display the red channel image and the 
            blue channel image sequentially.
            This mode is **recommended** for achromatic (grayscale) stimuli.
        - 'double-height': display the image in 1920x2160 resolution at 60 Hz, 
            and ProPixx will decompose each frame and display the top image and 
            bottom image sequentially.
            This mode is **recommended** for chromatic (color) stimuli.
            To use this mode, follow the procedure below:
            1. Open VPutil and select the ProPixx controller
                ``devsel ppc``
            2. Adjust EDID to double-height mode [1920x2160 @ 60 Hz] 
                ``edid > 18 > 18 > n``
            3. Restart the ProPixx controller (switch the blue box off and on).
            After the experiment, remember to restore the EDID to default mode,
            so the next user will not get confused: 
                ``edid > 0 > n > restart controller``
        - Other valid stereo mode for StereoWindow, without using any special 3D 
            functionalities from ProPixx. E.g., 'left/right', 'red/blue', etc.
    '''
    if mode == 'none':
        win.stereoMode = 'none'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
    elif mode == 'blueline':
        # https://docs.vpixx.com/python/a-simple-hello-world-in-stereo
        # Pros
        # - Support color stimuli
        # Cons
        # - This mode is susceptible to frame drops
        # - Only support binocuar 60 Hz frame rate
        win.stereoMode = 'sequential'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(True)
        pixx.setVesaFreeRun(False) # This will auto set VidVesaWaveform=PPX_DEPTHQ and VidVesaPhase=0
        pixx.updateRegisterCache()
    elif mode == 'freerun':
        # This is not really useable. Listed here only for completeness.
        # The image in the two eyes will randomly swap from time to time due to 
        # slow drift or frame drops.
        win.stereoMode = 'sequential'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(True)
        pixx.updateRegisterCache()
    elif mode == 'RB3D':
        # Pros
        # - Robust to frame drops
        # - Allow binocuar 120 Hz frame rate
        # Cons
        # - Can only display achromatic stimuli (do not support color stimuli)
        win.stereoMode = 'red/blue-anticross'
        pixx.setDlpSequencerProgram('RB3D')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
    elif mode == 'double-height':
        # This is the recommended mode for most purposes.
        # Use VPutil to adjust EDID to double-height mode [1920x2160 @ 60 Hz]
        # and hardware restart the ProPixx controller (switch off then on again).
        # You may need to adjust your screen resolution (dobule-height) if the 
        # OS doesn't do that automatically to use this mode.
        # Pros
        # - Robust to frame drops
        # - Support color stimuli
        # Cons
        # - Only support binocuar 60 Hz frame rate
        # - Need to adjust EDID and restart ProPixx controller.
        if not win.size[1] > win.size[0]:
            raise ValueError(f"The ProPixx controller is not set to double-height mode [1920x2160 @ 60 Hz]. Please adjust EDID using VPutil and restart ProPixx controller.")
        win.stereoMode = 'top/bottom-anticross'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
    else: # Must be valid stereomode for StereoWindow, e.g., 'left/right', 'red/blue', etc.
        win.stereoMode = mode
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()

