import hashlib
import logging
import os


some_bytes = b'x21'


class Upload():
    def __init__(self, filename) -> None:
        self.filename = filename
        self.fd = open(filename, "rb")
        self.size = os.path.getsize(filename)


up = Upload(
    "/home/oem/Desktop/Universidad/DistribuidosLab/Iceflix/Iceflix/hola.txt")

print(up.fd.read().decode("utf-8"))

class Vids():
    def __init__(self, name, tags) -> None:
        self.name = name
        self.tags = tags

print("Títulos encontrados:")
i = 0
vids = [Vids("hola", ["hola", "mundo"]), Vids("adios", ["adios", "mundo"])]
for vid in vids:
    print(str(i) + ": " + vid.name
          + ". Tags: " + str(vid.tags))
    i += 1
