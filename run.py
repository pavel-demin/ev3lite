import os
import sys
import struct
import serial

def send(port, code, data):
  buffer = bytearray()
  buffer.extend(struct.pack('<H', len(data) + 4))
  buffer.append(0x34)
  buffer.append(0x12)
  buffer.append(0x01)
  buffer.append(code)

  port.write(buffer)
  port.write(data)

  length = struct.unpack('<H', port.read(2))[0]
  result = port.read(length)

  if(result[0] != 0x34 or result[1] != 0x12 or result[2] == 0x05 or result[3] != code or result[4] == 0x0a):
    sys.exit('send error')

  return result[5]

def upload(port, path, data):
  length = len(data)

  buffer = bytearray()
  buffer.extend(struct.pack('<I', length))
  buffer.extend(path.encode('ascii'))
  buffer.append(0x00)

  result = send(port, 0x92, buffer)

  offset = 0

  while(offset < length):
    buffer = bytearray()
    buffer.append(result)

    if(offset + 1016 < length):
      buffer.extend(data[offset:offset + 1016])
      offset += 1016
    else:
      buffer.extend(data[offset:])
      offset = length

    send(port, 0x93, buffer)

def start(port, path):
  buffer = bytearray()
  buffer.extend(struct.pack('<H', len(path) + 25))
  buffer.extend(bytes.fromhex('3412800020c00882010084'))
  buffer.extend(path.encode('ascii'))
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
start(port, path + '.rbf')
