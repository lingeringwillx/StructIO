import unittest
from structio import *

class PackUnpackFunctionsTest(unittest.TestCase):
    def testbool(self):
        self.assertEqual(True, unpack_bool(pack_bool(True))) #True
        self.assertEqual(True, unpack_bool(b'\x02')) #True not one
        self.assertEqual(False, unpack_bool(pack_bool(False))) #False
        
    def testbits(self):
        self.assertEqual([0,1,0,1,0,1,0,1], unpack_bits(pack_bits([0,1,0,1,0,1,0,1])))
        
    def testint(self):
        self.assertEqual(10, unpack_int(pack_int(10, 2, 'little'), 'little')) #little endian unsigned
        self.assertEqual(10, unpack_int(pack_int(10, 2, 'big'), 'big'))#big endian unsigned
        self.assertEqual(-10, unpack_int(pack_int(-10, 2, 'little', signed=True), 'little', signed=True)) #little endian signed
        self.assertEqual(-10, unpack_int(pack_int(-10, 2, 'big', signed=True), 'big', signed=True)) #big endian signed
        
    def testfloat(self):
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 2, 'little'), 2, 'little'), 2)) #half little endian
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 2, 'big'), 2, 'big'), 2)) #half big endian
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 4, 'little'), 4,'little'), 2)) #single little endian
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 4, 'big'), 4, 'big'), 2)) #single big endian
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 8, 'little'), 8, 'little'), 2)) #double little endian
        self.assertEqual(3.14, round(unpack_float(pack_float(3.14, 8, 'big'), 8, 'big'), 2)) #double big endian
        
    def teststr(self):
        self.assertEqual('Unit Test', unpack_str(pack_str('Unit Test')))
        
    def testcstr(self):
        self.assertEqual('Unit Test', unpack_cstr(pack_cstr('Unit Test')))
        self.assertEqual('Test', unpack_cstr(b'Unit\x00Test\x00', 5))
        
    def testpstr(self):
        self.assertEqual('Unit Test', unpack_pstr(pack_pstr('Unit Test', 2, 'little'), 2, 'little')) #little endian
        self.assertEqual('Unit Test', unpack_pstr(pack_pstr('Unit Test', 2, 'big'), 2, 'big')) #big endian
        
        self.assertEqual('Test', unpack_pstr(b'\x04Unit\x04Test', 1, 'little', 5))
        
    def test7bint(self):
        self.assertEqual(128, unpack_7bint(pack_7bint(128)))
        self.assertEqual(128, unpack_7bint(b'\x00' + pack_7bint(128), start=1))
        
class GenericStreamMethodsTest(unittest.TestCase):
    def testlen(self):
        stream = StructIO(b'Unit Test', 'little')
        stream.seek(5)
        self.assertEqual(9, len(stream))
        self.assertEqual(5, stream.tell()) #should be unchanged
        
    def testeq(self):
        stream1 = StructIO(b'Test', 'little')
        stream2 = StructIO(b'Test', 'little')
        stream3 = StructIO(b' Test', 'little')
        stream2.seek(2)
        self.assertEqual(stream1, stream2)
        stream3.seek(1)
        self.assertNotEqual(stream1, stream3)
        
    def testclear(self):
        stream = StructIO(b'Unit Test', 'little')
        stream.seek(5)
        stream.clear()
        self.assertEqual(0, stream.tell())
        self.assertEqual(b'', stream.read())
        
    def testiseof(self):
        stream = StructIO(b'Unit Test', 'little')
        self.assertFalse(stream.is_eof())
        self.assertEqual(0, stream.tell())
        stream.seek(0, 2)
        self.assertTrue(stream.is_eof())
        
    def testcopy(self):
        stream = StructIO(b'Unit Test', 'little')
        stream2 = stream.copy()
        self.assertEqual(0, stream2.tell())
        self.assertEqual(stream.read(), stream2.read())
        
    def testappend(self):
        stream = StructIO(endian='little')
        stream.write(b'Test')
        stream.seek(0)
        stream.append(b'Unit ')
        stream.seek(0)
        self.assertEqual(b'Unit Test', stream.read())
    
    def testoverwrite(self):
        stream = StructIO(endian='little')
        stream.write(b'Unit Test')
        stream.overwrite(0, 4, b'New')
        stream.seek(0)
        self.assertEqual(b'New Test', stream.read())
        
    def testreadall(self):
        stream = StructIO(endian='little')
        stream.write(b'Unit Test')
        self.assertEqual(b'Unit Test', stream.read_all())
        self.assertEqual(0, stream.tell()) #should be back to start
        
    def testwriteall(self):
        stream = StructIO(b'Unit Test', 'little')
        stream.seek(0, 2)
        stream.write_all(b'New')
        self.assertEqual(0, stream.tell())
        self.assertEqual(b'New', stream.read())
        
    def testdelete(self):
        stream = StructIO(b'Unit Test', 'little')
        stream.seek(0, 2)
        stream.delete(5)
        self.assertEqual(4, stream.tell())
        stream.seek(0)
        self.assertEqual(b'Unit', stream.read())
        
        stream = StructIO(b'Unit Test', 'little')
        stream.seek(5)
        stream.delete(10)
        self.assertEqual(b'Test', stream.read())
        
    def testfind(self):
        stream = StructIO(b'Unit Test Unit Test', endian='little')
        self.assertEqual(5, stream.find(b'Test')) #first instance
        self.assertEqual(15, stream.find(b'Test', 2)) #second
        
    def testindex(self):
        stream = StructIO(b'Unit Test Unit Test', endian='little')
        self.assertEqual(5, stream.index(b'Test')) #first instance
        self.assertEqual(15, stream.index(b'Test', 2)) #second
        self.assertRaises(ValueError, lambda: stream.index(b'Test', 3))
        
