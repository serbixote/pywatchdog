from json import loads

class Event:

    def __init__(self, json_output):
        self.__dict__ = loads(json_output)

class Dam:

    def __init__(self, json_output):
        self.path =  loads(json_output)
        self.events = None

    def add_event(self,json_output):

        self.events.append(Event(json_output))
