''' Manifest - XML manifest file, loaded from an URL.
'''

import requests
import xml.etree.ElementTree


HTTP_HEADERS = {
    'user-agent': 'Atlas-Launcher/0.1'
}
RESPONSE_TIMEOUT = 1.0  # I have no idea if 1 second is reasonable or not.


class Manifest:
    def __init__(self, manifest_url):
        ''' Load manifest_url and pull out the useful bits.
        '''
        self.url = manifest_url

        self.root = None

        with requests.get(manifest_url, headers=HTTP_HEADERS, timeout=RESPONSE_TIMEOUT) as manifest:
            if manifest.status_code != 200:
                print()
                raise RuntimeError('Error requesting manifest: {0}'.format(manifest.status_code))

            if len(manifest.text) != int(manifest.headers['content-length']):
                print('Text length vs content-length: {0} vs {1}'.format(len(manifest.text), manifest.headers['content-length']))
                print('Will still attempt to parse.')

            if manifest.headers['content-type'] != 'text/xml':
                print('Weird content-type, will still attempt to parse. Fix your server.')

            self.root = xml.etree.ElementTree.fromstring(manifest.text)

        # Iterate over this to get <file>, with name, size, md5 attributes.
        self.file_list = self.root.find('filelist')

        # Get all the URLs for a <file>:
        # urls = [x.text for x in f.findall('.//url')]
