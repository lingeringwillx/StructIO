import unittest
from structio import *

class ExtendedStruct(Struct):
    def _get_7bstr_len(self, b, start=0):
        str_len, int_len = self.unpack_7bint(b, start)
        return int_len + str_len
        
    def unpack_7bstr(self, b, start=0):
        str_len, int_len = self.unpack_7bint(b, start)
        string = self.unpack_str(b[(start + int_len):(start + int_len + str_len)])
        return string, int_len + str_len
        
    def pack_7bstr(self, string):
        b = self.pack_str(string)
        return self.pack_7bint(len(b)) + b
        
class ExtendedStructIO(StructIO):
    def __init__(self, b=b'', endian='little', struct=ExtendedStruct):
        super().__init__(b, endian, struct=struct)
        
    def read_7bstr(self):
        return self._read(self._struct.unpack_7bstr, ())
        
    def write_7bstr(self, string):
        return self.write(self._struct.pack_7bstr(string))
        
    def append_7bstr(self, string):
        return self.append(self._struct.pack_7bstr(string))
        
    def overwrite_7bstr(self, string):
        return self._overwrite(self._struct._get_7bstr_len, (), self._struct.pack_7bstr, (string,))
        
    def skip_7bstr(self, n=1):
        return self._skip(self._struct._get_7bstr_len, ())
        
    def delete_7bstr(self):
        return self._delete(self._struct._get_7bstr_len, ())
        
class PackUnpackFunctionsTest(unittest.TestCase):
    def testbool(self):
        struct = Struct()
        self.assertEqual(True, struct.unpack_bool(struct.pack_bool(True))) #True byte
        self.assertEqual(True, struct.unpack_bool(b'\x02')) #True not one byte
        self.assertEqual(False, struct.unpack_bool(struct.pack_bool(False))) #False byte
        self.assertEqual(True, struct.unpack_bool(1)) #True int
        self.assertEqual(True, struct.unpack_bool(2)) #True not one int
        self.assertEqual(False, struct.unpack_bool(0)) #False int
        
    def testbits(self):
        struct = Struct()
        self.assertEqual([0,1,0,1,0,1,0,1], struct.unpack_bits(struct.pack_bits([0,1,0,1,0,1,0,1]))) #byte
        self.assertEqual([0,1,0,1,0,1,0,1], struct.unpack_bits(170)) #int
        
    def testint(self):
        struct = Struct('big')
        self.assertEqual(10, struct.unpack_int(struct.pack_int(10, 2))) #default endian unsigned
        self.assertEqual(10, struct.unpack_int(struct.pack_int(10, 2, 'little'), 'little')) #little endian unsigned
        self.assertEqual(10, struct.unpack_int(struct.pack_int(10, 2, 'big'), 'big'))#big endian unsigned
        
        self.assertEqual(-10, struct.unpack_int(struct.pack_int(-10, 2, signed=True), signed=True)) #default endian signed
        self.assertEqual(-10, struct.unpack_int(struct.pack_int(-10, 2, 'little', signed=True), 'little', signed=True)) #little endian signed
        self.assertEqual(-10, struct.unpack_int(struct.pack_int(-10, 2, 'big', signed=True), 'big', signed=True)) #big endian signed
        
    def testfloat(self):
        struct = Struct('big')
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 2), 2), 2)) #half defualt endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 4), 4), 2)) #single default endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 8), 8), 2)) #double default endian
        
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 2, 'little'), 2, 'little'), 2)) #half little endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 4, 'big'), 4, 'big'), 2)) #single big endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 8, 'little'), 8,'little'), 2)) #double little endian
        
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 2, 'big'), 2, 'big'), 2)) #single big endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 4, 'little'), 4, 'little'), 2)) #double little endian
        self.assertEqual(3.14, round(struct.unpack_float(struct.pack_float(3.14, 8, 'big'), 8, 'big'), 2)) #double big endian
        
    def teststr(self):
        struct = Struct()
        self.assertEqual('Unit Test', struct.unpack_str(struct.pack_str('Unit Test')))
        
    def testcstr(self):
        struct = Struct()
        self.assertEqual('Unit Test', struct.unpack_cstr(struct.pack_cstr('Unit Test'))[0])
        self.assertEqual('Test', struct.unpack_cstr(b'Unit\x00Test\x00', 5)[0])
        
    def testpstr(self):
        struct = Struct('big')
        self.assertEqual('Unit Test', struct.unpack_pstr(struct.pack_pstr('Unit Test', 2), 2)[0]) #default endian
        self.assertEqual('Unit Test', struct.unpack_pstr(struct.pack_pstr('Unit Test', 2, 'little'), 2, 'little')[0]) #little endian
        self.assertEqual('Unit Test', struct.unpack_pstr(struct.pack_pstr('Unit Test', 2, 'big'), 2, 'big')[0]) #big endian
        
        self.assertEqual('Test', struct.unpack_pstr(b'\x04Unit\x04Test', 1, 'little', 5)[0])
        
    def test7bint(self):
        struct = Struct()
        self.assertEqual(128, struct.unpack_7bint(struct.pack_7bint(128))[0])
        self.assertEqual(128, struct.unpack_7bint(b'\x00' + struct.pack_7bint(128), start=1)[0])
        
