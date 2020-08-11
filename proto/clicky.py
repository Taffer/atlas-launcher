#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def on_theButton_clicked(target):
    target.set_text('CLICK')


builder = Gtk.Builder()
builder.add_from_file('clicky.glade')

builder.connect_signals({'on_theButton_clicked': on_theButton_clicked})

win = builder.get_object('mainWindow')
win.connect("destroy", Gtk.main_quit)
win.show_all()

Gtk.main()
