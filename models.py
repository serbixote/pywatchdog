from json import loads

PATH_KEY = 'path'
EVENT_KEY = 'event'


class Event:

    """
    Each instance can have different variables, it depends on
    sent dictionary structure.
    """
    def __init__(self, event_dict):
        self.__dict__ = event_dict


class Dam:

    def __init__(self, dam_path, first_event_dict):

        self.path = dam_path
        self.events = []

        first_event = Event(first_event_dict)
        self.events.append(first_event)

    def add_event(self, dam_path, event_dict):

        if self.path == dam_path:
            self.events.append(Event(event_dict))

    @staticmethod
    def get_path_and_event_dict(json_output):

        dict_output = loads(json_output)
        return dict_output.get(PATH_KEY), dict_output.get(EVENT_KEY)