class GenericStreamMethodsTest(unittest.TestCase):
    def testgettersetter(self):
        stream = StructIO(b'', 'little', 'utf-8', 'errors')
        stream.endian = 'big'
        self.assertEqual(stream.endian, stream._struct.endian)
        
        stream.encoding = 'ascii'
        self.assertEqual(stream.encoding, stream._struct.encoding)
        
        stream.errors = 'strict'
        self.assertEqual(stream.errors, stream._struct.errors)
        
    def testlen(self):
        stream = StructIO(b'Unit Test')
        stream.seek(5)
        self.assertEqual(9, len(stream))
        self.assertEqual(5, stream.tell()) #should be unchanged
        
    def testeq(self):
        stream1 = StructIO(b'Test')
        stream2 = StructIO(b'Test')
        stream3 = StructIO(b' Test')
        stream2.seek(2)
        self.assertEqual(stream1, stream2)
        stream3.seek(1)
        self.assertNotEqual(stream1, stream3)
        
    def testclear(self):
        stream = StructIO(b'Unit Test')
        stream.seek(5)
        stream.clear()
        self.assertEqual(0, stream.tell())
        self.assertEqual(b'', stream.read())
        
    def testiseof(self):
        stream = StructIO(b'Unit Test')
        self.assertFalse(stream.is_eof())
        self.assertEqual(0, stream.tell())
        stream.seek(0, 2)
        self.assertTrue(stream.is_eof())
        
    def testcopy(self):
        stream = StructIO(b'Unit Test')
        stream2 = stream.copy()
        stream.seek(0)
        self.assertEqual(0, stream2.tell())
        self.assertEqual(stream.read(), stream2.read())
        
    def testappend(self):
        stream = StructIO()
        stream.write(b'Test')
        stream.seek(0)
        stream.append(b'Unit ')
        stream.seek(0)
        self.assertEqual(b'Unit Test', stream.read())
    
    def testoverwrite(self):
        stream = StructIO()
        stream.write(b'Unit Test')
        stream.overwrite(0, 4, b'New')
        stream.seek(0)
        self.assertEqual(b'New Test', stream.read())
        
    def testreadall(self):
        stream = StructIO()
        stream.write(b'Unit Test')
        self.assertEqual(b'Unit Test', stream.read_all())
        self.assertEqual(0, stream.tell()) #should be back to start
        
    def testwriteall(self):
        stream = StructIO(b'Unit Test')
        stream.seek(0, 2)
        stream.write_all(b'New')
        self.assertEqual(0, stream.tell())
        self.assertEqual(b'New', stream.read())
        
    def testdelete(self):
        stream = StructIO(b'Unit Test')
        stream.seek(4)
        stream.delete(5)
        stream.seek(0)
        self.assertEqual(b'Unit', stream.read())
        
        stream = StructIO(b'Unit Test')
        stream.delete(5)
        self.assertEqual(b'Test', stream.read())
        
    def testfind(self):
        stream = StructIO(b'Unit Test Unit Test')
        self.assertEqual(5, stream.find(b'Test')) #first instance
        self.assertEqual(15, stream.find(b'Test', 2)) #second
        
    def testindex(self):
        stream = StructIO(b'Unit Test Unit Test')
        self.assertEqual(5, stream.index(b'Test')) #first instance
        self.assertEqual(15, stream.index(b'Test', 2)) #second
        self.assertRaises(ValueError, lambda: stream.index(b'Test', 3))
        
