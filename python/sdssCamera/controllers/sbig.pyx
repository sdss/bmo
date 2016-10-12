#distutils: language = c++

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool
import numpy as np
cimport numpy as np

np.import_array()


cdef extern from '../src/csbigimg.h':
    cdef cppclass CSBIGImg:
        CSBIGImg()
        int GetHeight()
        int GetWidth()
        unsigned short *GetImagePointer()


cdef extern from '../src/sbigudrv.h':
    ctypedef enum PAR_ERROR:
        pass
    ctypedef enum SBIG_DEVICE_TYPE:
        DEV_USB1
    ctypedef unsigned short MY_LOGICAL
    ctypedef struct QUERY_USB_INFO:
        MY_LOGICAL cameraFound
        unsigned short cameraType
        char name[64]
        char serialNumber[10]
    ctypedef struct QueryUSBResults:
        unsigned short camerasFound
        QUERY_USB_INFO usbInfo[4]
    ctypedef enum PAR_COMMAND:
        CC_QUERY_USB
    extern short SBIGUnivDrvCommand(short command, void *Params, void *Results)

cdef extern from '../src/csbigcam.h':
    ctypedef enum SBIG_DARK_FRAME:
        SBDF_LIGHT_ONLY
    cdef cppclass CSBIGCam:
        CSBIGCam() except +
        CSBIGCam(SBIG_DEVICE_TYPE dev) except +
        PAR_ERROR OpenDriver()
        PAR_ERROR EstablishLink()
        void SetExposureTime(double exp)
        double GetExposureTime()
        string GetCameraTypeString()
        PAR_ERROR GrabImage(CSBIGImg *pImg, SBIG_DARK_FRAME dark)
        PAR_ERROR CloseDevice();
        PAR_ERROR CloseDriver();


cdef class SBIG:

    cdef CSBIGCam* thisptr
    # cdef bool _driver_is_open

    def __cinit__(self):
        # self._driver_is_open = False
        cdef SBIG_DEVICE_TYPE dev = DEV_USB1
        self.thisptr = new CSBIGCam(dev)

    def __dealloc__(self):
        self.thisptr.CloseDevice()
        self.thisptr.CloseDriver()
        del self.thisptr

    def establishLink(self):
        return self.thisptr.EstablishLink()

    def grabImage(self):
        cdef CSBIGImg pImg;

        self.thisptr.SetExposureTime(5.)

        self.thisptr.GrabImage(&pImg, SBDF_LIGHT_ONLY)

        cdef np.npy_intp shape[1]
        shape[0] = <np.npy_intp> (pImg.GetHeight() * pImg.GetWidth())
        ndarray = np.PyArray_SimpleNewFromData(1, shape,
                                               np.NPY_USHORT, pImg.GetImagePointer())

        return ndarray, pImg.GetHeight(), pImg.GetWidth()

    def getCameraTypeString(self):
        return self.thisptr.GetCameraTypeString()

    def queryUSB(self):
        cdef QueryUSBResults info
        SBIGUnivDrvCommand(CC_QUERY_USB, NULL, &info)
        return info.usbInfo[0]
