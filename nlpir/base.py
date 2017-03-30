# coding=utf-8

from __future__ import unicode_literals
from ctypes import (c_bool, c_char, c_char_p, c_double, c_int, c_uint,
                    c_ulong, c_void_p, cdll, POINTER, Structure)
import logging
import os
import sys

logger = logging.getLogger('nlpir.base')


#: NLPIR's GBK encoding constant.
GBK_CODE = 0
#: NLPIR's UTF-8 encoding constant.
UTF8_CODE = 1
#: NLPIR's BIG5 encoding constant.
BIG5_CODE = 2
#: NLPIR's GBK (Traditional Chinese) encoding constant.
GBK_FANTI_CODE = 3

#: The encoding configured by :func:`open`.
ENCODING = 'utf_8'

#: The encoding error handling scheme configured by :func:`open`.
ENCODING_ERRORS = 'strict'

#: The absolute path to this package (used by NLPIR to find its ``Data``
#: directory). This is a string in Python 2 and a bytes object in Python 3
#: (so it can be used with the :func:`Init` function below).
PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))

#: The absolute path to this path's lib directory.
LIB_DIR = os.path.join(PACKAGE_DIR, 'lib')

is_python3 = sys.version_info[0] > 2
if is_python3:
    # Python 3 expects bytes for data type ctypes.c_char_p.
    PACKAGE_DIR = PACKAGE_DIR.encode('utf_8')

IS_64BIT = sys.maxsize > 2**32

