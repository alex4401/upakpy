from typing import *
from thirdparty.purlovia.ue.stream import MemoryStream

class PakBaseObject(object):
    def __init__(self, owner: "PakBaseObject", stream=None):
        assert owner is not None, "Owner must be specified"
        self.stream: MemoryStream = stream or owner.stream
        self.field_values: Dict[str, Any] = {}
        self.start_offset: Optional[int] = None
        self.is_serialising = False
        self.is_serialised = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'deserialise' in vars(cls):
            raise TypeError('Cannot override "deserialise"')

    def deserialise(self, *args, **kwargs):
        if self.is_serialising:
            return

        if self.is_serialised:
            # return
            raise RuntimeError(f'Deserialise called twice for "{self.__class__.__name__}"')

        self.start_offset = self.stream.offset
        self.is_serialising = True
        self._deserialise(*args, **kwargs)
        self.is_serialising = False
        self.is_serialised = True
        return self

    def _deserialise(self, *args, **kwargs):
        raise NotImplementedError(f'Type "{self.__class__.__name__}" must implement a parse operation')

    def _newField(self, name: str, value, *extraArgs):
        '''Internal method used by subclasses to define new fields.'''
        if name in self.field_values:
            raise NameError(f'Field "{name}" is already defined')

        self.field_values[name] = value

        if isinstance(value, PakBaseObject) and not value.is_serialised:
            value.deserialise(*extraArgs)
        
    def __eq__(self, other):
        return self is other  # only the same object is considered the equal

    def __hash__(self):
        return id(self)  # use the id (memory address) so each item is unique

    def __getattr__(self, name: str):
        '''Override property accessor to allow reading of defined fields.'''
        try:
            return self.field_values[name]
        except KeyError:
            raise AttributeError(f'No field named "{name}"')