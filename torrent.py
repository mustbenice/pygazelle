class InvalidTorrentException(Exception):
    pass

class Torrent(object):
    def __init__(self, id, parent_api):
        self.id = id
        self.parent_api = parent_api
