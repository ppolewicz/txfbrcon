#!/usr/bin/python
from twisted.application import service
import serverstate
from rconservice import RconService

application = service.Application("Rcon Plugin System")
_service = RconService()
_service.setServiceParent(application)

