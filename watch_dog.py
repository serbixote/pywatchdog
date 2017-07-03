from _signal import SIGKILL
from multiprocessing import Process, Manager
from os import setsid, getpgid, killpg, path
from subprocess import Popen, PIPE
from models import Dam
from utils import are_valid_paths
import yaml


# pieces of command
INOTIFY = 'inotifywait'
MONITOR_RECURSIVE = '-rm'
EVENT = '-e'
FORMAT = '--format'
TIME_FORMAT = '--timefmt'
EVENT_FORMAT = '{"path": "%w", "event": {"time":"%T", "target":"%f", "events":"%Xe"}}'


class FileSystemWatchDog:

    def __init__(self, dams=None):
        """
        Check paths exists, raise ValueError if any path does not exists.

        :param dams: list of paths for watching.
        """
        if dams is not None and not are_valid_paths(dams):
            raise ValueError("Invalid dams, please check the paths")

        self.dams = dams
        self.process = None
        self.caught_dams = {}
        self.manager = Manager()
        self.output_list = self.manager.list()
        self.subprocess_pid = self.manager.Value('pid', -1)

    def release_the_watch_dog(self, new_dams=None):

        """
        Watching starts in a new process.

        :param new_dams:
        :return:
        """
        if new_dams is not None:
            if are_valid_paths(new_dams):
                self.dams = new_dams
            else:
                raise ValueError("Invalid dams, please check the paths")

        def __watch_dog_handler(dams, subprocess_pid, shared_list):
            """
            This method is executed in a different process that keep reading the output of the
            subprocess created with the inotifywait command.

            :param dams: list of paths for watching.
            :param subprocess_pid: Value object to hold the pid of the subprocess.
            :param shared_list: ListProxy object created by the Manager object to share date between process.
            """
            # compose the command to call inotify for watching the list of paths
            def __compose_command(dam_path_list):

                # load inotifywait-config.yaml
                path_dir = path.dirname(path.abspath(__file__))
                yaml_file = open(path_dir + "/inotifywait-config.yaml")
                yaml_dict = yaml.load(yaml_file)
                yaml_file.close()

                # concatenate the command
                command = [INOTIFY, MONITOR_RECURSIVE, EVENT, ','.join(yaml_dict['events_to_watch'])]
                command += [FORMAT, EVENT_FORMAT, TIME_FORMAT, yaml_dict['date_format']]
                command += dam_path_list
                return command

            dam_process = Popen(__compose_command(dams), stdin=PIPE, stdout=PIPE, stderr=PIPE, preexec_fn=setsid)
            subprocess_pid.value = dam_process.pid

            while dam_process.poll() is None:

                event_output = dam_process.stdout.readline().decode('utf-8')

                if event_output:
                    shared_list.append(event_output)

        self.process = Process(target=__watch_dog_handler, args=(self.dams, self.subprocess_pid, self.output_list))
        self.process.start()

    def get_caught_dams(self, caught_path=None):
        """
        Iterate ListProxy parsing result to caught_dams dictionary.

        :return: return a values list of the caught_dams dictionary.
        """
        while self.output_list:

            output_item = self.output_list.pop()
            dam_path, event_dict = Dam.get_path_and_event_dict(output_item)

            if dam_path not in self.caught_dams:
                self.caught_dams[dam_path] = Dam(dam_path, event_dict)
            else:
                self.caught_dams[dam_path].add_event(dam_path, event_dict)

        if caught_path:
            return self.caught_dams.get(caught_path)
        else:
            return self.caught_dams.values() if self.caught_dams else None

    def hold_on_to_the_watch_dog(self):
        """
        Kill subprocess by the pid and the Process if is still alive.
        """
        try:

            if self.subprocess_pid.value != -1:
                killpg(getpgid(self.subprocess_pid.value), SIGKILL)

        except ProcessLookupError:
            pass

        finally:

            if self.process.is_alive():
                self.process.terminate()
