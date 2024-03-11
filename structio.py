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
        
    def pack_int(self, number, numbytes, endian=None, signed=False):
        return number.to_bytes(numbytes, self._get_endian(endian), signed=signed)
        
    def _get_format(self, numbytes, endian=None):
        if numbytes not in _float_formats:
            raise ValueError("float size '{}' not supported".format(numbytes))
            
        if endian not in _endians:
            raise ValueError("endian '{}' is not recognized".format(endian))
            
        return _endians[endian] + _float_formats[numbytes]
        
    def unpack_float(self, b, numbytes, endian=None):
        return struct.unpack(self._get_format(numbytes, self._get_endian(endian)), b)[0]
        
    def pack_float(self, number, numbytes, endian=None):
        return struct.pack(self._get_format(numbytes, self._get_endian(endian)), number)
        
    def unpack_str(self, b):
        return b.decode(self.encoding, errors=self.errors)
        
    def pack_str(self, string):
        return string.encode(self.encoding, errors=self.errors)
        
    def _get_cstr_len(self, b, start=0):
        end = b.find(b'\x00', start)
        
        if end == -1:
            raise ValueError('null termination not found')
            
        return end - start + 1
        
    def unpack_cstr(self, b, start=0):
        length = self._get_cstr_len(b, start)
        string = self.unpack_str(b[start:(start + length - 1)])
        return string, length
        
    def pack_cstr(self, string):
        return self.pack_str(string) + b'\x00'
        
    def _get_pstr_len(self, b, numbytes, endian=None, start=0):
        return numbytes + self.unpack_int(b[start:(start + numbytes)], endian)
        
    def unpack_pstr(self, b, numbytes, endian=None, start=0):
        length = self._get_pstr_len(b, numbytes, endian, start)
        string = self.unpack_str(b[(start + numbytes):(start + length)])
        return string, length
        
    def pack_pstr(self, string, numbytes, endian=None):
        b = self.pack_str(string)
        return self.pack_int(len(b), numbytes, endian) + b
        
    def _get_7bint_len(self, b, start=0):
        i = 0
        while b[start + i] > 127:
            i += 1
            
        return i + 1
        
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
            
    def is_eof(self):
        if self.read(1) == b'':
            return True
        else:
            self.seek(-1, 1)
            return False
            
    def copy(self):
        return StructIO(self.getvalue(), self.endian, self.encoding, self.errors)
        
    def clear(self):
        self.seek(0)
        self.truncate()
        
    def append(self, b):
        return self.overwrite(0, b)
        
    def overwrite(self, length, b):
        position = self.tell()
        self.seek(length, 1)
        buffer = self.read()
        self.seek(position)
        length = self.write(b)
        self.write(buffer)
        self.truncate()
        self.seek(position + length)
        return length
        
    def delete(self, length):
        start = self.tell()
        buf_length = len(self)
        
        if start + length > buf_length:
            length = buf_length - start
            
        self.overwrite(length , b'')
        return length
        
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
        
    def _pack_bool(self, boolean):
        if boolean:
            return b'\x01'
        else:
            return b'\x00'
            
    def write_bool(self, boolean):
        return self.write(self._pack_bool(boolean))
        
    def append_bool(self, boolean):
        return self.append(self._pack_bool(boolean))
        
    def read_bits(self):
        number = self.read_int(1)
        return [number >> i & 1 for i in range(8)]
        
    def _pack_bits(self, bits):
        return self._pack_int(sum(bits[i] << i for i in range(8)), 1)
        
    def write_bits(self, bits):
        return self.write(self._pack_bits(bits))
        
    def append_bits(self, bits):
        return self.append(self._pack_bits(bits))
        
    def read_int(self, numbytes, endian=None, signed=False):
        return int.from_bytes(self.read(numbytes), self._get_endian(endian), signed=signed)
        
    def _pack_int(self, number, numbytes, endian=None, signed=False):
        return number.to_bytes(numbytes, self._get_endian(endian), signed=signed)
        
    def write_int(self, number, numbytes, endian=None, signed=False):
        return self.write(self._pack_int(number, numbytes, endian, signed))
        
    def append_int(self, number, numbytes, endian=None, signed=False):
        return self.append(self._pack_int(number, numbytes, endian, signed))
        
    def _get_format(self, numbytes, endian=None):
        if numbytes not in _float_formats:
            raise ValueError("float size '{}' not supported".format(numbytes))
            
        if endian not in _endians:
            raise ValueError("endian '{}' is not recognized".format(endian))
            
        return _endians[endian] + _float_formats[numbytes]
        
    def read_float(self, numbytes, endian=None):
        return struct.unpack(self._get_format(numbytes, self._get_endian(endian)), self.read(numbytes))[0]
        
    def _pack_float(self, number, numbytes, endian=None):
        return struct.pack(self._get_format(numbytes, self._get_endian(endian)), number)
        
    def write_float(self, number, numbytes, endian=None):
        return self.write(self._pack_float(number, numbytes, endian))
        
    def append_float(self, number, numbytes, endian=None):
        return self.append(self._pack_float(number, numbytes, endian))
        
    def read_str(self, length):
        return self.read(length).decode(self.encoding, errors=self.errors)
        
    def _pack_str(self, string):
        return string.encode(self.encoding, errors=self.errors)
        
    def write_str(self, string):
        return self.write(self._pack_str(string))
        
    def append_str(self, string):
        return self.append(self._pack_str(string))
        
    def overwrite_str(self, string, length):
        return self.overwrite(length, self._pack_str(string))
        
    def _get_cstr_len(self):
        end = self.find(b'\x00')
        
        if end == -1:
            raise ValueError('null termination not found')
            
        return end - self.tell() + 1
        
    def read_cstr(self):
        string = self.read_str(self._get_cstr_len() - 1)
        self.seek(1, 1)
        return string
        
    def _pack_cstr(self, string):
        return self._pack_str(string) + b'\x00'
        
    def write_cstr(self, string):
        return self.write(self._pack_cstr(string))
        
    def append_cstr(self, string):
        return self.append(self._pack_cstr(string))
        
    def overwrite_cstr(self, string):
        return self.overwrite(self._get_cstr_len(), self._pack_cstr(string))
        
    def skip_cstr(self):
        return self.seek(self._get_cstr_len(), 1)
        
    def delete_cstr(self):
        return self.delete(self._get_cstr_len())
        
    def _get_pstr_len(self, numbytes, endian=None):
        length = self.read_int(numbytes, endian)
        self.seek(-numbytes, 1)
        return numbytes + length
        
    def read_pstr(self, numbytes, endian=None):
        return self.read_str(self.read_int(numbytes, endian))
        
    def _pack_pstr(self, string, numbytes, endian=None):
        b = self._pack_str(string)
        return self._pack_int(len(b), numbytes, endian) + b
        
    def write_pstr(self, string, numbytes, endian=None):
        return self.write(self._pack_pstr(string, numbytes, endian))
        
    def append_pstr(self, string, numbytes, endian=None):
        return self.append(self._pack_pstr(string, numbytes, endian))
        
    def overwrite_pstr(self, string, numbytes, endian=None):
        return self.overwrite(self._get_pstr_len(numbytes, endian), self._pack_pstr(string, numbytes, endian))
        
    def skip_pstr(self, numbytes, endian=None):
        return self.seek(self._get_pstr_len(numbytes, endian), 1)
        
    def delete_pstr(self, numbytes, endian=None):
        return self.delete(self._get_pstr_len(numbytes, endian))
        
    def _get_7bint_len(self):
        i = 0
        while self.read_int(1) > 127:
            i += 1
            
        self.seek(- i - 1, 1)
        return i + 1
        
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
        
    def _pack_7bint(self, number):
        b = b''
        
        while number > 127:
            b += self._pack_int(number & 0b01111111 | 0b10000000, 1)
            number >>= 7
            
        b += self._pack_int(number, 1)
        return b
        
    def write_7bint(self, number):
        return self.write(self._pack_7bint(number))
        
    def append_7bint(self, number):
        return self.append(self._pack_7bint(number))
        
    def overwrite_7bint(self, number):
        return self.overwrite(self._get_7bint_len(), self._pack_7bint(number))
        
    def skip_7bint(self):
        return self.seek(self._get_7bint_len(), 1)
        
    def delete_7bint(self):
        return self.delete(self._get_7bint_len())