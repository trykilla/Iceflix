#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import logging
import signal
import time

import sys
import Ice
Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix

def handler(signum):
    msg = "\n[!] Has pulsado Ctrl+C. Saliendo..."
    print(msg, end="", flush=True)
    print("\n")
    exit(1)

class MainI(IceFlix.Main):

    # Authenticator* getAuthenticator() throws TemporaryUnavailable;
    def getAuthenticator(self, current=None):
        ''' Method returning a reference to remote authentication object (proxy) '''
        print("getAuthenticator")
        

    # MediaCatalog* getCatalog() throws TemporaryUnavailable;
    def getCatalog(self, current=None):
        ''' Method that returns a catalog service '''
        print("getCatalog")



class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = MainI()
        
        adapter = broker.createObjectAdapter("MainAdapter")

        proxy = adapter.add(servant, broker.stringToIdentity("Main"))
        print('El proxy es: "'+str(proxy)+'"')
        proxy = IceFlix.MainPrx.checkedCast(proxy)
   
        
        
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        
        return 0


if __name__ == '__main__':
   
    print("Iniciando servidor...")
    time.sleep(1)
    app = Server()
    app.daemon = True
    signal.signal(signal.SIGINT, handler)
    sys.exit(app.main(sys.argv))
    
        
