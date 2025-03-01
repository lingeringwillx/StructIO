from structio import StructIO
import unittest

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
        stream = StructIO(b'Test')
        self.assertEqual(stream.buffer, stream.getvalue())

        stream.seek(4)
        stream.buffer = b'Unit Test'
        self.assertEqual(b'Unit Test', stream.getvalue())
        self.assertEqual(0, stream.tell())

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
        self.assertEqual(5, stream.find(b'Test'))
        stream.seek(6)
        self.assertEqual(15, stream.find(b'Test'))

    def testindex(self):
        stream = StructIO(b'Unit Test Unit Test')
        self.assertEqual(5, stream.index(b'Test'))
        stream.seek(6)
        self.assertEqual(15, stream.index(b'Test'))
        stream.seek(16)
        self.assertRaises(ValueError, lambda: stream.index(b'Test'))

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

    def testints(self):
        stream = StructIO()
        stream.write_ints([0, 1, 2], 2)
        stream.seek(0)
        self.assertSequenceEqual([0, 1, 2], stream.read_ints(2, 3)) #default endian unsigned

        stream = StructIO(endian='big')
        stream.write_ints([0, 1, 2], 2, 'little')
        stream.seek(0)
        self.assertSequenceEqual([0, 1, 2], stream.read_ints(2, 3, 'little')) #little endian unsigned

        stream = StructIO()
        stream.write_ints([0, 1, 2], 2, 'big')
        stream.seek(0)
        self.assertSequenceEqual([0, 1, 2], stream.read_ints(2, 3, 'big')) #big endian unsigned

        stream = StructIO()
        stream.write_ints([0, -1, -2], 2, signed=True)
        stream.seek(0)
        self.assertSequenceEqual([0, -1, -2], stream.read_ints(2, 3, signed=True)) #default endian signed

        stream = StructIO(endian='big')
        stream.write_ints([0, -1, -2], 2, 'little', signed=True)
        stream.seek(0)
        self.assertSequenceEqual([0, -1, -2], stream.read_ints(2, 3, 'little', signed=True)) #little endian signed

        stream = StructIO()
        stream.write_ints([0, -1, -2], 2, 'big', signed=True)
        stream.seek(0)
        self.assertSequenceEqual([0, -1, -2], stream.read_ints(2, 3, 'big', signed=True)) #big endian signed

    def testfloat(self):
        stream = StructIO()
        stream.write_float(3.14, 2)
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(2), places=2) #half default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 2, 'little')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(2, 'little'), places=2) #half little endian

        stream = StructIO()
        stream.write_float(3.14, 2, 'big')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(2, 'big'), places=2) #half big endian

        stream = StructIO()
        stream.write_float(3.14, 4)
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(4), places=2) #single default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 4, 'little')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(4, 'little'), places=2) #single little endian

        stream = StructIO()
        stream.write_float(3.14, 4, 'big')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(4, 'big'), places=2) #single big endian

        stream = StructIO()
        stream.write_float(3.14, 8)
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(8), places=2) #double default endian

        stream = StructIO(endian='big')
        stream.write_float(3.14, 8, 'little')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(8, 'little'), places=2) #double little endian

        stream = StructIO()
        stream.write_float(3.14, 8, 'big')
        stream.seek(0)
        self.assertAlmostEqual(3.14, stream.read_float(8, 'big'), places=2) #double big endian

    def testfloats(self):
        #half default endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 2)
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(2, 3)
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #half little endian
        stream = StructIO(endian='big')
        stream.write_floats([0.0, 0.1, 0.2], 2, 'little')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(2, 3, 'little')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #half big endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 2, 'big')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(2, 3, 'big')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #single default endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 4)
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(4, 3)
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #single little endian
        stream = StructIO(endian='big')
        stream.write_floats([0.0, 0.1, 0.2], 4, 'little')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(4, 3, 'little')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #single big endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 4, 'big')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(4, 3, 'big')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #double default endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 8)
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(8, 3)
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #double little endian
        stream = StructIO(endian='big')
        stream.write_floats([0.0, 0.1, 0.2], 8, 'little')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(8, 3, 'little')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

        #double big endian
        stream = StructIO()
        stream.write_floats([0.0, 0.1, 0.2], 8, 'big')
        stream.seek(0)
        f0, f1, f2 = stream.read_floats(8, 3, 'big')
        self.assertAlmostEqual(0.0, f0 , places=2)
        self.assertAlmostEqual(0.1, f1 , places=2)
        self.assertAlmostEqual(0.2, f2 , places=2)

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