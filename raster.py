#!/usr/bin/env python

from __future__ import print_function

import StringIO
import argparse
import struct
import os.path

from PIL import Image
from PIL import ImageDraw


COLOR_SPACE_ENUM = {
  1: 'Rgb', # Device RGB (red green blue)
  3: 'Black', # Device black
  6: 'Cmyk', # Device CMYK (cyan magenta yellow black)
  18: 'Sgray', # sRGB grayscale
  19: 'RGB',#'Srgb', # sRGB color
  20: 'AdobeRgb', # Adobe RGB color
  48: 'Device1', # Device color, 1 colorant
  49: 'Device2', # Device color, 2 colorants
  50: 'Device3', # Device color, 3 colorants
  51: 'Device4', # Device color, 4 colorants
  52: 'Device5', # Device color, 5 colorants
  53: 'Device6', # Device color, 6 colorants
  54: 'Device7', # Device color, 7 colorants
  55: 'Device8', # Device color, 8 colorants
  56: 'Device9', # Device color, 9 colorants
  57: 'Device10', # Device color, 10 colorants
  58: 'Device11', # Device color, 11 colorants
  59: 'Device12', # Device color, 12 colorants
  60: 'Device13', # Device color, 13 colorants
  61: 'Device14', # Device color, 14 colorants
  62: 'Device15', # Device color, 15 colorants
}

PRINT_QUALITY_ENUM = {
  0: 'Default',
  3: 'Draft',
  4: 'Normal',
  5: 'High',
}


def to_b(byte_str):
  """Convert byte str to signed char."""
  return struct.unpack('b', byte_str)[0]

def to_B(byte_str):
  """Convert byte str to unsigned char."""
  return struct.unpack('B', byte_str)[0]


class Raster:

  @staticmethod
  def guess_format(file_path):
    """Guess the format from the file path and potentially contents."""
    if os.path.exists(file_path):
      header = open(file_path).read(4)[:4]
      if len(header) >= 4 and struct.unpack('4s', header)[0] == 'RaS2':
        return 'PWG'
      
      header = open(file_path).read(8)[:8]
      if len(header) >= 8 and struct.unpack('8s', header)[0] == 'UNIRAST\0':
        return 'URF'

    if file_path.endswith('.urf'):
      return 'URF'
    elif file_path.endswith('.pwg'):
      return 'PWG'
    elif file_path.endswith('.ras'):
      return 'CUPS'
    return None


  @staticmethod
  def create_best_raster(file_path):
    format_guess = Raster.guess_format(file_path)
    if format_guess == 'PWG':
      return PWG()
    elif format_guess == 'URF':
      return URF()
    return None


  def decode_packbits_like_(
      self,
      img,
      data,
      bytes_per_pixel=3,
      width=None,
      height=None,
      ):
    """Decode PackBits-like data. Returns PIL Image."""
    if len(data) <= 0:
      return
    
    if width is None:
      width = img.width

    if height is None:
      height = img.height

    x, y = 0, 0
    i = 0

    line_repeat = to_B(data[i])
    i += 1
    j = i

    while i < len(data) and y < height:
      code = data[i]
      code_int = to_b(data[i])

      if code == '\x80':
        #'FillRestOfLineWithFillByte'

        pixels_left_in_line = width - x

        for _ in range(pixels_left_in_line):
          img.putpixel((x, y), tuple([0xFF] * bytes_per_pixel))
          x += 1

        i += 1

      elif code < '\x80':
        #'copy single pixel and repeat it n+1 times'

        repeat_times = code_int + 1
        pixel = tuple([
            to_B(b)
            for b in
            data[i + 1:i + 1 + bytes_per_pixel]
            ])

        for _ in range(repeat_times):
          img.putpixel((x, y), pixel)
          x += 1

        i += 1 + bytes_per_pixel

      elif code > '\x80':
        #'copy the following (-n)+1 pixels verbatim'

        repeat_pixels = (-code_int) + 1

        for j in range(repeat_pixels):
          pixel = tuple([
              to_B(b)
              for b in
              data[i+1+(j*bytes_per_pixel):i+1+((1+j)*bytes_per_pixel)]
              ])
          img.putpixel((x, y), pixel)
          x += 1

        i += 1 + bytes_per_pixel * repeat_pixels

      if x >= width:
        x = 0
        y += 1

        if line_repeat > 0:
          i = j
          line_repeat -= 1
        elif i < len(data):
          line_repeat = to_B(data[i])
          i += 1
          j = i

    return img


  def encode_packbits_like_(
      self,
      output_file,
      img,
      colorspace_str,
      ):
    img_out = img.convert(colorspace_str)
    x = 0
    y = 0
    to_x = 0
    while y < img_out.height:
      output_file.write(b'\x00')
      while x < img_out.width:
        pixel = img_out.getpixel((x, y))
        to_x = x
        while ((to_x+1) < img_out.width
            and pixel == img_out.getpixel((to_x+1, y))
            # Don't overflow byte.
            and (to_x - x) < 127):
          to_x += 1
        output_file.write(chr(to_x - x))
        for channel in pixel:
          output_file.write(chr(channel))
        x = to_x + 1
      x = 0
      y += 1


  def load(self, urf_file):
    raise NotImplementedError()

  def save(self, output_file):
    raise NotImplementedError()

  def load_img(self, input_img):
    raise NotImplementedError()

  def save_img(self, output_file):
    raise NotImplementedError()


