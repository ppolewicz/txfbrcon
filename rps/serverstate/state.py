from twisted.internet import defer
from triggersystem import TriggerSystem

class Server(object):
    _GAME_MOD_ID_VANILLA = 1001
    _GAME_MOD_ID_KARKAND = 1002
    _TEAM_ID_NEUTRAL = 0
    _TEAM_NAME_NEUTRAL = 'UNASSIGNED'
    def __init__(self):
        self.teams = {}
        self.teams[self._TEAM_ID_NEUTRAL] = self.neutral_team = Team(self._TEAM_NAME_NEUTRAL)

    def add_player(self, player_name, player_guid):
        self.neutral_team.no_squad.add_player(player_name, player_guid)

    def authorize_player(self, player_name, guid):
        self.get_player(player_name).authorize(guid)

    def load_info(self, *args):
        print "SERVER INFO:", args # TODO

    def flush(self):
        pass # TODO

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for team_id in self.teams:
            team = self.teams[team_id]
            player_or_none = team.get_player(player_name)
            if player_or_none is not None:
                return player_or_none
        return None

class Team(object):
    _SQUAD_ID_NONE = 0
    _SQUAD_ID_NAME_MAP = {
            'NONE': 0,
            'ALHPA': 1,
            'BRAVO': 2,
            'CHARLIE': 3,
            'DELTA': 4,
            'ECHO': 5,
            'FOXTROT': 6,
            'GOLF': 7,
            'HOTEL': 8,
            }
    _SQUAD_NAME_ID_MAP = { # TODO: refactor so it's not copied from above
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
    def __init__(self, name):
        self.name = name
        self.squads = {}
        for squad_id in self._SQUAD_NAME_ID_MAP.keys():
            squad_name = self._SQUAD_NAME_ID_MAP[squad_id]
            self.squads[squad_id] = Squad(squad_name)
        self.no_squad = self.squads[self._SQUAD_ID_NONE]

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for squad_id in self.teams:
            squad = self.players[squad_id]
            player_or_none = squad.get_player(player_name)
            if player_or_none is not None:
                return player_or_none
        return None

class Squad(object):
    def __init__(self, name):
        self.name = name
        self.players = []

    def add_player(self, player_name, player_guid):
        if player_name in self.players:
            pass # TODO: handle this situation
        self.players.append(Player(player_name, player_guid))

    def search_for_player(self, player_name):
        """ returns Player object or None """
        for player in self.players:
            if player.name == player_name:
                return player
        return None

class Player(object):
    _MODERATION_LEVEL_MUTED  = 1001
    _MODERATION_LEVEL_NORMAL = 1002
    _MODERATION_LEVEL_VOICE  = 1003
    _MODERATION_LEVEL_ADMIN  = 1004
    def __init__(self, player_name, player_guid=None):
        self.name = player_name
        self.guid = player_guid
        print "player created (%s, %s)" % (self.name, self.guid)

    def authorize(self, guid):
        self.guid = guid

class StateAPI(object):
    def __init__(self, server, rcon):
        self._triggers = TriggerSystem()
        self.server = server
        self.rcon = rcon
    @defer.inlineCallbacks
    def connection_made(self,):
        self._triggers.pre_connection_made()
        players = yield self.rcon.admin_listPlayers()
        for player in players:
            pl = players[player]
            self.server.add_player(pl['name'], pl['guid'])
        server_info = yield self.rcon.updateServerInfo()
        self.server.load_info(server_info)
        self._triggers.post_connection_made()
    def connection_lost(self,):
        self._triggers.pre_connection_lost()
        self.server.flush()
        self._triggers.post_connection_lost()
    def server_info(self,):
        self._triggers.pre_server_info()
        pass
        self._triggers.post_server_info()
    def player_joined(self, player_name, player_guid):
        self._triggers.pre_player_joined(player_name, player_guid)
        pass
        self._triggers.post_player_joined(player_name, player_guid)
    def player_left(self, player_name, player_info_block):
        self._triggers.pre_player_left(player_name, player_info_block)
        pass
        self._triggers.post_player_left(player_name, player_info_block)
    def player_kicked(self, player_name, kick_reason):
        self._triggers.pre_player_kicked(player_name, kick_reason)
        pass
        self._triggers.post_player_kicked(player_name, kick_reason)
    def player_authenticated(self, player_name, player_guid):
        self._triggers.pre_player_authenticated(player_name, player_guid)
        player = self.server.search_for_player(player_name)
        if player is not None:
            player.authorize(player_guid)
        self._triggers.post_player_authenticated(player_name, player_guid)
    def player_spawned(self, player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3):
        self._triggers.pre_player_spawned(player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3)
        pass
        self._triggers.post_player_spawned(player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3)
    def player_killed(self, killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z):
        self._triggers.pre_player_killed(killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z)
        pass
        self._triggers.post_player_killed(killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z)
    def player_chat(self, player_name, message): # target_player_subset is documented argument... but the server doesn't send it
        self._triggers.pre_player_chat(player_name, message)
        pass
        self._triggers.post_player_chat(player_name, message)
    def player_team_changed(self, player_name, team_id, squad_id):
        self._triggers.pre_player_team_changed(player_name, team_id, squad_id)
        pass
        self._triggers.post_player_team_changed(player_name, team_id, squad_id)
    def player_squad_changed(self, player_name, team_id, squad_id):
        self._triggers.pre_player_squad_changed(player_name, team_id, squad_id)
        pass
        self._triggers.post_player_squad_changed(player_name, team_id, squad_id)
    def pb_message(self, message):
        self._triggers.pre_pb_message(message)
        pass
        self._triggers.post_pb_message(message)
    def server_loading_level(self, level_name, rounds_played, rounds_total):
        self._triggers.pre_server_loading_level(level_name, rounds_played, rounds_total)
        pass
        self._triggers.post_server_loading_level(level_name, rounds_played, rounds_total)
    def server_start_level(self):
        self._triggers.pre_server_start_level(self)
        pass
        self._triggers.post_server_start_level(self)
    def server_round_over(winning_team_id):
        self._triggers.pre_server_round_over(self, winning_team_id)
        pass
        self._triggers.post_server_round_over(winning_team_id)
    def server_round_over_playerdata(self, final_player_info_block):
        self._triggers.pre_server_round_over_playerdata(final_player_info_block)
        pass
        self._triggers.post_server_round_over_playerdata(final_player_info_block)
    def server_round_over_teamdata(self, final_team_scores):
        self._triggers.pre_server_round_over_teamdata(final_team_scores)
        pass
        self._triggers.post_server_round_over_teamdata(final_team_scores)

