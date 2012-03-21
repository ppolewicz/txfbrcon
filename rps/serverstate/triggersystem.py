class TriggerType(object):
    PRE_PLAYER_JOINED = 2001
    POST_PLAYER_JOINED = 2002
    PRE_PLAYER_LEFT = 2003
    POST_PLAYER_LEFT = 2004
    PRE_PLAYER_KICKED = 2005
    POST_PLAYER_KICKED = 2006
    PRE_PLAYER_AUTHENTICATED = 2007
    POST_PLAYER_AUTHENTICATED = 2008
    PRE_PLAYER_SPAWNED = 2009
    POST_PLAYER_SPAWNED = 2010
    PRE_PLAYER_KILLED = 2011
    POST_PLAYER_KILLED = 2012
    PRE_PLAYER_CHAT = 2013
    POST_PLAYER_CHAT = 2014
    PRE_PLAYER_TEAM_CHANGED = 2015
    POST_PLAYER_TEAM_CHANGED = 2016
    PRE_PLAYER_SQUAD_CHANGED = 2017
    POST_PLAYER_SQUAD_CHANGED = 2018
    PRE_PB_MESSAGE = 2019
    POST_PB_MESSAGE = 2020
    PRE_SERVER_LOADING_LEVEL = 2021
    POST_SERVER_LOADING_LEVEL = 2022
    PRE_SERVER_START_LEVEL = 2023
    POST_SERVER_START_LEVEL = 2024
    PRE_SERVER_ROUND_OVER = 2025
    POST_SERVER_ROUND_OVER = 2026
    PRE_SERVER_ROUND_OVER_PLAYERDATA = 2027
    POST_SERVER_ROUND_OVER_PLAYERDATA = 2028
    PRE_SERVER_ROUND_OVER_TEAMDATA = 2029
    POST_SERVER_ROUND_OVER_TEAMDATA = 2030

