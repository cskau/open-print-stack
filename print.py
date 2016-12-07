#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import struct

from pkipplib import pkipplib

# print-rendering-intent
# print-content-optimize

class IPP_TWO_ZERO:
  # [RFC2565] IPP/1.0 : Encoding and Transport
  # [RFC2566] IPP/1.0 : Model and Semantics
  # [RFC2910] IPP/1.1 : Encoding and Transport
  # [RFC2911] IPP/1.1 : Model and Semantics
  # [RFC3510] IPP/1.1 : IPP URL Scheme
  # [PWG5100.1] "finishings" attribute values extension
  # [PWG5100.2] "output-bin" attribute extension
  # [PWG5100.12] IPP/2.x
  # [PWG5101.1] PWG Media Standardized Names 2.0 (MSN2)
  # [PWG5100.3] Production Printing Attributes - Set1 (media-col)
  # [PWG5100.9] Printer State Extensions v1.0
  # [PWG5107.2] PWG Command Set Format for IEEE 1284 Device ID v1.0
  # [RFC3380] IPP : Job and Printer Set Operations
  # [RFC3382] IPP : The 'collection' attribute syntax

  # Operations
  #0x0002 Print-Job [RFC2911]
  #0x0004 Validate-Job [RFC2911]
  #0x0005 Create-Job
  #0x0008 Cancel-Job [RFC2911]
  #0x0009 Get-Job-Attributes [RFC2911]
  #0x000A Get-Jobs [RFC2911]
  #0x000B Get-Printer-Attributes [RFC2911]
  
  def encode_request(
      self,
      out,
      version=(2, 0),
      operation_id=0,
      request_id=0,
      data='',
      ):
    # version-number
    out.write(struct.pack('bb', version))

    # operation-id (request) OR status-code (response)
    out.write(struct.pack('>h', operation_id))

    # request-id
    # client chooses, possibly unique
    out.write(struct.pack('>i', request_id))
    
    # attribute-group
    
    # end-of-attributes-tag 0x03
    out.write(0x03)
    
    # data
    out.write(data)


  def parse(self, data):
    print('version-number', struct.unpack('bb', data[0:2]))
    
    print('operation-id', struct.unpack('>h', data[2:4])[0])
    
    print('request-id', struct.unpack('>i', data[4:8])[0])
    
    more_tags = True
    i = 8
    while more_tags:
      more_tags, ii = self.parse_tag(data[i:])
      i += ii


  def parse_tag(self, data):
    tag = struct.unpack('>b', data[0:1])[0]

    # 0x00 - 0x0F "delimiter-tags"
    if (tag == 0x00):
      print('Reserved (0x00)')
    elif (tag == 0x01):
      print('operation-attributes')
      _, i = self.parse_tag(data[1:])
      return (True, 1 + i)
    elif (tag == 0x02):
      print('job-attributes')
      _, i = self.parse_tag(data[1:])
      return (True, 1 + i)
    elif (tag == 0x03):
      print('end-of-attributes')
      return (False, 1)
    elif (tag == 0x04):
      print('printer-attributes-tag')
      return (True, 1)
    elif (tag == 0x05):
      print('unsupported-attributes-tag')
      return (True, 1)
    elif (tag <= 0x0F):
      print('Reserved', tag)

    # 0x10 - 0xFF "value-tags"
    elif (tag == 0x10):
      print('Unsupported (0x10)')
    elif (tag == 0x11):
      print('Reserved for default')
    elif (tag == 0x12):
      print('Unknown (0x12)')
    elif (tag == 0x13):
      print('no-value')
    elif (tag <= 0x1F):
      print('Reserved for out-of-band')
    elif (tag == 0x20):
      print('Reserved (0x20)')
    elif (tag == 0x21):
      print('integer')
      i, value = self.parse_attribute(data[1:])
      print(struct.unpack('>i', value)[0])
      return (True, 1 + i)
    elif (tag == 0x22):
      print('boolean')
      i, value = self.parse_attribute(data[1:])
      print(struct.unpack('?', value)[0])
      return (True, 1+i)
    elif (tag == 0x23):
      print('enum')
      i, value = self.parse_attribute(data[1:])
      return (True, 1 + i)
    elif (tag <= 0x2F):
      print('Reserved for integer types')

    elif (tag == 0x30):
      print('octetString')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)
    elif (tag == 0x31):
      print('dateTime')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)
    elif (tag == 0x32):
      print('resolution')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)

    elif (tag == 0x34):
      print('begCollection')
      i, value = self.parse_attribute(data[1:])
      return (True, 1 + i)
    elif (tag == 0x35):
      print('textWithLanguage')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)
    elif (tag == 0x36):
      print('nameWithLanguage')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)
    elif (tag == 0x37):
      print('endCollection')
      i, value = self.parse_attribute(data[1:])
      return (True, 1 + i)

    elif (tag == 0x42):
      print('nameWithoutLanguage')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x44):
      print('keyword')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x45):
      print('uri')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x46):
      print('uriScheme')
      #i, value = self.parse_attribute(data[1:])
      return (True, i)
    elif (tag == 0x47):
      print('charset')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x48):
      print('natural-language')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x49):
      print('mimeMediaType')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    elif (tag == 0x4A):
      print('memberAttrName')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)


    elif (tag == 0x52):
      print('mimeMediaType')
      i, value = self.parse_attribute(data[1:])
      print(value)
      return (True, 1 + i)
    
    else:
      print('Undefined', tag)
      i, value = self.parse_attribute(data[1:])
      return (True, i)


  def parse_attribute(self, data):
    value = None
    name_length = struct.unpack('>h', data[0:2])[0]
    print('name_length', name_length)
    if (name_length > 0):
      print('name', data[2:2 + name_length])
    value_length = struct.unpack('>h', data[2 + name_length:4 + name_length])[0]
    print('value_length', value_length)
    if (value_length > 0):
      value = data[4 + name_length:4 + name_length + value_length]
    
    return (4 + name_length + value_length, value)

  '''
   An operation request or response is encoded as follows:
   -----------------------------------------------
   |                  version-number             |   2 bytes  - required
   -----------------------------------------------
   |               operation-id (request)        |
   |                      or                     |   2 bytes  - required
   |               status-code (response)        |
   -----------------------------------------------
   |                   request-id                |   4 bytes  - required
   -----------------------------------------------
   |                 attribute-group             |   n bytes - 0 or more
   -----------------------------------------------
   |              end-of-attributes-tag          |   1 byte   - required
   -----------------------------------------------
   |                     data                    |   q bytes  - optional
   -----------------------------------------------

   Each "attribute-group" field is encoded as follows:
   -----------------------------------------------
   |           begin-attribute-group-tag         |  1 byte
   ----------------------------------------------------------
   |                   attribute                 |  p bytes |- 0 or more
   ----------------------------------------------------------

   An "attribute" field is encoded as follows:
   -----------------------------------------------
   |          attribute-with-one-value           |  q bytes
   ----------------------------------------------------------
   |             additional-value                |  r bytes |- 0 or more
   ----------------------------------------------------------
   
   Each "attribute-with-one-value" field is encoded as follows:
   -----------------------------------------------
   |                   value-tag                 |   1 byte
   -----------------------------------------------
   |               name-length  (value is u)     |   2 bytes
   -----------------------------------------------
   |                     name                    |   u bytes
   -----------------------------------------------
   |              value-length  (value is v)     |   2 bytes
   -----------------------------------------------
   |                     value                   |   v bytes
   -----------------------------------------------
   
   Each "additional-value" field is encoded as follows:
   -----------------------------------------------
   |                   value-tag                 |   1 byte
   -----------------------------------------------
   |            name-length  (value is 0x0000)   |   2 bytes
   -----------------------------------------------
   |              value-length (value is w)      |   2 bytes
   -----------------------------------------------
   |                     value                   |   w bytes
   -----------------------------------------------
   
   From the standpoint of a parser that performs an action based on a
   "tag" value, the encoding consists of:
   -----------------------------------------------
   |                  version-number             |   2 bytes  - required
   -----------------------------------------------
   |               operation-id (request)        |
   |                      or                     |   2 bytes  - required
   |               status-code (response)        |
   -----------------------------------------------
   |                   request-id                |   4 bytes  - required
   -----------------------------------------------------------
   |        tag (delimiter-tag or value-tag)     |   1 byte  |
   -----------------------------------------------           |-0 or more
   |           empty or rest of attribute        |   x bytes |
   -----------------------------------------------------------
   |              end-of-attributes-tag          |   1 byte   - required
   -----------------------------------------------
   |                     data                    |   y bytes  - optional
   -----------------------------------------------
   '''



