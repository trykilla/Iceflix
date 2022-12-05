#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import getpass
import logging
import Ice
import time
import sys
import hashlib

Ice.loadSlice("iceflix/iceflix.ice")
import IceFlix

MAXINT = 3
SEGDORMIR = 5.0


def menu():

    print("\n")
    print("Seleccione una opción:")
    print("1. Iniciar sesión")
    print("2. Buscar en catálogo")
    print("3. Editar catálogo")
    print("4. Cerrar sesión")
    print("5. Salir")

    opcion = input("Opción: ")
    print()
    if not opcion.isdigit() or int(opcion) not in range(1, 6):
        raise ValueError
    return int(opcion)


def login():
    usr = input("Usuario: ")
    contr = getpass.getpass("Contraseña: ")
    contr_hash = hashlib.sha256(contr.encode('utf-8')).hexdigest()
    return usr, contr_hash


def reconectar(prx):
    logging.info("Reconectando...")
    i = 0
    new_prx = None
    while not new_prx and i < MAXINT:
        time.sleep(SEGDORMIR)
        try:
            new_prx = IceFlix.MainPrx.checkedCast(prx)
        except Exception:
            logging.error("Reconexión fallida...\nIntentando de nuevo...")
        i += 1
    return new_prx


def buscarNombre(prx_catalogo, usr_tk):

    videos = []
    nombre_vid = input("Introduzca el nombre de la película/vídeo: ")
    res = input("¿Desea realizar una búsqueda de término exacto? (s/n): ")
    exacta = False
    if res == "s":
        exacta = True
    else:
        exacta = False    
    vidsId = prx_catalogo.getTilesByName(nombre_vid, exacta)
    if vidsId == []:
        logging.info("No se han encontrado resultados")
    else:
        try:
            for vids in vidsId:
                videos.append(prx_catalogo.getTile(vids,usr_tk))
            return videos
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.TemporallyUnavailable:
            logging.error("El vídeo no está disponible")


    


def buscarTag(prx_catalogo, usr_tk):
    
    vids = []
    videos = []
    vidsId = []
    todos = False
    tags = input("Introduzca los tags a buscar, sepáralos con una barra (/): ")
    tags = tags.split("/")
    res = input("¿Desea realizar una búsqueda con todos los tags? (s/n): ")
    if res == "s":
        todos = True
    else:
        todos = False

    
    vids = prx_catalogo.getTilesByTag(tags, todos, usr_tk)
    
    
    for i in vids:
        vidsId.append(i)
        
    if vidsId == []:
        logging.info("No se han encontrado resultados")
    else:
        try:
            for vids in vidsId:
                videos.append(prx_catalogo.getTile(vids,usr_tk))
            return videos
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.TemporallyUnavailable:
            logging.error("El vídeo no está disponible")


    
        
    
    return vids

def mostrarVids(vids):
    print("Títulos encontrados:")
    for i in vids:
        print(str(i.info.name) + " - " + str(i.info.tags))

def editarCatalogo(prx_catalogo, vid, tkn):
    opcion = input("Añadir o eliminar tag? (a/e): ")
    if opcion == "a":
        tags = input("Introduzca los tags a añadir: ")
        try:
            prx_catalogo.addTags(vid.mediaId, tags, tkn)
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        
        
    if opcion == "e":
        tags = input("Introduzca los tags a eliminar: ")
        try:
            prx_catalogo.removeTags(vid.mediaId, tags, tkn)
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")

            

