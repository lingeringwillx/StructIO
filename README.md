A small Python library based on the BytesIO object from the standard library, designed to make parsing and editing binary files easier.

### Installation

Using pip: 

```
pip install structio
```

### Example

Writing to a stream:

```python
>>> from structio import *
>>> stream = StructIO()
>>> stream.write_int(10, 2)
2
>>> stream.write_float(3.14, 4)
4
>>> stream.write_cstr('Hello')
6
>>> stream.write_pstr('World!', 1)
7
>>> stream.seek(0)
0
>>> stream.read()
b'\n\x00\xc3\xf5H@Hello\x00\x06World!'
```

Reading from the same stream:

```python
>>> stream.seek(0)
0
>>> stream.read_int(2)
10
>>> stream.read_float(4)
3.140000104904175
>>> stream.read_cstr()
'Hello'
>>> stream.read_pstr(1)
'World!'
```

### Objects

### Struct

Contains methods for unpacking and packing various data types.

### Attributes

**endian**: specifies the default endian that would be used by the object, can either be *'little'* or *'big'*.

**encoding**: specifies the default encoding used by string methods.

**errors**: specifies default error handling behavior when encoding or decoding strings. More information could be found in [Python's documentation](https://docs.python.org/3/library/codecs.html#error-handlers).

### Methods

**Struct(endian='little', encoding='utf-8', errors='ignore')**

Creates a new *Struct* object with the provided arguments used as defaults.

**unpack_bool(b)**

Converts byte *b* into a boolean. Returns False if *b* is a null byte, otherwise returns True.

**pack_bool(boolean)**

Converts boolean *boolean* into it's binary representaion.

**unpack_bits(b)**

Converts byte *b* into an list of integers representing the individual bits of the byte. First element in the list is the LSB in the byte.

**pack_bits(bits)**

Converts a list of integers into a byte.

**unpack_int(b, endian=None, signed=False)**

Converts bytes object *b* into an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**pack_int(number, size, endian=None, signed=False)**

Converts *number* into a bytes object with length *size* and endian *endian*. The *signed* argument is used to specify whether the integer is signed or not.

**unpack_float(b, size, endian=None)**

Converts bytes object *b* into a float. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**pack_float(number, size, endian=None)**

Converts *number* into a bytes object. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**unpack_str(b)**

Convert bytes object *b* into a string.

**pack_str(string)**

Converts *string* into a bytes object.

**unpack_cstr(b, start=0)**

Convert bytes object *b* into a string up to the null termination. If *start* is specified, then the bytes object will be converted starting from position *start*. Returns a tuple containing both the value and the length of the type.

**pack_cstr(string)**

Converts *string* into a bytes object representing a null-terminated string.

**unpack_pstr(b, size, endian=None, start=0)**

Converts bytes object *b* into a Pascal string. *size* is used to specify how many bytes are used for the string's length in the object. The endian of the length of the string can be specified with the *endian* argument. *b* will only be converted up to the length specified in the bytes object. If *start* is specified, then the bytes object will be converted starting from position *start*. Returns a tuple containing both the value and the length of the type.

**pack_pstr(string, size, endian=None)**

Converts *string* into a bytes object in the Pascal string format. *size* is used to specify how many bytes are used for the string's length. The endian of the length of the string can be specified with the *endian* argument.

**unpack_7bint(b, start=0)**

Converts bytes representing a 7 bit integer (Variable Length Quantity) into an integer.  If *start* is specified, then the bytes object will be converted starting from position *start*. Returns a tuple containing both the value and the length of the type.

**pack_7bint(number)**

Converts *number* into a 7 bit integer.

-----

### StructIO

File-like object stored in memory. Extends *io.BytesIO* from the standard library, which means that it has all of the basic methods of file-like objects, including *read*, *write*, *seek*, *tell*, and *truncate*.

### Attributes

**buffer**: the current content of the object.

**endian**: the default endian that would be used by the object.

**encoding**: the default encoding used by string methods.

**errors**: the default error handling behavior when encoding or decoding strings.

### Methods

**StructIO(b=b'', endian='little', encoding='utf-8', errors='ignore')**

Take bytes object *b* and returns a *StructIO* instance containing *b* with the provided arguments used as defaults.

**\_\_len\_\_()**

Returns the size/length of the file.

**\_\_eq\_\_(other)**

Checks if the content of the object is equal to the content of another instance of the same object.

**copy()**

Creates a copy of the object and returns it.

**clear()**

Clear the internal buffer of the object.

**find(bytes_sequence, n=1)**

Searches the object for *bytes_sequence*. Returns the location in which the *nth* occurrence of *bytes_sequence* can be found, returns -1 if it's not found. Starts searching from the current position in the buffer.

**index(bytes_sequence, n=1)**

Same as find but raises a *ValueError* if it fails to find *bytes_sequence*.

**read_bool()**

Read one byte from the object and converts it into a boolean.

**write_bool(boolean)**

Writes *boolean* to the object.

**read_bits()**

Reads one byte from the object and converts it into a list of integers representing the individual bits in the byte. The first element in the list is LSB in the byte.

**write_bits(bits)**

Converts list of integers *bits* into a byte and writes it to the object.

**read_int(size, endian=None, signed=False)**

Reads *size* bytes from the object and converts it into an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(number, size, endian=None, signed=False)**

Converts *number* into a bytes object with length *size* and endian *endian*, then writes it into the object. The *signed* argument is used to specify whether the integer is signed or not.

**read_float(size, endian=None)**

Reads *size* bytes from the object and converts them into a float. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**write_float(number, size, endian=None)**

Converts *number* into a bytes object then writes it into the object. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**read_str(length)**

Reads a string with length *length* from the object.

**write_str(string)**

Writes *string* into the object.

**read_cstr()**

Reads a string from the object up to the null termination. Raises a *ValueError* if it fails to find a null termination.

**write_cstr(string)**

Writes *string* into the object.

**skip_cstr()**

Skips the null-terminated string at the current position.

**read_pstr(size, endian=None)**

Reads a Pascal string from the object and returns it. *size* is used to specify how many bytes are used for the string's length in the object. The endian of the length of the string can be specified with the *endian* argument.

**write_pstr(string, size, endian=None)**

Writes *string* to the object as a Pascal string.

**skip_pstr(size, endian=None)**

Skips the Pascal string at the current position.

**read_7bint()**

Reads the bytes representing a 7 bit integer from the object at the current position and converts them into an integer.

**write_7bint(number)**

Converts *number* into a 7 bit integer and writes it to the object.

**skip_7bint()**

Skips the 7 bit integer at the current position.