class URF(Raster):
  """Apple URF UNIRAST raster format."""

  colorspace_str = 'RGB'

  pages = 0

  bpp = 0
  colorspace = 0
  duplex = 0
  quality = 0

  # LeadingEdge?
  unknown0 = 1
  # Reserved?
  unknown1 = 0

  page_width = 0
  page_height = 0

  dpi = 0

  # Reserved?
  unknown2 = 0
  # Reserved?
  unknown3 = 0
  
  # Potential unknowns
  # Orientation: {Portrait, Landscape, Reverse ..}
  # Reserved
  # HWResolution ?
  # LeadingEdge
  # TotalPageCount
  # CrossFeedTransform and FeedTransform
  # Tumble
  # NumCopies
  # Rendering intent
  
  '''
  urf-supported (1setOf keyword) = V1.4,CP1,PQ4-5,RS600,SRGB24,W8,OB9,OFU0,DM3,IS20-21
  
  CP1 : copies? Color Space? Copy Pages?
  PQ4-5 : Print Quality 4,5
  RS600 : Resolution 600 DPI
  SRGB24 : SRGB 24 bit
  W8 : White 8 bit
  OB9 : Operation ..? Output Bin?
  OFU0 : .. Full-bleed?
  DM3 : Duplex Mode?
  IS20-21 : Insert Sheet?
  '''


  def load(self, urf_file):
    urf_data = open(urf_file).read()

    # Parse header to get meta data.
    self.decode_header_(urf_data)

    n_channels = 3
    self.img = Image.new(
        mode=self.colorspace_str,
        size=(self.page_width, self.page_height),
        color=tuple([255] * n_channels),
        )

    raster_body = urf_data[44:]
    #self.decode_body_(raster_body)
    self.decode_packbits_like_(
        self.img, raster_body,
        n_channels,
        self.page_width,
        self.page_height,
        )


  def save(self, output_file):
    output_urf = open(output_file, 'wb+')
    self.encode_header_(output_urf)
    #self.encode_body_(output_urf)
    self.encode_packbits_like_(
        output_urf,
        self.img,
        self.colorspace_str,
        )


  def load_img(self, input_img):
    self.img = Image.open(input_img)

    self.pages = 1
    self.bpp = 24
    self.colorspace = 1
    self.duplex = 0
    self.quality = 5

    self.page_width = self.img.width
    self.page_height = self.img.height

    # PIL DPI is a tuple of either int or float, convert to int.
    dpi, _ = dpi_tuple = self.img.info.get('dpi')
    if not dpi_tuple:
      print('No DPI info found. Defaulting to 72 DPI.')
      dpi = 72
    elif not (type(dpi_tuple[0]) == int and dpi_tuple[0] == dpi_tuple[1]):
      dpi = int(dpi_tuple[0])
      print('Converting DPI {} to {}'.format(dpi_tuple, dpi))
    self.dpi = dpi


  def save_img(self, output_file):
    self.img.save(output_file)


  def decode_header_(self, urf_data):
    magic = struct.unpack('8s', urf_data[:8])[0]
    if magic != 'UNIRAST\0':
      raise Exception('Header magic does not match: {}'.format(magic))

    self.pages = struct.unpack('>I', urf_data[8:12])[0]
    if self.pages <= 0:
      print('WARNING: Zero or less pages found: {}'.format(self.pages))

    # Bits-per-pixel
    self.bpp = struct.unpack('B', urf_data[12:13])[0]
    if not self.bpp in [8, 24, 32, 64]:
      print('WARNING: BPP not in valid set: {}'.format(self.bpp))

    self.colorspace = struct.unpack('B', urf_data[13:14])[0]
    if not (0 <= self.colorspace <= 6):
      print('WARNING: Color space value is not in valid range: {}'.format(self.colorspace))

    self.duplex = struct.unpack('B', urf_data[14:15])[0]
    if not (0 <= self.duplex <= 3):
      print('WARNING: Duplex value is not in valid range: {}'.format(self.duplex))

    self.quality = struct.unpack('B', urf_data[15:16])[0]
    if not (3 <= self.quality <= 5):
      print('WARNING: Quality value is not in valid range: {}'.format(self.quality))

    # TODO
    self.unknown0 = struct.unpack('>I', urf_data[16:20])[0]
    self.unknown1 = struct.unpack('>I', urf_data[20:24])[0]

    self.page_width = struct.unpack('>I', urf_data[24:28])[0]
    self.page_height = struct.unpack('>I', urf_data[28:32])[0]

    if self.page_width <= 0:
      print(
          'WARNING: Zero or less page width found: {}'.format(self.page_width))

    if self.page_height <= 0:
      print(
          'WARNING: Zero or less page height found: {}'.format(
              self.page_height))

    self.dpi = struct.unpack('>I', urf_data[32:36])[0]

    # TODO
    self.unknown2 = struct.unpack('>I', urf_data[36:40])[0]
    self.unknown3 = struct.unpack('>I', urf_data[40:44])[0]


  def encode_header_(self, output_urf):
    output_urf.write(b'UNIRAST\0')

    output_urf.write(struct.pack('>I', self.pages))

    output_urf.write(struct.pack('B', self.bpp))

    output_urf.write(struct.pack('B', self.colorspace))

    output_urf.write(struct.pack('B', self.duplex))

    output_urf.write(struct.pack('B', self.quality))

    # TODO
    # unknown0
    output_urf.write(struct.pack('>I', self.unknown0))
    # unknown1
    output_urf.write(struct.pack('>I', self.unknown1))

    #print('Width: {}'.format(self.page_width))
    output_urf.write(struct.pack('>I', self.page_width))

    output_urf.write(struct.pack('>I', self.page_height))

    #print('DPI: {}'.format(self.dpi))
    output_urf.write(struct.pack('>I', self.dpi))

    # TODO
    # unknown2
    output_urf.write(struct.pack('>I', self.unknown2))
    # unknown3
    output_urf.write(struct.pack('>I', self.unknown3))


