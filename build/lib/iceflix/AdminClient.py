#!/usr/bin/env python3

# pylint: disable=C0411
# pylint: disable=C0113
# pylint: disable=E0401
# pylint: disable=C0103
# pylint: disable=C0413
# pylint: disable=R0801
# pylint: disable=W0201
# pylint: disable=C0301
# pylint: disable=R1702
# pylint: disable=C0303
# pylint: disable=W1201
# pylint: disable=R0912
# pylint: disable=R0915
# pylint: disable=E1101
# pylint: disable=W0613

"""Módulo principal del admin del cliente
    Raises:
        ValueError: Error de valor
"""


import logging
import os
import random
import Ice
import time
import sys
import hashlib
import Client
import threading
import IceStorm

Ice.loadSlice("iceflix/iceflix.ice")

import IceFlix


logging.basicConfig(level=logging.NOTSET)

mains = []
event = threading.Event()

def menu():
    """Menu de opciones

    Raises:
        ValueError: Opción no válida

    Returns:
        Int: opción elegida
    """    
    print("\n")
    print("Seleccione una opción:")
    print("1. Añadir usuario")
    print("2. Eliminar usuario")
    print("3. Editar un título")
    print("4. Subir un archivo")
    print("5. Borrar un archivo")
    print("6. Ver eventos de IceStorm")
    print("7. Salir")

    opcion = input("Opción: ")
    print()
    if not opcion.isdigit() or int(opcion) not in range(1, 8):
        raise ValueError
    return int(opcion)

def menu_monitorizacion():
    """Menu de opciones

    Raises:
        ValueError: Error de valor

    Returns:
        Opcion: Opcion elegida
    """
    print("\n")
    print("Seleccione una opción:")
    print("1. Nuevos anuncios")
    print("2. Nuevos CatalogUpdates")
    print("3. Nuevos MediaUpdates")
    print("4. Nuevos FileAvailabilities")
    print("5. Salir")


    opcion = input("Opción: ")
    print()
    if not opcion.isdigit() or int(opcion) not in range(1, 6):
        raise ValueError
    return int(opcion)
class FileUploaderI(IceFlix.FileUploader):
    """Clase FileUploaderI, Sirviente de FileUploader

    Args:
        IceFlix (Modulo): Interfaz utilizada
    """    
    
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")

    def receive(self, size, current=None):
        """Función que recibe el archivo

        Args:
            size (Int): Tamano del archivo
            current (Cualquiera, optional): Cualquiera. Defaults to None

        Returns:
            String: Archivo
        """        
        return self.fd.read(size)

    def close(self, current=None):
        """Cierra el archivo

        Args:
            current (None, optional): None. Defaults to None.
        """        
        self.file.close()

class FileAvailabilityI(IceFlix.FileAvailabilityAnnounce):
    
    """Clase FileAvailabilityI: Clase que se encarga de anunciar al servidor de los archivos disponibles"""
    def __init__(self):
        super().__init__()
        self.verbose = False
        
    """Función que activa el verbose"""
    def set_verbose(self, verbose, current=None):
        self.verbose = verbose
    
    """Función que anuncia los archivos disponibles"""
    def announceFiles(self, mediaIds, serviceId, current=None):
        if self.verbose:
            print("Archivos anunciados: " + mediaIds + " en el servicio: " + serviceId)

class CatalogUpdateI(IceFlix.CatalogUpdate):
    
    """Clase CatalogUpdateI: Clase que se encarga de anunciar los updates del catalogo"""
    
    def __init__(self) -> None:
        super().__init__()
        self.verbose = False
    
    """Función que activa el verbose"""
    def set_verbose(self, verbose, current=None):
        self.verbose = verbose
        
    def renameTile(self, mediaId, newName, serviceId, current=None):
        if self.verbose:
            logging.info("Renombrando titulo: " + mediaId + " a: " + newName + " en el servicio: " + serviceId)
    def addTags(self, mediaId, user, tags, serviceId, current=None):
        if self.verbose:
            logging.info("Añadiendo etiquetas: " + tags + " a: " + mediaId + " en el servicio: " + serviceId)
    def removeTags(self, mediaId, user, tags, serviceId, current=None):
        if self.verbose:
            logging.info("Eliminando etiquetas: " + tags + " a: " + mediaId + " en el servicio: " + serviceId)        
        


