#!/usr/bin/env python3

import gi
import threading
import time

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, GObject  # noqa: E402


def app_main():
    win = Gtk.Window(default_height=50, default_width=300)
    win.connect("destroy", Gtk.main_quit)

    progress = Gtk.ProgressBar(show_text=True)
    win.add(progress)

    def update_progress(i):
        progress.pulse()
        progress.set_text(str(i))
        return False

    def example_target():
        for i in range(50):
            GLib.idle_add(update_progress, i)  # I guess this is thread safe?
            time.sleep(0.2)

    win.show_all()

    thread = threading.Thread(target=example_target)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    app_main()
    Gtk.main()
