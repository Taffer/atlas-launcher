#!/usr/bin/env python3
#
# Grab a manifest, and do some XML parsing on it.

import argparse
import hashlib
import os
import requests
import xml.etree.ElementTree


def main():
    ''' Grab a manifest, do things with it.
    '''
    parser = argparse.ArgumentParser(description='Download a manifest, check files.')
    parser.add_argument('--checkonly', dest='check_only', action='store_true',
                        help="Check existing files, don't download.")
    parser.add_argument('--downloadonly', dest='download_only', action='store_true',
                        help="Download new/changed files, don't launch.")
    parser.add_argument('--dir', dest='output_dir', default=None, required=True,
                        help='Specify the game directory.')
    parser.add_argument('manifest', default=None,
                        help='Manifest URL.')
    args = parser.parse_args()
    print('args: {0}'.format(vars(args)))

    # Check to see if output_dir exists.
    if not os.path.exists(args.output_dir):
        print("Output directory {0} doesn't exist, creating it.".format(args.output_dir))
        try:
            os.mkdir(args.output_dir)
        except Exception as ex:
            print('Unable to create directory: {0}'.format(ex))
            raise SystemExit

    # Grab manifest.
    print('Downloading manifest from {0}...'.format(args.manifest))
    manifest_root = None
    with requests.get(args.manifest) as manifest:
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

        manifest_root = xml.etree.ElementTree.fromstring(manifest.text)

    if manifest_root is None:
        print("Unable to parse manifest.")
        return

    print("Manifest root - {0}: {1}".format(manifest_root.tag, manifest_root.attrib))
    for child in manifest_root:
        print("    {0}: {1}".format(child.tag, child.attrib))

    # Check existing files.
    print('Checking files in {0}...'.format(args.output_dir))
    filelist = manifest_root.find('filelist')
    if filelist is None:
        print("Empty file list.")
        return

    print("{0} files to check:".format(len(filelist)))
    for f in filelist:
        file_path = os.path.join(args.output_dir, f.get('name'))
        if os.path.exists(file_path):
            print('    -> check {0}'.format(file_path))

            file_data = None
            with open(file_path, 'rb') as fp:
                file_data = fp.read()

            if len(file_data) != int(f.get('size')):
                print('       ==> SIZE FAIL, will download.')
                continue

            md5 = hashlib.md5(file_data)
            if md5.hexdigest() != f.get('md5'):
                print('        ==> CHECKSUM FAIL, will download.')
            else:
                print('        ==> OK')
        else:
            print('    -> download {0}'.format(file_path))


if __name__ == '__main__':
    main()