def get_job(url, job_id):
  printer = pkipplib.CUPS(url=url)
  
  request = printer.newRequest(pkipplib.IPP_GET_JOB_ATTRIBUTES)
  request.setVersion('2.0')

  request.operation['job-uri'] = (
      'uri', '{}/jobs?{}'.format(url, job_id))

  return printer.doRequest(request)


def get_attributes(url):
  printer = pkipplib.CUPS(url=url)

  request = printer.newRequest(pkipplib.IPP_GET_PRINTER_ATTRIBUTES)
  request.setVersion('2.0')

  request.operation['printer-uri'] = (
      'uri', printer.identifierToURI('ipp', 'print'))

  request.operation['requested-attributes'] = (
      'nameWithoutLanguage', 'printer-uri-supported')
  request.operation['requested-attributes'] = (
      'nameWithoutLanguage', 'printer-type')
  request.operation['requested-attributes'] = (
      'nameWithoutLanguage', 'member-uris')

  return printer.doRequest(request)


def send_job(url, data, job_name='MyJobName', user_name='MyName'):
  printer = pkipplib.CUPS(url=url)

  request = printer.newRequest(pkipplib.IPP_PRINT_JOB)
  #request = printer.newRequest(pkipplib.IPP_VALIDATE_JOB)
  request.setVersion('2.0')

  # -*- Operation attributes -*-
  
  # "attributes-charset"
  # "attributes-natural-language"

  # Target
  request.operation['printer-uri'] = (
      'uri', printer.identifierToURI('ipp', 'print'))

  # SHOULD be supplied by the client
  request.operation['requesting-user-name'] = (
      'nameWithoutLanguage', user_name)

  # The client OPTIONALLY supplies this attribute.
  request.job['job-name'] = ( # ???
      'nameWithoutLanguage', job_name)

  # "ipp-attribute-fidelity" (boolean)
  # The client OPTIONALLY supplies this attribute.
  # .. total fidelity to client supplied Job Template attributes and values is
  # required, else the Printer object MUST reject the Print-Job request.
  request.operation['ipp-attribute-fidelity'] = (
      'boolean', True)

  # "document-name" (name(MAX))
  # The client OPTIONALLY supplies this attribute.
  
  # "compression" (type3 keyword):
  # The client OPTIONALLY supplies this attribute.
  
  # "document-format" (mimeMediaType):
  # The client OPTIONALLY supplies this attribute.
  request.operation['document-format'] = [
    ('mimeMediaType', 'image/jpeg'), # 0
    ('mimeMediaType', 'image/urf'), # 1
    ('mimeMediaType', 'image/pwg-raster'), # 2
  ][2]

  # "document-natural-language" (naturalLanguage)
  # The client OPTIONALLY supplies this attribute.

  # "job-k-octets" (integer(0:MAX)):
  # The client OPTIONALLY supplies this attribute.

  # "job-impressions" (integer(0:MAX)):
  # The client OPTIONALLY supplies this attribute.

  # "job-media-sheets" (integer(0:MAX)):
  # The client OPTIONALLY supplies this attribute.


  # -*- Job attributes -*-

  '' ''
  request.job['print-quality'] = [ #
    #('enum', 3), # "Draft"
    ('enum', 4), # "Standard"
    ('enum', 5), # "High"
  ][1]
  '' ''

  request.job['sides'] = [ #
    ('keyword', 'one-sided'),
    ('keyword', 'two-sided-long-edge'),
    ('keyword', 'two-sided-short-edge'),
  ][2]
  
  # Only Printer Description?
  # MUST be "Dpi" ??
