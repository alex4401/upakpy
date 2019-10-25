import sys

from thirdparty.purlovia.ue.stream import MemoryStream

from .archive import PakFile


def from_file(filename: str) -> PakFile:
    fp = open(filename, "rb")
    data = fp.read()
    mem = memoryview(data)

    stream = MemoryStream(mem)
    return PakFile(stream).deserialise()


def main():
    filename = sys.argv[1]
    pak = from_file(filename)
