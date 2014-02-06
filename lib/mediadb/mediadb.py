#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import os.path
import glob
import sys
import inspect
import imp

class Plugin(object):
    def __init__(self):
        pass

    def help(self):
        pass

    def do(self, args):
        pass

def get_plugins():
    modfile = dict(inspect.getmembers(sys.modules[__name__]))['__file__']
    path = os.path.join(os.path.split(modfile)[0], 'plugins')

    plugins = {}
    for fname in os.listdir(path):
        if fname.startswith('.') or not fname.endswith('.py') or fname == '__init__.py':
            continue

        fname = os.path.splitext(fname)[0]
        (fp, fpath, desc) = imp.find_module(fname, [path])
        try:
            mod = imp.load_module(fname, fp, fpath, desc)

            plugins.update(
                [(plug.__name__.lower(), plug) for plug in dict(inspect.getmembers(mod)).values() 
                    if inspect.isclass(plug) and plug != Plugin and plug.__base__ == Plugin]
            )
        finally:
            if fp:
                fp.close()


    return plugins
