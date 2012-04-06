from serverstate.triggersystem import TriggerType
from abstractplugin import AbstractPlugin

class ToyPlugin(AbstractPlugin):
    def __init__(self, state, rcon):
        self.triggertype_trigger = [
                (TriggerType.POST_CONNECTION_MADE, self.post_connection_made),
                (TriggerType.POST_CONNECTION_LOST, self.post_connection_lost),
                (TriggerType.POST_SERVER_INFO, self.post_server_info),
                (TriggerType.POST_PLAYER_JOINED, self.post_player_joined),
                (TriggerType.POST_PLAYER_LEFT, self.post_player_left),
                (TriggerType.POST_PLAYER_KICKED, self.post_player_kicked),
                (TriggerType.POST_PLAYER_AUTHENTICATED, self.post_player_authenticated),
                (TriggerType.POST_PLAYER_SPAWNED, self.post_player_spawned),
                (TriggerType.POST_PLAYER_KILLED, self.post_player_killed),
                (TriggerType.POST_PLAYER_CHAT, self.post_player_chat),
                (TriggerType.POST_PLAYER_TEAM_CHANGED, self.post_player_team_changed),
                (TriggerType.POST_PLAYER_SQUAD_CHANGED, self.post_player_squad_changed),
                (TriggerType.POST_PB_MESSAGE, self.post_pb_message),
                (TriggerType.POST_SERVER_LOADING_LEVEL, self.post_server_loading_level),
                (TriggerType.POST_SERVER_START_LEVEL, self.post_server_start_level),
                (TriggerType.POST_SERVER_ROUND_OVER, self.post_server_round_over),
                (TriggerType.POST_SERVER_ROUND_OVER_PLAYERDATA, self.post_server_round_over_playerdata),
                (TriggerType.POST_SERVER_ROUND_OVER_TEAMDATA, self.post_server_round_over_teamdata),
                ]
        super(ToyPlugin, self).__init__(state, rcon)
    def post_connection_made(self):
        pass
    def post_connection_lost(self, reason):
        pass
    def post_server_info(self, *args): # TODO
        pass
    def post_player_joined(self, player_name, player_guid):
        pass
    def post_player_left(self, player_name, player_info_block):
        pass
    def post_player_kicked(self, player_name, kick_reason):
        pass
    def post_player_authenticated(self, player_name):
        pass
    def post_player_spawned(self, player_name, team_id):
        pass
    def post_player_killed(self, killer_name, deadguy_name, weapon, is_headshot):
        pass
    def post_player_chat(self, player_name, message):
        player = self.state.server.search_for_player(player_name) # TODO
        if player is None:
            return
        words = message.split()
        if len(words)<1:
            return
        command = words[0]

        if command == '!killme':
            self.rcon.admin_killPlayer(player.name)
        elif command == 'test':
            duration = 7
            self.rcon.admin_yell([player], "A\t quite\n long test message", duration)

        if len(words)<2:
            return
        arguments = words[1:]
        message = " ".join(arguments)
        if command == '!say':
            self.rcon.admin_say([player], message)
        elif command == '!yell':
            duration = 7
            self.rcon.admin_yell([player], message, duration)
    def post_player_team_changed(self, player_name, team_id, squad_id):
        pass
    def post_player_squad_changed(self, player_name, team_id, squad_id):
        pass
    def post_pb_message(self, message):
        pass
    def post_server_loading_level(self, level_name, rounds_played, rounds_total):
        pass
    def post_server_start_level(self):
        pass
    def post_server_round_over(self, winning_team_id):
        pass
    def post_server_round_over_playerdata(self, final_player_info_block):
        pass
    def post_server_round_over_teamdata(self, final_team_scores):
        pass

