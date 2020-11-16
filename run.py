import os
import sys
import struct
import serial

def send(port, code, data):
    buffer = bytearray()
    buffer.extend(struct.pack('<H', len(data) + 4))
    buffer.extend(bytes.fromhex('341201'))
    buffer.append(code)

    port.write(buffer)
    port.write(data)

    result = port.read(8)

    if (result[0] != 0x06 or result[1] != 0x00 or
        result[2] != 0x34 or result[3] != 0x12 or
        result[4] == 0x05 or result[5] != code or
        result[6] == 0x0a):
        sys.exit('send error')

    return result[7]

def upload(port, path, data):
    length = len(data)

    buffer = bytearray()
    buffer.extend(struct.pack('<I', length))
    buffer.extend(path.encode('ascii'))
    buffer.append(0x00)

    handle = send(port, 0x92, buffer)

    offset = 0

    while offset < length:
        buffer = bytearray()
        buffer.append(handle)

        if offset + 1017 < length:
            buffer.extend(data[offset:offset + 1017])
            offset += 1017
        else:
            buffer.extend(data[offset:])
            offset = length

        send(port, 0x93, buffer)

def start(port, path):
    buffer = bytearray()
    buffer.extend(struct.pack('<H', len(path) + 17))
    buffer.extend(bytes.fromhex('3412800020c0080184'))
    buffer.extend(path.encode('ascii'))
    buffer.extend(bytes.fromhex('0040440301404400'))
    port.write(buffer)

def wrap(path):
    buffer = bytearray()
    buffer.extend(b'LEGO')
    buffer.extend(struct.pack('<I', len(path) + 42))
    buffer.extend(bytes.fromhex('6d000100000000001c00000000000000040000006084'))
    buffer.extend(path.encode('ascii'))
    buffer.extend(bytes.fromhex('00408413000000840083040a'))
    return buffer

name = sys.argv[1]

path = '../prjs/%s/%s' % (name, name)

command = 'arm-none-linux-gnueabi-gcc %s.c -o %s -lm -lpthread' % (name, name)
if os.system(command):
    sys.exit('gcc error')

command = 'arm-none-linux-gnueabi-strip %s' % name
if os.system(command):
    sys.exit('strip error')

port = serial.Serial('/dev/rfcomm0', 115200)

file = open(name, 'rb')
upload(port, path, file.read())
upload(port, path + '.rbf', wrap(path))
start(port, path + '.rbf')
