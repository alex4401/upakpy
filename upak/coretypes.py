import struct
import uuid
import zlib
from typing import *

from .base import PakBaseObject
from thirdparty.purlovia.ue.stream import MemoryStream
from .consts import COMPRESSION_ZLIB, COMPRESSION_NONE

class Guid(PakBaseObject):
    value: uuid.UUID

    def _deserialise(self, *args):
        raw_bytes = self.stream.readBytes(16)
        # Here we need to reverse the endian of each 4-byte word
        value = uuid.UUID(
            bytes=struct.pack('>4I', *struct.unpack('<4I', raw_bytes)))
        # some of the fields as the rest are single bytes.

        value = uuid.UUID(
            bytes=struct.pack('>4I', *struct.unpack('<4I', raw_bytes)))
        self._newField('value', value)


class String(PakBaseObject):
    def _deserialise(self, *args):
        self._newField('size', self.stream.readInt32())
        self._newField('value', self.stream.readTerminatedString(self.size))


class Table(PakBaseObject):
    count: int
    values: List[PakBaseObject]

    def _deserialise(self, itemType: Type[PakBaseObject],
                     count: int):  # type: ignore

        assert issubclass(
            itemType, PakBaseObject), f'Table item type must be PakBaseObject'
        assert count is not None
        assert issubclass(
            itemType, PakBaseObject), f'Table item type must be PakBaseObject'

        values = []
        for i in range(count):
            value = itemType(self).deserialise()
            value.table_index = i
            values.append(value)

        self._newField('itemType', itemType)
        self._newField('count', count)
        self._newField('values', values)

        return self

    def __getitem__(self, index: int):
        '''Provide access using the index via the table[index] syntax.'''
        if self.values is None:
            raise RuntimeError('Table not deserialised before read')

        return self.values[index]

    def __len__(self):
        return len(self.values)


class CompressedBlock(PakBaseObject):
    def _deserialise(self, *args):
        self._newField('start', self.stream.readUInt64())
        self._newField('end', self.stream.readUInt64())

        data_stream = MemoryStream(self.stream, self.start, self.end - self.start)
        self._load_data(data_stream)

    def _load_data(self, stream: MemoryStream):
        method = self.parent.parent.compression_method
        compressed_data = stream.readBytes(len(stream))

        if method == COMPRESSION_NONE:
            self._newField('data', compressed_data)
        elif method == COMPRESSION_ZLIB:
            self._newField('data', zlib.decompress(compressed_data))
        else:
            raise RuntimeError('A record uses an unsupported compression method.')