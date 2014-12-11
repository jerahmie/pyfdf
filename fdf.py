"""Fdf module for python"""
from __future__ import print_function
import struct
import numpy


FDF_ITEMNAME_LENGTH = 64
FDF_MAXDIMS = 32
C_INT = 4
C_LONG = 8

FDF_TYPE_LIST = ['fdf_char', 'fdf_i8', 'fdf_u8', 'fdf_i16',
                 'fdf_u16', 'fdf_i32', 'fdf_u32', 'fdf_float',
                 'fdf_double', 'fdf_complex', 'fdf_dcomplex']

FDF_TYPE_SIZE = {'fdf_char':1, 'fdf_i8':1, 'fdf_u8':1, 'fdf_i16':2,
                 'fdf_u16':2, 'fdf_i32':4, 'fdf_u32':4, 'fdf_float':2,
                 'fdf_double':8, 'fdf_complex':8, 'fdf_dcomplex':16}

FDF_NUMPY_TYPE = {'fdf_char':numpy.char, 'fdf_i8':numpy.int0,
                  'fdf_u8':numpy.uint0, 'fdf_i16':numpy.int16,
                  'fdf_u16':numpy.uint16, 'fdf_i32':numpy.int32,
                  'fdf_u32':numpy.uint32, 'fdf_float':numpy.float32,
                  'fdf_double':numpy.float64,
                  'fdf_complex':numpy.complex64,
                  'fdf_dcomplex':numpy.complex128}

FDF_UNPACK_TYPE = {'fdf_char':'c', 'fdf_i8':'c', 'fdf_u8':'c', \
                   'fdf_i16':'h', 'fdf_u16':'H', \
                   'fdf_i32':'i', 'fdf_u32':'I', \
                   'fdf_float':'f', 'fdf_double':'d', \
                   'fdf_complex':'f', 'fdf_dcomplex':'d'}

class Fdf:
    """A Python fdf interface."""
    fdf_file = None
    fdf_file_type = None
    header = None
    zcv = None
    vpc = None
    t0 = None
    dt = None
    nbits = None
    data = None
    units = None

    def __init__(self):
        print("Constructor!")

    def open_fdf(self, file_name):
        """Open the fdf file. """
        print(file_name)
        try:
            self.fdf_file = open(file_name, "rb")
        except IOError as err:
            print("I/O error({0}): {1}".format(err.errno, err.strerror))
        except:
            print("Unexpected error:")
            raise

    def read_preamble(self):
        """Read next fdf file header variable."""
        dims = []
        try:
            name = self.fdf_file.read(FDF_ITEMNAME_LENGTH)
            ndims = struct.unpack('i', self.fdf_file.read(C_INT))[0]
            for i in range(0, ndims):
                dims.append(struct.unpack('i',  \
                        self.fdf_file.read(C_INT))[0])
            fdf_type_index = struct.unpack('i',\
                        self.fdf_file.read(C_INT))[0]
            fdf_type = FDF_TYPE_LIST[fdf_type_index]
            if fdf_type_index == 0:
                return self.fdf_file.read(dims[0] * FDF_TYPE_SIZE[fdf_type])
            else:
                return struct.unpack(FDF_UNPACK_TYPE[fdf_type], \
                                    self.fdf_file.read(dims[0] * \
                                    FDF_TYPE_SIZE[fdf_type]))[0]
        except:
            print("something went wrong.")
            raise

    def read_header(self):
        """Read header of valid fdf file."""
        try:
            temp_name = self.fdf_file.read(4)
            if temp_name != "fdf\0":
                print("FDF file has invalid header")
            self.fdf_file_type = self.read_preamble()
            self.header = self.read_preamble()
            self.zcv = self.read_preamble()
            self.vpc = self.read_preamble()
            self.t0 = self.read_preamble()
            self.dt = self.read_preamble()
            self.nbits = self.read_preamble()
            self.units = self.read_preamble()
        except:
            print("something went wrong.")
            raise

    def read_data(self):
        """Read the data portion of the fdf_file. """
        fdf_data_name = self.fdf_file.read(FDF_ITEMNAME_LENGTH)
        fdf_data_ndims = struct.unpack('i', self.fdf_file.read(C_INT))[0]
        fdf_data_dims = []
        for i in range(0, fdf_data_ndims):
            fdf_data_dims.append(struct.unpack('i', \
                    self.fdf_file.read(C_INT))[0])
        fdf_data_type_index = struct.unpack('i', \
                    self.fdf_file.read(C_INT))[0]
        fdf_data_type = FDF_TYPE_LIST[fdf_data_type_index]
        self.data = numpy.zeros(fdf_data_dims, \
                    dtype=FDF_NUMPY_TYPE['fdf_float'])
        for i in range(0, fdf_data_dims[0]):
            self.data[i] = struct.unpack(FDF_UNPACK_TYPE[fdf_data_type], \
                        self.fdf_file.read(FDF_TYPE_SIZE[fdf_data_type]))[0] *\
                        self.vpc

    def load_fdf(self):
        """Load data from fdf file."""
        self.read_header()
        print("fdf file type: ", self.fdf_file_type)
        print("fdf header: ", self.header)
        print("fdf zero crossing voltage: ", self.zcv)
        print("fdf volts per channel(?): ", self.vpc)
        print("fdf t0: ", self.t0)
        print("fdf dt: ", self.dt)
        print("fdf nbits: ", self.nbits)
        print("fdf units: ", self.units)
        self.read_data()
        print("data size: ", self.data.size)

    def __del__(self):
        print("Destructor!")
        self.fdf_file.close()
