''' AtlasCache - Cache file info to speed up verification stage.
'''

import email.utils
import hashlib
import json
import os


class AtlasCache:
    _default = {
        "manifest": "",  # Manifest URL
        "last-modified": "",  # Last-Modified: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT
        "cache":
        {
            # "filename":
            # {
            #     "date": "file mtime in GMT",
            #     "size": "file size",
            #     "md5": "file MD5 tag"
            # },
            # "filename2":
            # {
            #     "date": "file mtime in GMT",
            #     "size": "file size",
            #     "md5": "file MD5 tag"
            # }
        }
    }

    def __init__(self, manifest_url, last_modified):
        ''' Make sure the cache exists.

        manifest_url - the URL of the manifest file
        last_modified - the Last-Modified header from the manifest file's URL
        '''
        self.cache_dir = os.path.expanduser('~/.config/atlas-launcher/cache')
        self.cache_file = hashlib.md5(bytes(manifest_url, 'utf-8')).hexdigest() + '.json'
        self.cache_path = os.path.join(self.cache_dir, self.cache_file)

        self.last_modified = email.utils.parsedate_to_datetime(last_modified)

        # Create cache directory if it doesn't exist.
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # If the cache file doesn't exist, we create an empty cache. Otherwise,
        # load the existing cache.
        if not os.path.exists(self.cache_path):
            self.cache = AtlasCache._default.copy()
            self.cache.manifest = manifest_url
            self.cache.last_modified = last_modified
        else:
            with open(self.cache_path, 'r') as fp:
                self.cache = json.load(fp)

            # If this somehow doesn't match the URL, empty the cache.
            if self.cache.manifest != manifest_url:
                self.cache.cache = {}
                self.cache.manifest = manifest_url
                self.last_modified = last_modified

    def save(self):
        ''' Save the cache data.
        '''
        tmp_filename = self.cache_path + '.atlas'

        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

        with open(self.tmp_filename, 'w') as fp:
            json.dump(self.cache, fp)

        os.unlink(self.cache_path)
        os.rename(tmp_filename, self.cache_path)

    def needs_check(self, file_name, file_date, file_size):
        ''' Returns true if we need to MD5 file_name.

        If the size matches and the file_date is <= the last_modified, you
        don't need to MD5 the file to check it.
        '''
        if file_name not in self.cache.cache:
            return true

        if file_size != self.cache.cache[file_name].get('size', -1):
            return true
