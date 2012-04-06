class AbstractPlugin(object):
    def __init__(self, state, rcon):
        self.state = state
        self.rcon = rcon
        self.register_triggers()

    def register_triggers(self):
        tsr = self.state.triggers.register_trigger
        for trigger_type, trigger in self.triggertype_trigger:
            tsr(trigger_type, trigger)

    def log(self, message):
        print "[%s] %s" % (self.__class__.__name__, message)