class WriteReadMethodsTest(unittest.TestCase):
    def testbool(self):
        stream = StructIO()
        stream.write_bool(True)
        stream.seek(0)
        self.assertEqual(True, stream.read_bool()) #True
        
        stream = StructIO()
        stream.write_bool(False)
        stream.seek(0)
        self.assertEqual(False, stream.read_bool()) #False
        
    def testbits(self):
        stream = StructIO()
        stream.write_bits([0,1,0,1,0,1,0,1])
        stream.seek(0)
        self.assertEqual([0,1,0,1,0,1,0,1], stream.read_bits())
        
    def testint(self):
        stream = StructIO(endian='little')
        stream.write_int(10, 2)
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2)) #default endian unsigned
        
        stream = StructIO(endian='big')
        stream.write_int(10, 2, 'little')
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2, 'little')) #little endian unsigned
        
        stream = StructIO(endian='little')
        stream.write_int(10, 2, 'big')
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2, 'big')) #big endian unsigned
        
        stream = StructIO(endian='little')
        stream.write_int(-10, 2, signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, signed=True)) #default endian signed
        
        stream = StructIO(endian='big')
        stream.write_int(-10, 2, 'little', signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, 'little', signed=True)) #little endian signed
        
        stream = StructIO(endian='little')
        stream.write_int(-10, 2, 'big', signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, 'big', signed=True)) #big endian signed
        
    def testfloat(self):
        stream = StructIO(endian='little')
        stream.write_float(3.14, 2)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2), 2)) #half default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 2, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2, 'little'), 2)) #half little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 2, 'big')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2, 'big'), 2)) #half big endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4), 2)) #single default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 4, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4, 'little'), 2)) #single little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4, 'big')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4, 'big'), 2)) #single big endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(8), 2)) #double default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 8, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(8, 'little'), 2)) #double little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8, 'big')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(8, 'big'), 2)) #double big endian
        
    def teststr(self):
        stream = StructIO()
        stream.write_str('Unit Test')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_str(len('Unit Test')))
        
    def testcstr(self):
        stream = StructIO()
        stream.write_cstr('Unit Test')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_cstr())
        self.assertEqual(10, stream.tell())
        
    def testpstr(self):
        stream = StructIO(endian='little')
        stream.write_pstr('Unit Test', 2)
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_pstr('Unit Test', 2, 'little')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2, 'little')) #little endian
        
        stream = StructIO(endian='little')
        stream.write_pstr('Unit Test', 2, 'big')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2, 'big')) #big endian
        
    def test7bint(self):
        stream = StructIO()
        stream.write_7bint(128)
        stream.seek(0)
        self.assertEqual(128, stream.read_7bint())
        self.assertEqual(2, stream.tell())
        