class BaseNlpirSDK(object):

    def __init__(self, lib_name, short_name):
        #: A :class:`ctypes.CDLL` instance for the NLPIR API library.
        self.lib_name = lib_name
        self.lib_nlpir = self.load_library(sys.platform, IS_64BIT, lib_name)

        # C函数定义
        # Get the exported NLPIR API functions.
        try:
            self.Init = self.get_func('%s_Init' % short_name, [c_char_p, c_int, c_char_p])  # must be defined
            self.Exit = self.get_func('%s_Exit' % short_name, restype=c_bool)               # must be defined
        except AttributeError, e:
            self.Init = self.get_func('%s_Inits' % short_name, [c_char_p, c_int, c_char_p])  # must be defined
            self.Exit = self.get_func('%s_Exits' % short_name, restype=c_bool)               # must be defined


    def _decode(self, s, encoding=None, errors=None):
        """Decodes *s*."""
        if encoding is None:
            encoding = ENCODING
        if errors is None:
            errors = ENCODING_ERRORS
        return s if isinstance(s, unicode) else s.decode(encoding, errors)


    def _encode(self, s, encoding=None, errors=None):
        """Encodes *s*."""
        if encoding is None:
            encoding = ENCODING
        if errors is None:
            errors = ENCODING_ERRORS
        return s.encode(encoding, errors) if isinstance(s, unicode) else s


    def open(self, data_dir=PACKAGE_DIR, encoding=ENCODING,
             encoding_errors=ENCODING_ERRORS, license_code=None):
        """Initializes the NLPIR API.

        This calls the function :func:`~pynlpir.nlpir.Init`.

        :param str data_dir: The absolute path to the directory that has NLPIR's
            `Data` directory (defaults to :data:`pynlpir.nlpir.PACKAGE_DIR`).
        :param str encoding: The encoding that the Chinese source text will be in
            (defaults to ``'utf_8'``). Possible values include ``'gbk'``,
            ``'utf_8'``, or ``'big5'``.
        :param str encoding_errors: The desired encoding error handling scheme.
            Possible values include ``'strict'``, ``'ignore'``, and ``'replace'``.
            The default error handler is 'strict' meaning that encoding errors
            raise :class:`ValueError` (or a more codec specific subclass, such
            as :class:`UnicodeEncodeError`).
        :param str license_code: The license code that should be used when
            initializing NLPIR. This is generally only used by commercial users.
        :raises RuntimeError: The NLPIR API failed to initialize. Sometimes, NLPIR
            leaves an error log in the current working directory or NLPIR's
            ``Data`` directory that provides more detailed messages (but this isn't
            always the case).

        """
        if license_code is None:
            license_code = ''
        global ENCODING
        if encoding.lower() in ('utf_8', 'utf-8', 'u8', 'utf', 'utf8'):
            ENCODING = 'utf_8'
            encoding_constant = UTF8_CODE
        elif encoding.lower() in ('gbk', '936', 'cp936', 'ms936'):
            ENCODING = 'gbk'
            encoding_constant = GBK_CODE
        elif encoding.lower() in ('big5', 'big5-tw', 'csbig5'):
            ENCODING = 'big5'
            encoding_constant = BIG5_CODE
        else:
            raise ValueError("encoding must be one of 'utf_8', 'big5', or 'gbk'.")
        logger.debug("Initializing the NLPIR API: {'data_dir': '%s', 'encoding': "
                     "'%s', 'license_code': '%s'}"
                     % (data_dir, encoding, license_code))

        global ENCODING_ERRORS
        if encoding_errors not in ('strict', 'ignore', 'replace'):
            raise ValueError("encoding_errors must be one of 'strict', 'ignore', "
                             "or 'replace'.")
        else:
            ENCODING_ERRORS = encoding_errors

        # Init in Python 3 expects bytes, not strings.
        if is_python3 and isinstance(data_dir, str):
            data_dir = self._encode(data_dir)
        if is_python3 and isinstance(license_code, str):
            license_code = self._encode(license_code)

        # TODO: 如何判断证书是否已经过期，并且设计出一种自动从github拉取最新证书的功能
        if not self.Init(data_dir, encoding_constant, license_code):
            raise RuntimeError("%s function '%s_Init' failed." % (self.lib_name, self.lib_name))
        else:
            logger.debug("%s API initialized." % self.lib_name)

    def close(self):
        """Exits the NLPIR API and frees allocated memory.

        This calls the function :func:`~pynlpir.nlpir.Exit`.

        """
        logger.debug("Exiting the %s API." % self.lib_name)
        if not self.Exit():
            logger.warning("%s function '%s_Exit' failed." % (self.lib_name, self.lib_name))
        else:
            logger.debug("%s API exited." % self.lib_name)

    def get_func(self, name, argtypes=None, restype=c_int):
        """Retrieves the corresponding NLPIR function.

        :param str name: The name of the NLPIR function to get.
        :param list argtypes: A list of :mod:`ctypes` data types that correspond
            to the function's argument types.
        :param restype: A :mod:`ctypes` data type that corresponds to the
            function's return type (only needed if the return type isn't
            :class:`ctypes.c_int`).
        :param lib: A :class:`ctypes.CDLL` instance for the NLPIR API library where
            the function will be retrieved from (defaults to :data:`libNLPIR`).
        :returns: The exported function. It can be called like any other Python
            callable.

        """
        logger.debug("Getting NLPIR API function: {'name': '%s', 'argtypes': '%s',"
                     " 'restype': '%s'}." % (name, argtypes, restype))
        func = getattr(self.lib_nlpir, name)
        if argtypes is not None:
            func.argtypes = argtypes
        if restype is not c_int:
            func.restype = restype
        logger.debug("NLPIR API function '%s' retrieved." % name)
        return func

    @staticmethod
    def load_library(platform, is_64bit, lib_name, lib_dir=LIB_DIR):
        """Loads the NLPIR library appropriate for the user's system.

        This function is called automatically when this module is loaded.

        :param str platform: The platform identifier for the user's system.
        :param bool is_64bit: Whether or not the user's system is 64-bit.
        :param str lib_dir: The directory that contains the library files
            (defaults to :data:`LIB_DIR`).
        :raises RuntimeError: The user's platform is not supported by NLPIR.

        """
        logger.debug("Loading NLPIR library file from '%s'" % lib_dir)
        if platform.startswith('win') and is_64bit:
            lib = os.path.join(lib_dir, 'win64', lib_name)
            logger.debug("Using library file for 64-bit Windows.")
        elif platform.startswith('win'):
            lib = os.path.join(lib_dir, 'win32', lib_name)
            logger.debug("Using library file for 32-bit Windows.")
        elif platform.startswith('linux') and is_64bit:
            lib = os.path.join(lib_dir, 'linux64', 'lib%s.so' % lib_name)
            logger.debug("Using library file for 64-bit GNU/Linux.")
        elif platform.startswith('linux'):
            lib = os.path.join(lib_dir, 'linux32', 'lib%s.so' % lib_name)
            logger.debug("Using library file for 32-bit GNU/Linux.")
        else:
            raise RuntimeError("Platform '%s' is not supported by NLPIR." %
                               platform)
        libNLPIR = cdll.LoadLibrary(lib)
        logger.debug("NLPIR library file '%s' loaded." % lib)
        return libNLPIR
