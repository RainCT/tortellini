#! /usr/bin/env python
# -.- coding: utf-8 -.-
#
# Copyright © 2012 Siegfried-Angel Gevatter Pujals <siegfried@gevatter.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from importlib import import_module

class RestartingLauncher:

    def __init__(self, module_name, start_function, stop_function, path="."):
        self._module_name = module_name
        self._filename = '%s.py' % module_name
        self._start_function = start_function
        self._stop_function = stop_function
        self._path = path
        self._setup()

    def _setup(self):
        import pyinotify
        self._wm = pyinotify.WatchManager()

        self._notifier = pyinotify.ThreadedNotifier(
                self._wm, self._on_file_modified)
        self._notifier.start()

        # We monitor the directory (instead of just the file) because
        # otherwise inotify gets confused by editors such a Vim.
        flags = pyinotify.EventsCodes.OP_FLAGS['IN_MODIFY']
        wdd = self._wm.add_watch(self._path, flags)

    def _on_file_modified(self, event):
        if event.name == self._filename:
            print "File modification detected. Restarting application..."
            self._reload_request = True
            getattr(self._module, self._stop_function)()

    def run(self):
        self._module = import_module(self._module_name)

        self._reload_request = True
        while self._reload_request:
            self._reload_request = False
            reload(self._module)
            getattr(self._module, self._start_function)()

        print 'Bye!'
        self._notifier.stop()

def launch_app(module_name, start_func, stop_func):
    try:
        import pyinotify
    except ImportError:
        print 'Pyinotify not found. Launching app anyway...'
        m = import_module(self._module_name)
        getattr(m, start_func)()
    else:
        RestartingLauncher(module_name, start_func, stop_func).run()

if __name__ == '__main__':
    launch_app('main', 'main', 'force_exit')
