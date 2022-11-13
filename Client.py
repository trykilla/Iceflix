#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import Ice
import time
import sys
import hashlib
import tkinter as tk
# Ice.loadSlice("iceflix.ice")
# import IceFlix


def login():

    w2 = tk.Toplevel()
    w2.title = 'Inicio de sesión'
    w2.geometry('300x300')
    txtInputUser = tk.Entry(w2)
    txtInputPass = tk.Entry(w2, width=17, show="*")
    button1 = tk.Button(w2, text='Salir', command=w2.destroy)
    buttonAcceopt = tk.Button(w2, text='Aceptar', command=w2.destroy)
    labelUser = tk.Label(w2, text='Usuario')
    labelPass = tk.Label(w2, text='Contraseña')
    button1.place(x=100, y=200)
    buttonAcceopt.place(x=100, y=120)
    labelUser.place(x=40, y=50)
    labelPass.place(x=40, y=80)
    txtInputUser.place(x=100, y=50)
    txtInputPass.place(x=124, y=80)


def accion2():
    texto.configure(text='Has elegido la opción 2 del menú principal')


def acciona():
    texto.configure(text='Has elegido la opción a del submenú')


def accionb():
    texto.configure(text='Has elegido la opción b del submenú')
    ventana.destroy()


# creamos la ventana principal
ventana = tk.Tk()
ventana.title('Ventana principal')
ventana.geometry('400x400')

texto = tk.Label(ventana, text='Elija una opción del menú.',
                 font=('Arial', 20))
button1 = tk.Button(ventana, text='1. Iniciar sesión ', command=login)
button2 = tk.Button(ventana, text='2. Cerrar sesión ', command=accion2)
button3 = tk.Button(ventana, text='3. Buscar en catálogo ', command=acciona)
button4 = tk.Button(ventana, text='4. Salir ', command=accionb)


button1.place(x=100, y=100)
button2.place(x=100, y=150)
button3.place(x=100, y=200)
button4.place(x=100, y=250)

texto.place(x=50, y=50)

#   print("1. Iniciar sesión")
#     print("2. Buscar en catálogo")
#     print("3. Cambiar configuración de conexión con el servidor")
#     print("4. Cerrar sesión")
#     print("5. Parar reproducción")
#     print("6. Salir")


if __name__ == '__main__':
    ventana.mainloop()  # ejecutamos la ventana principal
