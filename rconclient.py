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

class CommandHandler(object):
    def __init__(self, api_handle, len_arguments):
        self.api_handle = api_handle
        self.len_arguments = len_arguments

    def __call__(self, packet):
        args = packet.words[1:]
        self.api_handle(*args)

class ClientRconProtocol(FBRconProtocol):
    """a unique instance of this spawns for each rcon connection. i think."""
    STATUS_OK = 'OK'
    PLAYER_INFO_BLOCK_GROUPING_COLUMN = 'name'
    
    def __init__(self):
        FBRconProtocol.__init__(self)
        self.stateapi = StateAPI()
        self.handlers = {}
        self._register_handler('player.onJoin', self.stateapi.player_joined, 2)
        self._register_handler('player.onLeave', self.stateapi.player_left, 2)
        self._register_handler('player.onAuthenticated', self.stateapi.player_authenticated, 2)
        self._register_handler('player.onSpawn', self.stateapi.player_spawned, 1+1+3+3)
        self._register_handler('player.onKicked', self.stateapi.player_kicked, 2)
        self._register_handler('player.onChat', self.stateapi.player_chat, 3)
        self._register_handler('player.onTeamChange', self.stateapi.player_team_changed, 3)
        self._register_handler('player.onSquadChange', self.stateapi.player_squad_changed, 3)
        self._register_handler('punkBuster.onMessage', self.stateapi.pb_message, 1)
        self._register_handler('server.onLoadingLevel', self.stateapi.server_loading_level, 3)
        self._register_handler('server.onLevelStarted', self.stateapi.server_start_level, 0)
        self._register_handler('server.onRoundOver', self.stateapi.server_round_over, 1)
        self._register_handler('server.onRoundOverPlayers', self.stateapi.server_round_over_playerdata, 1)
        self._register_handler('server.onRoundOverTeamScores', self.stateapi.server_round_over_teamdata, 1)
        self._register_handler('player.onKill', self.stateapi.player_killed, 3+3+3)
        self.seq = 1
        self.callbacks = {}
        self.server = Server(self)

    def _register_handler(self, command, api_handle, len_arguments):
        self.handlers[command] = CommandHandler(api_handle, len_arguments)
    
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

    @classmethod
    def _parse_player_info_block(cls, raw_structure):
        return cls._parse_two_dimensional_structure(raw_structure, cls.PLAYER_INFO_BLOCK_GROUPING_COLUMN)

    @classmethod
    def _parse_two_dimensional_structure(cls, raw_structure, grouping_column):
        # TODO: this ".pop(0)" implementation was probably written by someone who thinks python lists are Deque objects... Refactor
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

        return parsed_structure

    @defer.inlineCallbacks
    def admin_listPlayers(self):
        raw_structure_with_status = yield self.sendRequest(["admin.listPlayers", "all"])
        status = raw_structure_with_status[0]
        raw_structure = raw_structure_with_status[1:]
        parsed_structure = self._parse_player_info_block(raw_structure)
        defer.returnValue(parsed_structure)
    
    @defer.inlineCallbacks
    def admin_listOnePlayer(self, player):
        raw_structure_with_status = yield self.sendRequest(["admin.listPlayers", "player", player])
        status = raw_structure_with_status[0]
        raw_structure = raw_structure_with_status[1:]
        parsed_structure = self._parse_player_info_block(raw_structure)
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
