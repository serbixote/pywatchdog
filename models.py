from json import loads

PATH_KEY = 'path'
EVENT_KEY = 'event'


class Event:

    def __init__(self, event_dict):
        """
        Each instance can have different variables, it depends on sent dictionary structure.

        :param event_dict: dictionary returned by get_path_and_event_dict with the json output.
        """
        self.__dict__ = event_dict


class Dam:

    def __init__(self, dam_path, first_event_dict):
        """
        This method stores the path and add the first Event to the event list.

        :param dam_path: path of watching file/directory returned by get_path_and_event_dict.
        :param first_event_dict: dictionary that represents occurred event returned by get_path_and_event_dict.
        """
        self.path = dam_path
        self.events = []

        first_event = Event(first_event_dict)
        self.events.append(first_event)

    def add_event(self, dam_path, event_dict):
        """
        It adds a Event object to the events list if the dam_path match to path.

        :param dam_path: path of watching file/directory returned by get_path_and_event_dict.
        :param event_dict: dictionary that represents occurred event returned by get_path_and_event_dict.
        :return: nothing
        """
        if self.path == dam_path:
            self.events.append(Event(event_dict))
        else:
            raise ValueError('Paths do not match, the event does not belong to this Dam.')

    @staticmethod
    def get_path_and_event_dict(json_output):
        """
        It has to be called passing to get the path and the event dictionary
        to create a Dam, and add new events.

        :param json_output: output json with path and event values.
        :return: a string with the path of the watching file/directory and a dictionary that represents
        the event occurred.
        """
        dict_output = loads(json_output)
        return dict_output.get(PATH_KEY), dict_output.get(EVENT_KEY)
