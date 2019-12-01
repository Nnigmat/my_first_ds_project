import threading
import sys
import os
import threading
import requests
import time
import shutil
import distutils.dir_util as dir_util
from flask import Flask, request, send_file, abort
from multiprocessing import Pool

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
                requests.get(url=url)
            except requests.exceptions.ConnectionError:
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
                requests.get(url=url)
            except requests.exceptions.ConnectionError:
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
        return ','.join(self.nodes)

    def add_node(self, node):
        self.nodes.append(node)