class AppendMethodsTest(unittest.TestCase):
    def testappendbool(self):
        stream = StructIO()
        stream.write_bool(False)
        stream.seek(0)
        stream.append_bool(True)
        stream.seek(0)
        self.assertEqual(True, stream.read_bool())
        
    def testappendbits(self):
        stream = StructIO()
        stream.write_bits([0,0,0,0,0,0,0,0])
        stream.seek(0)
        stream.append_bits([1,1,1,1,1,1,1,1])
        stream.seek(0)
        self.assertEqual([1,1,1,1,1,1,1,1], stream.read_bits()) #default endian unsigned
        
    def testappendint(self):
        stream = StructIO(endian='little')
        stream.write_int(2, 2)
        stream.seek(0)
        stream.append_int(1, 2)
        stream.seek(0)
        self.assertEqual(1, stream.read_int(2)) #default endian unsigned
        
        stream = StructIO(endian='big')
        stream.write_int(2, 2, 'little')
        stream.seek(0)
        stream.append_int(1, 2, 'little')
        stream.seek(0)
        self.assertEqual(1, stream.read_int(2, 'little')) #little endian unsigned
        
        stream = StructIO(endian='little')
        stream.write_int(2, 2, 'big')
        stream.seek(0)
        stream.append_int(1, 2, 'big')
        stream.seek(0)
        self.assertEqual(1, stream.read_int(2, 'big')) #big endian unsigned
        
        stream = StructIO(endian='little')
        stream.write_int(-2, 2, signed=True)
        stream.seek(0)
        stream.append_int(-1, 2, signed=True)
        stream.seek(0)
        self.assertEqual(-1, stream.read_int(2, signed=True)) #default endian signed
        
        stream = StructIO(endian='big')
        stream.write_int(-2, 2, 'little', signed=True)
        stream.seek(0)
        stream.append_int(-1, 2, 'little', signed=True)
        stream.seek(0)
        self.assertEqual(-1, stream.read_int(2, 'little', signed=True)) #little endian signed
        
        stream = StructIO(endian='little')
        stream.write_int(-2, 2, 'big', signed=True)
        stream.seek(0)
        stream.append_int(-1, 2, 'big', signed=True)
        stream.seek(0)
        self.assertEqual(-1, stream.read_int(2, 'big', signed=True)) #big endian signed
        
    def testappendfloat(self):
        stream = StructIO(endian='little')
        stream.write_float(3.14, 2)
        stream.seek(0)
        stream.append_float(6.28, 2)
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(2), 2)) #default endian half
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 2, 'little')
        stream.seek(0)
        stream.append_float(6.28, 2, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(2, 'little'), 2)) #little endian half
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 2, 'big')
        stream.seek(0)
        stream.append_float(6.28, 2, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(2, 'big'), 2)) #big endian half
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4)
        stream.seek(0)
        stream.append_float(6.28, 4)
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4), 2)) #default endian single
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 4, 'little')
        stream.seek(0)
        stream.append_float(6.28, 4, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4, 'little'), 2)) #little endian single
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4, 'big')
        stream.seek(0)
        stream.append_float(6.28, 4, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4, 'big'), 2)) #big endian single
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8)
        stream.seek(0)
        stream.append_float(6.28, 8)
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8), 2)) #default endian double
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 8, 'little')
        stream.seek(0)
        stream.append_float(6.28, 8, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8, 'little'), 2)) #little endian double
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8, 'big')
        stream.seek(0)
        stream.append_float(6.28, 8, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8, 'big'), 2)) #big endian double
        
    def testappendstr(self):
        stream = StructIO()
        stream.write_str('Test')
        stream.seek(0)
        stream.append_str('Unit ')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_str(len('Unit Test')))
        
    def testappendcstr(self):
        stream = StructIO()
        stream.write_cstr('Test')
        stream.seek(0)
        stream.append_cstr('Unit')
        stream.seek(0)
        self.assertEqual('Unit', stream.read_cstr())
        self.assertEqual('Test', stream.read_cstr())
        self.assertEqual(10, stream.tell())
        
    def testappendpstr(self):
        stream = StructIO(endian='little')
        stream.write_pstr('Test', 2)
        stream.seek(0)
        stream.append_pstr('Unit', 2)
        stream.seek(0)
        self.assertEqual('Unit', stream.read_pstr(2)) #default endian
        self.assertEqual('Test', stream.read_pstr(2))
        
        stream = StructIO(endian='big')
        stream.write_pstr('Test', 2, 'little')
        stream.seek(0)
        stream.append_pstr('Unit', 2, 'little')
        stream.seek(0)
        self.assertEqual('Unit', stream.read_pstr(2, 'little')) #little endian
        self.assertEqual('Test', stream.read_pstr(2, 'little'))
        
        stream = StructIO(endian='little')
        stream.write_pstr('Test', 2, 'big')
        stream.seek(0)
        stream.append_pstr('Unit', 2, 'big')
        stream.seek(0)
        self.assertEqual('Unit', stream.read_pstr(2, 'big')) #big endian
        self.assertEqual('Test', stream.read_pstr(2, 'big'))
        
    def testappend7bint(self):
        stream = StructIO()
        stream.write_7bint(128)
        stream.seek(0)
        stream.append_7bint(127)
        stream.seek(0)
        self.assertEqual(127, stream.read_7bint())
        
