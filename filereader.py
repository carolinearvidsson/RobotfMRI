import os

class FilesList:
    def get_transfiles(path):
        path = path
        files = os.listdir(path)
        transfiles = [f for f in files if f.startswith('S') and f.endswith('.TextGrid')]
        return [f for f in transfiles]
