from twisted.internet import defer
from triggersystem import TriggerSystem
from fbrconconst import PlayerSubsetPrefix

class AbstractMessagesystemParticipant(object):
    MESSAGE_PREFIX = None
    def get_message_participant_info(self):
        return self.MESSAGE_PREFIX, self.identifier

class Server(AbstractMessagesystemParticipant):
    _GAME_MOD_ID_VANILLA = 1001
    _GAME_MOD_ID_KARKAND = 1002
    _TEAM_ID_NEUTRAL = 0
    MESSAGE_PREFIX = PlayerSubsetPrefix.ALL
    def __init__(self):
        self.teams = {}
        self.teams[self._TEAM_ID_NEUTRAL] = self.neutral_team = Team(self._TEAM_ID_NEUTRAL, self)
        self.info = None

    def add_player(self, player_name, player_guid):
        squad = self.neutral_team.no_squad
        return Player(player_name, player_guid, squad)

    def remove_player(self, player_name):
        player_or_none = self.search_for_player(player_name)
        if player_or_none is None:
            return
        player_or_none.remove()

    def authorize_player(self, player_name, guid):
        player_or_none = self.search_for_player(player_name)
        if player_or_none is None:
            return
        player_or_none.authorize(guid)

    def load_info(self, *args):
        print "SERVER INFO:", args # TODO
        self.info = args

    def flush(self):
        pass # TODO

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for team_id in self.teams:
            team = self.teams[team_id]
            player_or_none = team.search_for_player(player_name)
            if player_or_none is not None:
                return player_or_none
        return None

    def process_spawn(self, player_name, team_id):
        pass # TODO

    def process_kill(self, killer_name, deadguy_name, weapon, is_headshot):
        pass # TODO

    def get_message_participant_info(self):
        return self.MESSAGE_PREFIX


class Team(AbstractMessagesystemParticipant):
    MESSAGE_PREFIX = PlayerSubsetPrefix.TEAM
    _MAX_SQUAD = 8
    _SQUAD_ID_NONE = 0
    def __init__(self, team_id, server):
        self.identifier = team_id
        self.name = "Team %d" % team_id
        self.server = server
        self.squads = {}
        for squad_id in range(self._MAX_SQUAD):
            self.squads[squad_id] = Squad(self, squad_id)
        self.no_squad = self.squads[self._SQUAD_ID_NONE]

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for squad_id in self.squads:
            squad = self.squads[squad_id]
            player_or_none = squad.search_for_player(player_name)
            if player_or_none is not None:
                return player_or_none
        return None

class Squad(AbstractMessagesystemParticipant):
    _SQUAD_NAME_ID_MAP = {
            0: 'NONE',
            1: 'ALHPA',
            2: 'BRAVO',
            3: 'CHARLIE',
            4: 'DELTA',
            5: 'ECHO',
            6: 'FOXTROT',
            7: 'GOLF',
            8: 'HOTEL',
            }
    MESSAGE_PREFIX = PlayerSubsetPrefix.SQUAD
    def __init__(self, team, squad_id):
        self.team = team
        self.identifier = squad_id
        self.name = self._SQUAD_NAME_ID_MAP[squad_id]
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)

    @property
    def server(self):
        return self.team.server

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for player in self.players:
            if player.name == player_name:
                return player
        return None

    def get_message_participant_info(self):
        return self.MESSAGE_PREFIX, self.team.identifier, self.identifier

class Player(AbstractMessagesystemParticipant):
    MESSAGE_PREFIX = PlayerSubsetPrefix.PLAYER
    _MODERATION_LEVEL_MUTED  = 1001
    _MODERATION_LEVEL_NORMAL = 1002
    _MODERATION_LEVEL_VOICE  = 1003
    _MODERATION_LEVEL_ADMIN  = 1004
    def __init__(self, player_name, player_guid, squad):
        self.name = player_name
        self.guid = player_guid
        self.squad = squad
        self.authenticated = False
        self.identifier = self.name

    @property
    def team(self):
        return self.squad.team

    @property
    def server(self):
        return self.squad.team.server

    def authenticate(self):
        self.authenticated = True

