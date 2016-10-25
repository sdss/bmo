#distutils: language = c++

from libcpp.string cimport string
from libc.stdlib cimport malloc, realloc
from libc.stdint cimport uint8_t
from libcpp cimport bool

from bmo.controllers.exceptions import SXError, SXHandlerError

import time

import numpy as np
cimport numpy as np

np.import_array()


cdef extern from '<libusb-1.0/libusb.h>':
    ctypedef struct libusb_device
    ctypedef struct libusb_device_handle


cdef extern from './sxccdusb.h':

    ctypedef libusb_device * DEVICE
    ctypedef libusb_device_handle * HANDLE

    ctypedef struct t_sxccd_params:
        unsigned short hfront_porch
        unsigned short hback_porch
        unsigned short width
        unsigned short vfront_porch
        unsigned short vback_porch
        unsigned short height
        float pix_width
        float pix_height
        unsigned short color_matrix
        char bits_per_pixel
        char num_serial_ports
        char extra_caps
        char vclk_delay

    int sxList(DEVICE * sxDevices, const char **names, int maxCount)
    int sxOpen(DEVICE sxDevice, HANDLE *sxHandle);
    int sxGetCameraParams(HANDLE sxHandle, unsigned short camIndex, t_sxccd_params *params)
    unsigned short sxGetCameraModel(HANDLE sxHandle)
    bool sxIsInterlaced(short model)
    int sxClearPixels(HANDLE sxHandle, unsigned short flags, unsigned short camIndex)
    int sxLatchPixels(HANDLE sxHandle, unsigned short flags, unsigned short camIndex,
                      unsigned short xoffset, unsigned short yoffset, unsigned short width,
                      unsigned short height, unsigned short xbin, unsigned short ybin)
    int sxReadPixels(HANDLE sxHandle, void *pixels, unsigned long count)

def sx_info():

    cdef DEVICE devices[20]
    cdef const char* names[20]

    n_devices = sxList(devices, names, 20)

    return n_devices, [str(names[ii]) for ii in range(n_devices)]


CCD_EXP_FLAGS_FIELD_ODD = 0x01
CCD_EXP_FLAGS_FIELD_EVEN = 0x02
CCD_EXP_FLAGS_FIELD_BOTH = (CCD_EXP_FLAGS_FIELD_EVEN | CCD_EXP_FLAGS_FIELD_ODD)


cdef class SXCamera:

    cdef DEVICE dev
    cdef string name_bytes
    cdef HANDLE handle
    cdef uint8_t *RawFrame

    def __cinit__(self, ii=0):

        self.RawFrame = <uint8_t *>malloc(sizeof(uint8_t))

        cdef DEVICE devices[20]
        cdef const char* names[20]

        n_devices = sxList(devices, names, 20)

        if n_devices == 0:
            raise SXError('no camera connected.')

        self.dev = devices[ii]
        self.name_bytes = (string)(names[ii])

        result = sxOpen(self.dev, &self.handle)
        if result < 0:
            raise SXHandlerError('failed to get camera handle. Error code {0}.'.format(result))

    @property
    def name(self):
        return self.name_bytes.decode('utf-8')

    @property
    def model(self):
        return sxGetCameraModel(self.handle)

    @property
    def is_interlaced(self):
        return sxIsInterlaced(self.model)

    def get_params(self, do_print=False):
        """Returns a dictionary of camera parameters."""

        cdef t_sxccd_params params

        sxGetCameraParams(self.handle, 0, &params)

        if do_print:
            print('camera_name       =  {0}'.format(self.name))
            print('height            =  {0}'.format(params.height))
            print('width             =  {0}'.format(params.width))
            print('pix_height        =  {0}'.format(params.pix_height))
            print('pix_width         =  {0}'.format(params.pix_width))
            print('bits_per_pixel    =  {0}'.format(params.bits_per_pixel))
            print('hback_porch       =  {0}'.format(params.hback_porch))
            print('hfront_porch      =  {0}'.format(params.hfront_porch))
            print('vback_porch       =  {0}'.format(params.vback_porch))
            print('vfront_porch      =  {0}'.format(params.vfront_porch))
            print('extra_caps        =  {0}'.format(params.extra_caps))
            print('color_matrix      =  {0}'.format(params.color_matrix))
            print('num_serial_ports  =  {0}'.format(params.num_serial_ports))
            print('vclk_delay        =  {0}'.format(params.vclk_delay))
            print('is_interlaced     =  {0}'.format(self.is_interlaced))

        params_dict = dict(params)
        params_dict.update({'camera_name': self.name, 'is_interlaced': self.is_interlaced})

        return params_dict

    def expose(self, exp_time=1.):

        print('Starting exposure ... ')
        sxClearPixels(self.handle, CCD_EXP_FLAGS_FIELD_BOTH, 0)

        time.sleep(exp_time)

        params = self.get_params()

        cdef int subX = 0
        cdef int subY = 0
        cdef int subW = <int>params['width']
        cdef int subH = <int>params['height']
        cdef int binX = 1
        cdef int binY = 1

        cdef int size
        size = subW * subH / binX / binY

        cdef int nbuf = subW * subH * 2
        self.RawFrame = <uint8_t *>realloc(self.RawFrame, nbuf * sizeof(uint8_t))

        rc = sxLatchPixels(self.handle, CCD_EXP_FLAGS_FIELD_BOTH, 0,
                           subX, subY, subW, subH, binX, binY)

        if rc < 0:
            raise SXHandlerError('failed to latch pixels. Error code {0}.'.format(rc))

        cdef uint8_t *buf = self.RawFrame
        rc = sxReadPixels(self.handle, buf, size * 2)

        if rc < 0:
            raise SXHandlerError('failed to read pixels. Error code {0}.'.format(rc))

        cdef np.npy_intp shape[1]

        shape[0] = <np.npy_intp> (subH * subW)

        ndarray = np.PyArray_SimpleNewFromData(1, shape, np.NPY_USHORT, buf)
        rect_ndarray = ndarray.reshape((subH, subW))

        return rect_ndarray
