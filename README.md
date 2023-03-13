A small Python library based on the BytesIO object from the standard library, designed to make parsing and editing binary files easier.

### Installation

Using pip: 

```
pip install structio
```

### Example

Writing to a stream:

```python
>>> import structio
>>> stream = structio.StructIO(endian='little')
>>> stream.write_int(10, 2)
2
>>> stream.write_float(3.14)
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
>>> stream.read_float()
3.140000104904175
>>> stream.read_cstr()
'Hello'
>>> stream.read_pstr(1)
'World!'
```

### Functions

**unpack_bool(b)**

Converts byte *b* into a boolean. Returns False if *b* is a null byte, otherwise returns True.

**pack_bool(boolean)**

Converts boolean *boolean* into it's binary representaion.

**unpack_bits(b)**

Converts byte *b* into an list of integers representing the individual bits of the byte. First element in the list is the LSB in the byte.

**pack_bits(bits)**

Converts a list of integers into a byte.

**unpack_int(b, endian, signed=False)**

Converts bytes object *b* into an integer. The endian is specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**pack_int(number, numbytes, endian, signed=False)**

Converts *number* into a bytes object with length *numbytes* and endian *endian*. The *signed* argument is used to specify whether the integer is signed or not.

**unpack_float(b, numbytes, endian)**

Converts bytes object *b* into a float. *numbytes* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian is specified with the *endian* argument.

**pack_float(number, numbytes, endian)**

Converts *number* into a bytes object. *numbytes* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian is specified with the *endian* argument.

**unpack_str(b)**

Convert bytes object *b* into a string.

**pack_str(string)**

Converts *string* into a bytes object.

**unpack_cstr(b, start=0)**

Convert bytes object *b* into a string up to the null termination. If *start* is specified, then the bytes object will be converted starting from position *start*.

**pack_cstr(string)**

Converts *string* into a bytes object representing a null-terminated string.

**unpack_pstr(b, numbytes, endian, start=0)**

Converts bytes object *b* into a Pascal string. *numbytes* is used to specify how many bytes are used for the string's length in the object. The endian of the length of the string is specified with the *endian* argument. *b* will only be converted up to the length specified in the bytes object. If *start* is specified, then the bytes object will be converted starting from position *start*.

**pack_pstr(string, numbytes, endian)**

Converts *string* into a bytes object in the Pascal string format. *numbytes* is used to specify how many bytes are used for the string's length. The endian of the length of the string is specified with the *endian* argument.

**unpack_7bint(b, start=0)**

Converts bytes representing a 7 bit integer (Variable Length Quantity) into an integer.  If *start* is specified, then the bytes object will be converted starting from position *start*.

**pack_7bint(number)**

Converts *number* into a 7 bit integer.

### Objects

### StructIO

File-like object stored in memory. Extends *io.BytesIO* from the standard library, which means that it has all of the basic methods of file-like objects, including *read*, *write*, *seek*, *tell*, and *truncate*.

### Attributes

**endian**: specifies the default endian that would be used by the object.          

### Methods

**StructIO(b='', endian=None)**

Take bytes object *b* and returns a *StructIO* instance containing *b*. The endian argument specifies the default endian that would be used by the object, should either be *'little'* or *'big'*.

**\_\_len\_\_()**

Returns the size/length of the file.

**\_\_eq\_\_(other)**

Checks if the content of the object is equal to the content of another instance of the same object.

**is_eof()**

Return True if the end of the stream has been reached.

**copy()**

Creates a copy of the object and returns it.

**read_all()**

Reads and returns all of the content of the object.

**write_all(buffer)**

Overwrites the entire object with bytes object *buffer*.

**clear()**

Clear the internal buffer of the object.

**append(b)**

Appends bytes object *b* to the object at the current location.

**overwrite(self, start, end, b)**

Replaces the bytes between positions *start* and *end* with *b*.

**read_bool()**

Read one byte from the object and converts it into a boolean.

