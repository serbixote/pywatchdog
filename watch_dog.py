from subprocess import Popen, PIPE
from multiprocessing import Process, Manager
import os

DAM_SUBPROCESS = 'dam_subprocess'
DAM_EVENTS = 'dam_events'

INOTIFY = 'inotifywait'
MONITOR = '-m'
RECURSIVE = '-r'
EVENT = '-e'
CREATE = 'create'
MODIFY = 'modify'
MOVE_FROM_AND_TO = 'move'
DELETE = 'delete'


class FileSystemWatchDog:

    def __init__(self, dams):
        if not self.are_valid_dams(dams):
            raise ValueError("Invalid dams, please check the paths")

        self.dams = dams
        self.process = None
        self.manager = Manager()
        self.watching = self.manager.Value('running', True)
        self.watched_dams = self.manager.dict()

    @staticmethod
    def are_valid_dams(dams):
        if not dams:
            return False

        for dam in dams:
            if not os.path.isdir(dam) and not os.path.isfile(dam):
                return False
        return True

    def release_the_watch_dog(self, new_dams=None):

        if new_dams is not None:
            if self.are_valid_dams(new_dams):
                self.dams = new_dams
            else:
                raise ValueError("Invalid dams, please check the paths")

        def __watch_dog_handler(dams, watched_dams, running):

            # processes
            dam_processes = {}

            # Compose the command list
            def __compose_command(dam_path):
                return [INOTIFY, MONITOR, RECURSIVE, EVENT, CREATE, EVENT, MODIFY, EVENT, MOVE_FROM_AND_TO,
                        EVENT, DELETE, dam_path]

            # Starting subprocess
            for dam in dams:
                dam_process = Popen(__compose_command(dam), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                dam_processes[dam] = dam_process

            # Watching dams
            while running.value:
                for dam_process in dam_processes:
                    if dam_processes[dam_process].poll() is None:
                        pass
                        '''
                        event = dam_processes[dam_process].stdout.readline().decode('utf-8')
                        if event is not None:
                            watched_dams[dam_process] = event
                        '''

            # Stopping subprocess
            for dam_process in dam_processes:
                if dam_processes[dam_process].poll() is None:
                    dam_processes[dam_process].kill()

        self.process = Process(target=__watch_dog_handler, args=(self.dams, self.watched_dams, self.watching))
        self.process.start()

    def get_caught_dams(self):
        return self.watched_dams

    def hold_on_to_the_watch_dog(self):
        self.watching.value = False


