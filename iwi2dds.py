import struct
import sys
from enum import Enum
import dds
import math

class GfxImageFormat(Enum):
    INVALID = 0
    BITMAP_RGBA = 1
    BITMAP_RGB = 2
    BITMAP_LUMINANCE_ALPHA = 3
    BITMAP_LUMINANCE = 4
    BITMAP_ALPHA = 5
    WAVELET_RGBA = 6
    WAVELET_RGB = 7
    WAVELET_LUMINANCE_ALPHA = 8
    WAVELET_LUMINANCE = 9
    WAVELET_ALPHA = 10
    DXT1 = 11
    DXT3 = 12
    DXT5 = 13
    
IMAGE_FLAGS_NONE = 0
IMAGE_FLAGS_NOPICMIP = 1 
IMAGE_FLAGS_NOMIPMAP = 2 
IMAGE_FLAGS_CUBEMAP = 4
IMAGE_FLAGS_VOLMAP = 8

if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <input_file>')
    sys.exit(1)

input_filename = sys.argv[1]

gfx_image_header_format = "<3sbbb3h4i"

class GfxImageHeader:
    def __init__(self, tag, version, format, flags, dimensions, file_size_for_picmip):
        self.tag = tag
        self.version = version
        self.format = format
        self.flags = flags
        self.dimensions = dimensions
        self.file_size_for_picmip = file_size_for_picmip

    def pack(self):
        return struct.pack(gfx_image_header_format, self.tag, self.version, self.format,
                           self.flags, *self.dimensions, *self.file_size_for_picmip)

    @classmethod
    def unpack(cls, data):
        unpacked_data = struct.unpack(gfx_image_header_format, data)
        return cls(unpacked_data[0], unpacked_data[1], unpacked_data[2], unpacked_data[3],
                   unpacked_data[4:7], unpacked_data[7:11])


def export_dds(path, format, width, height, data):
    print(path, format, width, height, len(data))
    dxt_format = None

    match format:
        case GfxImageFormat.DXT1:
            dxt_format = '1'
        case GfxImageFormat.DXT3:
            dxt_format = '3'
        case GfxImageFormat.DXT5:
            dxt_format = '5'

    if dxt_format is None:
        raise Exception('Not a DXT format.')
    if len(data) == 0:
        raise Exception('No image data')
        
    depth = 1
    mipcount = math.log2(max(width, height, depth)) + 1

    hdr = dds.DDS_Header(
        dwFlags=dds.DDSD_CAPS | dds.DDSD_HEIGHT | dds.DDSD_WIDTH | dds.DDSD_PIXELFORMAT,
        #dwFlags=dds.DDSD_CAPS | dds.DDSD_HEIGHT | dds.DDSD_WIDTH | dds.DDSD_PIXELFORMAT | dds.DDSD_LINEARSIZE,
        dwHeight=width,
        dwWidth=height,
        dwDepth=depth,
        dwMipMapCount=int(mipcount),
        sPixelFormat_dwSize=32,
        sPixelFormat_dwFlags=dds.DDPF_FOURCC,
        # is this portable?
        # or use int.from_bytes(..., byteorder='little') instead
        sPixelFormat_dwFourCC=ord('D') | (ord('X') << 8) | (ord('T') << 16) | (ord(dxt_format) << 24),
        sCaps_dwCaps1=dds.DDSCAPS_TEXTURE
    )

    with open("image.dds", "wb") as f:
        f.write(hdr.pack())
        f.write(data)

with open(input_filename, "rb") as file:
    data = file.read()
    header = GfxImageHeader.unpack(data[:28])
    

    print("data:", len(data))
    print("tag:", header.tag)
    print("version:", header.version)
    image_format = GfxImageFormat(header.format)
    print("format:", image_format)
    print("flags:", header.flags)
    if header.flags & IMAGE_FLAGS_NOPICMIP:
        print("IMAGE_FLAGS_NOPICMIP is set")
    if header.flags & IMAGE_FLAGS_NOMIPMAP:
        print("IMAGE_FLAGS_NOMIPMAP is set")
    if header.flags & IMAGE_FLAGS_CUBEMAP:
        print("IMAGE_FLAGS_CUBEMAP is set")
    if header.flags & IMAGE_FLAGS_VOLMAP:
        print("IMAGE_FLAGS_VOLMAP is set")
    print("dimensions:", header.dimensions)
    print("file_size_for_picmip:", header.file_size_for_picmip)
    #print(header.__dict__)

    numfaces = 1
    if header.flags & IMAGE_FLAGS_CUBEMAP:
        numfaces = 6

    bpp = 8
    if image_format != GfxImageFormat.DXT1:
        bpp = 16

    texture_size = ((header.dimensions[0] + 3) // 4) * ((header.dimensions[1] + 3) // 4) * bpp
    texture_data_offset = header.file_size_for_picmip[0]
    texture_data_offset -= texture_size
    for face in range(numfaces):
        print(f'face: {face}, offset: {texture_data_offset}, size: {texture_size}')
        image_data = data[texture_data_offset:texture_size + texture_data_offset]
        print(f'image_data: {len(image_data)}')
        export_dds("test.dds", GfxImageFormat(header.format), header.dimensions[0], header.dimensions[1], image_data)