class OverwriteMethodsTest(unittest.TestCase):
    def testoverwritestr(self):
        stream = StructIO()
        stream.write_str('Unit Test')
        stream.seek(0)
        stream.overwrite_str('Working', 9)
        stream.seek(0)
        self.assertEqual('Working', stream.read_str(len('Working')))
        
    def testoverwritecstr(self):
        stream = StructIO()
        stream.write_cstr('Unit Test')
        stream.seek(0)
        stream.overwrite_cstr('Working')
        self.assertEqual(8, stream.tell())
        stream.seek(0)
        self.assertEqual('Working', stream.read_cstr())
        
    def testoverwritepstr(self):
        stream = StructIO(endian='big')
        stream.write_pstr('Unit Test', 2)
        stream.seek(0)
        stream.overwrite_pstr('Working', 3)
        stream.seek(0)
        self.assertEqual('Working', stream.read_pstr(3)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_pstr('Unit Test', 2, 'little')
        stream.seek(0)
        stream.overwrite_pstr('Working', 3, 'little')
        stream.seek(0)
        self.assertEqual('Working', stream.read_pstr(3, 'little')) #little endian
        
        stream = StructIO(endian='little')
        stream.write_pstr('Unit Test', 2, 'big')
        stream.seek(0)
        stream.overwrite_pstr('Working', 3, 'big')
        stream.seek(0)
        self.assertEqual('Working', stream.read_pstr(3, 'big')) #big endian
        
    def testoverwrite7bint(self):
        stream = StructIO()
        stream.write_7bint(128)
        stream.seek(0)
        stream.overwrite_7bint(127)
        stream.seek(0)
        self.assertEqual(127, stream.read_7bint())
        
class SkipMethodsTest(unittest.TestCase):
    def testskipcstr(self):
        stream = StructIO()
        stream.write_cstr('Unit')
        stream.write_cstr('Test')
        stream.seek(0)
        stream.skip_cstr()
        self.assertEqual('Test', stream.read_cstr())
        
    def testskippstr(self):
        stream = StructIO()
        stream.write_pstr('Unit', 2)
        stream.write_pstr('Test', 2)
        stream.seek(0)
        stream.skip_pstr(2)
        self.assertEqual('Test', stream.read_pstr(2))
        
    def testskip7bint(self):
        stream = StructIO()
        stream.write_7bint(127)
        stream.write_7bint(128)
        stream.seek(0)
        stream.skip_7bint()
        self.assertEqual(128, stream.read_7bint())
        
class DeleteMethodsTest(unittest.TestCase):
    def testdeletecstr(self):
        stream = StructIO()
        stream.write_cstr('Unit')
        stream.write_cstr('Test')
        stream.seek(0)
        stream.delete_cstr()
        self.assertEqual('Test', stream.read_cstr())
        
    def testdeletepstr(self):
        stream = StructIO(endian='big')
        stream.write_pstr('Unit', 2)
        stream.write_pstr('Test', 2)
        stream.seek(0)
        stream.delete_pstr(2)
        self.assertEqual('Test', stream.read_pstr(2)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_pstr('Unit', 2, 'little')
        stream.write_pstr('Test', 2, 'little')
        stream.seek(0)
        stream.delete_pstr(2, 'little')
        self.assertEqual('Test', stream.read_pstr(2, 'little')) #little endian
        
        stream = StructIO(endian='little')
        stream.write_pstr('Unit', 2, 'big')
        stream.write_pstr('Test', 2, 'big')
        stream.seek(0)
        stream.delete_pstr(2, 'big')
        self.assertEqual('Test', stream.read_pstr(2, 'big')) #big endian
        
    def testdelete7bint(self):
        stream = StructIO()
        stream.write_7bint(128)
        stream.write_7bint(127)
        stream.seek(0)
        stream.delete_7bint()
        self.assertEqual(127, stream.read_7bint())
        
class InheritanceTest(unittest.TestCase):
    def testattraccess(self):
        struct = ExtendedStruct()
        struct.endian
        
        stream = ExtendedStructIO()
        stream.encoding
        
    def testpackunpack7bstr(self):
        struct = ExtendedStruct()
        self.assertEqual('Unit Test', struct.unpack_7bstr(struct.pack_7bstr('Unit Test'))[0])
        
    def testreadwrite7bstr(self):
        stream = ExtendedStructIO()
        stream.write_7bstr('Unit Test')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_7bstr())
        self.assertEqual(10, stream.tell())
        
    def testappend7bstr(self):
        stream = ExtendedStructIO()
        stream.write_7bstr('Test')
        stream.seek(0)
        stream.append_7bstr('Unit')
        stream.seek(0)
        self.assertEqual('Unit', stream.read_7bstr())
        
    def testoverwrite7bstr(self):
        stream = ExtendedStructIO()
        stream.write_7bstr('Unit Test')
        stream.seek(0)
        stream.overwrite_7bstr('Working')
        stream.seek(0)
        self.assertEqual('Working', stream.read_7bstr())
        
    def testskip7bstr(self):
        stream = ExtendedStructIO()
        stream.write_7bstr('Unit')
        stream.write_7bstr('Test')
        stream.seek(0)
        stream.skip_7bstr()
        self.assertEqual('Test', stream.read_7bstr())
        
    def testdelete7bstr(self):
        stream = ExtendedStructIO()
        stream.write_7bstr('Unit')
        stream.write_7bstr('Test')
        stream.seek(0)
        stream.delete_7bstr()
        self.assertEqual('Test', stream.read_7bstr())
        
unittest.main()