class StateAPI(object):
    def __init__(self, server, rcon):
        self.triggers = TriggerSystem()
        self.server = server
        self.rcon = rcon
    @defer.inlineCallbacks
    def connection_made(self):
        self.triggers.pre_connection_made()
        players = yield self.rcon.admin_listPlayers()
        if players is not None:
            for player in players:
                pl = players[player]
                self.server.add_player(pl['name'], pl['guid'])
        else:
            print "after connection was made, admin_listPlayers gave no result" # TODO
        self.triggers.post_connection_made()
        self.server_info_hint()
    def connection_lost(self, reason):
        self.triggers.pre_connection_lost(reason)
        self.server.flush() # TODO: ? maybe better in connection_made?
        self.triggers.post_connection_lost(reason)
    def server_info_hint(self):
        server_info = yield self.rcon.updateServerInfo()
        self.triggers.pre_server_info(server_info)
        self.server.load_info(server_info)
        self.triggers.post_server_info(server_info)
    def player_joined(self, player_name, player_guid):
        self.triggers.pre_player_joined(player_name, player_guid)
        self.server.add_player(player_name, player_guid)
        self.triggers.post_player_joined(player_name, player_guid)
    def player_left(self, player_name, player_info_block):
        self.triggers.pre_player_left(player_name, player_info_block)
        self.server.remove_player(player_name)
        self.triggers.post_player_left(player_name, player_info_block)
    def player_kicked(self, player_name, kick_reason):
        self.triggers.pre_player_kicked(player_name, kick_reason)
        self.server.remove_player(player_name)
        self.triggers.post_player_kicked(player_name, kick_reason)
    def player_authenticated(self, player_name):
        player = self.server.search_for_player(player_name)
        if player is not None:
            print "AUTHENTICATION ERROR: PLAYER '%s' DOES NOT EXIST BUT IS AUTHENTICATED" % player_name # TODO
            self.triggers.pre_player_authenticated(player_name)
            player.authenticate()
            self.triggers.post_player_authenticated(player_name)
    def player_spawned(self, player_name, team_id):
        self.triggers.pre_player_spawned(player_name, team_id)
        self.server.process_spawn(player_name, team_id)
        self.triggers.post_player_spawned(player_name, team_id)
    def player_killed(self, killer_name, deadguy_name, weapon, is_headshot):
        self.triggers.pre_player_killed(killer_name, deadguy_name, weapon, is_headshot)
        self.server.process_kill(killer_name, deadguy_name, weapon, is_headshot)
        self.triggers.post_player_killed(killer_name, deadguy_name, weapon, is_headshot)
    def player_chat(self, player_name, message): # target_player_subset is documented argument... but the server doesn't send it
        self.triggers.pre_player_chat(player_name, message)
        if message == "I don't want to live on this planet anymore...":
            self.rcon.admin_killPlayer(player_name)
        pass
        self.triggers.post_player_chat(player_name, message)
    def player_team_changed(self, player_name, team_id, squad_id):
        self.triggers.pre_player_team_changed(player_name, team_id, squad_id)
        pass
        self.triggers.post_player_team_changed(player_name, team_id, squad_id)
    def player_squad_changed(self, player_name, team_id, squad_id):
        self.triggers.pre_player_squad_changed(player_name, team_id, squad_id)
        pass
        self.triggers.post_player_squad_changed(player_name, team_id, squad_id)
    def pb_message(self, message):
        self.triggers.pre_pb_message(message)
        pass
        self.triggers.post_pb_message(message)
    def server_loading_level(self, level_name, rounds_played, rounds_total):
        self.triggers.pre_server_loading_level(level_name, rounds_played, rounds_total)
        pass
        self.triggers.post_server_loading_level(level_name, rounds_played, rounds_total)
    def server_start_level(self):
        self.triggers.pre_server_start_level(self)
        pass
        self.triggers.post_server_start_level(self)
    def server_round_over(winning_team_id):
        self.triggers.pre_server_round_over(self, winning_team_id)
        pass
        self.triggers.post_server_round_over(winning_team_id)
    def server_round_over_playerdata(self, final_player_info_block):
        self.triggers.pre_server_round_over_playerdata(final_player_info_block)
        pass
        self.triggers.post_server_round_over_playerdata(final_player_info_block)
    def server_round_over_teamdata(self, final_team_scores):
        self.triggers.pre_server_round_over_teamdata(final_team_scores)
        pass
        self.triggers.post_server_round_over_teamdata(final_team_scores)