class PWG(Raster):
  """PWG Raster format, defined by [PWG5102.4]."""
  '''
  ftp://ftp.pwg.org/pub/pwg/candidates/cs-ippraster10-20120420-5102.4.pdf

  A4 according to the internet
  4960 x 7016
  4961 x 7016

  Maths:
  9.64 / 72 * 254 =~ 340
  14.38 / 72 * 254 =~ 500
  842 - 833.50 = 8.5
  595 - 585.64 = 9.36
  8.5 / 72 * 254 =~ 300
  
  585.64 - 9.64 = 576
  833.50 - 14.38 = 819.12
  
  (576 / 72) * 2.54 = 20.32
  (833.50 / 72) * 2.54 = 29.4040277778

  (576 / 72) * 600 = 4800
  (833.50 / 72) * 600 = 6945.83333333

  (595 / 72) * 600 = 4958.33333333
  (842 / 72) * 600 = 7016.66666667
  
  (4800 / 600) * 2.54 = 20.32 cm
  (6826 / 600) * 2.54 = 28.8967333333 cm
  
  (5102 px / 600) * 2.54 = 21.5984666667 cm
  (7181 px / 600) * 2.54 = 30.3995666667 cm
  
  ((5.00 mm / 25.4 mm/in) * 600 px/in) = 118.11 px
  (3.40 / 25.4) * 600 = 80.31 px
  
  20.13
  28.6
  
  4958, 7016 from example PWGs
  

  From the Canon PPD:

  *ImageableArea A4: "9.64 14.38 585.64 833.50"
  *PaperDimension A4: "595 842"
  *%CNSizeToPrintArea A4 4800 6826

  *ImageableArea A4.bl: "0 0 594 841"
  *PaperDimension A4.bl: "595 842"
  *%CNSizeToPrintArea A4.bl 5102 7181
  
  *PageSize A4/A4 [8.27"x11.69" 210.0x297.0mm]: "<</CNPageSizeName(A4)/PageSize[595 842]/ImagingBBox null>>setpagedevice"
  *PageSize A4.bl/A4(borderless) [8.27"x11.69" 210.0x297.0mm]: "<</CNPageSizeName(A4.bl)/PageSize[595 842]/ImagingBBox null>>setpagedevice"
  *PageRegion A4/A4 [8.27"x11.69" 210.0x297.0mm]: "<</CNPageSizeName(A4)/PageSize[595 842]/ImagingBBox null>>setpagedevice"
  *PageRegion A4.bl/A4(borderless) [8.27"x11.69" 210.0x297.0mm]: "<</CNPageSizeName(A4.bl)/PageSize[595 842]/ImagingBBox null>>setpagedevice"

  
  From CUPS PPD:
  *PageSize A4/A4:	"<</PageSize[595 842]/ImagingBBox null>>setpagedevice"
  *PageRegion A4/A4:	"<</PageSize[595 842]/ImagingBBox null>>setpagedevice"
  *ImageableArea A4/A4:	"0 0 595 842"
  *PaperDimension A4/A4:	"595 842"

  
  From CUPS:
  unsigned	HWResolution[2];	/* Resolution in dots-per-inch */
  unsigned	ImagingBoundingBox[4];	/* Pixel region that is painted (points, left, bottom, right, top) */
  unsigned	Margins[2];		/* Lower-lefthand margins in points */
  unsigned	PageSize[2];		/* Width and length of page in points */
  unsigned	cupsWidth;		/* Width of page image in pixels */
  unsigned	cupsHeight;		/* Height of page image in pixels */
  float		cupsPageSize[2];	/* Floating point PageSize (scaling *
  					 * factor not applied) @since CUPS 1.2/macOS 10.5@ */
  float		cupsImagingBBox[4];	/* Floating point ImagingBoundingBox
				 * (scaling factor not applied, left,
				 * bottom, right, top) @since CUPS 1.2/macOS 10.5@ */
  '''

  img = None

  media_color = ''
  # When the empty string, the default media type is used.
  media_type = ''
  # This field specifies the general document type.
  print_content_optimize = ''
  cut_media = 0 # for cutting rolls
  duplex = 1 # Double-sided
  
  '''
  Duplex   Tumble   Sides
  FALSE(0) FALSE(0) OneSided
  TRUE(1)  FALSE(0) TwoSidedLongEdge
  TRUE(1)  TRUE(1)  TwoSidedShortEdge
  '''
  
  # The HWResolution field consists of two integers representing the cross-feed
  # and feed resolutions of the page bitmap in pixels (dots) per inch.
  # MUST be initialized to one of the supported values reported by the
  # "PwgRasterDocumentResolutionSupported" element.
  hw_resolution = (0, 0)

  # This field specifies whether to insert a single blank sheet prior to the
  # current page, using the media defined by the current page header.
  insert_sheet = 0
  # This field specifies whether to jog (offset) pages in the output bin.
  jog = 0
  # 0:"FeedDirection", 1:'LongEdgeFirst'
  leading_edge = 0
  # Media input tray or source.
  media_position = 0
  media_weight_metric = 0 # grams/m^2
  # When 0, the default number of copies is used.
  num_copies = 1

  # 0  Portrait  Not rotated
  # 1  Landscape  Rotated 90 degrees, counter-clockwise
  # 2  ReversePortrait  Rotated 180 degrees
  # 3  ReverseLandscape  Rotated 90 degrees clockwise
  orientation = 0

  # Width and length of the current page in points.
  # When the width and length are 0 the default media size is used, typically as
  # defined by the Width, Height, and HWResolution fields for the page bitmap.
  page_size = (0, 0)
  tumble = 0 # tumble = flip short edge if portrait

  # The Width and Height fields MUST be initialized to the full width and height
  # of the current page in addressable units as defined by the HWResolution field.
  width = 0
  height = 0

  bits_per_color = 0
  bits_per_pixel = 0
  # BytesPerLine = TRUNCATE((BitsPerPixel * Width + 7) / 8)
  bytes_per_line = 0
  
  # 0:chunked, 1:banded, 2:planar
  color_order = 0
  # 1 RGB, 6 CMYK, 19 sRGB
  color_space = 0
  colorspace_str = 'RGB'
  num_colors = 0
  total_page_count = 0 # "cupsInteger[0]"
  cross_feed_transform = 0 # "cupsInteger[1]"
  feed_transform = 0 # "cupsInteger[2]"
  
  # Area, in pixels, that contains non-empty content.
  # Pixels are measured from the beginning of the page bitmap, so the
  # coordinates reflect the orientation specified by the XFeedTransform and
  # FeedTransform fields.
  # All fields MUST have the value 0 if the ImageBox is unknown.
  image_box_left = 0 # "cupsInteger[3]"
  image_box_top = 0 # "cupsInteger[4]"
  image_box_right = 0 # "cupsInteger[5]"
  image_box_bottom = 0 # "cupsInteger[6]"
  # From tocnpwg:
  # image_box_left = header.cupsImagingBBox[0] * r->header.HWResolution[0]

  alternate_primary = (0, 255, 255, 255) # "cupsInteger[7]"
  # 3:draft, 4:standard, 5:high
  print_quality = 0 # "cupsInteger[8]"
  
  # The VendorIdentifier field contains to the USB vendor identification number
  # for the vendor providing the data.
  vendor_identifier = 0 # "cupsInteger[14]"
  # The VendorLength field specifies the number of octets that are used in the
  # VendorData field.
  vendor_length = 0 # "cupsInteger[15]"
  # The VendorData field contains the vendor octets.
  vendor_data = ''
  
  # The RenderingIntent field specifies the colorimetric rendering intent for
  # the page.
  # When the empty string, the default rendering intent is used.
  # Specifies how out-of-gamut colors (or shades of gray) are mapped to device
  # colors when printing.
  # 'absolute' Clip out-of-gamut colors to preserve in-gamut accuracy without
  # adjusting the white point.
  # 'auto' Automatically determine the rendering intent based on the document
  # and job ticket.
  # 'perceptual' Map out-of-gamut colors at the expense of ingamut accuracy.
  # 'relative' Clip out-of-gamut colors to preserve in-gamut accuracy, adjusting
  # the white point as necessary.
  # 'relative-bpc' Clip out-of-gamut colors to preserve in-gamut accuracy,
  # adjusting both the white and black points as necessary.
  # (bpc = Black Point Compensation)
  # 'saturation' Preserve saturated colors.
  rendering_intent = ''

  # Named size as defined by the PWG Standard for Media Standardized Names
  # [PWG5101.1].
  page_size_name = ''


  def load(self, raster_file):
    raster_data = open(raster_file).read()

    # Parse header to get meta data.
    self.decode_header_(raster_data)

    n_channels = 3

    self.img = Image.new(
        mode=self.colorspace_str,
        size=(self.width, self.height),
        color=tuple([0] * n_channels),
        )

    raster_body = raster_data[1800:]
    self.decode_packbits_like_(
        self.img,
        raster_body,
        n_channels,
        self.width,
        self.height,
        )


  def save(self, output_path):
    output_file = open(output_path, 'wb+')

    self.encode_header_(output_file)
    
    #self.encode_body_(output_file)
    self.encode_packbits_like_(
        output_file,
        self.img,
        self.colorspace_str,
        )


  def load_img(self, input_img):
    self.img = Image.open(input_img)
    
    # TODO
    self.colorspace_str = 'RGB'
    self.img = self.img.convert(self.colorspace_str)
    
    source_size = (self.img.width, self.img.height)
    
    self.hw_resolution = (600, 600) # DPI
    
    self.num_copies = 1

    # 72 DPI dots
    self.page_size = (595, 842) # A4
    #self.page_size = (4958, 7016) # A4
    #self.page_size = (self.img.width, self.img.height) # A4
    
    # TODO
    n_channels = 3
    
    # CHECK!!!
    #self.width = self.img.width
    #self.height = self.img.height
    
    #self.width = 4958
    #self.height = 7016
    
    #self.width = 595
    #self.height = 842
    
    #self.width = 5102
    #self.height = 7181
    
    #self.width = 4800
    #self.height = 6826

    #self.width = 4960
    #self.height = 7016

    self.width = 4961
    self.height = 7016
    
    if (self.width != self.img.width and self.height != self.img.height):
      print('Size mismatch!')

    img2 = Image.new(
        mode=self.colorspace_str,
        size=(self.width, self.height),
        color=(255, 255, 255),
        )
    offset = (
        #(self.width - self.img.width) // 2,
        #(self.height - self.img.height) // 2,
        #64, 64,
        0,0
        )
    img2.paste(
        self.img,
        box=(offset[0], offset[1], self.img.width + offset[0], self.img.height + offset[1]),
        )
    self.img = img2

    self.bits_per_color = 8
    self.bits_per_pixel = self.bits_per_color * n_channels
    self.bytes_per_line = (self.bits_per_pixel / 8) * self.width

    # CHECK!!!
    self.color_space = 1 # 1 RGB, 6 CMYK, 19 sRGB

    self.num_colors = 3
    self.total_page_count = 1 # CHECK!!!
    
    self.tumble = 0 # CHECK!!!
    
    # CHECK!!!
    #self.rendering_intent = 'absolute'
    #self.rendering_intent = 'perceptual'
    #self.rendering_intent = 'relative'
    #self.rendering_intent = 'relative-bpc'
    self.rendering_intent = 'saturation'
    
    '''
    self.image_box_left = 0
    self.image_box_top = 0
    self.image_box_right = self.img.width
    self.image_box_bottom = self.img.height
    #self.image_box_right = source_size[0]
    #self.image_box_bottom = source_size[1]
    '''

    '''
    self.image_box_left = offset[0]
    self.image_box_top = offset[1]
    self.image_box_right = self.img.width + offset[0]
    self.image_box_bottom = self.img.height + offset[1]
    '''
    
    #self.image_box_left = 150
    #self.image_box_top = 150
    #self.image_box_right = 4808
    #self.image_box_bottom = 6866
    
    ''' '
    self.image_box_left = 80
    self.image_box_top = 110
    self.image_box_right = 4880
    self.image_box_bottom = 6946
    ' '''
    
    '' ''
    self.image_box_left = 0
    self.image_box_top = 0
    self.image_box_right = 0
    self.image_box_bottom = 0
    '' ''

    #self.page_size_name = 'A4'
    #self.page_size_name = 'A4.Fullbleed'
    #self.page_size_name = 'A4.bl' # borderless
    self.page_size_name = ''


  def save_img(self, output_file):
    self.img.save(output_file)


  def decode_header_(self, raster_data):
    # "synchronization word"
    magic = struct.unpack('4s', raster_data[:4])[0]
    if magic != 'RaS2':
      raise Exception('Header magic does not match: {}'.format(magic))
    
    # Page Header

    pwg_raster = struct.unpack('64s', raster_data[4:4+64])[0]
    if pwg_raster != ('PwgRaster' + '\0'*55):
      print('WARNING: Second header does not match expectations: {}'.format(
          pwg_raster))

    self.media_color = struct.unpack('64s', raster_data[4+64:4+128])[0]

    self.media_type = struct.unpack('64s', raster_data[4+128:4+192])[0]

    self.print_content_optimize = struct.unpack('64s', raster_data[4+192:4+256])[0]
    
    # 256-267 Reserved

    self.cut_media = struct.unpack('>I', raster_data[4+268:4+272])[0]

    self.duplex = bool(struct.unpack('>I', raster_data[4+272:4+276])[0])

    # HWResolution
    w = struct.unpack('>I', raster_data[4+276:4+280])[0]
    h = struct.unpack('>I', raster_data[4+280:4+284])[0]
    self.hw_resolution = (w, h)
    
    # 284-299 Reserved

    self.insert_sheet = struct.unpack('>I', raster_data[4+300:4+304])[0]

    self.jog = struct.unpack('>I', raster_data[4+304:4+308])[0]

    self.leading_edge = struct.unpack('>I', raster_data[4+308:4+312])[0]
    
    # 312-323 Reserved

    self.media_position = struct.unpack('>I', raster_data[4+324:4+328])[0]

    self.media_weight_metric = struct.unpack('>I', raster_data[4+328:4+332])[0]
    
    # 332-339 Reserved

    self.num_copies = struct.unpack('>I', raster_data[4+340:4+344])[0]

    self.orientation = struct.unpack('>I', raster_data[4+344:4+348])[0]
    
    # 348-351 Reserved

    # PageSize
    page_w = struct.unpack('>I', raster_data[4+352:4+356])[0]
    page_h = struct.unpack('>I', raster_data[4+356:4+360])[0]
    self.page_size = (page_w, page_h)
    
    # 360-367 Reserved

    self.tumble = bool(struct.unpack('>I', raster_data[4+368:4+372])[0])

    # width, height in pixels
    self.width = struct.unpack('>I', raster_data[4+372:4+376])[0]

    self.height = struct.unpack('>I', raster_data[4+376:4+380])[0]
    
    # 380-383 Reserved

    self.bits_per_color = struct.unpack('>I', raster_data[4+384:4+388])[0]

    self.bits_per_pixel = struct.unpack('>I', raster_data[4+388:4+392])[0]

    self.bytes_per_line = struct.unpack('>I', raster_data[4+392:4+396])[0]

    # 0: CUPS_ORDER_CHUNKED
    self.color_order = struct.unpack('>I', raster_data[4+396:4+400])[0]

    # 6: CUPS_CSPACE_CMYK
    self.color_space = struct.unpack('>I', raster_data[4+400:4+404])[0]
    self.colorspace_str = COLOR_SPACE_ENUM[self.color_space].upper()
    
    # 404-419 Reserved

    self.num_colors = struct.unpack('>I', raster_data[4+420:4+424])[0]
    
    # 424-451 Reserved

    self.total_page_count = struct.unpack('>I', raster_data[4+452:4+456])[0]

    self.cross_feed_transform = struct.unpack('>I', raster_data[4+456:4+460])[0]

    self.feed_transform = struct.unpack('>I', raster_data[4+460:4+464])[0]

    self.image_box_left = struct.unpack('>I', raster_data[4+464:4+468])[0]

    self.image_box_top = struct.unpack('>I', raster_data[4+468:4+472])[0]

    self.image_box_right = struct.unpack('>I', raster_data[4+472:4+476])[0]

    self.image_box_bottom = struct.unpack('>I', raster_data[4+476:4+480])[0]

    # 8 bit per channel color
    self.alternate_primary = struct.unpack('BBBB', raster_data[4+480:4+484])

    self.print_quality = struct.unpack('>I', raster_data[4+484:4+488])[0]
    
    # 488-507 Reserved

    self.vendor_identifier = struct.unpack('>I', raster_data[4+508:4+512])[0]

    self.vendor_length = struct.unpack('>I', raster_data[4+512:4+516])[0]

    self.vendor_data = struct.unpack('1088s', raster_data[4+516:4+1604])[0]
    
    # 1604-1667 Reserved

    self.rendering_intent = struct.unpack('64s', raster_data[4+1668:4+1732])[0]

    self.page_size_name = struct.unpack('64s', raster_data[4+1732:4+1796])[0]


  def encode_header_(self, output_file):
    # "synchronization word"
    output_file.write('RaS2')

    # Page Header

    output_file.write('PwgRaster' + ('\0' * 55))

    output_file.write(struct.pack('64s', self.media_color))

    output_file.write(struct.pack('64s', self.media_type))

    output_file.write(struct.pack('64s', self.print_content_optimize))

    # 256-267 Reserved
    output_file.write('\0' * 12)

    output_file.write(struct.pack('>I', self.cut_media))

    output_file.write(struct.pack('>I', self.duplex))

    # HWResolution
    output_file.write(struct.pack('>I', self.hw_resolution[0]))
    output_file.write(struct.pack('>I', self.hw_resolution[1]))

    # 284-299 Reserved
    output_file.write('\0' * 16)

    output_file.write(struct.pack('>I', self.insert_sheet))

    output_file.write(struct.pack('>I', self.jog))

    output_file.write(struct.pack('>I', self.leading_edge))

    # 312-323 Reserved
    output_file.write('\0' * 12)

    output_file.write(struct.pack('>I', self.media_position))

    output_file.write(struct.pack('>I', self.media_weight_metric))

    # 332-339 Reserved
    output_file.write('\0' * 8)

    output_file.write(struct.pack('>I', self.num_copies))

    output_file.write(struct.pack('>I', self.orientation))

    # 348-351 Reserved
    output_file.write('\0' * 4)

    # PageSize
    output_file.write(struct.pack('>I', self.page_size[0]))
    output_file.write(struct.pack('>I', self.page_size[1]))

    # 360-367 Reserved
    output_file.write('\0' * 8)

    output_file.write(struct.pack('>I', self.tumble))

    output_file.write(struct.pack('>I', self.width))

    output_file.write(struct.pack('>I', self.height))

    # 380-383 Reserved
    output_file.write('\0' * 4)

    output_file.write(struct.pack('>I', self.bits_per_color))

    output_file.write(struct.pack('>I', self.bits_per_pixel))

    output_file.write(struct.pack('>I', self.bytes_per_line))

    output_file.write(struct.pack('>I', self.color_order))

    output_file.write(struct.pack('>I', self.color_space))

    # 404-419 Reserved
    output_file.write('\0' * 16)

    output_file.write(struct.pack('>I', self.num_colors))

    # 424-451 Reserved
    output_file.write('\0' * 28)

    output_file.write(struct.pack('>I', self.total_page_count))

    output_file.write(struct.pack('>I', self.cross_feed_transform))

    output_file.write(struct.pack('>I', self.feed_transform))

    output_file.write(struct.pack('>I', self.image_box_left))

    output_file.write(struct.pack('>I', self.image_box_top))

    output_file.write(struct.pack('>I', self.image_box_right))

    output_file.write(struct.pack('>I', self.image_box_bottom))

    # 8 bit per channel color

    output_file.write(struct.pack('BBBB', *self.alternate_primary))

    output_file.write(struct.pack('>I', self.print_quality))

    # 488-507 Reserved
    output_file.write('\0' * 20)

    output_file.write(struct.pack('>I', self.vendor_identifier))

    output_file.write(struct.pack('>I', self.vendor_length))

    output_file.write(struct.pack('1088s', self.vendor_data))

    # 1604-1667 Reserved
    output_file.write('\0' * 64)

    output_file.write(struct.pack('64s', self.rendering_intent))

    output_file.write(struct.pack('64s', self.page_size_name))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description='Encode and decode URF UNIRAST and PWG files.')

  parser.add_argument('action', choices=['encode', 'decode'])
  parser.add_argument('input', help='Input file')
  parser.add_argument('output', help='Output file')

  args = parser.parse_args()

  action = args.action
  input_file = args.input
  output_file = args.output

  if action == 'encode':
    raster_obj = Raster.create_best_raster(output_file)
    if raster_obj is None:
      exit('Unrecognised output format')

    raster_obj.load_img(input_file)
    raster_obj.save(output_file)

  elif action == 'decode':
    raster_obj = Raster.create_best_raster(input_file)
    if raster_obj is None:
      exit('Unrecognised input format')

    raster_obj.load(input_file)
    raster_obj.save_img(output_file)
