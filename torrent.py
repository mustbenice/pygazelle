import re

class InvalidTorrentException(Exception):
    pass

class Torrent(object):
    def __init__(self, id, parent_api):
        self.id = id
        self.parent_api = parent_api
        self.group = None
        self.media = None
        self.format = None
        self.encoding = None
        self.remaster_year = None
        self.remastered = None
        self.remaster_title = None
        self.remaster_record_label = None
        self.remaster_catalogue_number = None
        self.scene = None
        self.has_log = None
        self.has_cue = None
        self.log_score = None
        self.file_count = None
        self.free_torrent = None
        self.size = None
        self.leechers = None
        self.seeders = None
        self.snatched = None
        self.time = None
        self.has_file = None
        self.description = None
        self.file_list = []
        self.file_path = None
        self.user = None

    def set_torrent_artist_data(self, artist_torrent_json_response):
        if self.id != artist_torrent_json_response['id']:
            raise InvalidTorrentException("Tried to update a Torrent's information from an 'artist' API call with a different id." +
                                       " Should be %s, got %s" % (self.id, artist_torrent_json_response['id']) )

        self.group = self.parent_api.get_torrent_group(artist_torrent_json_response['groupId'])
        self.media = artist_torrent_json_response['media']
        self.format = artist_torrent_json_response['format']
        self.encoding = artist_torrent_json_response['encoding']
        self.remaster_year = artist_torrent_json_response['remasterYear']
        self.remastered = artist_torrent_json_response['remastered']
        self.remaster_title = artist_torrent_json_response['remasterTitle']
        self.remaster_record_label = artist_torrent_json_response['remasterRecordLabel']
        self.scene = artist_torrent_json_response['scene']
        self.has_log = artist_torrent_json_response['hasLog']
        self.has_cue = artist_torrent_json_response['hasCue']
        self.log_score = artist_torrent_json_response['logScore']
        self.file_count = artist_torrent_json_response['fileCount']
        self.free_torrent = artist_torrent_json_response['freeTorrent']
        self.size = artist_torrent_json_response['size']
        self.leechers = artist_torrent_json_response['leechers']
        self.seeders = artist_torrent_json_response['seeders']
        self.snatched = artist_torrent_json_response['snatched']
        self.time = artist_torrent_json_response['time']
        self.has_file = artist_torrent_json_response['hasFile']

    def set_torrent_group_data(self, group_torrent_json_response):
        if self.id != group_torrent_json_response['id']:
            raise InvalidTorrentException("Tried to update a Torrent's information from a 'torrentgroup' API call with a different id." +
                                          " Should be %s, got %s" % (self.id, group_torrent_json_response['id']) )

        self.group = self.parent_api.get_torrent_group(group_torrent_json_response['groupId'])
        self.media = group_torrent_json_response['media']
        self.format = group_torrent_json_response['format']
        self.encoding = group_torrent_json_response['encoding']
        self.remastered = group_torrent_json_response['remastered']
        self.remaster_year = group_torrent_json_response['remasterYear']
        self.remaster_title = group_torrent_json_response['remasterTitle']
        self.remaster_record_label = group_torrent_json_response['remasterRecordLabel']
        self.remaster_catalogue_number = group_torrent_json_response['remasterCatalogueNumber']
        self.scene = group_torrent_json_response['scene']
        self.has_log = group_torrent_json_response['hasLog']
        self.has_cue = group_torrent_json_response['hasCue']
        self.log_score = group_torrent_json_response['logScore']
        self.file_count = group_torrent_json_response['fileCount']
        self.size = group_torrent_json_response['size']
        self.seeders = group_torrent_json_response['seeders']
        self.leechers = group_torrent_json_response['leechers']
        self.snatched = group_torrent_json_response['snatched']
        self.free_torrent = group_torrent_json_response['freeTorrent']
        self.time = group_torrent_json_response['time']
        self.description = group_torrent_json_response['description']
        self.file_list = [ re.match("(.+){{{(\d+)}}}", item).groups()
                           for item in group_torrent_json_response['fileList'].split("|||") ] # tuple ( filename, filesize )
        self.file_path = group_torrent_json_response['filePath']
        self.user = self.parent_api.get_user(group_torrent_json_response['userId'])

    def set_torrent_search_data(self, search_torrent_json_response):
        # TODO: handle torrent data from a torrent search
        pass

    def __repr__(self):
        return "Torrent: %s - %s - ID: %s" % (self.group.name, self.encoding, self.id)