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
        if len(b) == 1:
            return b != b'\x00'
        else:
            raise ValueError('expected bytes object of length 1')
            
    def pack_bool(self, boolean):
        if boolean:
            return b'\x01'
        else:
            return b'\x00'
            
    def unpack_bits(self, b):
        if len(b) == 1:
            number = self.unpack_int(b) 
            return [number >> i & 1 for i in range(8)]
        else:
            raise ValueError('expected bytes object of length 1')
            
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
        
    def unpack_cstr(self, b, start=0):
        end = b.find(b'\x00', start)
        
        if end == -1:
            raise ValueError('null termination not found')
            
        return self.unpack_str(b[start:end])
        
    def pack_cstr(self, string):
        return self.pack_str(string) + b'\x00'
        
    def unpack_pstr(self, b, numbytes, endian=None, start=0):
        int_end = start + numbytes
        length = self.unpack_int(b[start:int_end], endian)
        return self.unpack_str(b[int_end:(int_end + length)])
        
    def pack_pstr(self, string, numbytes, endian=None):
        return self.pack_int(len(string), numbytes, endian) + self.pack_str(string)
        
    def unpack_7bint(self, b, start=0):
        number = 0
        i = 0
        
        byte = b[start + i]
        while byte & 0b10000000 != 0:
            number |= (byte & 0b01111111) << (7 * i)
            i += 1
            
            byte = b[start + i]
            
        number |= byte << (7 * i)
        
        return number
        
    def pack_7bint(self, number):
        b = bytearray()
        
        while number > 127:
            b += self.pack_int(number & 0b01111111 | 0b10000000, 1) 
            number >>= 7
            
        b += self.pack_int(number, 1)
        return b
        
class StructIO(io.BytesIO):
    def __init__(self, b=b'', endian='little', encoding='utf-8', errors='ignore'):
        super().__init__(b)
        self._struct = Struct(endian, encoding, errors)
        
    @property
    def endian(self):
        return self._struct.endian
        
    @endian.setter
    def endian(self, value):
        self._struct.endian = value
        
    @property
    def encoding(self):
        return self._struct.encoding
        
    @encoding.setter
    def encoding(self, value):
        self._struct.encoding = value
        
    @property
    def errors(self):
        return self._struct.errors
        
    @errors.setter
    def errors(self, value):
        self._struct.errors = value
        
    def __len__(self):
        position = self.tell()
        self.seek(0, 2)
        length = self.tell()
        self.seek(position)
        return length
        
    def __eq__(self, other):
        return self.getvalue() == other.getvalue()
        
    def is_eof(self):
        if self.read(1) == b'':
            return True
        else:
            self.seek(-1, 1)
            return False
            
    def copy(self):
        return StructIO(self.getvalue(), self._struct.endian, self._struct.encoding, self._struct.errors)
        
    def read_all(self):
        self.seek(0)
        return self.getvalue()
        
    def write_all(self, buffer):
        self.seek(0)
        length = self.write(buffer)
        self.truncate()
        self.seek(0)
        return length
        
    def clear(self):
        self.seek(0)
        self.truncate()
        
    def append(self, b):
        current_position = self.tell()
        return self.overwrite(current_position, current_position, b)
        
    def overwrite(self, start, end, b):
        self.seek(end)
        buffer = self.read()
        self.seek(start)
        length = self.write(b)
        self.write(buffer)
        self.truncate()
        self.seek(start + length)
        return length
        
    def read_bool(self):
        return self._struct.unpack_bool(self.read(1))
        
    def write_bool(self, boolean):
        return self.write(self._struct.pack_bool(boolean))
        
    def append_bool(self, boolean):
        return self.append(self._struct.pack_bool(boolean))
        
    def read_bits(self):
        return self._struct.unpack_bits(self.read(1))
        
    def write_bits(self, bits):
        return self.write(self._struct.pack_bits(bits))
        
    def append_bits(self, bits):
        return self.append(self._struct.pack_bits(bits))
        
    def read_int(self, numbytes, endian=None, signed=False):
        return self._struct.unpack_int(self.read(numbytes), endian, signed)
        
    def write_int(self, number, numbytes, endian=None, signed=False):
        return self.write(self._struct.pack_int(number, numbytes, endian, signed))
        
    def append_int(self, number, numbytes, endian=None, signed=False):
        return self.append(self._struct.pack_int(number, numbytes, endian, signed))
        
    def read_float(self, numbytes, endian=None):
        return self._struct.unpack_float(self.read(numbytes), numbytes, endian)
        
    def write_float(self, number, numbytes, endian=None):
        return self.write(self._struct.pack_float(number, numbytes, endian))
        
    def append_float(self, number, numbytes, endian=None):
        return self.append(self._struct.pack_float(number, numbytes, endian))
        
    def read_str(self, length):
        return self._struct.unpack_str(self.read(length))
        
    def write_str(self, string):
        return self.write(self._struct.pack_str(string))
        
    def append_str(self, string):
        return self.append(self._struct.pack_str(string))
        
    def overwrite_str(self, string, length):
        start = self.tell()
        return self.overwrite(start, start + length, self._struct.pack_str(string))
        
    def read_cstr(self):
        end = self.find(b'\x00')
        
        if end == -1:
            raise ValueError('null termination not found')
            
        start = self.tell()
        string = self._struct.unpack_str(self.read(end - start))
        self.seek(1, 1)
        return string
        
    def write_cstr(self, string):
        return self.write(self._struct.pack_cstr(string))
        
    def append_cstr(self, string):
        return self.append(self._struct.pack_cstr(string))
        
    def overwrite_cstr(self, string, encoding=None, errors=None):
        end = self.find(b'\x00')
        
        if end == -1:
            raise ValueError('null termination not found')
            
        start = self.tell()
        return self.overwrite(start, end + 1, self._struct.pack_cstr(string))
        
    def read_pstr(self, numbytes, endian=None):
        return self.read_str(self.read_int(numbytes, endian))
        
    def write_pstr(self, string, numbytes, endian=None):
        return self.write_int(len(string), numbytes, endian) + self.write_str(string)
        
    def append_pstr(self, string, numbytes, endian=None):
        return self.append(self._struct.pack_pstr(string, numbytes, endian))
        
    def overwrite_pstr(self, string, numbytes, endian=None):
        start = self.tell()
        length = self.read_int(numbytes, endian)
        return self.overwrite(start, start + numbytes + length, self._struct.pack_pstr(string, numbytes, endian))
        
    def read_7bint(self):
        number = 0
        i = 0
        
        byte = self.read_int(1)
        while byte & 0b10000000 != 0:
            number |= (byte & 0b01111111) << (7 * i)
            i += 1
            
            byte = self.read_int(1)
            
        number |= byte << (7 * i)
        
        return number
        
    def write_7bint(self, number):
        return self.write(self._struct.pack_7bint(number))
        
    def append_7bint(self, number):
        return self.append(self._struct.pack_7bint(number))
        
    def overwrite_7bint(self, number):
        start = self.tell()
        
        while self.read_int(1) & 0b10000000 != 0:
            pass
            
        end = self.tell()
        
        return self.overwrite(start, end, self._struct.pack_7bint(number))
        
    def delete(self, length):
        current_position = self.tell()
        
        if current_position - length < 0:
            length = current_position
            
        start = current_position - length
        self.overwrite(start, current_position, b'')
        
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
        end = self.find(bytes_sequence, n)
        
        if end == -1:
            raise ValueError('{} not found'.format(bytes_sequence))
            
        return end
