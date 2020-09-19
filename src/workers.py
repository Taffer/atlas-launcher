''' Atlas worker threads.

https://docs.python.org/3/library/threading.html#threading.Thread.run
https://wiki.gnome.org/Projects/PyGObject/Threading
'''

import requests
import threading

from manifest import Manifest


class FileChecker(threading.Thread):
    ''' Check a file for validity.
    '''
    def __init__(self):
        super().__init__()


class FileDownloader(threading.Thread):
    ''' Download a file.
    '''
    def __init__(self):
        super().__init__()


class ManifestLoader(threading.Thread):
    ''' Download a manifest.xml file.
    '''
    def __init__(self, manifest_url, owner):
        ''' Create a thread to load a manifest.xml.

        manifest_url - URL of the manifest.xml to load
        owner - object who should own the manifest once it's loaded
        '''
        super().__init__(args=(manifest_url, owner,))

    def run(self, manifest_url, owner):
        ''' Download the given manifest and give it to the owner.
        '''
        manifest = Manifest(manifest_url)
        owner.manifest = manifest
