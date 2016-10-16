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
        double GetExposureTime()
        unsigned short *GetImagePointer()


cdef extern from '../src/sbigudrv.h':
    ctypedef enum PAR_ERROR:
        CE_NO_ERROR
    ctypedef enum SBIG_DEVICE_TYPE:
        DEV_USB1
    ctypedef unsigned short MY_LOGICAL
    ctypedef struct QUERY_USB_INFO:
        MY_LOGICAL cameraFound
        unsigned short cameraType
        char name[64]
        char serialNumber[10]
    ctypedef struct OpenDeviceParams:
        unsigned short deviceType
    ctypedef struct QueryUSBResults:
        unsigned short camerasFound
        QUERY_USB_INFO usbInfo[4]
    ctypedef struct GetCCDInfoParams:
        unsigned short request
    ctypedef struct READOUT_INFO:
        unsigned short mode
        unsigned short width
        unsigned short height
        unsigned short gain
        unsigned long pixelWidth
        unsigned long pixelHeight
    ctypedef struct GetCCDInfoResults0:
        unsigned short firmwareVersion
        unsigned short cameraType
        char name[64]
        unsigned short readoutModes
        READOUT_INFO readoutInfo[20]
    ctypedef enum PAR_COMMAND:
        CC_QUERY_USB
        CC_GET_CCD_INFO
    extern short SBIGUnivDrvCommand(short command, void *Params, void *Results)


cdef extern from '../src/csbigcam.h':
    ctypedef enum SBIG_DARK_FRAME:
        SBDF_LIGHT_ONLY
    cdef cppclass CSBIGCam:
        CSBIGCam() except +
        CSBIGCam(SBIG_DEVICE_TYPE dev) except +
        PAR_ERROR OpenDriver()
        PAR_ERROR OpenDevice(OpenDeviceParams odp)
        PAR_ERROR EstablishLink()
        void SetExposureTime(double exp)
        double GetExposureTime()
        string GetCameraTypeString()
        PAR_ERROR GrabImage(CSBIGImg *pImg, SBIG_DARK_FRAME dark)
        PAR_ERROR CloseDevice();
        PAR_ERROR CloseDriver();


cdef class SBIGImg:

    cdef CSBIGImg* thisptr

    def __cinit__(self):
        self.thisptr = new CSBIGImg()

    def __dealloc__(self):
        del self.thisptr

    def getWidth(self):
        return self.thisptr.GetWidth()

    def getHeight(self):
        return self.thisptr.GetHeight()

    def getExposureTime(self):
        return self.thisptr.GetExposureTime()

    def getNumpyArray(self):

        cdef np.npy_intp shape[1]

        cdef int height = self.getHeight()
        cdef int width = self.getWidth()
        shape[0] = <np.npy_intp> (height * width)

        ndarray = np.PyArray_SimpleNewFromData(1, shape, np.NPY_USHORT,
                                               self.thisptr.GetImagePointer())
        rect_ndarray = ndarray.reshape((height, width))

        return rect_ndarray


class SBIGHandlerError(Exception):
    pass


cdef class SBIGCam:

    cdef CSBIGCam* thisptr
    cdef bool is_linked

    def __cinit__(self):

        self.thisptr = new CSBIGCam()
        self.is_linked = False

    def __dealloc__(self):

        self.thisptr.CloseDevice()
        self.thisptr.CloseDriver()
        del self.thisptr

    def openDriver(self):

        error = self.thisptr.OpenDriver()

        if error == CE_NO_ERROR:
            return True
        else:
            raise SBIGHandlerError('cannot connect to camera. '
                                   'OpenDriver failed with error: {0}'.format(error))


    def linkDevice(self):

        if self.is_linked:
            return True

        cdef OpenDeviceParams odp
        odp.deviceType = DEV_USB1

        error = self.thisptr.OpenDevice(odp)
        if error != CE_NO_ERROR:
            raise SBIGHandlerError('cannot connect to camera. '
                                   'OpenDevice failed with error: {0}'.format(error))

        error = self.thisptr.EstablishLink()
        if error != CE_NO_ERROR:
            raise SBIGHandlerError('cannot connect to camera. '
                                   'EstablishLink failed with error: {0}'.format(error))

        self.is_linked = True

        return True

    def grabImage(self, expTime=0.01):

        pImg = SBIGImg()
        pImg_ptr = pImg.thisptr

        self.thisptr.SetExposureTime(expTime)

        error = self.thisptr.GrabImage(pImg_ptr, SBDF_LIGHT_ONLY)

        if error != CE_NO_ERROR:
            raise SBIGHandlerError('GrabImage failed with error {0}'.format(error))

        return pImg

    def getCameraTypeString(self):
        return self.thisptr.GetCameraTypeString()

    cdef _runDrvCommand(self, short command, void *Params, void *Results, command_name=''):

        error = SBIGUnivDrvCommand(command, Params, Results)

        if error != CE_NO_ERROR:
            raise SBIGHandlerError('cannot execute command {0} ({1}). '
                                   'Failed with error {2}.'.format(command, command_name, error))

        return error

    def queryUSB(self):

        cdef QueryUSBResults info

        self._runDrvCommand(CC_QUERY_USB, NULL, &info, command_name='CC_QUERY_USB')

        return info.usbInfo[0]

    def getCCDInfoParams(self):

        cdef GetCCDInfoParams params
        params.request = 0

        cdef GetCCDInfoResults0 info

        self._runDrvCommand(CC_GET_CCD_INFO, &params, &info, command_name='CC_GET_CCD_INFO')

        return info
