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

import matplotlib.pyplot as plt


ss = sbig.SBIG()
ss.establishLink()
data, height, width = ss.grabImage()

data = data.reshape((height, width))

fig, ax = plt.subplots()
ax.imshow(data, origin='lower')
plt.show()
del ss
