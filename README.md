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

### StructIO

File-like object stored in memory. Extends *io.BytesIO* from the standard library, which means that it has all of the basic methods of file-like objects, including *read*, *write*, *seek*, *tell*, and *truncate*.

### Attributes

**buffer**: the current content of the object.

**endian**: the default endian that would be used by the object.

**encoding**: the default encoding used by string methods.

**errors**: the default error handling behavior when encoding or decoding strings. More information could be found in [Python's documentation](https://docs.python.org/3/library/codecs.html#error-handlers).

### Methods

**StructIO(b=b'', endian='little', encoding='utf-8', errors='ignore')**

Take bytes object *b* and returns a *StructIO* instance containing *b* with the provided arguments used as defaults.

**\_\_len\_\_()**

Returns the size/length of the file.

**\_\_eq\_\_(other)**

Checks if the content of the buffer is equal to the content of another StructIO or BytesIO object.

**copy()**

Creates a copy of the object and returns it.

**clear()**

Clear the internal buffer of the object.

**find(b)**

Searches the buffer for *b*. Returns the location in which *b* can be found, returns -1 if it's not found. Starts searching from the current position in the buffer.

**index(b)**

Same as *find* but raises a *ValueError* if it fails to find *b*.

**read_bool()**

Read one byte from the buffer and converts it into a boolean.

**write_bool(boolean)**

Writes *boolean* to the buffer.

**read_bits()**

Reads one byte from the buffer and converts it into a list of integers representing the individual bits in the byte. The first element in the list is LSB in the byte.

**write_bits(bits)**

Converts list of integers *bits* into a byte and writes it to the buffer.

**read_int(size, endian=None, signed=False)**

Reads *size* bytes from the buffer and converts it into an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(number, size, endian=None, signed=False)**

Converts *number* into a bytes buffer with length *size* and endian *endian*, then writes it into the buffer. The *signed* argument is used to specify whether the integer is signed or not.

**read_ints(size, n endian=None, signed=False)**

Reads *n* integers of *size* bytes from the buffer. Can be faster than *read_int* when multiple reads are required but limited to sizes 1, 2, 4, 8.

**write_ints(numbers, size, endian=None, signed=False)**

Converts a list of integers *numbers* into a bytes buffer with length *size* and endian *endian*, then writes it into the buffer. Can be faster than *write_int* when multiple writes are required but limited to sizes 1, 2, 4, 8.

**read_float(size, endian=None)**

Reads *size* bytes from the buffer and converts them into a float. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**write_float(number, size, endian=None)**

Converts *number* into a bytes buffer then writes it into the buffer. *size* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**read_floats(size, n, endian=None)**

Reads *n* floats of *size* bytes from the buffer. Can be faster than *read_float* when multiple reads are required.

**write_floats(numbers size, endian=None)**

Converts a list of floats *numbers* into a bytes buffer then writes it into the buffer. Can be faster than *write_float* when multiple writes are required.

**read_str(length)**

Reads a string with length *length* from the buffer.

**write_str(string)**

Writes *string* into the buffer.

**read_cstr()**

Reads a string from the buffer up to the null termination. Raises a *ValueError* if it fails to find a null termination.

**write_cstr(string)**

Writes *string* into the buffer.

**skip_cstr()**

Skips the null-terminated string at the current position.

**read_pstr(size, endian=None)**

Reads a Pascal string from the buffer and returns it. *size* is used to specify how many bytes are used for the string's length in the buffer. The endian of the length of the string can be specified with the *endian* argument.

**write_pstr(string, size, endian=None)**

Writes *string* to the buffer as a Pascal string.

**skip_pstr(size, endian=None)**

Skips the Pascal string at the current position.

**read_7bint()**

Reads the bytes representing a 7 bit integer from the buffer at the current position and converts them into an integer.

**write_7bint(number)**

Converts *number* into a 7 bit integer and writes it to the buffer.

**skip_7bint()**

Skips the 7 bit integer at the current position.