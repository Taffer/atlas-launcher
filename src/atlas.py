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


def aboutButton_clicked(button, aboutDialog):
    ''' Main window's About button has been clicked.
    '''
    response = aboutDialog.run()
    aboutDialog.hide()


def main():
    ''' Atlas Launcher
    '''
    builder = Gtk.Builder()
    builder.add_from_file('ui/atlas-launcher.glade')

    mainWindow = builder.get_object('mainWindow')
    aboutButton = builder.get_object('aboutButton')

    aboutDialog = builder.get_object('aboutDialog')

    mainWindow.connect('destroy', Gtk.main_quit)
    aboutButton.connect('clicked', aboutButton_clicked, aboutDialog)

    mainWindow.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