**write_bool(boolean)**

Writes *boolean* to the object.

**append_bool()**

Appends *boolean* to the object.

**read_bits()**

Reads one byte from the object and converts it into a list of integers representing the individual bits in the byte. The first element in the list is LSB in the byte.

**write_bits(bits)**

Converts list of integers *bits* into a byte and writes it to the object.

**append_bits(bits)**

Converts list of integers *bits* into a byte and writes it to the object.

**read_int(numbytes, endian=None, signed=False)**

Reads *numbytes* bytes from the object and converts it into an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(number, numbytes, endian=None, signed=False)**

Converts *number* into a bytes object with length *numbytes* and endian *endian*, then writes it into the object. The *signed* argument is used to specify whether the integer is signed or not.

**append_int(number, numbytes, endian=None, signed=False)**

Same as *write_int* but appends the value to the object at the current position instead of overwriting existing bytes.

**read_float(numbytes, endian=None)**

Reads *numbytes* bytes from the object and converts them into a float. *numbytes* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**write_float(number, numbytes, endian=None)**

Converts *number* into a bytes object then writes it into the object. *numbytes* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**append_float(number, numbytes, endian=None)**

Same as *write_float* but appends the value to the object at the current position instead of overwriting existing bytes. *numbytes* can be 2 for half precision, 4 for single precision, or 8 for double precision. The endian can be specified with the *endian* argument.

**read_str(length)**

Reads a string with length *length* from the object.

**write_str(string)**

Writes *string* into the object.

**append_str(string)**

Same as *write_str* but appends the value to the object at the current position instead of overwriting existing bytes.

**overwrite_str(string, length)**

Deletes *length* bytes starting from the current location, then writes *string* in it's place.

**read_cstr()**

Reads a string from the object up to the null termination. Raises a *ValueError* if it fails to find a null termination.

**write_cstr(string)**

Writes *string* into the object.

**append_cstr(string)**

Same as *write_cstr* but appends the value to the object at the current position instead of overwriting existing bytes.

**overwrite_cstr(string)**

Deletes the null-terminated string existing at the current location, then writes *string* as a null-terminated string in it's place.  Raises a *ValueError* if it fails to find a null termination.

**read_pstr(numbytes, endian=None)**

Reads a Pascal string from the object and returns it. *numbytes* is used to specify how many bytes are used for the string's length in the object. The endian of the length of the string can be specified with the *endian* argument.

**write_pstr(string, numbytes, endian=None)**

Writes *string* to the object as a Pascal string. *numbytes* is used to specify how many bytes are used for the string's length in the object. The endian of the length of the string can be specified with the *endian* argument.

**append_pstr(string, numbytes, endian=None)**

Same as *write_pstr* but appends the value to the object at the current position instead of overwriting existing bytes. The endian of the length of the string can be specified with the *endian* argument.

**overwrite_pstr(string, numbytes, endian=None)**

Deletes the existing Pascal string at the current position and writes *string* as a Pascal string in it's place. *numbytes* is used to specify how many bytes are used for the integer holding the string's length. The endian of the length of the string can be specified with the *endian* argument.

**read_7bint()**

Reads the bytes representing a 7 bit integer from the object at the current position and converts them into an integer.

**write_7bint(number)**

Converts *number* into a 7 bit integer and writes it to the object.

**append_7bint(number)**

Converts *number* into a 7 bit integer and appends it to the object.

**overwrite_7bint(number)**

Overwrites the 7 bit integer at the current position with *number*.

**delete(length)**

Deletes *length* bytes from the object starting from *current position - length* to *current position*.

**find(bytes_sequence, n=1)**

Searches the object for *bytes_sequence*. Returns the location in which the *nth* occurrence of *bytes_sequence* can be found, returns -1 if it's not found. Starts searching from the current position in the buffer.

**index(bytes_sequence, n=1)**

Same as find but raises a *ValueError* if it fails to find *bytes_sequence*.
