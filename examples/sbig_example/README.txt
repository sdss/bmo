CCDOpsLite for Linux Readme
===========================

CCDOpsLite for Linux is a sample Qt project that allows
taking and saving images with SBIG Cameras under Linux.
It is provided as an example of what can be done with
Qt, the SBIG Drivers and the SBIG Class Libraries.
This software is provided AS-IS. SBIG makes no claims
as to the suitability of this software or as the
state of bugs.

Features
========
* Works with SBIG Parallel and USB Cameras
* Works with Cameras serverd by EthSrvWin
* Reads and writes SBIG Type 3 images
* Write FITS format images
* Supports Imaging and Tracking CCDs
* Supports Cooling
* Supports High, Medium and Low readout modes

Requirements
============
Qt Version 3.3 or later
SBIG Linux Drivers Version 4.37 or Later
SBIG USB or Parallel Port camera
gcc
CFitsIO Library available from NASA:
 <http://heasarc.gsfc.nasa.gov/docs/software/fit>

To Build
========
qmake -o MakeFile ccdOpsLite.pro
make

Special Thanks
==============
Special thanks to Chris Curran for his many efforts.  Without
him this software would not exist.  Linux users owe him a
debt of gratitude.

Send any comments to
<matto@sbig.com>

