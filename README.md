# Distributed file system. Innopolis University 2019
> Team: Amir Subaev (SB), Nikita Nigmatullin (SB), Salavat Dinmukhametov (SB)

The Distributed File System (DFS) is a file system with data stored on a server. The
data is accessed and processed as if it was stored on the local client machine. The DFS
makes it convenient to share information and files among users on a network.

## Project installation
Used technologies:
* **Python3** - programming language
* **Requests** - library for http requests
* **Flask** - web framework
* **Pickledb** - small file database

Installation for Debian:
```
apt install python3
apt install python3-pip
pip3 install requests pickledb flask

git clone https://github.com/Nnigmat/my_first_ds_project && cd my_first_ds_project
```

## Project starting
We have nameserver and storage server.
To start nameserver:
```
cd nameserver/ && python3 app.py
```

Before starting storage server we need to specify the IP address or DNS name in the storage/app.py
```
cd storage/ && python3 app.py
```

## Architecture
![](https://i.imgur.com/tChlkdK.png)
## Nameserver and client
![](https://i.imgur.com/a2JmUkP.png)