class ReadWriteMethodsTest(unittest.TestCase):
    def testbool(self):
        stream = StructIO(endian='little')
        stream.write_bool(True)
        stream.seek(0)
        self.assertEqual(True, stream.read_bool()) #True
        
        stream = StructIO(endian='little')
        stream.write_bool(False)
        stream.seek(0)
        self.assertEqual(False, stream.read_bool()) #False
        
    def testbits(self):
        stream = StructIO(endian='little')
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
        stream = StructIO(endian='little')
        stream.write_str('Unit Test')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_str(len('Unit Test')))
        
    def testcstr(self):
        stream = StructIO(endian='little')
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
        stream = StructIO(endian='little')
        stream.write_7bint(128)
        stream.seek(0)
        self.assertEqual(128, stream.read_7bint()) #default endian
        
class AppendOverwriteMethodsTest(unittest.TestCase):
    def testappendbool(self):
        stream = StructIO(endian='little')
        stream.write_bool(False)
        stream.seek(0)
        stream.append_bool(True)
        stream.seek(0)
        self.assertEqual(True, stream.read_bool())
        
    def testappendbits(self):
        stream = StructIO(endian='little')
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
        self.assertEqual(6.28, round(stream.read_float(2), 2)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 2, 'little')
        stream.seek(0)
        stream.append_float(6.28, 2, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(2, 'little'), 2)) #little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 2, 'big')
        stream.seek(0)
        stream.append_float(6.28, 2, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(2, 'big'), 2)) #big endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4)
        stream.seek(0)
        stream.append_float(6.28, 4)
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4), 2)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 4, 'little')
        stream.seek(0)
        stream.append_float(6.28, 4, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4, 'little'), 2)) #little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 4, 'big')
        stream.seek(0)
        stream.append_float(6.28, 4, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(4, 'big'), 2)) #big endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8)
        stream.seek(0)
        stream.append_float(6.28, 8)
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8), 2)) #default endian
        
        stream = StructIO(endian='big')
        stream.write_float(3.14, 8, 'little')
        stream.seek(0)
        stream.append_float(6.28, 8, 'little')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8, 'little'), 2)) #little endian
        
        stream = StructIO(endian='little')
        stream.write_float(3.14, 8, 'big')
        stream.seek(0)
        stream.append_float(6.28, 8, 'big')
        stream.seek(0)
        self.assertEqual(6.28, round(stream.read_float(8, 'big'), 2)) #big endian
        
    def testappendstr(self):
        stream = StructIO(endian='little')
        stream.write_str('Test')
        stream.seek(0)
        stream.append_str('Unit ')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_str(len('Unit Test')))
        
    def testappendcstr(self):
        stream = StructIO(endian='little')
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
        stream = StructIO(endian='little')
        stream.write_7bint(128)
        stream.seek(0)
        stream.append_7bint(127)
        stream.seek(0)
        self.assertEqual(127, stream.read_7bint())
        
    def testoverwritestr(self):
        stream = StructIO(endian='little')
        stream.write_str('Unit Test')
        stream.seek(0)
        stream.overwrite_str('Working', 9)
        stream.seek(0)
        self.assertEqual('Working', stream.read_str(len('Working')))
        
    def testoverwritecstr(self):
        stream = StructIO(endian='little')
        stream.write_cstr('Unit Test')
        stream.seek(0)
        stream.overwrite_cstr('Working')
        stream.seek(0)
        self.assertEqual('Working', stream.read_cstr())
        self.assertEqual(8, stream.tell())
        
    def testoverwritepstr(self):
        stream = StructIO(endian='little')
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
        stream = StructIO(endian='little')
        stream.write_7bint(128)
        stream.seek(0)
        stream.overwrite_7bint(127)
        stream.seek(0)
        self.assertEqual(127, stream.read_7bint())
        
unittest.main()