#  request.job['printer-resolution'] = [ #
#    ('resolution', '600dpi'),
#  ][0]

  # The client MUST NOT supply both the "media" and the "media-col" member
  # attribute.
  ''' '
  request.job['media'] = [ #
    ('keyword', 'oe_photo-l_3.5x5in'), # 0
    ('keyword', 'jpn_hagaki_100x148mm'),
    ('keyword', 'na_index-4x6_4x6in'),
    ('keyword', 'na_number-10_4.125x9.5in'),
    ('keyword', 'iso_dl_110x220mm'),
    ('keyword', 'na_5x7_5x7in'),
    ('keyword', 'iso_a5_148x210mm'),
    ('keyword', 'jis_b5_182x257mm'),
    ('keyword', 'na_govt-letter_8x10in'),
    ('keyword', 'iso_a4_210x297mm'), # 9
    ('keyword', 'na_letter_8.5x11in'),
    ('keyword', 'na_legal_8.5x14in'),
    ('keyword', 'custom_min_55x91mm'),
    ('keyword', 'custom_max_329x676mm'),
  ][9]
  ' '''

  # IPP [PWG5100.16]
  # REQUIRED "print-scaling" Job Template attribute.
  request.job['print-scaling'] = [
    ('keyword', 'none'), # 0
    ('keyword', 'fill'), # 1
    ('keyword', 'fit'), # 2
    ('keyword', 'auto-fit'), # 3
    ('keyword', 'auto'), # 4
  ][0]

  # ??

  '''
  job-creation-attributes-supported (1setOf keyword) =
    copies
    finishings
    sides #
    orientation-requested
    media #
    print-quality #
    printer-resolution #
    output-bin
    media-col
    print-color-mode
    ipp-attribute-fidelity
    job-name #
  '''

  '''
  media-col-supported (1setOf keyword) =
    media-top-margin
    media-left-margin
    media-right-margin
    media-bottom-margin
    media-size
    media-source
    media-type
  '''

  # media-*-margin
  # Each value is a non-negative integer in hundredths of millimeters or
  # 1/2540th of an inch and specifies a hardware margin supported by the Printer
  # [PWG5100.13]
  
  # [PWG5100.3] x-dimension, y-dimension
  # Indicates the size of the media in hundredths of a millimeter along the
  # bottom edge of the media.
  # This unit is equivalent to 1/2540th of an inch resolution.

  '' ''
  request.job['media-col'] = ('begCollection', bytes(
#      '\x02' # Job Attribute
#      '\x34' '\x00\x09' 'media-col' '\x00\x00'
          '\x4A' '\x00\x00' '\x00\x0A' 'media-size'
              '\x34' '\x00\x00' '\x00\x00' # 0x34 begCollection
                  '\x4A' '\x00\x00' '\x00\x0B' 'x-dimension' # 0x4A memberAttrName
                      '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 21000) + ''
                  '\x4A' '\x00\x00' '\x00\x0B' 'y-dimension'
                      '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 29700) + ''
              '\x37' '\x00\x00' '\x00\x00' # 0x37 endCollection
          '\x4A' '\x00\x00' '\x00\x10' 'media-top-margin'
              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 500) + '' # 0x21 int
#              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 0) + ''
          '\x4A' '\x00\x00' '\x00\x11' 'media-left-margin'
              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 340) + ''
