#!/usr/bin/env python3

import queue
import random 
import threading
import keyboard
# import numpy as np
import time
import curses


def main(stdscr):
    stdscr.nodelay(True)
    try:
        return stdscr.getkey()
    except:
        return None

def key_pressed(key):
    inp_key = curses.wrapper(main)

    while inp_key is not None:
        if key == inp_key:
            return True
        inp_key = curses.wrapper(main)
    return False

event = threading.Event()

# event.set()
# event.clear()

# event.wait()

#event.is_set()

# def flag():
#     time.sleep(3)
#     event.set()
#     print("Empezando cuenta atrás")
#     time.sleep(7)
#     print("Terminando cuenta atrás")
#     event.clear()
    
# def start_operation():
#     print("Esperando a que se active el evento")
#     event.wait()
#     while event.is_set():
#         print("Evento activado")
#         x = random.randint(1,30)
#         time.sleep(.5)
#         if x == 29:
#             print("Evento desactivado")
        
#     print("Evento activado")

def func(mains):
    time.sleep(4)
    mains.append(random.randint(1,30))
    event.set()
    

mains = []

# t1 = threading.Thread(target=func, args=([mains]))
# t1.start()
# event = threading.Event()
# print("Espero...")
# while not mains:
#     print("Esperando a que se active el evento")
#     event.wait()
    
# print("Para parar pulse 'x'")
# # while True:
# #     if keyboard.is_pressed('x'):
# #         break
# #     print("Me paré uwu")
# #     time.sleep(1)
# while not key_pressed('x'):
#     print("Me ejecuto")
#     time.sleep(1)
vids = ["Pico de gallo",2,3,4,5,6,7,8,9,10]

print("Vídeos: ", str(vids))
op = int(input("Vídeo que desea editar (número):\nVídeos: "+ str(list(range(len(vids)))))) 

for i in range(len(vids)):
    if op == i:
        print("Vídeo seleccionado: ", vids[i])
        break
# op = int(input("Vídeo que desea editar (número):\nVídeos: ",
#                                    str(list(range(len(vids))))))
    
    
    

