from os import system
from sys import argv, exit
from struct import pack
from socket import socket, AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM, MSG_WAITALL

def send(sock, code, data):
    buffer = bytearray()
    buffer.extend(pack('<H', len(data) + 4))
    buffer.extend(bytes.fromhex('341201'))
    buffer.append(code)

    sock.send(buffer)
    sock.send(data)

    result = sock.recv(8, MSG_WAITALL)

    if (result[0] != 0x06 or result[1] != 0x00 or
        result[2] != 0x34 or result[3] != 0x12 or
        result[4] == 0x05 or result[5] != code or
        result[6] == 0x0a):
        exit('send error')

    return result[7]

def upload(sock, path, data):
    length = len(data)

    buffer = bytearray()
    buffer.extend(pack('<I', length))
    buffer.extend(path.encode('ascii'))
    buffer.append(0x00)

    handle = send(sock, 0x92, buffer)

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

        send(sock, 0x93, buffer)

def start(sock, path):
    buffer = bytearray()
    buffer.extend(pack('<H', len(path) + 17))
    buffer.extend(bytes.fromhex('3412800020c0080184'))
    buffer.extend(path.encode('ascii'))
    buffer.extend(bytes.fromhex('0040440301404400'))
    sock.send(buffer)

def wrap(path):
    buffer = bytearray()
    buffer.extend(b'LEGO')
    buffer.extend(pack('<I', len(path) + 42))
    buffer.extend(bytes.fromhex('6d000100000000001c00000000000000040000006084'))
    buffer.extend(path.encode('ascii'))
    buffer.extend(bytes.fromhex('00408413000000840083040a'))
    return buffer

addr = argv[1]
name = argv[2]

path = '../prjs/%s/%s' % (name, name)

command = 'arm-none-linux-gnueabi-gcc %s.c -o %s -lm -lpthread' % (name, name)
if system(command):
    exit('gcc error')

command = 'arm-none-linux-gnueabi-strip %s' % name
if system(command):
    exit('strip error')

sock = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)
sock.connect((addr, 1))

file = open(name, 'rb')
upload(sock, path, file.read())
upload(sock, path + '.rbf', wrap(path))
start(sock, path + '.rbf')

sock.close()