class Cliente(Ice.Application):

    usr = None
    contra = None
    usr_tok = ""
    vids = []
    log_prx = None
    catalog_proxy = None
    
    def run(self, argv):
        catalogo = ""
        vids = []
        opcion = 0
        Cliente_prx = self.communicator().stringToProxy(argv[1])

        try:
            Cliente_ice_prx = IceFlix.MainPrx.checkedCast(Cliente_prx)
            print("[*] Conectado al servidor")

        except:
            logging.error("No se pudo conectar...")
            Cliente_ice_prx = reconectar(Cliente_prx)
            if not Cliente_ice_prx:
                exit(1)

        while opcion != 5:
            try:
                if self.usr_tok != "":
                    print("Hay una sesión iniciada")
                opcion = menu()
            except ValueError:
                logging.error("Opción inválida")
            if opcion == 1:
                self.usr, self.contra = login()
                try:
                    self.log_prx = Cliente_ice_prx.getAuthenticator()
                    self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                    
                except IceFlix.TemporaryUnavailable:
                    logging.error("Servicio no disponible")
                except IceFlix.Unauthorized:
                    self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                    logging.error("Usuario o contraseña incorrectos")

            if opcion == 2:
                try:
                    self.catalog_proxy = Cliente_ice_prx.getCatalog()
                    buscar = input("¿Quiere buscar por nombre o por tag?\n1. Nombre\n2. Tag\n")
                    if buscar == "1":
                        try:
                            self.vids = buscarNombre(self.catalog_proxy,self.usr_tok)
                        except IceFlix.Unauthorized:
                            self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                            logging.error("No tiene permisos para realizar la búsqueda")
                    if self.usr_tok != "":
                        if buscar == "2":
                            try:
                                vids = buscarTag(self.catalog_proxy, self.usr_tok)
                            except IceFlix.Unauthorized:
                                self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                                logging.error("No tiene permisos para realizar la búsqueda")
                    else:
                        print("Para buscar por tags debes iniciar sesión.")
                    
                    if self.vids != []:
                        mostrarVids(vids)
                        op = input("¿Desea descargar algún vídeo? (s/n): ")
                        if op == "s":
                            if self.usr_tok != "":
                                vid = input("Introduzca el vídeo a descargar:\nVídeos: " + str(list(range(len(vids)))))
                                pro_prx = self.vids[vid].provider
                                fi_hand_prx = pro_prx.openFile(self.vids[vid].mediaId, self.usr_tok)
                                arch = fi_hand_prx.receive(4096, self.usr_tok)
                                bin_file = open(self.vids[vid].info.name, "wb")
                                bin_file.write(arch)
                                bin_file.close()
                            else:
                                print("Para descargar vídeos debes iniciar sesión.")
                        else:
                            print("Volviendo al menú principal...")
                            time.sleep(1)     
                             
                except IceFlix.TemporaryUnavailable:
                    logging.error("Servicio no disponible")
                except IceFlix.Unauthorized:
                    self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                    logging.error("Token incorrectos")
                    
                except IceFlix.WrongMediaId:
                    logging.error("Id incorrecto")
                    
            if opcion == 3:
                seguir = True
                if self.usr_tok == "":
                    logging.error(
                        "No hay sesión iniciada, debe iniciar sesión para poder editar el catálogo")
                    seguir = False
                if self.vids == []:
                    logging.error(
                        "No ha seleccionado ningún título, debe buscar un vídeo para poder editar el catálogo")
                    seguir = False
                
                if seguir:
                    op = input("Vídeo que desea editar:\nVídeos: ", str(list(range(len(self.vids)))))
                    try:
                        editarCatalogo(self.catalog_proxy, self.vids[op], self.usr_tok)
                    except IceFlix.Unauthorized:
                        self.usr_tok = self.log_prx.refreshAuthorization(self.usr, self.contra)
                        logging.error("No tiene permisos para editar el catálogo")
                else:
                    print("Volviendo al menú principal...")
                    time.sleep(1)
                

            if opcion == 4:
                if self.usr_tok == "":
                    logging.error("No hay sesión iniciada")
                else:
                    self.usr_tok = ""
                    print("Sesión cerrada")
                time.sleep(0.5)
            if opcion == 5:
                print("[!] Saliendo...")
                time.sleep(0.5)


if __name__ == "__main__":
    APP = Cliente()
    sys.exit(APP.main(sys.argv))
