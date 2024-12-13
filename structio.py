import io
import struct

_endians = {'big': '>', 'little': '<'}
_float_formats = {2: 'e', 4: 'f', 8: 'd'}

class Struct:
    def __init__(self, endian='little', encoding='utf-8', errors='ignore'):
        self.endian = endian
        self.encoding = encoding
        self.errors = errors

    def _get_endian(self, endian):
        if endian is None:
            return self.endian
        else:
            return endian

    def unpack_bool(self, b):
        if isinstance(b, int):
            return b != 0
        elif len(b) == 1:
            return b != b'\x00'
        else:
            raise ValueError('expected int or bytes object of length 1')

    def pack_bool(self, boolean):
        if boolean:
            return b'\x01'
        else:
            return b'\x00'

    def unpack_bits(self, b):
        if isinstance(b, int):
            number = b
        elif len(b) == 1:
            number = self.unpack_int(b)
        else:
            raise ValueError('expected int or bytes object of length 1')

        return [number >> i & 1 for i in range(8)]

    def pack_bits(self, bits):
        return self.pack_int(sum(bits[i] << i for i in range(8)), 1)

    def unpack_int(self, b, endian=None, signed=False):
        return int.from_bytes(b, self._get_endian(endian), signed=signed)

    def pack_int(self, number, size, endian=None, signed=False):
        return number.to_bytes(size, self._get_endian(endian), signed=signed)

    def _get_format(self, size, endian=None):
        if size not in _float_formats:
            raise ValueError("float size '{}' not supported".format(size))

        if endian not in _endians:
            raise ValueError("endian '{}' is not recognized".format(endian))

        return _endians[endian] + _float_formats[size]

    def unpack_float(self, b, size, endian=None):
        return struct.unpack(self._get_format(size, self._get_endian(endian)), b)[0]

    def pack_float(self, number, size, endian=None):
        return struct.pack(self._get_format(size, self._get_endian(endian)), number)

    def unpack_str(self, b):
        return b.decode(self.encoding, errors=self.errors)

    def pack_str(self, string):
        return string.encode(self.encoding, errors=self.errors)

    def unpack_cstr(self, b, start=0):
        end = b.find(b'\x00', start)

        if end == -1:
            raise ValueError('null termination not found')

        string = self.unpack_str(b[start:end])
        return string, end - start + 1

    def pack_cstr(self, string):
        return self.pack_str(string) + b'\x00'

    def unpack_pstr(self, b, size, endian=None, start=0):
        length = self.unpack_int(b[start:start + size], endian)
        string = self.unpack_str(b[start + size:start + size + length])
        return string, size + length

    def pack_pstr(self, string, size, endian=None):
        b = self.pack_str(string)
        return self.pack_int(len(b), size, endian) + b

    def unpack_7bint(self, b, start=0):
        number = 0
        i = 0

        byte = b[start]
        while byte > 127:
            number += (byte & 0b01111111) << (7 * i)
            i += 1

            byte = b[start + i]

        number += byte << (7 * i)
        length = i + 1

        return number, length

    def pack_7bint(self, number):
        b = b''

        while number > 127:
            b += self.pack_int(number & 0b01111111 | 0b10000000, 1)
            number >>= 7

        b += self.pack_int(number, 1)
        return b

class StructIO(io.BytesIO):
    def __init__(self, b=b'', endian='little', encoding='utf-8', errors='ignore'):
        super().__init__(b)
        self.endian = endian
        self.encoding = encoding
        self.errors = errors

    @property
    def buffer(self):
        return self.getvalue()

    @buffer.setter
    def buffer(self, b):
        position = self.tell()
        self.seek(0)
        self.write(b)
        self.truncate()

        if position < len(b):
            self.seek(position)

    def __len__(self):
        position = self.tell()
        self.seek(0, 2)
        length = self.tell()
        self.seek(position)
        return length

    def __eq__(self, other):
        return self.getvalue() == other.getvalue()

    def _get_endian(self, endian):
        if endian is None:
            return self.endian
        else:
            return endian

    def copy(self):
        return StructIO(self.getvalue(), self.endian, self.encoding, self.errors)

    def clear(self):
        self.seek(0)
        self.truncate()

    def find(self, bytes_sequence, n=1):
        start = self.tell()
        content = self.getvalue()
        location = content.find(bytes_sequence, start)

        for i in range(1, n):
            location = content.find(bytes_sequence, location + 1)

            if location == -1:
                break

        return location

    def index(self, bytes_sequence, n=1):
        location = self.find(bytes_sequence, n)

        if location == -1:
            raise ValueError('{} not found'.format(bytes_sequence))

        return location

    def read_bool(self):
        return self.read(1) != b'\x00'

    def write_bool(self, boolean):
        if boolean:
            return self.write(b'\x01')
        else:
            return self.write(b'\x00')

    def read_bits(self):
        number = self.read_int(1)
        return [number >> i & 1 for i in range(8)]

    def write_bits(self, bits):
        return self.write_int(sum(bits[i] << i for i in range(8)), 1)

    def read_int(self, size, endian=None, signed=False):
        return int.from_bytes(self.read(size), self._get_endian(endian), signed=signed)

    def write_int(self, number, size, endian=None, signed=False):
        return self.write(number.to_bytes(size, self._get_endian(endian), signed=signed))

    def _get_format(self, size, endian=None):
        if size not in _float_formats:
            raise ValueError("float size '{}' not supported".format(size))

        if endian not in _endians:
            raise ValueError("endian '{}' is not recognized".format(endian))

        return _endians[endian] + _float_formats[size]

    def read_float(self, size, endian=None):
        return struct.unpack(self._get_format(size, self._get_endian(endian)), self.read(size))[0]

    def write_float(self, number, size, endian=None):
        return self.write(struct.pack(self._get_format(size, self._get_endian(endian)), number))

    def read_str(self, length):
        return self.read(length).decode(self.encoding, errors=self.errors)

    def write_str(self, string):
        return self.write(string.encode(self.encoding, errors=self.errors))

    def read_cstr(self):
        start = self.tell()
        end = self.find(b'\x00')

        if end == -1:
            raise ValueError('null termination not found')

        string = self.read_str(end - start)
        self.seek(1, 1)
        return string

    def write_cstr(self, string):
        return self.write_str(string) + self.write(b'\x00')

    def skip_cstr(self):
        end = self.find(b'\x00')

        if end == -1:
            raise ValueError('null termination not found')

        return self.seek(end + 1)

    def read_pstr(self, size, endian=None):
        return self.read_str(self.read_int(size, endian))

    def write_pstr(self, string, size, endian=None):
        b = string.encode(self.encoding, errors=self.errors)
        return self.write_int(len(b), size, endian) + self.write(b)

    def skip_pstr(self, size, endian=None):
        return self.seek(self.read_int(size, endian), 1)

    def read_7bint(self):
        number = 0
        i = 0

        byte = self.read_int(1)
        while byte > 127:
            number += (byte & 0b01111111) << (7 * i)
            i += 1

            byte = self.read_int(1)

        number += byte << (7 * i)

        return number

    def write_7bint(self, number):
        length = 0

        while number > 127:
            length += self.write_int(number & 0b01111111 | 0b10000000, 1)
            number >>= 7

        length += self.write_int(number, 1)

        return length

    def skip_7bint(self):
        while self.read_int(1) > 127:
            pass

        return self.tell()