from .base import PakBaseObject
from .consts import PAK_MAGIC_NUMBER, PAK_INDEX_SIZE
from .coretypes import CompressedBlock, Guid, String, Table


class PakFile(PakBaseObject):
    def __init__(self, stream):
        super().__init__(self, stream)

    def _deserialise(self, *args):
        self.stream.offset = self.stream.size - PAK_INDEX_SIZE

        self._newField('key_guid', Guid(self))
        self._newField('is_index_encrypted', self.stream.readUInt8())
        assert not self.is_index_encrypted
        self._newField('magic', self.stream.readUInt32())
        assert self.magic == PAK_MAGIC_NUMBER
        self._newField('version', self.stream.readUInt32())
        self._newField('index_offset', self.stream.readUInt64())
        self._newField('index_size', self.stream.readInt64())
        self._newField('index_sha1', self.stream.readBytes(20))

        self.stream.offset = self.index_offset
        self._newField('mount_point', String(self))
        self._newField('entry_count', self.stream.readInt32())
        self._newField('records',
                       Table(self).deserialise(PakRecord, self.entry_count))


class PakRecord(PakBaseObject):
    def _deserialise(self, *args):
        self._newField('name', String(self))
        self._newField('offset', self.stream.readUInt64())
        self._newField('compressed_size', self.stream.readUInt64())
        self._newField('uncompressed_size', self.stream.readUInt64())
        self._newField('compression_method', self.stream.readUInt32())
        self._newField('sha1', self.stream.readBytes(20))
        if self.compression_method != 0:
            self._newField('compressed_blocks', Table(self).deserialise(CompressedBlock, self.stream.readInt32()))
        self._newField('is_encrypted', self.stream.readBool8())
        assert not self.is_encrypted
        self._newField('compressed_block_size', self.stream.readUInt32())
