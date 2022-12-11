# Welcome to Iceflix
* Link to the repo: https://github.com/trykilla/Iceflix.git 
## ¿What is Iceflix?

Iceflix is a project that imitates Netflix. A distributed system way more simple but with similar 
functionalities. Done with Ice and Python.
## Client

* In my case, I'm implementing the Client service. The Client has to be capable of doing several accesses or changes to other services. There are two kind of clients: Clien and AdminClient
  * [Client](iceflix/Client.py): The client should offer the user this methods: Login, search in the catalog, edit the catalog and logout. Also, when searching in the catalog, we can download the media we want.
  * [AdminClient](iceflix/AdminClient.py): The AdminClient should offer the user this methods: add user, remove user, edit a title, upload a file and delete a file.

## ¿How to run the client?

* To run the cliente, you have to run the script (previously you have to change the config for the server you want to connect to, explained later) [run_client](run_client) and then, you have to write "s" or "n". For example, if you want to run the AdminClient, you will be asked "¿Quieres entrar como administrador? (s/n)" and you have to answer either "s" or "n".

*To change the server where the client is going to connect, you have to change the IP and the port in the [client.config](configs/client.config) for the ones you are going to use.*