class UserUpdateI(IceFlix.UserUpdate):
    
    """Clase UserUpdateI: Clase que se encarga de anunciar los updates de los usuarios"""
    
    def __init__(self) -> None:
        super().__init__()
        self.verbose = False
    
    def set_verbUserUpdate(self, verbose, current=None):
        self.verbose = verbose
        
    def newToken(self, user, token, serviceId, current=None):
        if self.verbose:
            logging.info("Nuevo token: " + token + " para el usuario: " + user + " en el servicio: " + serviceId)
    def revokeToken(self, token, serviceId, current=None):
        if self.verbose:
            logging.info("Token revocado: " + token + " en el servicio: " + serviceId)
    def newUser(self, user, passwordHash, serviceId, current=None):
        if self.verbose:
            logging.info("Nuevo usuario: " + user + " en el servicio: " + serviceId)
    def removeUser(self, user, serviceId, current=None):
        if self.verbose:
            logging.info("Usuario eliminado: " + user + " en el servicio: " + serviceId)

class AnnouncemntI(IceFlix.Announcement):
    """Clase AnnouncemntI: Clase que se encarga de anunciar al servidor principal"""

    def __init__(self):
        self.verbose = False
    
    """Función que activa el verbose"""
    
    def set_verbose(self, verbose, current=None):
        self.verbose = verbose
            
    def announce(self, service, srvId, current=None):
        if service.ice_isA("::IceFlix::Main"):
            if service not in mains:
                mains.append(IceFlix.MainPrx.uncheckedCast(service))
                logging.info("Servidor principal conectado con id: " + srvId)
                event.set()
            if self.verbose:
                logging.info("Nuevo main: " + srvId)
        
        if service.ice_isA("::IceFlix::FileService"):
            if self.verbose:
                logging.info("Nuevo servicio de ficheros: " + srvId)
        if service.ice_isA("::IceFlix::MediaCatalog"):
            if self.verbose:
                logging.info("Nuevo servicio de catálogo: " + srvId)
        if service.ice_isA("::IceFlix::Authenticator"):
            if self.verbose:
                logging.info("Nuevo servicio de autenticación: " + srvId)
        


