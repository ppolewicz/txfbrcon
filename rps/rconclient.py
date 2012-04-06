import hashlib
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from fbrcon import FBRconFactory, FBRconProtocol
from serverstate.state import StateAPI, Server

from plugins.debug_plugin import DebugPlugin
from plugins.toy_plugin import ToyPlugin

def getClientRconFactory(params):
    factory = ClientRconFactory(False, params)
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

class SimpleCommandHandler(object):
    def __init__(self, api_handle, len_arguments):
        self.api_handle = api_handle
        self.len_arguments = len_arguments # TODO: this length seems to be useless after last refactor. Remove?

    def __call__(self, packet):
        #packet.words[0] = 'player.OnChat' etc
        args = packet.words[1:]
        self.api_handle(*args)

class PreProcessorCommandHandler(object):
    def __init__(self, api_handle, len_arguments, processor):
        self.api_handle = api_handle
        self.len_arguments = len_arguments
        self.processor = processor

    def __call__(self, packet):
        #packet.words[0] = 'serverInfo' etc
        args = packet.words[1:]
        pre_processed_args = self.processor(args)
        self.api_handle(*pre_processed_args)

class ClientRconProtocol(FBRconProtocol):
    """a unique instance of this spawns for each rcon connection. i think."""
    STATUS_OK = 'OK'
    PLAYER_INFO_BLOCK_GROUPING_COLUMN = 'name'
    
    def __init__(self):
        FBRconProtocol.__init__(self)
        self.server = Server()
        self.stateapi = StateAPI(self.server, self)
        self.handlers = {}
        self._register_handler('player.onJoin', self.stateapi.player_joined, 2)
        self._register_handler('player.onLeave', self.stateapi.player_left, 2)
        self._register_handler('player.onAuthenticated', self.stateapi.player_authenticated, 1)
        self._register_handler('player.onSpawn', self.stateapi.player_spawned, 1+1)
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
        self._register_handler('player.onKill', self.stateapi.player_killed, 3)
        self._register_handler('serverInfo', self.stateapi.server_info_hint, 0)
        #self._register_handler('serverInfo', self.stateapi.server_info, 7, processor=self.server_info_parser)
        self.connection_made_handler = self.stateapi.connection_made
        self.connection_lost_handler = self.stateapi.connection_lost
        self.seq = 1
        self.callbacks = {}
        self.plugins = []
        self.plugins.append( DebugPlugin(self.stateapi, self) )
        self.plugins.append( ToyPlugin(self.stateapi, self) )

    def _register_handler(self, command, api_handle, len_arguments, processor=None):
        if processor is None:
            self.handlers[command] = SimpleCommandHandler(api_handle, len_arguments)
        else:
            self.handlers[command] = PreProcessorCommandHandler(api_handle, len_arguments, processor)
    
    # "Kentucky Fried Server" "64" "64" "ConquestLarge0" "XP1_001" "0" "2" "2" "60.563736" "109.1357" "0" "" "true" "true" "false" "6972" "781" "" "" "" "NAm" "iad" "US"
    def server_info_parser(self, raw_structure):
        sinfo = raw_structure
        print "SERVER_INFO_PARSER:", raw_structure # TODO this needs to be all read
        retval = [
            sinfo[0], # serverName
            int(sinfo[1]), # curPlayers
            int(sinfo[2]), # maxPlayers
            MODEHASH[sinfo[3]], # mode
            LEVELHASH[sinfo[4]], # level
            int(sinfo[5]) + 1, # roundsPlayed
            int(sinfo[6]), # roundsTotal
        ]
        return retval

    @defer.inlineCallbacks
    def updateServerInfo(self):
        sinfo = yield self.sendRequest(["serverInfo"])
        retval = self.server_info_parser(sinfo[1:])
        defer.returnValue(retval)

    @classmethod
    def _parse_player_info_block(cls, raw_structure):
        return cls._parse_two_dimensional_structure(raw_structure, cls.PLAYER_INFO_BLOCK_GROUPING_COLUMN)

    @classmethod
    def _parse_two_dimensional_structure(cls, raw_structure, grouping_column):
        # TODO: this ".pop(0)" implementation was probably written by someone who thinks python lists are Deque objects... Refactor
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
        #status = raw_structure_with_status[0]
        raw_structure = raw_structure_with_status[1:]
        parsed_structure = self._parse_player_info_block(raw_structure)
        defer.returnValue(parsed_structure)
    
    @defer.inlineCallbacks
    def admin_listOnePlayer(self, player):
        raw_structure_with_status = yield self.sendRequest(["admin.listPlayers", "player", player])
        #status = raw_structure_with_status[0]
        raw_structure = raw_structure_with_status[1:]
        parsed_structure = self._parse_player_info_block(raw_structure)
        defer.returnValue(parsed_structure)
    
    @defer.inlineCallbacks
    def admin_kickPlayer(self, player, reason):
        retval = yield self.sendRequest(["admin.kickPlayer", player, reason])

    @defer.inlineCallbacks
    def admin_killPlayer(self, player):
        retval = yield self.sendRequest(["admin.killPlayer", player])
    
    def admin_say(self, li_targets, message):
        return self._send_message("admin.say", li_targets, message)
    
    def admin_yell(self, li_targets, message, duration):
        return self._send_message("admin.yell", li_targets, message, duration)

    @classmethod
    def _target_to_player_subset(cls, target):
        quantifier, identifier = target.get_message_participant_info()
        return (quantifier, identifier)

    def _send_message(self, command, li_targets, *args):
        """ args ex.: [message] or [message, duration] """
        for target in li_targets:
            subset = self._target_to_player_subset(target)
            request = [command]
            request.extend(args)
            request.extend(subset)
            self.sendRequest(request)

    # Unhandled event: IsFromServer, Request, Sequence: 132, Words: "server.onLevelLoaded" "MP_007" "ConquestLarge0" "0" "2"
    def server_onLevelLoaded(self, packet): 
        params = {
        'level':    LEVELHASH[packet.words[1]],
        'mode':     MODEHASH[packet.words[2]],
        'curRound': int(packet.words[3]) + 1,
        'maxRound': int(packet.words[4]),
        }
        self.postMessage("server.onLevelLoaded", params)

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
        self.connection_made_handler()
    
    def connectionLost(self, reason):
        self.connection_lost_handler(reason)
        FBRconProtocol.connectionLost(self, reason)
    
    def sendRequest(self, strings):
        """sends something to the other end, returns a Deferred"""
        # TODO: this needs to add items to a cache so we can fire the deferred later
        #       we should probably also track command rtt
        cb = Deferred()

        # TODO: remove debug:
        print "[rcon] sending", strings
        if not strings[0].startswith('login'):
            def printer(response):
                print """[rcon] response = %s""" % response
                return response
            cb.addCallback(printer)

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
            #try:
            handler(packet)
            #except Exception, e:
            #    print "Caught Exception in gotRequest:", e
        else:
            print "Unhandled event:", packet
        self.sendResponse(packet)
