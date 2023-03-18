from abc import ABCMeta
from collections.abc import ByteString, Sequence


class NonStrSequence(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStrSequence:
            if issubclass(C, (ByteString, str)):
                return False
            return issubclass(C, Sequence)
        return NotImplemented