#              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 0) + ''
          '\x4A' '\x00\x00' '\x00\x12' 'media-right-margin'
              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 340) + ''
#              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 0) + ''
          '\x4A' '\x00\x00' '\x00\x13' 'media-bottom-margin'
              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 500) + ''
#              '\x21' '\x00\x00' '\x00\x04' + struct.pack('>I', 0) + ''
#          '\x4A' '\x00\x00' '\x00\x0A' 'media-type'
#              '\x44' '\x00\x00' '\x00\x0C' + 'photographic'
      '\x37' '\x00\x00' '\x00\x00' # 0x37 endCollection
      ))
      #      '#\x00\x0Dprint-quality\x00\x04' + struct.pack('>I', 5) #'\x00\x00\x00\x05'
  '' ''

  '''
  ['media-top-margin'] = [
    ('integer', 0),
    ('integer', 500),
    ('integer', 800),
  ][0]
  
  request.job['media-col']['media-left-margin'] = [
    ('integer', 0),
    ('integer', 340),
    ('integer', 560),
    ('integer', 640),
  ][0],
  
  request.job['media-col']['media-right-margin'] = [
    ('integer', 0),
    ('integer', 340),
    ('integer', 560),
    ('integer', 630),
  ][0],

  request.job['media-col']['media-bottom-margin'] = [
    ('integer', 0),
    ('integer', 500),
    ('integer', 3740),
  ][0],
  
  '' '
  
  # IPP Printer Description Attributes
  request.operation['pwg-raster-document-resolution'] = [
    ('resolution', '600dpi'),
  ][0]
  
  request.operation['pwg-raster-document-type'] = [
    ('keyword', 'srgb_8'),
    ('keyword', 'sgray_8'),
  ][0]
  '' ' '''
  
  ''' '
  data = request.dump()
  data = data.split('media-col')[0] + 'media-col\x00\x00' + data.split('media-col')[1][2:]
  print(data.encode('string-escape'))
  ipp20 = IPP_TWO_ZERO()
  ipp20.parse(data)
  
  print()

  data = (
      '\x34' '\x00\x09' 'media-col' '\x00\x00'
        '\x4A' '\x00\x00' '\x00\x0B' 'media-color'
        '\x44' '\x00\x00' '\x00\x04' 'blue'
        '\x4A' '\x00\x00' '\x00\x0A' 'media-size'
        '\x34' '\x00\x00' '\x00\x00'
          '\x4A' '\x00\x00' '\x00\x0B' 'x-dimension'
          '\x21' '\x00\x00' '\x00\x04' '\x00\x00\x3B\x88'
          '\x4A' '\x00\x00' '\x00\x0B' 'y-dimension'
          '\x21' '\x00\x00' '\x00\x04' '\x00\x00\x27\xB0'
        '\x37' '\x00\x00' '\x00\x00'
      '\x37' '\x00\x00' '\x00\x00'
      )
      
  more_tags = True
  i = 0
  while more_tags and i< len(data):
    more_tags, ii = ipp20.parse_tag(data[i:])
    i += ii
  

  exit(0)
  ' '''

  request.data = data

  return printer.doRequest(request)


def get_status(response):
  try:
    if 'status-message' in response.operation:
      return response.operation['status-message'][0][1]
  except:
    return None


def get_job_state_reason(response):
  try:
    if 'job-state-reasons' in response.job:
      return response.job['job-state-reasons'][0][1]
  except:
    return None


def get_job_id(response):
  try:
    if 'job-id' in response.job:
      return response.job['job-id'][0][1]
  except:
    return None


if __name__ == '__main__':
  import sys
  data = open(sys.argv[1], 'rb').read()

  URL = 'http://192.168.2.165:631'
  # printer-uri-supported : [('uri', 'ipp://192.168.2.165/ipp/print')]

  #Job attributes :
  #job-state-reasons : [('keyword', 'job-printing')]
  #job-id : [('integer', 159)]
  #job-state : [('enum', 5)]
  #job-uri : [('uri', 'ipp://192.168.2.165/jobs?159')]

  #print(get_attributes(URL))
  #exit(0)

  response = send_job(URL, data)
  print(response)

  print(get_status(response))

  job_id = get_job_id(response)
  #job_id = 26

  if job_id:
    response = get_job(URL, job_id)
    
    print(response)
    
    print(get_job_state_reason(response))
