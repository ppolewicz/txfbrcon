import os
import base64
import hashlib
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from serverstate.server import Server

from fbrcon import FBRconFactory, FBRconProtocol
from serverstate.state import StateAPI


def getClientRconFactory(params, rm):
    factory = ClientRconFactory(False, params, rm)
    factory.protocol = ClientRconProtocol
    return factory

class ClientRconFactory(ReconnectingClientFactory, FBRconFactory):
    ReconnectingClientFactory.maxdelay = 15
    ReconnectingClientFactory.factor = 1.6180339887498948
    instance = None
    
    def __init__(self, isServer = False, params = {}): # TODO: params is shared between objects. That can't be good.
        FBRconFactory.__init__(self, isServer, params)
    
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        self.instance = p
        return p
        
LEVELHASH = {
    'MP_001':    'Grand Bazaar',
    'MP_003':    'Teheran Highway',
    'MP_007':    'Caspian Border',
    'MP_011':    'Seine Crossing',
    'MP_012':    'Operation Firestorm',
    'MP_013':    'Damavand Peak',
    'MP_017':    'Noshahar Canals',
    'MP_018':    'Kharg Island',
    'MP_Subway': 'Operation Metro',
    'XP1_001':   'Strike at Karkand',
    'XP1_002':   'Gulf of Oman',
    'XP1_003':   'Sharqi Peninsula',
    'XP1_004':   'Wake Island',
}

MODEHASH = {
    'ConquestLarge0':    'Conquest',
    'ConquestSmall0':    'Consolequest',
    'RushLarge0':        'Rush',
    'SquadRush0':        'Squad Rush',
    'SquadDeathMatch0':  'Squad Deathmatch',
    'TeamDeathMatch0':   'Team Deathmatch',
}

