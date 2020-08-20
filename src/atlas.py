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

import gi
from cache import AtlasCache
from settings import AtlasSettings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


class MainWindow:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file('ui/atlas-launcher.glade')

        self.mainWindow = builder.get_object('mainWindow')
        self.aboutButton = builder.get_object('aboutButton')

        self.aboutDialog = builder.get_object('aboutDialog')

        self.mainWindow.connect('destroy', Gtk.main_quit)
        self.aboutButton.connect('clicked', self.aboutButton_clicked)

    def aboutButton_clicked(self, button):
        ''' Main window's About button has been clicked.
        '''
        response = self.aboutDialog.run()
        self.aboutDialog.hide()

    def show(self):
        self.mainWindow.show_all()


def main():
    ''' Atlas Launcher
    '''
    mainWindow = MainWindow()
    mainWindow.show()

    Gtk.main()


if __name__ == '__main__':
    main()
