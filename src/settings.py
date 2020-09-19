''' AtlasSettings - Application settings for Atlas Launcher.
'''

import json
import os


class AtlasSettings:
    HOMECOMING_MANIFEST = 'http://patch.savecoh.com/manifest.xml'
    HOMECOMING_GAMEDIR = '~/City of Heroes - Homecoming'

    ''' Not sure what belongs in here yet.

    _default = {
        "manifests":
        [
            {
                "url": "manifest url",
                "game": "game directory",
                "last_launch": "profile 'exec' string"
            },
            {
                "url": "manifest2",
                "game": "gamedir2",
                "last_launch": "profile 'exec' 2"
            }
        ],
        "last_manifest": "manifest2",
        "md_threads": 2,
        "dl_threads": 4,
        "window_position":
        {
            "x": 0, "y": 0
        }
    }
    '''

    # Minimal settings for now.
    _default = {
        'manifests': [],
        'last_manifest': None,
        'md_threads': 1,  # MD5 checker threads
        'dl_threads': 1,  # Download threads
        'window_position': {
            'x': 100, 'y': 100
        }
    }

    def __init__(self, path, name='atlas.config'):
        ''' Create/initialize settings.

        The path should be a directory in the user's home directory; if it
        doesn't exist, it will be created.

        Inside will be one settings file named "atlas.config", and caches for
        any manifests the user has loaded. New settings files are created from
        AtlasSettings._default.
        '''

        # Verify settings folder's existence.
        if os.path.exists(path) and not os.path.isdir(path):
            raise RuntimeError("Settings: {0} exists but isn't a directory.".format(path))

        if not os.path.exists(path):
            os.makedirs(path)

        # Verify settings file's existence.
        self.pathname = os.path.join(path, name)
        if os.path.exists(self.pathname) and not os.path.isfile(self.pathname):
            raise RuntimeError("Settings: {0} exists but isn't a file.".format(self.pathname))

        if not os.path.exists(self.pathname):
            with open(self.pathname, 'w') as fp:
                json.dump(AtlasSettings._default, fp)

        # Load settings.
        self.settings = None
        with open(self.pathname, 'r') as fp:
            self.settings = json.load(fp)

    def save(self):
        ''' Save current settings, overwrites old settings.
        '''
        if os.path.exists(self.pathname) and not os.path.isfile(self.pathname):
            raise RuntimeError("Settings: {0} exists but isn't a file.".format(self.pathname))

        if os.path.exists(self.pathname):
            os.unlink(self.pathname)

        with open(self.pathname, 'w') as fp:
            json.dump(self.settings, fp)

    def get_cache(self, manifest_url):
        ''' Returns a manifest cache for the given manifest_url.

        If the manifest URL has never been loaded, the cache will be empty.
        '''
        raise NotImplementedError('no cache for you')

    def set_position(self, x, y):
        ''' Record the window's position.
        '''
        new_pos = {
            'x': x,
            'y': y
        }
        self.settings['window_position'] = new_pos

        self.save()