class ClientRconProtocol(FBRconProtocol):
    """a unique instance of this spawns for each rcon connection. i think."""
    STATUS_OK = 'OK'
    PLAYER_STRUCTURE_GROUPING_COLUMN = 'name'
    
    def __init__(self):
        FBRconProtocol.__init__(self)
        self.handlers = {
            "player.onJoin":                self.player_onJoin,
            "player.onLeave":               self.player_onLeave,
            "player.onAuthenticated":       self.player_onAuthenticated,
            "player.onChat":                self.player_onChat,
            "player.onTeamChange":          self.player_onTeamChange,
            "player.onSquadChange":         self.player_onSquadChange,
            "player.onKill":                self.nullop, # temporary
            "server.onLevelLoaded":         self.server_onLevelLoaded,
            "punkBuster.onMessage":         self.nullop,
            "player.onSpawn":               self.nullop,
            "version":                      self.nullop,
            "serverInfo":                   self.nullop,
            "listPlayers":                  self.nullop,
            "server.onRoundOver":           self.nullop,
            "server.onRoundOverPlayers":    self.nullop,
            "server.onRoundOverTeamScores": self.nullop,
        }
        self.seq = 1
        self.callbacks = {}
        self.server = Server(self)
        self.stateapi = StateAPI()
    
    # "OK" "Kentucky Fried Server" "64" "64" "ConquestLarge0" "XP1_001" "0" "2" "2" "60.563736" "109.1357" "0" "" "true" "true" "false" "6972" "781" "" "" "" "NAm" "iad" "US"
    @defer.inlineCallbacks
    def serverInfo(self):
        sinfo = yield self.sendRequest(["serverInfo"])
        retval = {
            'serverName': sinfo[1],
            'curPlayers': int(sinfo[2]),
            'maxPlayers': int(sinfo[3]),
            'mode': modehash[sinfo[4]],
            'level': levelhash[sinfo[5]],
            'roundsPlayed': int(sinfo[6]) + 1,
            'roundsTotal': int(sinfo[7]),
        }
        defer.returnValue(retval)
    
    def nullop(self, packet):
        pass

    @classmethod
    def _parse_listPlayers(cls, raw_structure):
        return cls._parse_two_dimensional_structure_with_status(raw_structure, cls.PLAYER_STRUCTURE_GROUPING_COLUMN)

    @classmethod
    def _parse_two_dimensional_structure_with_status(cls, raw_structure, grouping_column):
        # TODO: this ".pop(0)" implementation was probably written by someone who thinks python lists are Deque objects... Refactor
        status = raw_structure.pop(0)
        if status!=cls.STATUS_OK:
            raise Exception("Unhandled error occured. Status of parsed structure: %s" % status)
        fields = []
        numparams = int(raw_structure.pop(0))
        for i in range(numparams):
            fields.append(raw_structure.pop(0))
        len_rows = int(raw_structure.pop(0))

        parsed_structure = {}
        for i in range(len_rows):
            parsed_entry = {}
            for key in fields:
                parsed_entry[key] = raw_structure.pop(0)
            entry_grouping_key = parsed_entry[grouping_column] # if this raises KeyError, it is a programming error
            parsed_structure[entry_grouping_key] = parsed_entry

        return status, parsed_structure

    # IsFromClient,  Response,  Sequence: 2  Words: "OK" "7" "name" "guid" "teamId" "squadId" "kills" "deaths" "score" "0" 
    @defer.inlineCallbacks
    def admin_listPlayers(self):
        raw_structure_with_status = yield self.sendRequest(["admin.listPlayers", "all"])
        status, parsed_structure = self._parse_listPlayers(raw_structure_with_status)
        defer.returnValue(parsed_structure)
    
    @defer.inlineCallbacks
    def admin_listOnePlayer(self, player):
        raw_structure_with_status = yield self.sendRequest(["admin.listPlayers", "player", player])
        status, parsed_structure = self._parse_listPlayers(raw_structure_with_status)
        defer.returnValue(parsed_structure)
    
    @defer.inlineCallbacks
    def admin_kickPlayer(self, player, reason):
        retval = yield self.sendRequest(["admin.kickPlayer", player, reason])

    @defer.inlineCallbacks
    def admin_killPlayer(self, player):
        retval = yield self.sendRequest(["admin.killPlayer", player])
    
    @defer.inlineCallbacks
    def admin_say(self, message, players):
        retval = yield self.sendRequest(["admin.say", message, players])
    
    # Unhandled event: IsFromServer, Request, Sequence: 132, Words: "server.onLevelLoaded" "MP_007" "ConquestLarge0" "0" "2"
    def server_onLevelLoaded(self, packet): 
        params = {
        'level':    levelhash[packet.words[1]],
        'mode':     modehash[packet.words[2]],
        'curRound': int(packet.words[3]) + 1,
        'maxRound': int(packet.words[4]),
        }
        self.postMessage("server.onLevelLoaded", params)

    def player_onJoin(self, packet):
        self.postMessage("player.onJoin", {'player': packet.words[1], 'guid': packet.words[2]})

    def player_onAuthenticated(self, packet):
        self.postMessage("player.onAuthenticated", {'player': packet.words[1]})
        
    def player_onLeave(self, packet):
        self.postMessage("player.onLeave", {'player': packet.words[1]})
    
    def player_onChat(self, packet):
        self.postMessage("player.onChat", {'player': packet.words[1], 'message': packet.words[2]})
    
    # "player.onTeamChange" "toomuchmoney678" "2" "0"
    def player_onTeamChange(self, packet):
        pass
    
    # "player.onSquadChange" "toomuchmoney678" "2" "3"
    def player_onSquadChange(self, packet):
        pass
        
    @defer.inlineCallbacks
    def connectionMade(self):
        self.params = self.factory.params
        FBRconProtocol.connectionMade(self)
        ver   = yield self.sendRequest(["version"])
        salt  = yield self.sendRequest(["login.hashed"])
        m = hashlib.md5()
        m.update(salt[1].decode("hex"))
        m.update(self.factory.params["secret"])
        login = yield self.sendRequest(["login.hashed", m.digest().encode("hex").upper()])
        event = yield self.sendRequest(["admin.eventsEnabled", "true"])
        players = yield self.admin_listPlayers()
        for player in players:
            pl = players[player]
            ph = self.server.addPlayer(pl['name'], pl['guid'])
    
    def connectionLost(self, reason):
        FBRconProtocol.connectionLost(self, reason)
    
    def sendRequest(self, strings):
        """sends something to the other end, returns a Deferred"""
        # TODO: this needs to add items to a cache so we can fire the deferred later
        #       we should probably also track command rtt
        cb = Deferred()
        seq = self.peekSeq()
        self.callbacks[seq] = cb
        self.transport.write(self.EncodeClientRequest(strings))
        return cb
    
    def gotResponse(self, packet):
        """handles incoming response packets"""
        if packet.sequence in self.callbacks:
            self.callbacks[packet.sequence].callback(packet.words)
            del self.callbacks[packet.sequence]
        else:
            print "gotResponse WITHOUT callback"
    
    def sendResponse(self, pkt, words=["OK"]):
        """called by gotRequest to send a response"""
        self.transport.write(self.EncodeServerResponse(pkt.sequence, words))
    
    def gotRequest(self, packet):
        """handles incoming request packets
           in client mode, these are events
        """
        handler = None
        command = packet.words[0]
        if command in self.handlers:
            handler = self.handlers[command]
            try:
                handler(packet)
            except Exception, e:
                print "Caught Exception in gotRequest:", e
        else:
            print "Unhandled event:", packet
        self.sendResponse(packet)
