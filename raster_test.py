#!/usr/bin/env python

import unittest

from raster import Raster
from raster import URF
from raster import PWG


class TestRaster(unittest.TestCase):

  def test_URF_decode_header(self):
    urf_data = (
      'UNIRAST\0'
      '\x00\x00\x00\x01' # pages
      '\x08' # bpp
      '\x02' # colorspace
      '\x01' # duplex
      '\x05' # quality
      '\x00\x00\x00\x01' # unknown0
      '\x00\x00\x00\x02' # unknown1
      '\x00\x00\x00\x03' # width
      '\x00\x00\x00\x04' # height
      '\x00\x00\x00\x05' # dpi
      '\x00\x00\x00\x06' # unknown2
      '\x00\x00\x00\x07' # unknown3
    )

    urf = URF()
    urf.decode_header_(urf_data)

    self.assertEqual(urf.pages, 1)
    self.assertEqual(urf.bpp, 8)
    self.assertEqual(urf.colorspace, 2)
    self.assertEqual(urf.duplex, 1)
    self.assertEqual(urf.quality, 5)
    self.assertEqual(urf.unknown0, 1)
    self.assertEqual(urf.unknown1, 2)
    self.assertEqual(urf.page_width, 3)
    self.assertEqual(urf.page_height, 4)
    self.assertEqual(urf.dpi, 5)
    self.assertEqual(urf.unknown2, 6)
    self.assertEqual(urf.unknown3, 7)


if __name__ == '__main__':
  unittest.main()