class Cliente(Ice.Application):

    """Clase cliente, cliente de IceFlix, implementa los métodos necesarios para el usuario
    """    
    
    auth_prx = ""
    Cliente_prx = ""
    ex = False

    def cerrar(self):
    
        while True:
            
            if not mains:
                logging.error("TIEMPO EXCEDIDO: No hay servidores principales disponibles")
                event.set()
                break
            if mains:
                break
    def renovar_main(self):
        while True:
            self.Cliente_ice_prx = random.choice(mains)
            if self.ex:
                break 

    def run(self, args):
        """Ejecuta el cliente

        Args:
            args (String): Argumentos de entrada
        """        
        # Creamos el proxy del objeto remoto
        print("Está intentando acceder al modo administrador")
        salir = False
        opcion = 0
        
        
        broker = self.communicator()
        adapter_ann = broker.createObjectAdapter("AnnouncementAdapter")
        adapter_ann.activate()
        
        adapter_usr = broker.createObjectAdapter("UserUpdateAdapter")
        adapter_files = broker.createObjectAdapter("FileUpdateAdapter")
        adapter_med = broker.createObjectAdapter("MediaCatalogAdapter")
        
        adapter_usr.activate()
        adapter_med.activate()
        adapter_files.activate()
        
        #  try:
        #     topic_manager = IceStorm.TopicManagerPrx.checkedCast(n_proxy)
        # except Ice.ConnectionRefusedException:
        #     print("No se ha podido conectar con el Topic Manager, intentando reconectar...")
        #     time.sleep(5)
        #     try:
        #         topic_manager = IceStorm.TopicManagerPrx.checkedCast(n_proxy)
        #     except Ice.ConnectionRefusedException:
        #         print("No se ha podido reconectar, pruebe más tarde...")
        #         return 0
        
        n_proxy = broker.propertyToProxy("IceStorm.TopicManager")
        
        try:
            topic_manager = IceStorm.TopicManagerPrx.checkedCast(n_proxy)
        except Ice.ConnectionRefusedException:
            print("No se ha podido conectar con el Topic Manager, intentando reconectar...")
            time.sleep(5)
            try:
                topic_manager = IceStorm.TopicManagerPrx.checkedCast(n_proxy)
            except Ice.ConnectionRefusedException:
                print("No se ha podido reconectar, pruebe más tarde...")
                return 0
        
        usr_topic = topic_manager.retrieve("UserUpdates")
        usr_ser = UserUpdateI()
        
        usr_upPrx = adapter_usr.addWithUUID(usr_ser)
        usr_topic.subscribeAndGetPublisher({},usr_upPrx)
        
        cat_topic = topic_manager.retrieve("CatalogUpdates")
        cat_ser = CatalogUpdateI()
        
        cat_upPrx = adapter_med.addWithUUID(cat_ser)
        cat_topic.subscribeAndGetPublisher({},cat_upPrx)
        
        file_topic = topic_manager.retrieve("FileAvailabilityAnnounces")
        file_ser = FileAvailabilityI()
        
        file_upPrx = adapter_files.addWithUUID(file_ser)
        file_topic.subscribeAndGetPublisher({},file_upPrx)
        
        announcement_topic = topic_manager.retrieve("Announcements")
        annnoun_ser = AnnouncemntI()
        
        announPrx = adapter_ann.addWithUUID(annnoun_ser)
        announcement_topic.subscribeAndGetPublisher({},announPrx)
        

        # Cliente_prx = self.communicator().propertyToProxy("Cliente_prx")
        adapter = self.communicator().createObjectAdapter("FileUploaderAdapter")
        adapter.activate()
        
        if not mains:
            print("Esperando al servidor principal...")
            self.hi = threading.Timer(15.0,function=self.cerrar)
            self.hi.start()
            event.wait()

        if not mains:
            return 0
        
        
        re_main = threading.Timer(10.0,function=self.renovar_main)
        re_main.start()
        try:
            Cliente_ice_prx = IceFlix.MainPrx.uncheckedCast(random.choice(mains))
            print("[*] Conectado al servidor")
            print("Proxy main utilizado: ", Cliente_ice_prx)

        except:
            logging.error("No se pudo conectar...")
            Cliente_ice_prx = Client.reconectar(random.choice(mains))
            if not Cliente_ice_prx:
                print("Imposible reconectar")
                salir = True
        
        if not salir:
            tk_admin = input("Introduzca el token de administrador: ")
        

        if not salir:
            try:
                self.auth_prx = IceFlix.AuthenticatorPrx.checkedCast(
                Cliente_ice_prx.getAuthenticator())
            except IceFlix.TemporaryUnavailable:
                logging.error("Servidor temporalmente no disponible")
                salir = True

        if not salir:  
            es_admin = self.auth_prx.isAdmin(tk_admin)
            if not es_admin:
                print("No tiene permisos de administrador")
                salir = True
            
        
        if not salir:
            print("Bienvenido al modo administrador")
            

            while opcion != 7:
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
                        logging.error(
                        "El servidor no está disponible en este momento")
                    except IceFlix.Unauthorized:
                        logging.error(
                        "No tiene permisos para realizar esta acción")

                elif opcion == 2:
                    usr = input("Introduzca el nombre de usuario: ")

                    try:
                        self.auth_prx.removeUser(usr, tk_admin)
                        print("Usuario borrado")
                    except IceFlix.TemporaryUnavailable:
                        logging.error(
                        "El servidor no está disponible en este momento")
                    except IceFlix.Unauthorized:
                        logging.error(
                        "No tiene permisos para realizar esta acción")

                elif opcion == 3:
                    try:

                        catalog_proxy = IceFlix.AuthenticatorPrx.checkedCast(
                            Cliente_ice_prx.getCatalog())
                        vids = Client.buscarNombre(catalog_proxy, tk_admin)
                        Client.mostrarVids(vids)
                        vid = input("Introduzca el vídeo a editar(número):\nVídeos: "+ str(
                        list(range(len(vids)))))
                        nombre = input("Introduzca el nuevo nombre: ")
                        nombre = nombre+".mp4"

                        try:
                            catalog_proxy.renameTile(vid.mediaId, nombre, tk_admin)
                        except IceFlix.Unauthorized:
                            logging.error(
                            "No tiene permisos para realizar esta acción")
                        except IceFlix.WrongMediaId:
                            logging.error("El id del vídeo no es válido")

                    except IceFlix.TemporaryUnavailable:
                        logging.error(
                        "El servidor no está disponible en este momento")

                elif opcion == 4:
                    ruta = input("Introduzca la ruta del archivo: \n")
                    if not os.path.isfile(ruta):
                        logging.error("El archivo debe ser un fichero")
                    else:
                        uploader = FileUploaderI(ruta)
                        prx_ad = adapter.addWithUUID(uploader)
                        prx_uploader = IceFlix.FileUploaderPrx.checkedCast(
                        prx_ad)
                        try:
                            prx_fs = IceFlix.FileServicePrx.checkedCast(
                            Cliente_ice_prx.getFileService())
                            prx_fs.uploadFile(prx_uploader, tk_admin)
                            print("Archivo subido")
                        except IceFlix.Unauthorized:
                            logging.error(
                            "No tiene permisos para realizar esta acción")
                        except IceFlix.TemporaryUnavailable:
                            logging.error(
                            "El servidor no está disponible en este momento")
                        except Ice.ConnectionRefusedException:
                            logging.error("No se pudo conectar con el servidor")
                            opcion = 7

                elif opcion == 5:
                    try:
                        catalog_proxy = IceFlix.MediaCatalogPrx.checkedCast(
                        Cliente_ice_prx.getCatalog())
                        vids = Client.buscarNombre(catalog_proxy, "def")
                        Client.mostrarVids(vids)
                        vid = input(
                        "Introduzca el fichero del vídeo a eliminar:\nVídeos: " + str(list(range(len(vids)))))
                        pro_prx = IceFlix.FileServicePrx.checkedCast(
                                        self.vids[vid].provider)
                        pro_prx.removeFile(vids[vid].mediaId, tk_admin)
                        print("Archivo eliminado")
                    except IceFlix.Unauthorized:
                        logging.error(
                        "No tiene permisos para realizar esta acción")
                    except IceFlix.WrongMediaId:
                        logging.error("El id del vídeo no es correcto")
                    except IceFlix.TemporaryUnavailable:
                        logging.error(
                        "El servidor no está disponible en este momento")
                    except Ice.ConnectionRefusedException:
                        logging.error("No se pudo conectar con el servidor")
                        opcion = 7

                elif opcion == 6:
                    
                    local_verbose = True
                    
                    while opcion != 5:
                        try:
                
                            opcion = menu_monitorizacion()
                        except ValueError:
                            logging.error("Opción no válida")
                        
                        if opcion == 1:
                            
                            annnoun_ser.set_verbose(local_verbose)
                            input("Pulse intro para cerrar...\n")
                            local_verbose = False
                            annnoun_ser.set_verbose(local_verbose)
                            
                        elif opcion == 2:
                            usr_ser.set_verbUserUpdate(local_verbose)
                            input("Pulse intro para cerrar...\n")
                            local_verbose = False
                            usr_ser.set_verbUserUpdate(local_verbose)

                        elif opcion == 3:
                            cat_ser.set_verbose(local_verbose)
                            input("Pulse intro para cerrar...\n")
                            local_verbose = False
                            cat_ser.set_verbose(local_verbose)
                    
                        elif opcion == 4:
                            file_ser.set_verbose(local_verbose)
                            input("Pulse intro para cerrar...\n")
                            local_verbose = False
                            file_ser.set_verbose(local_verbose)
                        
  
                    time.sleep(1)
                    print("[!] Cerrado")
                            
                
                elif opcion == 7:
                    print("[!] Saliendo...")
                    
                    cat_topic.unsubscribe(cat_upPrx)
                    usr_topic.unsubscribe(usr_upPrx)
                    file_topic.unsubscribe(file_upPrx)
                    announcement_topic.unsubscribe(announPrx)
                    self.ex = True

                    
        else:
            print("[!] No es posible conectarse (Servicio no disponible o token de administrador no válido)")

if __name__ == '__main__':
    APP = Cliente()
    sys.exit(APP.main(sys.argv))
