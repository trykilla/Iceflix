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
"""Módulo principal del cliente
    Raises:
        ValueError: Error de valor
"""

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
    """Menu de opciones

    Raises:
        ValueError: Error de valor

    Returns:
        Opcion: Opcion elegida
    """
    print("\n")
    print("Seleccione una opción:")
    print("1. Iniciar sesión")
    print("2. Buscar en catálogo")
    print("3. Editar catálogo")
    print("4. Acceder a una búsqueda reciente")
    print("5. Cerrar sesión")
    print("6. Salir")

    opcion = input("Opción: ")
    print()
    if not opcion.isdigit() or int(opcion) not in range(1, 7):
        raise ValueError
    return int(opcion)


def login():
    """Método para iniciar sesión

    Returns:
        String: Devuelve el usuario y la contraseña
    """
    usr = input("Usuario: ")
    contr = getpass.getpass("Contraseña: ")
    contr_hash = hashlib.sha256(contr.encode('utf-8')).hexdigest()
    return usr, contr_hash


def reconectar(prx):
    """Método para reconectar

    Args:
        prx (Proxy): Proxy del objeto remoto

    Returns:
        Proxy: Nuevo proxy del objeto remoto
    """
    logging.info("Reconectando...")
    i = 0
    new_prx = None
    while not new_prx and i < MAXINT:
        time.sleep(SEGDORMIR)
        try:
            new_prx = IceFlix.MainPrx.checkedCast(prx)
        except Ice.ConnectionRefusedException:
            logging.error("Reconexión fallida...\nIntentando de nuevo...")
        i += 1
    return new_prx


def buscarNombre(prx_catalogo, usr_tk):
    """Método para buscar por nombre

    Args:
        prx_catalogo (proxy): proxy del objeto remoto
        usr_tk (String): token del usuario

    Returns:
        Lista: Lista de vídeos
    """

    videos = []
    nombre_vid = input("Introduzca el nombre de la película/vídeo: ")
    res = input("¿Desea realizar una búsqueda de término exacto? (s/n): ")

    exacta = bool(res == "s")

    vidsId = prx_catalogo.getTilesByName(nombre_vid, exacta)
    if vidsId:
        try:
            for vids in vidsId:
                videos.append(prx_catalogo.getTile(vids, usr_tk))
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.TemporallyUnavailable:
            logging.error("El vídeo no está disponible")

    return videos


def buscarTag(prx_catalogo, usr_tk):
    """Buscar por tag

    Returns:
        Lista: lista de vídeos
    """

    videos = []
    vidsId = []

    tags = input("Introduzca los tags a buscar, sepáralos con una barra (/): ")
    tags = tags.split("/")
    res = input("¿Desea realizar una búsqueda con todos los tags? (s/n): ")
    todos = bool(res == "s")

    vidsId = prx_catalogo.getTilesByTag(tags, todos, usr_tk)

    if vidsId:
        try:
            for vids in vidsId:
                videos.append(prx_catalogo.getTile(vids, usr_tk))
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.TemporallyUnavailable:
            logging.error("El vídeo no está disponible")

    return videos


def mostrarVids(vids):
    """Método para mostrar los vídeos

    Args:
        vids (Lista): Lista de vídeos
    """
    print("Títulos encontrados:")
    i = 0
    for vid in vids:
        print(str(i) + ": " + vid.info.name
              + ". Tags: " + str(vid.info.tags))
        i += 1


def editarCatalogo(prx_catalogo, vid, tkn):
    """Método para editar el catálogo

    Args:
        prx_catalogo (Proxy): Proxy del objeto remoto
        vid (Media): Vídeo
        tkn (String): Token del usuario
    """

    opcion = input("Añadir o eliminar tag? (a/e): ")
    if opcion == "a":
        tags = input("Introduzca los tags a añadir (Sepáralos con comas): ").split(",")
        try:
            prx_catalogo.addTags(vid.mediaId, tags, tkn)
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.Unauthorized:
            logging.error("No tiene permisos para editar el catálogo")

    if opcion == "e":
        tags = input("Introduzca los tags a eliminar(separados por comas): ").split(",")
        try:
            prx_catalogo.removeTags(vid.mediaId, tags, tkn)
        except IceFlix.WrongMediaId:
            logging.error("No se ha encontrado el vídeo")
        except IceFlix.Unauthorized:
            logging.error("No tiene permisos para editar el catálogo")


