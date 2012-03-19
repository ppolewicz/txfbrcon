#!/usr/bin/python
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from newclientrcon import getClientRconFactory
from iniparse import ConfigParser

class RconService(MultiService):
    """ runs multiple rcon instances """
    servers = {}
    
    def __init__(self):
        MultiService.__init__(self)
        self.server = {}

    def startService(self):
        cfgpr = ConfigParser()
        cfgpr.read('config.ini')
        ip = cfgpr.get('main', 'ip')
        port = cfgpr.getint('main', 'port')
        tag = cfgpr.get('main', 'tag')
        password = cfgpr.get('main', 'password')

        server_data = {
                'ip': ip,
                'port': port,
                'tag': tag, # TODO: what is this:
                'secret': password, # TODO: refactor how this kind of data is passed and stored in factory
                }
        factory = getClientRconFactory(server_data, self)
        client  = TCPClient(server_data["ip"], server_data["port"], factory)
        client.setServiceParent(self)
        self.server["factory"] = factory
        MultiService.startService(self)
        
    def sendRcon(self, strings):
        return self.server["factory"].instance.sendRequest(strings)

