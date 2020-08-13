#!/usr/bin/env python3
#
# Grab a manifest, and do some XML parsing on it.

import argparse
import hashlib
import os
import requests
import shutil
import subprocess
import sys
import xml.etree.ElementTree

BLOCK_SIZE = 1024 * 1024  # 1M seems to do well in limited testing.
HTTP_HEADERS = {
    'user-agent': 'Atlas-Prototype/0.1'
}
RESPONSE_TIMEOUT = 1.0  # I have no idea if 1 second is reasonable or not.


def get_tag(filename):
    ''' Return the MD5 tag for the given filename.
    '''
    md5 = hashlib.md5()
    with open(filename, 'rb') as fp:
        data = fp.read(BLOCK_SIZE)
        while len(data) != 0:
            md5.update(data)
            data = fp.read(BLOCK_SIZE)

    return md5.hexdigest()


def download_file(file_path, file_size, file_md5, file_url):
    ''' Download the URL to the given path. Must match file size and MD5 tag.
    '''
    tmp_file_path = '.'.join([file_path, 'atlas-download'])  # Maybe use tempfile instead?
    md5 = hashlib.md5()
    downloaded_size = 0

    # Make sure any extra directories are made.
    dirs = os.path.dirname(file_path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    print('Downloading {0}: {1}'.format(file_path, downloaded_size), end='\r')

    with requests.get(file_url, stream=True, headers=HTTP_HEADERS, timeout=RESPONSE_TIMEOUT) as request:
        if request.status_code != requests.codes.ok:
            request.raise_for_status()

        # Check 'Content-Length' against file_size if it's present?

        with open(tmp_file_path, 'wb') as fp:
            for chunk in request.iter_content(chunk_size=BLOCK_SIZE):
                fp.write(chunk)
                md5.update(chunk)
                downloaded_size = downloaded_size + len(chunk)
                print('Downloading {0}: {1}'.format(file_path, downloaded_size), end='\r')

    if downloaded_size != file_size:
        print('{0}: Downloaded {1} bytes, expected {2}'.format(file_path, downloaded_size, file_size))
        return

    if md5.hexdigest() != file_md5:
        print('{0}: MD5 tag is invalid'.format(file_path))
        return

    if os.path.exists(file_path):
        os.unlink(file_path)
    os.rename(tmp_file_path, file_path)
    print('{0} downloaded successfully.'.format(file_path))

    # # If there's an existing download, continue.
    # # Check the request header for 'accept-ranges: bytes' first! See here
    # # for details:
    # # https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests
    # request_offset = 0
    # if os.path.existing(tmp_file_path):
    #     request_offset = os.path.getsize(tmp_file_path)

    #     with open(tmp_file_path, 'rb') as fp:
    #         data = fp.read(BLOCK_SIZE)
    #         while len(data) > 0:
    #             md5.update(data)
    #             data = fp.read(BLOCK_SIZE)

    # while request_offset < file_size:
    #     # Request BLOCK_SIZE bytes from URL at request_offset.
    #     pass


def main():
    ''' Grab a manifest, do things with it.
    '''
    parser = argparse.ArgumentParser(description='Download a manifest, check files.')
    parser.add_argument('--checkonly', dest='check_only', action='store_true',
                        help="Check existing files, don't download.")
    parser.add_argument('--downloadonly', dest='download_only', action='store_true',
                        help="Download new/changed files, don't launch.")
    parser.add_argument('--launchonly', dest='launch_only', action='store_true',
                        help="Don't check or download, only launch. DANGEROUS!")
    parser.add_argument('--dir', dest='output_dir', default=None, required=True,
                        help='Specify the game directory.')
    parser.add_argument('manifest', default=None,
                        help='Manifest URL.')
    args = parser.parse_args()
    print('args: {0}'.format(vars(args)))

    # Check to see if output_dir exists.
    if not os.path.exists(args.output_dir):
        if args.launch_only:
            print("Launch directory {0} doesn't exist.".format(args.output_dir))
            raise SystemExit

        print("Output directory {0} doesn't exist, creating it.".format(args.output_dir))
        try:
            os.mkdir(args.output_dir)
        except Exception as ex:
            print('Unable to create directory: {0}'.format(ex))
            raise SystemExit

    # Grab manifest.
    print('Downloading manifest from {0}...'.format(args.manifest))
    manifest_root = None
    with requests.get(args.manifest, headers=HTTP_HEADERS, timeout=RESPONSE_TIMEOUT) as manifest:
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
    dl_list = []
    if not args.launch_only:
        print('Checking files in {0}...'.format(args.output_dir))
        filelist = manifest_root.find('filelist')
        if filelist is None:
            print("Empty file list.")
            return

        print("{0} files to check:".format(len(filelist)))
        for f in filelist:
            file_path = os.path.join(args.output_dir, f.get('name'))
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)

                if file_size != int(f.get('size')):
                    print('    {0} ==> SIZE FAIL, will download.'.format(file_path))
                    dl_list.append(f)
                    continue

                md5 = get_tag(file_path)
                if md5 != f.get('md5'):
                    print('    {0} ==> CHECKSUM FAIL, will download.'.format(file_path))
                    dl_list.append(f)
                else:
                    print('    {0} ==> OK'.format(file_path))
            else:
                print('    -> download {0}'.format(file_path))
                dl_list.append(f)

        if args.check_only:
            # We done.
            return

    if not args.launch_only:
        for f in dl_list:
            urls = [x.text for x in f.findall('.//url')]

            if len(urls) < 1:
                print("Can't download {0}, no URLs.".format(f.get('name')))
                continue

            file_path = os.path.join(args.output_dir, f.get('name'))
            file_size = int(f.get('size'))
            file_md5 = f.get('md5')
            file_url = urls[0]  # How to choose? There's no region info... ping?

            download_file(file_path, file_size, file_md5, file_url)

    if args.download_only:
        return

    # If that all worked, launch!
    if sys.platform == 'linux':
        print('Launching for Linux via wine...')

        prefix = shutil.which('nvidia-optimus-offload-glx')  # or shutil.which("TODO: What's the AMD equivalent?")
        os.putenv('WINEARCH', 'win64')  # I think the 32-bit client is deprecated?

        launch_args = []
        if prefix:
            launch_args.append(prefix)
        launch_args.append('wine')
        launch = manifest_root.find('.//launch[@architecture="x64"]')
        launch_args.append(launch.get('exec'))
        for param in launch.get('params').split():
            launch_args.append(param)

        retval = subprocess.run(launch_args, cwd=args.output_dir)

    elif sys.platform == 'darwin':  # Need to double-check that.
        print('Launching for MacOS via wine...')

        os.putenv('WINEARCH', 'win64')  # I think the 32-bit client is deprecated?

        launch_args = []
        if prefix:
            launch_args.append(prefix)
        launch_args.append('wine')
        launch = manifest_root.find('.//launch[@architecture="x64"]')
        launch_args.append(launch.get('exec'))
        for param in launch.get('params').split():
            launch_args.append(param)

        retval = subprocess.run(launch_args, cwd=args.output_dir)

    else:
        print('Unsupported platform "{0}", will try launching without wine.'.format(sys.platform))

        launch_args = []
        if prefix:
            launch_args.append(prefix)
        launch = manifest_root.find('.//launch[@architecture="x64"]')
        launch_args.append(launch.get('exec'))
        for param in launch.get('params').split():
            launch_args.append(param)

        retval = subprocess.run(launch_args, cwd=args.output_dir)

if __name__ == '__main__':
    main()
