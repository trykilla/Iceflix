# Welcome to Iceflix
* Link to the repo: https://github.com/trykilla/Iceflix.git 
## ¿What is Iceflix?

Iceflix is a project that imitates Netflix. A distributed system way more simple but with similar 
functionalities. Done with Ice and Python.
## Client

* In my case, I'm implementing the Client service. The Client has to be capable of doing several accesses or changes to other services. There are two kind of clients: Clien and AdminClient
  * [Client](iceflix/Client.py): The client should offer the user this methods: Login, search in the catalog, edit the catalog and logout. Also, when searching in the catalog, we can download the media we want. 

    * V.1.1
    Now the client supports Indirect Communication with IceStorm, discovering the main using the announce method, subscribing to that topic.

  * [AdminClient](iceflix/AdminClient.py): The AdminClient should offer the user this methods: add user, remove user, edit a title, upload a file and delete a file. 

    * V.1.1
    Now the client supports Indirect Communication with IceStorm, discovering the main using the announce method, subscribing to that topic. Also we can monitorize different topics' announcements.

## ¿How to run the client?

* To start running the client, previously you have to run icestorm, you can do it running ./run_icestorm in the root of the project. After that, with the icestorm running, you can run the client with the following command: ./run_client, where you can select enter the client or the admin client with S or N, meaning yes or no respectively.

## Extra points

* I tried to make my project distributable making it a module. You can now install it with pip install with the following command: pip install dist/(name_of_the_package).

* I also tried to get > 9 mark using pylint, altough I think I have lot of disables.

* For last, I have a simple configuration for logging, using it for errors and events.



