import os
import sys
import struct
import serial

def send(port, data):
  port.write(struct.pack('<H', len(data) + 2) + struct.pack('<H', 0x1234))
  port.write(data)

  size = struct.unpack('<H', port.read(2))[0]
  result = port.read(size)

  if(struct.unpack('<H', result[0:2])[0] != 0x1234):
    sys.exit('send error')

  return result[2:]

def upload(port, path, data):
  size = len(data)

  buffer = bytearray()

  buffer.append(0x01)
  buffer.append(0x92)
  buffer.extend(struct.pack('<I', size))
  buffer.extend(path.encode('utf-8'))
  buffer.append(0x00)

  result = send(port, buffer)

  if(result[0] == 0x05 or result[1] != 0x92 or result[2] == 0x0A):
    sys.exit('upload error')

  buffer = bytearray()

  buffer.append(0x01)
  buffer.append(0x93)
  buffer.append(result[3])

  offset = 0

  while(offset < size):
    del buffer[3:]

    if(offset + 1016 < size):
      buffer.extend(data[offset:offset + 1016])
      offset += 1016
    else:
      buffer.extend(data[offset:])
      offset = size

    result = send(port, buffer)

    if(result[0] == 0x05 or result[1] != 0x93 or result[2] == 0x0A):
      sys.exit('upload error')

def start(port, path):
  size = len(path) + 25

  buffer = bytearray()

  buffer.extend(struct.pack('<H', size))
  buffer.extend(bytes.fromhex('3412800020c00882010084'))
  buffer.extend(path.encode('utf-8'))
  buffer.extend(bytes.fromhex('00c100c10403820100c100c10400'))

  port.write(buffer)

def wrap(path):
  buffer = bytearray()

  buffer.extend(b'LEGO')
  buffer.extend(struct.pack('<I', len(path) + 40))
  buffer.extend(bytes.fromhex('6d000100000000001c00000000000000080000006080'))
  buffer.extend(path.encode('ascii'))
  buffer.extend(bytes.fromhex('00448582e8034086400a'))
  
  return buffer

name = sys.argv[1]

path = '../prjs/%s/%s' % (name, name)

command = 'arm-none-linux-gnueabi-gcc %s.c -o %s -lm -lpthread' % (name, name)
if os.system(command):
  sys.exit('compilation error')

port = serial.Serial('/dev/rfcomm0', 115200)

file = open(name, 'rb')
upload(port, path, file.read())
upload(port, path + '.rbf', wrap(path))
start(port, path)
