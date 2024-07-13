#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024-07-13: created by qcc
import numpy as np
import matplotlib.pyplot as plt
from .data import data_path


def load_tags():
    '''
    Load QR code tags to be used with the pupil-labs cloud marker mapper.

    The function will return 48 tags; each is a 383*383 uint8 grayscale image.
    Put four different tags on each corner of your stimulus surface, and the 
    marker mapper of the pupil cloud will be able to extract the coordinates of
    gaze within the stimulus surface, e.g., a computer screen or a poster.

    Returns
    -------
    tags : array, 48*383*383, uint8

    References
    ----------
    https://docs.pupil-labs.com/neon/pupil-cloud/enrichments/marker-mapper/
    '''
    tags = []
    for fname in ['apriltags_tag36h11_0-23.jpg', 'apriltags_tag36h11_24-47.jpg']:
        im = plt.imread(f"{data_path}/{fname}")
        for m in range(6):
            for n in range(4):
                tags.append(im[65+m*384:448+m*384,65+n*384:448+n*384])
    tags = np.array(tags) # 48*383*383, uint8
    return tags
