#!/usr/bin/env python
# Makes use of / builds on the API implementation from 'whatbetter', by Zachary Denton
# See https://github.com/zacharydenton/whatbetter

import re
import os
import json
import time
import requests
import HTMLParser
from cStringIO import StringIO

from user import User
from artist import Artist
from tag import Tag
from request import Request
from torrent import Torrent

class LoginException(Exception):
    pass

class RequestException(Exception):
    pass

class GazelleAPI(object):
    default_headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3)'\
                      'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79'\
                      'Safari/535.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
                  ',*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}


    def __init__(self, username=None, password=None):
        self.session = requests.session(headers=self.default_headers)
        self.username = username
        self.password = password
        self.authkey = None
        self.passkey = None
        self.userid = None
        self.logged_in_user = None
        self.cached_users = {}
        self.cached_artists = {}
        self.cached_tags = {}
        self.cached_torrents = {}
        self.cached_requests = {}
        self.site = "https://what.cd/"
        self.last_request = time.time()
        self.rate_limit = 2.0 # seconds between requests
        self._login()

    def _login(self):
        """
        Private method.
        Logs in user and gets authkey from server.
        """
        loginpage = 'https://what.cd/login.php'
        data = {'username': self.username,
                'password': self.password}
        r = self.session.post(loginpage, data=data)
        if r.status_code != 200:
            raise LoginException
        accountinfo = self.request('index')
        self.userid = accountinfo['id']
        self.authkey = accountinfo['authkey']
        self.passkey = accountinfo['passkey']
        self.logged_in_user = User(self.userid, self)
        self.logged_in_user.set_index_data(accountinfo)

    def request(self, action, **kwargs):
        """
        Makes an AJAX request at a given action.
        Pass an action and relevant arguments for that action.
        """

        ajaxpage = 'ajax.php'
        content = self.unparsed_request(ajaxpage, action, **kwargs)
        try:
            parsed = json.loads(content)
            if parsed['status'] != 'success':
                raise RequestException
            return parsed['response']
        except ValueError:
            raise RequestException

    def unparsed_request(self, page, action, **kwargs):
        """
        Makes a generic HTTP request at a given page with a given action.
        Also pass relevant arguments for that action.
        """
        while time.time() - self.last_request < self.rate_limit:
            time.sleep(0.1)

        url = "%s/%s" % (self.site, page)
        params = {'action': action}
        if self.authkey:
            params['auth'] = self.authkey
        params.update(kwargs)
        r = self.session.get(url, params=params, allow_redirects=False)
        self.last_request = time.time()
        return r.content

    def get_user(self, id):
        """
        Returns a User for the passed ID, associated with this API object. If the ID references the currently logged in
        user, the user returned will be pre-populated with the information from an 'index' API call. Otherwise, you'll
        need to call User.update_user_data(). This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id == self.userid:
            return self.logged_in_user
        elif id in self.cached_users.keys():
            return self.cached_users[id]
        else:
            return User(id, self)

    def search_users(self, search_query):
        """
        Returns a list of users returned for the search query. You can search by name, part of name, and ID number. If
        one of the returned users is the currently logged-in user, that user object will be pre-populated with the
        information from an 'index' API call. Otherwise only the limited info returned by the search will be pre-pop'd.
        You can query more information with User.update_user_data(). This is done on demand to reduce unnecessary API calls.
        """
        response = self.request(action='usersearch', search=search_query)
        results = response['results']

        found_users = []
        for result in results:
            user = self.get_user(result['userId'])
            user.set_search_result_data(result)
            found_users.append(user)

        return found_users

    def get_artist(self, id):
        """
        Returns an Artist for the passed ID, associated with this API object. You'll need to call Artist.update_data()
        if the artist hasn't already been cached. This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id in self.cached_artists.keys():
            return self.cached_artists[id]
        else:
            return Artist(id, self)

    def get_tag(self, name):
        """
        Returns a Tag for the passed name, associated with this API object. If you know the count value for this tag,
        pass it to update the object. There is no way to query the count directly from the API, but it can be retrieved
        from other calls such as 'artist', however.
        """
        if name in self.cached_tags.keys():
            return self.cached_tags[name]
        else:
            return Tag(id, self)

    def get_request(self, id):
        """
        Returns a Request for the passed ID, associated with this API object. You'll need to call Request.update_data()
        if the request hasn't already been cached. This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id in self.cached_requests.keys():
            return self.cached_requests[id]
        else:
            return Request(id, self)

    def get_torrent_group(self, id):
        """
        Returns a TorrentGroup for the passed ID, associated with this API object. You'll need to call Request.update_data()
        if the request hasn't already been cached. This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id in self.cached_requests.keys():
            return self.cached_requests[id]
        else:
            return Request(id, self)

    def get_torrent(self, id):
        """
        Returns a TorrentGroup for the passed ID, associated with this API object. You'll need to call Request.update_data()
        if the request hasn't already been cached. This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id in self.cached_torrents.keys():
            return self.cached_torrents[id]
        else:
            return Torrent(id, self)

    def generate_torrent_link(self, id):
        url = "https://%s/torrents.php?action=download&id=%s&authkey=%s&torrent_pass=%s" %\
              (self.site, id, self.logged_in_user.authkey, self.logged_in_user.passkey)
        return url

    def save_torrent_file(self, id, dest):
        file_data = self.unparsed_request("torrents.php", 'download',
            id=id, authkey=self.logged_in_user.authkey, torrent_pass=self.logged_in_user.passkey)
        with open(dest, 'w+') as dest_file:
            dest_file.write(file_data)