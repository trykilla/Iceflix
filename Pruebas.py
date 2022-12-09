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


videos = []
videos = ["Video 1", "video 2", "video 3", "video 4"]
print(videos.__str__())
try:
    vid = input("Introduzca el nombre del vídeo a descargar:\nVídeos: " +
                str(list(range(len(videos)))))
    print(videos[int(vid)])
except IndexError:
    print("El vídeo no existe")
    logging.error("El vídeo no existe")
except ValueError:
    logging.error("El vídeo no existe(solo números)")

print("hola")
res = input("¿Desea realizar una búsqueda de término exacto? (s/n): ")
exacta = False
exacta = bool(res == "s")
print(exacta)