class Cliente(Ice.Application):

    """Clase Cliente: Ejecuta todos los métodos que necesite el usuario.
    """

    usr = None
    contra = None
    usr_tok = ""
    vids = []
    log_prx = None
    catalog_proxy = None

    def run(self, args):
        """Método que ejecuta el cliente
        """

        
        opcion = 0
        Cliente_prx = self.communicator().propertyToProxy("Cliente_prx")

        try:
            Cliente_ice_prx = IceFlix.MainPrx.checkedCast(Cliente_prx)
            print("[*] Conectado al servidor")

        except:
            logging.error("No se pudo conectar...")
            Cliente_ice_prx = reconectar(Cliente_prx)
            if not Cliente_ice_prx:
                raise SystemExit

        while opcion != 6:
            if self.vids:
                print("Tiene vídeos almacenados")
            try:
                if self.usr_tok != "":
                    print("Hay una sesión iniciada")
                opcion = menu()
            except ValueError:
                logging.error("Opción inválida")
            if opcion == 1:
                self.usr, self.contra = login()
                try:
                    self.log_prx = IceFlix.AuthenticatorPrx.checkedCast(
                        Cliente_ice_prx.getAuthenticator())
                    self.usr_tok = self.log_prx.refreshAuthorization(
                        self.usr, self.contra)

                except IceFlix.TemporaryUnavailable:
                    logging.error("Servicio no disponible")
                except IceFlix.Unauthorized:
                    self.usr_tok = self.log_prx.refreshAuthorization(
                        self.usr, self.contra)
                    logging.error("Usuario o contraseña incorrectos")

            if opcion == 2:
                try:
                    self.catalog_proxy = IceFlix.MediaCatalogPrx.checkedCast(
                        Cliente_ice_prx.getCatalog())
                    buscar = input(
                        "¿Quiere buscar por nombre o por tag?\n1. Nombre\n2. Tag\n")
                    if buscar == "1":
                        try:
                            self.vids = buscarNombre(
                                self.catalog_proxy, self.usr_tok)
                        except IceFlix.Unauthorized:
                            self.usr_tok = self.log_prx.refreshAuthorization(
                                self.usr, self.contra)
                            logging.error(
                                "No tiene permisos para realizar la búsqueda")
                    if self.usr_tok != "":
                        if buscar == "2":
                            try:
                                self.vids = buscarTag(
                                    self.catalog_proxy, self.usr_tok)
                            except IceFlix.Unauthorized:
                                self.usr_tok = self.log_prx.refreshAuthorization(
                                    self.usr, self.contra)
                                logging.error(
                                    "No tiene permisos para realizar la búsqueda")
                    else:
                        print("Para buscar por tags debes iniciar sesión.")

                    if self.vids:
                        mostrarVids(self.vids)
                        op = input("¿Desea descargar algún vídeo? (s/n): ")
                        if op == "s":
                            if self.usr_tok != "":
                                vid = int(input(
                                    "Introduzca el vídeo a descargar:\nVídeos: " + 
                                    str(list(range(len(self.vids))))))
                                try:
                                    pro_prx = self.vids[vid].provider
                                except IndexError:
                                    logging.error(
                                        "El índice introducido no existe")
                                    sys.exit(1)
                                except ValueError:
                                    logging.error(
                                        "El índice introducido no es válido (Solo números)")
                                    sys.exit(1)
                                fi_hand_prx = pro_prx.openFile(
                                    self.vids[vid].mediaId, self.usr_tok)
                                arch = fi_hand_prx.receive(4096, self.usr_tok)
                                with open (self.vids[vid].info.name, "wb") as bin_file:
                                    bin_file.write(arch)
                                bin_file.close()
                                self.vids.pop(vid)
                            else:
                                print("Para descargar vídeos debes iniciar sesión.")
                        else:
                            print("Volviendo al menú principal...")
                            time.sleep(1)
                    else:
                        logging.error("No se han encontrado vídeos")
                except IceFlix.TemporaryUnavailable:
                    logging.error("Servicio no disponible")
                except IceFlix.Unauthorized:
                    self.usr_tok = self.log_prx.refreshAuthorization(
                        self.usr, self.contra)
                    logging.error("Token incorrectos")

                except IceFlix.WrongMediaId:
                    logging.error("Id incorrecto")

            if opcion == 3:
                seguir = True
                if self.usr_tok == "":
                    logging.error(
                        "No hay sesión iniciada, debe iniciar sesión" +
                        "para poder editar el catálogo")
                    seguir = False
                if self.vids:
                    logging.error(
                        "No ha seleccionado ningún título, debe buscar" +
                        "un vídeo para poder editar el catálogo")
                    seguir = False

                if seguir:
                    
                    op = int(input("Vídeo que desea editar:\nVídeos: ",
                                   str(list(range(len(self.vids))))))
                    try:
                        editarCatalogo(self.catalog_proxy,
                                       self.vids[op], self.usr_tok)
                    except IceFlix.Unauthorized:
                        self.usr_tok = self.log_prx.refreshAuthorization(
                            self.usr, self.contra)
                        logging.error(
                            "No tiene permisos para editar el catálogo")
                    except ValueError:
                        logging.error(
                            "El índice introducido no es válido (Solo números)")
                        sys.exit(1)
                    except IndexError:
                        logging.error("El índice introducido no existe")
                        sys.exit(1)
                else:
                    print("Volviendo al menú principal...")
                    time.sleep(1)

            if opcion == 4:
                if self.vids:
                    mostrarVids(self.vids)
                    op = input("¿Desea descargar algún vídeo? (s/n): ")
                    if op == "s":
                        if self.usr_tok != "":
                            vid = input(
                                "Introduzca el vídeo a descargar:\nVídeos: " + 
                                str(list(range(len(self.vids)))))
                            try:
                                pro_prx = self.vids[vid].provider
                            except IndexError:
                                logging.error(
                                    "El índice introducido no existe")
                                sys.exit(1)
                            except ValueError:
                                logging.error(
                                    "El índice introducido no es válido (Solo números)")
                                sys.exit(1)
                            try:
                                fi_hand_prx = pro_prx.openFile(
                                    self.vids[vid].mediaId, self.usr_tok)
                                arch = fi_hand_prx.receive(4096, self.usr_tok)
                                with open (self.vids[vid].info.name, "wb") as bin_file:
                                    bin_file.write(arch)
                                bin_file.close()
                                self.vids.pop(vid)
                            except IceFlix.Unauthorized:
                                self.usr_tok = self.log_prx.refreshAuthorization(
                                    self.usr, self.contra)
                                logging.error(
                                    "No tiene permisos para descargar el vídeo")
                            except IceFlix.WrongMediaId:
                                logging.error("Id incorrecto")

                        else:
                            logging.error(
                                "Para descargar vídeos debes iniciar sesión.")
                    else:
                        print("Volviendo al menú principal...")
                        time.sleep(1)
                else:
                    logging.error("No hay vídeos para mostrar")
            if opcion == 5:
                if self.usr_tok == "":
                    logging.error("No hay sesión iniciada")
                else:
                    self.usr_tok = ""
                    print("Sesión cerrada")
                time.sleep(0.5)
            if opcion == 6:
                print("[!] Saliendo...")
                time.sleep(0.5)


if __name__ == "__main__":
    APP = Cliente()
    sys.exit(APP.main(sys.argv))
