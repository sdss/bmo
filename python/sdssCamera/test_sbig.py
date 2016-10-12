#!/usr/bin/env python3
# encoding: utf-8
#
# test_sbig.py
#
# Created by José Sánchez-Gallego on 12 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from controllers import sbig

import cv2


ss = sbig.SBIG()
ss.establishLink()
expTime = 0.1

kk = 0
while kk != 13:
    data = ss.grabImage(expTime)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', data)
    kk = cv2.waitKey(500)

# cv2.destroyAllWindows()
# cv2.destroyAllWindows()
