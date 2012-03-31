from serverstate.triggersystem import TriggerType
from abstractplugin import AbstractPlugin

class DebugPlugin(AbstractPlugin):
    def __init__(self, state, rcon):
        self.triggertype_trigger = [
                (TriggerType.PRE_CONNECTION_MADE, self.pre_connection_made),
                (TriggerType.POST_CONNECTION_MADE, self.post_connection_made),
                (TriggerType.PRE_CONNECTION_LOST, self.pre_connection_lost),
                (TriggerType.POST_CONNECTION_LOST, self.post_connection_lost),
                (TriggerType.PRE_SERVER_INFO, self.pre_server_info),
                (TriggerType.POST_SERVER_INFO, self.post_server_info),
                (TriggerType.PRE_PLAYER_JOINED, self.pre_player_joined),
                (TriggerType.POST_PLAYER_JOINED, self.post_player_joined),
                (TriggerType.PRE_PLAYER_LEFT, self.pre_player_left),
                (TriggerType.POST_PLAYER_LEFT, self.post_player_left),
                (TriggerType.PRE_PLAYER_KICKED, self.pre_player_kicked),
                (TriggerType.POST_PLAYER_KICKED, self.post_player_kicked),
                (TriggerType.PRE_PLAYER_AUTHENTICATED, self.pre_player_authenticated),
                (TriggerType.POST_PLAYER_AUTHENTICATED, self.post_player_authenticated),
                (TriggerType.PRE_PLAYER_SPAWNED, self.pre_player_spawned),
                (TriggerType.POST_PLAYER_SPAWNED, self.post_player_spawned),
                (TriggerType.PRE_PLAYER_KILLED, self.pre_player_killed),
                (TriggerType.POST_PLAYER_KILLED, self.post_player_killed),
                (TriggerType.PRE_PLAYER_CHAT, self.pre_player_chat),
                (TriggerType.POST_PLAYER_CHAT, self.post_player_chat),
                (TriggerType.PRE_PLAYER_TEAM_CHANGED, self.pre_player_team_changed),
                (TriggerType.POST_PLAYER_TEAM_CHANGED, self.post_player_team_changed),
                (TriggerType.PRE_PLAYER_SQUAD_CHANGED, self.pre_player_squad_changed),
                (TriggerType.POST_PLAYER_SQUAD_CHANGED, self.post_player_squad_changed),
                (TriggerType.PRE_PB_MESSAGE, self.pre_pb_message),
                (TriggerType.POST_PB_MESSAGE, self.post_pb_message),
                (TriggerType.PRE_SERVER_LOADING_LEVEL, self.pre_server_loading_level),
                (TriggerType.POST_SERVER_LOADING_LEVEL, self.post_server_loading_level),
                (TriggerType.PRE_SERVER_START_LEVEL, self.pre_server_start_level),
                (TriggerType.POST_SERVER_START_LEVEL, self.post_server_start_level),
                (TriggerType.PRE_SERVER_ROUND_OVER, self.pre_server_round_over),
                (TriggerType.POST_SERVER_ROUND_OVER, self.post_server_round_over),
                (TriggerType.PRE_SERVER_ROUND_OVER_PLAYERDATA, self.pre_server_round_over_playerdata),
                (TriggerType.POST_SERVER_ROUND_OVER_PLAYERDATA, self.post_server_round_over_playerdata),
                (TriggerType.PRE_SERVER_ROUND_OVER_TEAMDATA, self.pre_server_round_over_teamdata),
                (TriggerType.POST_SERVER_ROUND_OVER_TEAMDATA, self.post_server_round_over_teamdata),
                ]
        super(DebugPlugin, self).__init__(state, rcon)
    def log(self, message):
        print message
    def pre_connection_made(self):
        self.log("""pre_connection_made()""")
    def post_connection_made(self):
        self.log("""post_connection_made()""")
    def pre_connection_lost(self, reason):
        self.log("""pre_connection_lost(
    reason = %(reason)s
)""" % locals())
    def post_connection_lost(self, reason):
        self.log("""post_connection_lost(
    reason = %(reason)s
)""" % locals())
    def pre_server_info(self, *args): # TODO
        self.log("""pre_server_info(
    args = %(args)s
)""" % locals())
    def post_server_info(self, *args): # TODO
        self.log("""post_server_info(
    args = %(args)s
)""" % locals())
    def pre_player_joined(self, player_name, player_guid):
        self.log("""pre_player_joined(
    player_name = %(player_name)s
    player_guid = %(player_guid)s
)""" % locals())
    def post_player_joined(self, player_name, player_guid):
        self.log("""post_player_joined(
    player_name = %(player_name)s
    player_guid = %(player_guid)s
)""" % locals())
    def pre_player_left(self, player_name, player_info_block):
        self.log("""pre_player_left(
    player_name = %(player_name)s
    player_info_block = %(player_info_block)s
)""" % locals())
    def post_player_left(self, player_name, player_info_block):
        self.log("""post_player_left(
    player_name = %(player_name)s
    player_info_block = %(player_info_block)s
)""" % locals())
    def pre_player_kicked(self, player_name, kick_reason):
        self.log("""pre_player_kicked(
    player_name = %(player_name)s
    kick_reason = %(kick_reason)s
)""" % locals())
    def post_player_kicked(self, player_name, kick_reason):
        self.log("""post_player_kicked(
    player_name = %(player_name)s
    kick_reason = %(kick_reason)s
)""" % locals())
    def pre_player_authenticated(self, player_name):
        self.log("""pre_player_authenticated(
    player_name = %(player_name)s
)""" % locals())
    def post_player_authenticated(self, player_name):
        self.log("""post_player_authenticated(
    player_name = %(player_name)s
)""" % locals())
    def pre_player_spawned(self, player_name, team_id):
        self.log("""pre_player_spawned(
    player_name = %(player_name)s
    team_id = %(team_id)s
)""" % locals())
    def post_player_spawned(self, player_name, team_id):
        self.log("""post_player_spawned(
    player_name = %(player_name)s
    team_id = %(team_id)s
)""" % locals())
    def pre_player_killed(self, killer_name, deadguy_name, weapon, is_headshot):
        self.log("""pre_player_killed(
    killer_name = %(killer_name)s
    deadguy_name = %(deadguy_name)s
    weapon = %(weapon)s
    is_headshot = %(is_headshot)s
)""" % locals())
    def post_player_killed(self, killer_name, deadguy_name, weapon, is_headshot):
        self.log("""post_player_killed(
    killer_name = %(killer_name)s
    deadguy_name = %(deadguy_name)s
    weapon = %(weapon)s
    is_headshot = %(is_headshot)s
)""" % locals())
    def pre_player_chat(self, player_name, message):
        self.rcon.admin_say("%s %s" % (player_name, message)) # TODO: ?!
        self.log("""pre_player_chat(
    player_name = %(player_name)s
    message = %(message)s
)""" % locals())
    def post_player_chat(self, player_name, message):
        self.log("""post_player_chat(
    player_name = %(player_name)s
    message = %(message)s
)""" % locals())
    def pre_player_team_changed(self, player_name, team_id, squad_id):
        self.log("""pre_player_team_changed(
    player_name = %(player_name)s
    team_id = %(team_id)s
    squad_id = %(squad_id)s
)""" % locals())
    def post_player_team_changed(self, player_name, team_id, squad_id):
        self.log("""post_player_team_changed(
    player_name = %(player_name)s
    team_id = %(team_id)s
    squad_id = %(squad_id)s
)""" % locals())
    def pre_player_squad_changed(self, player_name, team_id, squad_id):
        self.log("""pre_player_squad_changed(
    player_name = %(player_name)s
    team_id = %(team_id)s
    squad_id = %(squad_id)s
)""" % locals())
    def post_player_squad_changed(self, player_name, team_id, squad_id):
        self.log("""post_player_squad_changed(
    player_name = %(player_name)s
    team_id = %(team_id)s
    squad_id = %(squad_id)s
)""" % locals())
    def pre_pb_message(self, message):
        self.log("""pre_pb_message(
    message = %(message)s
)""" % locals())
    def post_pb_message(self, message):
        self.log("""post_pb_message(
    message = %(message)s
)""" % locals())
    def pre_server_loading_level(self, level_name, rounds_played, rounds_total):
        self.log("""pre_server_loading_level(
    level_name = %(level_name)s
    rounds_played = %(rounds_played)s
    rounds_total = %(rounds_total)s
)""" % locals())
    def post_server_loading_level(self, level_name, rounds_played, rounds_total):
        self.log("""post_server_loading_level(
    level_name = %(level_name)s
    rounds_played = %(rounds_played)s
    rounds_total = %(rounds_total)s
)""" % locals())
    def pre_server_start_level(self):
        self.log("""pre_server_start_level()""")
    def post_server_start_level(self):
        self.log("""post_server_start_level()""")
    def pre_server_round_over(self, winning_team_id):
        self.log("""pre_server_round_over(
    winning_team_id = %(winning_team_id)s
)""" % locals())
    def post_server_round_over(self, winning_team_id):
        self.log("""post_server_round_over(
    winning_team_id = %(winning_team_id)s
)""" % locals())
    def pre_server_round_over_playerdata(self, final_player_info_block):
        self.log("""pre_server_round_over_playerdata(
    final_player_info_block = %(final_player_info_block)s
)""" % locals())
    def post_server_round_over_playerdata(self, final_player_info_block):
        self.log("""post_server_round_over_playerdata(
    final_player_info_block = %(final_player_info_block)s
)""" % locals())
    def pre_server_round_over_teamdata(self, final_team_scores):
        self.log("""pre_server_round_over_teamdata(
    final_team_scores = %(final_team_scores)s
)""" % locals())
    def post_server_round_over_teamdata(self, final_team_scores):
        self.log("""post_server_round_over_teamdata(
    final_team_scores = %(final_team_scores)s
)""" % locals())

