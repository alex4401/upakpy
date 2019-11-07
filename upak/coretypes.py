import struct
import uuid
from typing import *

from .base import PakBaseObject


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