class TriggerSystem(object):
    def __init__(self):
        self._trigger_index[TriggerType.PRE_PLAYER_JOINED] = self._triggers_pre_player_joined = []
        self._trigger_index[TriggerType.POST_PLAYER_JOINED] = self._triggers_post_player_joined = []
        self._trigger_index[TriggerType.PRE_PLAYER_LEFT] = self._triggers_pre_player_left = []
        self._trigger_index[TriggerType.POST_PLAYER_LEFT] = self._triggers_post_player_left = []
        self._trigger_index[TriggerType.PRE_PLAYER_KICKED] = self._triggers_pre_player_kicked = []
        self._trigger_index[TriggerType.POST_PLAYER_KICKED] = self._triggers_post_player_kicked = []
        self._trigger_index[TriggerType.PRE_PLAYER_AUTHENTICATED] = self._triggers_pre_player_authenticated = []
        self._trigger_index[TriggerType.POST_PLAYER_AUTHENTICATED] = self._triggers_post_player_authenticated = []
        self._trigger_index[TriggerType.PRE_PLAYER_DIED] = self._triggers_pre_player_died = []
        self._trigger_index[TriggerType.POST_PLAYER_DIED] = self._triggers_post_player_died = []
        self._trigger_index[TriggerType.PRE_PLAYER_SPAWNED] = self._triggers_pre_player_spawned = []
        self._trigger_index[TriggerType.POST_PLAYER_SPAWNED] = self._triggers_post_player_spawned = []
        self._trigger_index[TriggerType.PRE_PLAYER_KILLED] = self._triggers_pre_player_killed = []
        self._trigger_index[TriggerType.POST_PLAYER_KILLED] = self._triggers_post_player_killed = []
        self._trigger_index[TriggerType.PRE_PLAYER_CHAT] = self._triggers_pre_player_chat = []
        self._trigger_index[TriggerType.POST_PLAYER_CHAT] = self._triggers_post_player_chat = []
        self._trigger_index[TriggerType.PRE_PLAYER_TEAM_CHANGED] = self._triggers_pre_player_team_changed = []
        self._trigger_index[TriggerType.POST_PLAYER_TEAM_CHANGED] = self._triggers_post_player_team_changed = []
        self._trigger_index[TriggerType.PRE_PLAYER_SQUAD_CHANGED] = self._triggers_pre_player_squad_changed = []
        self._trigger_index[TriggerType.POST_PLAYER_SQUAD_CHANGED] = self._triggers_post_player_squad_changed = []
        self._trigger_index[TriggerType.PRE_PB_MESSAGE] = self._triggers_pre_pb_message = []
        self._trigger_index[TriggerType.POST_PB_MESSAGE] = self._triggers_post_pb_message = []
        self._trigger_index[TriggerType.PRE_SERVER_LOADING_LEVEL] = self._triggers_pre_server_loading_level = []
        self._trigger_index[TriggerType.POST_SERVER_LOADING_LEVEL] = self._triggers_post_server_loading_level = []
        self._trigger_index[TriggerType.PRE_SERVER_START_LEVEL] = self._triggers_pre_server_start_level = []
        self._trigger_index[TriggerType.POST_SERVER_START_LEVEL] = self._triggers_post_server_start_level = []
        self._trigger_index[TriggerType.PRE_SERVER_ROUND_OVER] = self._triggers_pre_server_round_over = []
        self._trigger_index[TriggerType.POST_SERVER_ROUND_OVER] = self._triggers_post_server_round_over = []
        self._trigger_index[TriggerType.PRE_SERVER_ROUND_OVER_PLAYERDATA] = self._triggers_pre_server_round_over_playerdata = []
        self._trigger_index[TriggerType.POST_SERVER_ROUND_OVER_PLAYERDATA] = self._triggers_post_server_round_over_playerdata = []
        self._trigger_index[TriggerType.PRE_SERVER_ROUND_OVER_TEAMDATA] = self._triggers_pre_server_round_over_teamdata = []
        self._trigger_index[TriggerType.POST_SERVER_ROUND_OVER_TEAMDATA] = self._triggers_post_server_round_over_teamdata = []
    def _get_trigger_collection(self, trigger_type):
        return self._trigger_index[trigger_type]
    def register_trigger(self, trigger_type, trigger):
        self._get_trigger_collection(trigger_type).append(trigger)
    def unregister_trigger(self, trigger_type, trigger):
        self._get_trigger_collection(trigger_type).remove(trigger)
    def pre_player_joined(self, player_name, player_guid):
        for trigger in self._triggers_pre_player_joined:
            trigger(player_name, player_guid)
    def post_player_joined(self, player_name, player_guid):
        for trigger in self._triggers_post_player_joined:
            trigger(player_name, player_guid)
    def pre_player_left(self, player_name, player_info_block):
        for trigger in self._triggers_pre_player_left:
            trigger(player_name, player_info_block)
    def post_player_left(self, player_name, player_info_block):
        for trigger in self._triggers_post_player_left:
            trigger(player_name, player_info_block)
    def pre_player_kicked(self, player_name, kick_reason):
        for trigger in self._triggers_pre_player_kicked:
            trigger(player_name, kick_reason)
    def post_player_kicked(self, player_name, kick_reason):
        for trigger in self._triggers_post_player_kicked:
            trigger(player_name, kick_reason)
    def pre_player_authenticated(self, player_name, player_guid):
        for trigger in self._triggers_pre_player_authenticated:
            trigger(player_name, player_guid)
    def post_player_authenticated(self, player_name, player_guid):
        for trigger in self._triggers_post_player_authenticated:
            trigger(player_name, player_guid)
    def pre_player_spawned(self, player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3):
        for trigger in self._triggers_pre_player_spawned:
            trigger(player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3)
    def post_player_spawned(self, player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3):
        for trigger in self._triggers_post_player_spawned:
            trigger(player_name, player_kit, weapon1, weapon2, weapon3, gadget1, gadget2, gadget3)
    def pre_player_killed(self, killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z):
        for trigger in self._triggers_pre_player_killed:
            trigger(killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z)
    def post_player_killed(self, killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z):
        for trigger in self._triggers_post_player_killed:
            trigger(killer_name, deadguy_name, weapon, is_headshot, killer_approx_x, killer_approx_y, killer_approx_z, deadguy_approx_x, deadguy_approx_y, deadguy_approx_z)
    def pre_player_chat(self, player_name, message, target_player_subset):
        for trigger in self._triggers_pre_player_chat:
            trigger(player_name, message, target_player_subset)
    def post_player_chat(self, player_name, message, target_player_subset):
        for trigger in self._triggers_post_player_chat:
            trigger(player_name, message, target_player_subset)
    def pre_player_team_changed(self, player_name, team_id, squad_id):
        for trigger in self._triggers_pre_player_team_changed:
            trigger(player_name, team_id, squad_id)
    def post_player_team_changed(self, player_name, team_id, squad_id):
        for trigger in self._triggers_post_player_team_changed:
            trigger(player_name, team_id, squad_id)
    def pre_player_squad_changed(self, player_name, team_id, squad_id):
        for trigger in self._triggers_pre_player_squad_changed:
            trigger(player_name, team_id, squad_id)
    def post_player_squad_changed(self, player_name, team_id, squad_id):
        for trigger in self._triggers_post_player_squad_changed:
            trigger(player_name, team_id, squad_id)
    def pre_pb_message(self, message):
        for trigger in self._triggers_pre_pb_message:
            trigger(message)
    def post_pb_message(self, message):
        for trigger in self._triggers_post_pb_message:
            trigger(message)
    def pre_server_loading_level(self, level_name, rounds_played, rounds_total):
        for trigger in self._triggers_pre_server_loading_level:
            trigger(level_name, rounds_played, rounds_total)
    def post_server_loading_level(self, level_name, rounds_played, rounds_total):
        for trigger in self._triggers_post_server_loading_level:
            trigger(level_name, rounds_played, rounds_total)
    def pre_server_start_level(self):
        for trigger in self._triggers_pre_server_start_level:
            trigger(self)
    def post_server_start_level(self):
        for trigger in self._triggers_post_server_start_level:
            trigger(self)
    def pre_server_round_over(self, winning_team_id):
        for trigger in self._triggers_pre_server_round_over:
            trigger(winning_team_id)
    def post_server_round_over(self, winning_team_id):
        for trigger in self._triggers_post_server_round_over:
            trigger(winning_team_id)
    def pre_server_round_over_playerdata(self, final_player_info_block):
        for trigger in self._triggers_pre_server_round_over_playerdata:
            trigger(final_player_info_block)
    def post_server_round_over_playerdata(self, final_player_info_block):
        for trigger in self._triggers_post_server_round_over_playerdata:
            trigger(final_player_info_block)
    def pre_server_round_over_teamdata(self, final_team_scores):
        for trigger in self._triggers_pre_server_round_over_teamdata:
            trigger(final_team_scores)
    def post_server_round_over_teamdata(self, final_team_scores):
        for trigger in self._triggers_post_server_round_over_teamdata:
            trigger(final_team_scores)

