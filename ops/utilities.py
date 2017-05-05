import os
from glob import iglob


def get_files(file, wildcard):
    return iglob(os.path.join(file, wildcard))
