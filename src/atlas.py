#!/usr/bin/env python3
''' Atlas Launcher

A downloader/launcher for games that use an XML manifest file, similar to the
one used by City of Heroes.

Requires:

* Python 3.8 (earlier versions might work?)
* GTK 3
* PyGObject 3.36

This attempts to mimic the behaviour of the original game downloader/launcher,
with modern conveniences.
'''

import argparse
import gi
import threading
import os

from cache import AtlasCache
from settings import AtlasSettings
from workers import ManifestLoader

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

ATLAS_CONFIG = '~/.config/atlas-launcher'


class MainWindow:
    def __init__(self, manifest_url, settings):
        builder = Gtk.Builder()
        builder.add_from_file('ui/atlas-launcher.glade')

        self.mainWindow = builder.get_object('mainWindow')
        self.aboutButton = builder.get_object('aboutButton')
        self.manifestLabel = builder.get_object('manifestLabel')

        self.aboutDialog = builder.get_object('aboutDialog')

        self.mainWindow.connect('destroy', self.mainWindow_destroy)
        self.aboutButton.connect('clicked', self.aboutButton_clicked)

        self.manifest_url = manifest_url
        self.settings = settings

        # TODO: Trigger this via idle event. GLib.idle_add()
        # Fire up a thread to load the manifest so we don't block the UI.
        self.manifest_thread_done = False
        self.manifest_thread = threading.Thread(name='atlas-download-manifest', args=(self,), target=MainWindow.manifest_loader)
        self.manifest_thread.start()

    @staticmethod
    def manifest_loader(self):
        ''' Load the manifest data in a separate thread.
        '''
        # TODO: UI changes should happen in the main thread. Maybe that's
        # what happens when you change properties like the label text?
        self.manifestLabel.set_text('Downloading {0}'.format(self.manifest_url))
        self.manifest = Manifest(self.manifest_url)
        self.manifestLabel.set_text(self.manifest_url)
        self.manifest_thread_done = True

    def aboutButton_clicked(self, button):
        ''' Main window's About button has been clicked.
        '''
        response = self.aboutDialog.run()
        self.aboutDialog.hide()

    def mainWindow_destroy(self, widget):
        ''' Window is being destroyed, clean up and get out.
        '''
        self.manifest_thread.join()  # This should have been finished ages ago.
        Gtk.main_quit()

    def show(self):
        self.mainWindow.show_all()


def main():
    ''' Atlas Launcher
    '''
    parser = argparse.ArgumentParser(description='Download a manifest, check files.')
    parser.add_argument('--dir', dest='output_dir', default=AtlasSettings.HOMECOMING_GAMEDIR,
                        help='Specify the game directory.')
    parser.add_argument('--manifest', dest='manifest', default=AtlasSettings.HOMECOMING_MANIFEST,
                        help='Manifest URL.')
    args = parser.parse_args()

    config_path = os.path.expanduser(ATLAS_CONFIG)
    config = AtlasSettings(config_path)

    mainWindow = MainWindow(args.manifest, config)
    mainWindow.show()

    Gtk.main()


if __name__ == '__main__':
    main()
