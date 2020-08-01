#!/usr/bin/env python3
#
# Grab a manifest, and do some XML parsing on it.

import requests
import sys
import xml.etree.ElementTree


def main(args):
    # Pass in the manifest URL as an argument.
    if len(args) != 1:
        print('One manifest, please.')
        raise SystemExit

    with requests.get(args[0]) as manifest:
        if manifest.status_code != 200:
            print('Request returned: {0}'.format(manifest.status_code))
            raise SystemExit

        if len(manifest.text) != int(manifest.headers['content-length']):
            print('Text length vs content-length: {0} vs {1}'.format(len(manifest.text), manifest.headers['content-length']))
            print('Will still attempt to parse.')

        if manifest.headers['content-type'] != 'text/xml':
            print('Weird content-type, will still attempt to parse. Fix your server.')

        print('Content type: {0}'.format(manifest.headers['content-type']))
        print('Encoding: {0}'.format(manifest.encoding))
        print('Last modified: {0}'.format(manifest.headers['last-modified']))

        root = xml.etree.ElementTree.fromstring(manifest.text)

        print("{0}: {1}".format(root.tag, root.attrib))
        for child in root:
            print("    {0}: {1}".format(child.tag, child.attrib))


if __name__ == '__main__':
    main(sys.argv[1:])
