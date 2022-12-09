#!/usr/bin/env python3


import getpass
import logging
import os
import Ice
import time
import sys
import hashlib
import Client

Ice.loadSlice("iceflix/iceflix.ice")
import IceFlix

def menu():

    print("\n")
    print("Seleccione una opción:")
    print("1. Añadir usuario")
    print("2. Eliminar usuario")
    print("3. Editar un título")
    print("4. Subir un archivo")
    print("5. Borrar un archivo")
    print("6. Salir")

    opcion = input("Opción: ")
    print()
    if not opcion.isdigit() or int(opcion) not in range(1, 7):
        raise ValueError
    return int(opcion)

class FileUploaderI(IceFlix.FileUploader):
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")

    def receive(self, size, current=None):
        return self.fd.read(size)
    
    def close(self, current=None):
        self.file.close()
        

class Cliente(Ice.Application):

    auth_prx = ""
    def run(self, argv):

        # Creamos el proxy del objeto remoto
        print("Está usted en el modo admin")
        
        opcion = 0
        Cliente_prx = self.communicator().propertyToProxy("Cliente_prx")
        adapter = self.communicator().createObjectAdapter("FileUploaderAdapter")
        adapter.activate()
        try:
            Cliente_ice_prx = IceFlix.MainPrx.checkedCast(Cliente_prx)
            print("[*] Conectado al servidor")

        except:
            logging.error("No se pudo conectar...")
            Cliente_ice_prx = Client.reconectar(Cliente_prx)
            if not Cliente_ice_prx:
                exit(1)
                
        tk_admin = input("Introduzca el token de administrador: ")
        tk_admin = hashlib.sha256(tk_admin.encode('utf-8')).hexdigest()
        
        try:
            self.auth_prx = Cliente_ice_prx.getAuthenticator()
        except IceFlix.TemporaryUnavailable:
            logging.error("Servidor temporalmente no disponible")
            exit(1)
            
        es_admin = self.auth_prx.isAdmin(tk_admin)
        if not es_admin:
            print("No tiene permisos de administrador")
            exit(1)
        
        while opcion != 6:
            try:
                opcion = menu()
            except ValueError:
                logging.error("Opción no válida")
            
            if opcion == 1:
                usr, contr = Client.login()
                contr = hashlib.sha256(contr.encode('utf-8')).hexdigest()
                try:
                    self.auth_prx.addUser(usr, contr, tk_admin)
                    print("Usuario añadido")
                except IceFlix.TemporaryUnavailable:
                    logging.error("El servidor no está disponible en este momento")
                except IceFlix.Unauthorized:
                    logging.error("No tiene permisos para realizar esta acción") 
                
            elif opcion == 2:
                usr = input("Introduzca el nombre de usuario: ")
               
                try:
                    self.auth_prx.removeUser(usr, tk_admin)
                    print("Usuario borrado")
                except IceFlix.TemporaryUnavailable:
                    logging.error("El servidor no está disponible en este momento")
                except IceFlix.Unauthorized:
                    logging.error("No tiene permisos para realizar esta acción")   
            
            elif opcion == 3:
                try:
                    
                    catalog_proxy = Cliente_ice_prx.getCatalog()
                    vids = Client.buscarNombre(catalog_proxy, tk_admin)
                    Client.mostrarVids(vids)
                    vid = input("Introduzca el vídeo a editar:\nVídeos: ", str(list(range(len(vids)))))
                    nombre = input("Introduzca el nuevo nombre: ")
                    nombre = nombre+".mp4"
                    
                    try:
                        catalog_proxy.renameTile(vid.mediaId,nombre,tk_admin)
                    except IceFlix.Unauthorized:
                        logging.error("No tiene permisos para realizar esta acción")
                    except IceFlix.WrongMediaId:
                        logging.error("El id del vídeo no es válido")
                    
                    
                except IceFlix.TemporaryUnavailable:
                    logging.error("El servidor no está disponible en este momento")
                    
            elif opcion == 4:
                ruta = input("Introduzca la ruta del archivo: \n")
                if not ruta.endswith(".mp4") or not os.path.isfile(ruta):
                    logging.error("El archivo debe ser un .mp4")
                else:
                    uploader = FileUploaderI(ruta)
                    prx_uploader = adapter.addWithUUID(uploader)
                    prx_uploader = IceFlix.FileUploaderPrx.checkedCast(prx_uploader)
                    try:
                        prx_fs = Cliente_ice_prx.getFileService()
                        prx_fs.uploadFile(prx_uploader, tk_admin)
                        print("Archivo subido")
                    except IceFlix.Unauthorized:
                        logging.error("No tiene permisos para realizar esta acción")
                    except IceFlix.TemporaryUnavailable:
                        logging.error("El servidor no está disponible en este momento")
                        
            elif opcion == 5:
                try:
                    catalog_proxy = Cliente_ice_prx.getCatalog()
                    vids = Client.buscarNombre(catalog_proxy, None)
                    Client.mostrarVids(vids)
                    vid = input("Introduzca el nombre del vídeo a eliminar:\nVídeos: " + str(list(range(len(vids)))))
                    file_provider = vids[vid].provider
                    file_provider.removeFile(vids[vid].mediaId, tk_admin)
                except IceFlix.Unauthorized:
                    logging.error("No tiene permisos para realizar esta acción")
                except IceFlix.WrongMediaId:
                    logging.error("El id del vídeo no es correcto")
                except IceFlix.TemporaryUnavailable:
                    logging.error("El servidor no está disponible en este momento")
                    
            elif opcion == 6:
                print("[!] Saliendo...")
                time.sleep(1)

if __name__ == '__main__':
    APP = Cliente()
    sys.exit(APP.main(sys.argv))