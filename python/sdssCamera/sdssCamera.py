from __future__ import absolute_import, division, print_function

import xml.etree.ElementTree as ET
import re
import time
import os

import numpy
from astropy.io import fits

import cv2

import pymba

class VimbaConfig(object):
    RW = "R/W"
    Integer = "Integer"
    Boolean = "Boolean"
    Float = "Float"
    Enumeration = "Enumeration"
    def __init__(self, xmlFile):
        """An object representing a configuration state of an AlliedVision GigE camera

        @param[in] xmlFile: configuation file to be loaded (the output of VimbaViewer configuation save)
        """
        self.integerSettings = {}
        self.booleanSettings = {}
        self.enumSettings = {}
        self.floatSettings = {}
        self.fromXML(xmlFile)

    @property
    def allSettings(self):
        return dict(self.integerSettings.items() + self.booleanSettings.items() + self.enumSettings.items() + self.floatSettings.items())

    def fromXML(self, xmlFile):
        """populate settings dicts from xmlFile

        @param[in] xmlFile: configuation file to be loaded (the output of VimbaViewer configuation save)
        """
        # Vimba-written xml files are not parseable without this hack:
        # http://stackoverflow.com/questions/38853644/python-xml-parseerror-junk-after-document-element
        with open(xmlFile) as f:
            xml = f.read()
        tree = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")
        cameraSettings = tree.find("CameraSettings")
        # save this camera ID
        self.cameraID = cameraSettings.attrib["CameraID"]
        # iterate over all (relevant features in xml file)
        for feature in cameraSettings.find("FeatureGroup").getchildren():
            # only keep read/write values
            if feature.attrib["Access"] != self.RW:
                continue
            value = feature.text
            name = feature.attrib["Name"]
            featureType = feature.attrib["Type"]
            # cast value into expected type
            if featureType == self.Enumeration:
                # leave as a string
                self.enumSettings[name] = str(value)
            elif featureType == self.Integer:
                self.integerSettings[name] = int(value)
            elif featureType == self.Boolean:
                self.booleanSettings[name] = value == "True"
            elif featureType == self.Float:
                self.floatSettings[name] = float(value)
            else:
                print("unknown feature type: %s: %s"%(name, featureType))
                continue

class VimbaCamera(object):
    def __init__(self, xmlFile=None, imgSaveDir=None):
        """An object representing a Vimba controlled camera

        @param[in] xmlFile: configuation file to be loaded (the output of VimbaViewer configuation save)
        @param[in] imgSaveDir: directory where saved images will be put
        """
	if xmlFile is None:
            xmlFile = os.path.join(os.getenv("SDSSCAMERA_DIR"), "etc", "baseMantaConfig.xml")
        if not os.path.exists(xmlFile):
            raise RuntimeError("could not locate xml config file: %s"%xmlFile)
        self.config = VimbaConfig(xmlFile)
        if imgSaveDir is None:
            # use a default location
            imgSaveDir = os.path.join(os.path.expanduser("~"), self.config.cameraID)
        if not os.path.exists(imgSaveDir):
            os.makedirs(imgSaveDir)
        self.imgSaveDir = imgSaveDir
        self.vimba = pymba.Vimba()
        self.vimba.startup()
        self.system = self.vimba.getSystem()
        self.system.runFeatureCommand("GeVDiscoveryAllOnce")
        self.camera = self.vimba.getCamera(self.config.cameraID)
        self.camera.openCamera()
        self.loadConfig()
        self.nImg = 0
        self.tstart = numpy.nan
        self.showImg = False
        self.saveImg = False
        self.overwrite = True
        # use 3 frames in queue for async acquision
        frames = [
            self.camera.getFrame(),
            self.camera.getFrame(),
            self.camera.getFrame()
            ]

        # define the callback, called each time a frame is ready
        def frameCB(frame):
            imgData = numpy.ndarray(buffer = frame.getBufferByteData(),
                                   dtype = numpy.uint8,
                                   shape = (frame.height,
                                            frame.width)
                                    )
            self.nImg += 1
            print("fps: %.4f, nimg: %i, medianVal: %.2f"%(self.nImg/float(time.time()-self.tstart), self.nImg, numpy.median(imgData)))
            if self.showImg:
                cv2.imshow("frame", imgData)
                cv2.waitKey(1)
            if self.saveImg:
                strNum = ("%i"%self.nImg).zfill(10)
                self.writeFits(imgData, os.path.join(self.imgSaveDir, "img%s.fits"%strNum))
            frame.queueFrameCapture(frameCB)

        # announce the frames, and specify the callback
        for frame in frames:
            frame.announceFrame()
            frame.queueFrameCapture(frameCB)

        self.camera.startCapture()

    def loadConfig(self):
        """Explicitly set all configuation specified in the config obj
        """
        for key, val in self.config.allSettings.iteritems():
            setattr(self.camera, key, val)

    def beginContinuousCapture(self):
        self.camera.AcquisionMode = "Continuous"
        self.tstart = time.time()
        self.camera.runFeatureCommand("AcquisitionStart")

    def writeFits(self, imgData, filename):
        if os.path.exists(filename):
            if not self.overwrite:
                print("Image %s exists already, not writing, overwrite flag NOT set.")
                return
            else:
                print("WARNING OVERWRITING PREVIOUS IMAGE! %s"%filename)
                os.path.remove(filename)
        hdu = fits.PrimaryHDU(imgData)
        hdulist = fits.HDUList([hdu])
        prihdr = hdulist[0].header
        prihdr["tstamp"] = time.time(), "UNIX time of exposure"
        prihdr["exptime"] = self.camera.ExposureTimeAbs / 1e6, "Exposure time in seconds"
        hdulist.writeto(filename)


    def stopCapture(self):
        self.tstart = numpy.nan
        self.camera.runFeatureCommand("AcquisitionStop")

    def captureOneImage(self):
        self.camera.AcquisionMode = "SingleFrame"
        self.camera.runFeatureCommand("AcquisitionStart")
        self.camera.runFeatureCommand("AcquisitionStop")

    def setExpTime(self, expTime):
        """Set the exposure time of the camera

        @param[in] expTime: float value in seconds
        """
        # camera attribute expects microsecond values
        self.camera.ExposureTimeAbs = expTime * 1e6


    def __del__(self):
        self.camera.endCapture()
        self.camera.revokeAllFrames()
        cv2.destroyAllWindows()
        self.vimba.shutdown()


