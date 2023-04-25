import struct
import sys
from enum import Enum
import dds
import math
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mipmaps', action='store_true')
parser.add_argument('input_file', type=str, help='input file')
args = parser.parse_args()

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
        
    hdr = dds.DDS_Header(
        dwFlags=dds.DDSD_CAPS | dds.DDSD_HEIGHT | dds.DDSD_WIDTH | dds.DDSD_PIXELFORMAT,
        #dwFlags=dds.DDSD_CAPS | dds.DDSD_HEIGHT | dds.DDSD_WIDTH | dds.DDSD_PIXELFORMAT | dds.DDSD_LINEARSIZE,
        dwHeight=height,
        dwWidth=width,
        dwDepth=1,
        sPixelFormat_dwSize=32,
        sPixelFormat_dwFlags=dds.DDPF_FOURCC,
        # is this portable?
        # or use int.from_bytes(..., byteorder='little') instead
        sPixelFormat_dwFourCC=ord('D') | (ord('X') << 8) | (ord('T') << 16) | (ord(dxt_format) << 24),
        sCaps_dwCaps1=dds.DDSCAPS_TEXTURE
    )

    with open(path, "wb") as f:
        f.write(hdr.pack())
        f.write(data)

def calculate_compressed_mipmap_size(width, height, bpp):
    return ((width + 3) // 4) * ((height + 3) // 4) * bpp

class Mipmap:
    def __init__(self, level, w, h, offset, size, data = None):
        self.level = level
        self.width = w
        self.height = h
        self.offset = offset
        self.size = size
        self.data = data

with open(args.input_file, "rb") as file:
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

    path = os.path.realpath(args.input_file)
    dirpath = os.path.dirname(path)
    filename = os.path.basename(path)
    basename = os.path.splitext(filename)[0]

    numfaces = 1
    if header.flags & IMAGE_FLAGS_CUBEMAP:
        numfaces = 6

    bpp = 8
    if image_format != GfxImageFormat.DXT1:
        bpp = 16

    mipmaps = []
    mipcount = int(math.log2(max(header.dimensions[0], header.dimensions[1], 1))) + 1
    if header.flags & IMAGE_FLAGS_NOMIPMAP:
        mipcount = 1
    total = 0

    offsz = 28

    for miplevel in range(mipcount - 1, -1, -1):
        w = max(header.dimensions[0] >> miplevel, 1)
        h = max(header.dimensions[1] >> miplevel, 1)
        sz = calculate_compressed_mipmap_size(w, h, bpp) * numfaces

        mipmap = Mipmap(miplevel, w, h, offsz, sz, data[offsz:offsz+sz])
        mipmaps.append(mipmap)

        offsz += sz
    
    if args.mipmaps:
        for mipmap in mipmaps:
            print(f'level: {mipmap.level}, width: {mipmap.width}, height: {mipmap.height}, size: {mipmap.size}')
            export_dds(f'{dirpath}/{basename}_{mipmap.level}.dds', GfxImageFormat(header.format), mipmap.width, mipmap.height, mipmap.data)
    else:
        mipmap = mipmaps[-1]
        export_dds(f'{dirpath}/{basename}.dds', GfxImageFormat(header.format), mipmap.width, mipmap.height, mipmap.data)