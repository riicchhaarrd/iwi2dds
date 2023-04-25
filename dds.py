import struct

# #define\s+(\w+)\s+(.*)
# $1 = $2

DDSD_CAPS = 0x00000001
DDSD_HEIGHT = 0x00000002
DDSD_WIDTH = 0x00000004
DDSD_PITCH = 0x00000008
DDSD_PIXELFORMAT = 0x00001000
DDSD_MIPMAPCOUNT = 0x00020000
DDSD_LINEARSIZE = 0x00080000
DDSD_DEPTH = 0x00800000

DDPF_ALPHAPIXELS = 0x00000001
DDPF_ALPHA = 0x00000002
DDPF_FOURCC = 0x00000004
DDPF_RGB = 0x00000040

DDSCAPS_COMPLEX = 0x00000008
DDSCAPS_TEXTURE = 0x00001000
DDSCAPS_MIPMAP = 0x00400000

DDSCAPS2_CUBEMAP = 0x00000200
DDSCAPS2_CUBEMAP_POSITIVEX = 0x00000400
DDSCAPS2_CUBEMAP_NEGATIVEX = 0x00000800
DDSCAPS2_CUBEMAP_POSITIVEY = 0x00001000
DDSCAPS2_CUBEMAP_NEGATIVEY = 0x00002000
DDSCAPS2_CUBEMAP_POSITIVEZ = 0x00004000
DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x00008000
DDSCAPS2_VOLUME = 0x00200000

class DDS_Header:
    def __init__(self, **kwargs):
        self.dwMagic = 0x20534444
        self.dwSize = 124
        self.dwFlags = 0
        self.dwHeight = 0
        self.dwWidth = 0
        self.dwPitchOrLinearSize = 0
        self.dwDepth = 0
        self.dwMipMapCount = 0
        self.dwReserved1 = 0
        self.dwReserved12 = 0
        self.dwReserved13 = 0
        self.dwReserved14 = 0
        self.dwReserved15 = 0
        self.dwReserved16 = 0
        self.dwReserved17 = 0
        self.dwReserved18 = 0
        self.dwReserved19 = 0
        self.dwReserved110 = 0
        self.dwReserved111 = 0
        self.sPixelFormat_dwSize = 0
        self.sPixelFormat_dwFlags = 0
        self.sPixelFormat_dwFourCC = 0
        self.sPixelFormat_dwRGBBitCount = 0
        self.sPixelFormat_dwRBitMask = 0
        self.sPixelFormat_dwGBitMask = 0
        self.sPixelFormat_dwBBitMask = 0
        self.sPixelFormat_dwAlphaBitMask = 0
        self.sCaps_dwCaps1 = 0
        self.sCaps_dwCaps2 = 0
        self.sCaps_dwDDSX = 0
        self.sCaps_dwReserved = 0
        self.dwReserved2 = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def pack(self):
        return struct.pack("<32I", self.dwMagic, self.dwSize, self.dwFlags, self.dwHeight, self.dwWidth, self.dwPitchOrLinearSize, self.dwDepth, self.dwMipMapCount, self.dwReserved1, self.dwReserved12, self.dwReserved13, self.dwReserved14, self.dwReserved15, self.dwReserved16, self.dwReserved17, self.dwReserved18, self.dwReserved19, self.dwReserved110, self.dwReserved111, self.sPixelFormat_dwSize, self.sPixelFormat_dwFlags, self.sPixelFormat_dwFourCC, self.sPixelFormat_dwRGBBitCount, self.sPixelFormat_dwRBitMask, self.sPixelFormat_dwGBitMask, self.sPixelFormat_dwBBitMask, self.sPixelFormat_dwAlphaBitMask, self.sCaps_dwCaps1, self.sCaps_dwCaps2, self.sCaps_dwDDSX, self.sCaps_dwReserved, self.dwReserved2)