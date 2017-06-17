from _signal import SIGKILL
from subprocess import Popen, PIPE
from multiprocessing import Process, Manager
from os import setsid, getpgid, killpg
from utils import are_valid_paths


DAM_EVENT = 'dam_event'
DAM_ON = 'on'

INOTIFY = 'inotifywait'
MONITOR_RECURSIVE = '-rm'
EVENT = '-e'
CREATE = 'create'
MODIFY = 'modify'
MOVE = 'move'
DELETE = 'delete'
FORMAT = '--format'
PATTERN = '"%w,%e,%f"'


class FileSystemWatchDog:

    def __init__(self, dams=None):
        if dams is not None and not are_valid_paths(dams):
            raise ValueError("Invalid dams, please check the paths")

        self.dams = dams
        self.process = None
        self.manager = Manager()
        self.subprocess_pid = self.manager.Value('pid', -1)
        self.caught_dams = self.manager.dict()

    def release_the_watch_dog(self, new_dams=None):

        if new_dams is not None:
            if are_valid_paths(new_dams):
                self.dams = new_dams
            else:
                raise ValueError("Invalid dams, please check the paths")

        def __watch_dog_handler(dams, caught_dams, subprocess_pid):

            # compose the command to call inotify for watching the list of paths
            def __compose_command(dam_path):
                return [INOTIFY, MONITOR_RECURSIVE, EVENT, ','.join([CREATE, MODIFY, MOVE, DELETE])] + \
                       [FORMAT, PATTERN] + dam_path

            # parse output string
            def __parse_event_output(output):
                output = [piece.replace('"', '') for piece in output.rstrip().split(',')]
                return {'dam': output[0], DAM_EVENT: output[1], DAM_ON: output[-1]}

            # subprocess starts and its pid is saved
            dam_process = Popen(__compose_command(dams), stdin=PIPE, stdout=PIPE, stderr=PIPE, preexec_fn=setsid)
            subprocess_pid.value = dam_process.pid

            # loop checks subprocess' output
            while dam_process.poll() is None:

                event_output = dam_process.stdout.readline().decode('utf-8')

                if event_output:
                    caught_dam = __parse_event_output(event_output)
                    event_key = caught_dam['dam']
                    del caught_dam['dam']

                    if event_key in caught_dams:
                        caught_dams[event_key] = caught_dams[event_key] + [caught_dam]
                    else:
                        caught_dams[event_key] = [caught_dam]

        # process starts __watch_dog_handler
        self.process = Process(target=__watch_dog_handler, args=(self.dams, self.caught_dams, self.subprocess_pid))
        self.process.start()

    def get_caught_dams(self):
        return self.caught_dams if self.caught_dams else None

    def hold_on_to_the_watch_dog(self):

        if self.subprocess_pid.value != -1:
            killpg(getpgid(self.subprocess_pid.value), SIGKILL)

        if self.process.is_alive():
            self.process.terminate()
