from os import path as os_path


def are_valid_paths(paths):
    """
    This method checks all paths given by a string list are right.

    :param paths: List of strings with the paths.
    :return: False if any path of the list is a wrong one, otherwise False.
    """

    if not paths:
        return False

    for path in paths:
        if not os_path.isdir(path) and not os_path.isfile(path):
            return False
    return True
