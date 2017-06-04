from _signal import SIGKILL
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
        self.subprocess_pid = self.manager.Value('pid', -1)
        self.caught_dams = self.manager.dict()

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

        def __watch_dog_handler(dams, caught_dams, subprocess_pid):

            # compose a command to call the bash script TODO: creating bash script and modify __compose_command
            def __compose_command(dam_path):
                return [INOTIFY, MONITOR, RECURSIVE, EVENT, CREATE, EVENT, MODIFY, EVENT, MOVE_FROM_AND_TO,
                        EVENT, DELETE, dam_path]

            # subprocess starts and its pid is saved
            dam_process = Popen(__compose_command(dams[0]), stdin=PIPE, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid)
            subprocess_pid.value = dam_process.pid

            # loop checks subprocess' output
            while dam_process.poll() is None:

                try:
                    output = dam_process.stdout.readline().decode('utf-8')
                    if output:
                        # TODO: parse result method
                        caught_dams['event'] = output
                except Exception:
                    break

        # process starts __watch_dog_handler
        self.process = Process(target=__watch_dog_handler, args=(self.dams, self.caught_dams, self.subprocess_pid))
        self.process.start()

    def get_caught_dams(self):
        return self.caught_dams

    def hold_on_to_the_watch_dog(self):
        if self.subprocess_pid.value != -1:
            os.killpg(os.getpgid(self.subprocess_pid.value), SIGKILL)
        if self.process.is_alive():
            self.process.terminate()
