#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import os
import os.path
import sqlite3
import argparse

from mediadb.mediadb import Plugin

def tpl_ext(params):
	def __tpl_ext(ctx):
		print(os.path.splitext(ctx['filename']))
		ext = os.path.splitext(ctx['filename'])[1]
		if ext != '':
			ext = ext[1:]

		return ext
		
	return __tpl_ext

def tpl_path(params):
	index = None
	if len(params) == 1:
		index = int(params[0])

	def __tpl_path(ctx):
		if index is None:
			return ctx['path']

		return os.path.split(ctx['path'])[index]

	return __tpl_path

class Index(Plugin):
    def __init__(self):
        super(Plugin, self).__init__()

    def help(self):
        pass

    def do(self, args):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--path') 
        parser.add_argument('--mode') 
        parser.add_argument('--tags') 
        args = vars(parser.parse_args(args))

        path = os.path.abspath(os.path.expanduser(args['path']))
        mode = args['mode']

        # parsing tags
        # a tag is a mix of static string and dynamic parts
        # i.e: 'foo%(ext)s' => 'foo' + file extension
        #
        tags = {'static': [], 'dyn': []}
        for tag in args['tags'].split(','):
            tpls = []
            idx  = -1
            def template(m):
                nonlocal idx

                try:
                    tpls.append(eval('tpl_' + m.group(1))(m.groups()[1:]))
                except NameError as e:
                    raise Exception("tag '{0}': invalid '{1}' template".format(tag, m.group(1)))
                
                idx += 1
                return "{" + str(idx) + "}"

            (tag, count) = re.subn("%\(([^)\]]*)(?:\[([^\]]*)\])?\)s", template, tag.strip())
            if count == 0:
                tags['static'].append(tag)
            else:
                tags['dyn'].append((tag, tpls))
        print(args['tags'],"\n",tags)

        db = sqlite3.connect('./mediadb.db')
        c = db.cursor()

        # tags resolution (static ones only)
        c.execute("SELECT * FROM tag WHERE name IN ({0})".format(','.join(["'{0}'".format(x) for x in tags['static']])))
        dbtags = dict(c)

        for t in set(tags['static']).difference(dbtags.values()):
            c.execute('''INSERT INTO tag VALUES (NULL, ?)''', (t,))
            dbtags[c.lastrowid] = t
        db.commit()
        print(dbtags)
        print(path, mode)

        tagcache = {}
        for root, dirs, files in os.walk(path):
            if mode == 'file':
                for name in files:
                    c.execute('''INSERT INTO resource VALUES (NULL, 1, ?, ?, NULL, NULL)''', (name, root))
                    rid = c.lastrowid
                    print(name, rid)

                    for tid in dbtags.keys():
                        c.execute('''INSERT INTO rtag VALUES (?,?)''', (rid, tid))

                    ctx = {'filename': name, 'path': root}
                    for tag, tpls in tags['dyn']:
                        ntag = tag.format(*[tpl(ctx) for tpl in tpls])
                        
                        if not ntag in tagcache:
                            c.execute("SELECT id FROM tag WHERE name = ?", (ntag,))
                            res = c.fetchone()

                            if res:
                                tagcache[ntag] = res[0]
                            else:
                                c.execute('''INSERT INTO tag VALUES (NULL, ?)''', (ntag,))
                                tagcache[ntag] = c.lastrowid

                        c.execute('''INSERT INTO rtag VALUES (?, ?)''', (rid, tagcache[ntag]))


        db.commit()
        #db.rollback()
        db.close()

