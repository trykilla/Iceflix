import os


some_bytes = b'x21'

class Upload():
    def __init__(self,filename) -> None:
        self.filename = filename
        self.fd = open(filename, "rb")
        self.size = os.path.getsize(filename)
        
up = Upload("/home/oem/Desktop/Universidad/DistribuidosLab/Iceflix/Iceflix/hola.txt")

print(up.fd.read().decode("utf-8"))