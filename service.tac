#!/usr/bin/python
from twisted.application import service
import os
print os.getcwd()
import serverstate
from rconservice import RconService # TODO: fix path hack (probably will fix itself when packaging for production usage)

application = service.Application("Rcon Plugin System")
_service = RconService()
_service.setServiceParent(application)

