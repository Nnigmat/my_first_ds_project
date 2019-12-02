import threading
import requests
import threading

import requests


class NodeManager():
    def __init__(self):
        self.nodes = []
        self.failed_nodes = []
        self.storage_port = 8080

    def createURL(self, addr='', port='', path=''):
        return "http://{}:{}/{}".format(addr, port, path)

    def heartbeat_ask(self, repeatTime=15.0):
        """
        Every repeatTime seconds check that node is reachable
        """
        timer = threading.Timer(repeatTime, self.heartbeat_ask)
        timer.start()
        for node in self.nodes + self.failed_nodes:
            url = self.createURL(node, self.storage_port)
            try:
                requests.get(url=url, timeout=0.1)
            except requests.exceptions.RequestException:
                if node in self.failed_nodes:
                    self.failed_nodes.remove(node)
                    print(node, "removed")
                elif node in self.nodes:
                    self.nodes.remove(node)
                    self.failed_nodes.append(node)
                    print(node, "failed")
            else:
                if node in self.failed_nodes:
                    self.failed_nodes.remove(node)
                    self.nodes.append(node)
        return timer

    def get_storages(self):
        for node in self.nodes + self.failed_nodes:
            url = self.createURL(node, self.storage_port)
            try:
                requests.get(url=url, timeout=0.1)
            except requests.exceptions.RequestException:
                if node in self.failed_nodes:
                    self.failed_nodes.remove(node)
                    print(node, "removed")
                elif node in self.nodes:
                    self.nodes.remove(node)
                    self.failed_nodes.append(node)
                    print(node, "failed")
            else:
                if node in self.failed_nodes:
                    self.failed_nodes.remove(node)
                    self.nodes.append(node)
        return self.nodes

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def add_dir(self, dir):
        storages = self.get_storages()
        url = self.createURL(storages[0], self.storage_port, 'dir' + dir)
        print(url)
        requests.get(url)

    def del_dir(self, dir):
        storages = self.get_storages()
        url = self.createURL(storages[0], self.storage_port, 'delete' + dir)
        print(url)
        requests.get(url)

    def move_dir(self, dir, to_dir):
        storages = self.get_storages()
        if len(to_dir) > 1:
            to_dir = to_dir[1:]
        url = self.createURL(storages[0], self.storage_port, 'move' + dir + '?to=' + to_dir)
        print(url)
        requests.get(url)

    def copy_dir(self, dir, to_dir):
        storages = self.get_storages()
        if len(to_dir) > 1:
            to_dir = to_dir[1:]
        url = self.createURL(storages[0], self.storage_port, 'copy' + dir + '?to=' + to_dir)
        print(url)
        requests.get(url)

    def create_empty_file(self, dir):
        storages = self.get_storages()
        url = self.createURL(storages[0], self.storage_port, 'create_file' + dir)
        print(url)
        requests.get(url)
