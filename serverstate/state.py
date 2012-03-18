class Server(object):
    _GAME_MOD_ID_VANILLA = 1001
    _GAME_MOD_ID_KARKAND = 1002
    _TEAM_ID_NEUTRAL = 0
    def __init__(self):
        self.neutral_team = Team(self._TEAM_ID_NEUTRAL)

    def add_player(self, player_name):
        self.neutral_team.no_squad.add_player(player_name)

    def authorize_player(self, player_name, guid):
        self.get_player(player_name).authorize(guid)

    def get_player(self, player_name):
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
    def __init__(self):
        self.squads = {}
        for squad_id in self._SQUAD_NAME_ID_MAP.keys():
            squad_name = self._SQUAD_NAME_ID_MAP[squad_id]
            self.squads[squad_id] = Squad(squad_name)
        self.no_squad = self.squads[self._SQUAD_ID_NONE]

    def get_player(self, player_name):
        """ returns Player object or None """
        for squad_id in self.teams:
            squad = self.players[squad_id]
            player_or_none = squad.get_player(player_name)
            if player_or_none is not None:
                return player_or_none
        return None

class Squad(object):
    def __init__(self):
        self.players = []

    def add_player(self, player_name):
        if player_name in self.players:
            pass # TODO: handle this situation
        self.players.append(Player(player_name))

    def get_player(self, player_name):
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
    def __init__(self, player_name):
        self.name = player_name
        self.guid = None

    def authorize(self, guid):
        self.guid = guid

class StateAPI(object):
    def player_joined(self, player_name):
        pass
    def player_left(self, player_name, player_info_block):
        pass
    def player_kicked(self, player_name, kick_reason):
        pass
    def player_authenticated(self, player_name, player_guid):
        pass
    def player_died(self, player_info_block):
        pass
    def player_spawned(self, player_name, player_kit, weapons, gadgets):
        pass
    def player_killed(self, killer_name, deadguy_name, weapon, is_headshot, killer_approx_location, deadguy_approx_location):
        pass
    def player_chat(self, player_name, message, target_player_subset):
        pass
    def player_team_changed(self, player_name, team_id, squad_id):
        pass
    def player_squad_changed(self, player_name, team_id, squad_id):
        pass
    def pb_message(self, message):
        pass
    def server_loading_level(self, level_name, rounds_played, rounds_total):
        pass
    def server_start_level(self):
        pass
    def server_round_over(self, winning_team_id):
        pass
    def server_round_over_playerdata(self, final_player_info_block):
        pass
    def server_round_over_teamdata(self, final_team_scores):
        pass
