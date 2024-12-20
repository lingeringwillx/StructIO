import unittest
from structio import *

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

class ExampleTest(unittest.TestCase):
    def testexample(self):
        #making sure that the example at least doesn't crash
        stream = StructIO()
        stream.write_int(10, 2)
        stream.write_float(3.14, 4)
        stream.write_cstr('Hello')
        stream.write_pstr('World!', 1)
        stream.seek(0)
        stream.read()

        stream.seek(0)
        stream.read_int(2)
        stream.read_float(4)
        stream.read_cstr()
        stream.read_pstr(1)

class GenericStreamMethodsTest(unittest.TestCase):
    def testbufgettersetter(self):
        stream = StructIO()
        self.assertEqual(stream.buffer, stream.getvalue())

        stream.seek(4)
        stream.buffer = b'Unit Test'
        self.assertEqual(b'Unit Test', stream.getvalue())

        stream.seek(10)
        stream.buffer = b'Unit Test'
        self.assertEqual(9, stream.tell())

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

    def testcopy(self):
        stream = StructIO(b'Unit Test')
        stream2 = stream.copy()
        stream.seek(0)
        self.assertEqual(0, stream2.tell())
        self.assertEqual(stream.read(), stream2.read())

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
        stream = StructIO()
        stream.write_int(10, 2)
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2)) #default endian unsigned

        stream = StructIO(endian='big')
        stream.write_int(10, 2, 'little')
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2, 'little')) #little endian unsigned

        stream = StructIO()
        stream.write_int(10, 2, 'big')
        stream.seek(0)
        self.assertEqual(10, stream.read_int(2, 'big')) #big endian unsigned

        stream = StructIO()
        stream.write_int(-10, 2, signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, signed=True)) #default endian signed

        stream = StructIO(endian='big')
        stream.write_int(-10, 2, 'little', signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, 'little', signed=True)) #little endian signed

        stream = StructIO()
        stream.write_int(-10, 2, 'big', signed=True)
        stream.seek(0)
        self.assertEqual(-10, stream.read_int(2, 'big', signed=True)) #big endian signed

    def testfloat(self):
        stream = StructIO()
        stream.write_float(3.14, 2)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2), 2)) #half default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 2, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2, 'little'), 2)) #half little endian

        stream = StructIO()
        stream.write_float(3.14, 2, 'big')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(2, 'big'), 2)) #half big endian

        stream = StructIO()
        stream.write_float(3.14, 4)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4), 2)) #single default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 4, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4, 'little'), 2)) #single little endian

        stream = StructIO()
        stream.write_float(3.14, 4, 'big')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(4, 'big'), 2)) #single big endian

        stream = StructIO()
        stream.write_float(3.14, 8)
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(8), 2)) #double default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 8, 'little')
        stream.seek(0)
        self.assertEqual(3.14, round(stream.read_float(8, 'little'), 2)) #double little endian

        stream = StructIO()
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
        stream = StructIO()
        stream.write_pstr('Unit Test', 2)
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2)) #default endian

        stream = StructIO(endian='big')
        stream.write_pstr('Unit Test', 2, 'little')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2, 'little')) #little endian

        stream = StructIO()
        stream.write_pstr('Unit Test', 2, 'big')
        stream.seek(0)
        self.assertEqual('Unit Test', stream.read_pstr(2, 'big')) #big endian

    def test7bint(self):
        stream = StructIO()
        stream.write_7bint(128)
        stream.seek(0)
        self.assertEqual(128, stream.read_7bint())
        self.assertEqual(2, stream.tell())

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
        stream.write_7bint(128)
        stream.write_7bint(127)
        stream.seek(0)
        stream.skip_7bint()
        self.assertEqual(127, stream.read_7bint())

unittest.main()