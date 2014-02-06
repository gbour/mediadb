#!/usr/bin/env python
# -*- coding: utf8 -*-

import sqlite3
from mediadb.mediadb import Plugin

class Init(Plugin):
    def __init__(self):
        super(Plugin, self).__init__()

    def help(self):
        pass

    def do(self, args):
        db = sqlite3.connect('./mediadb.db')

        db.execute('''CREATE TABLE resource (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            type  INTEGER NOT NULL, -- 0 = dir, 1 = file
            name  TEXT NOT NULL,
            path  TEXT NOT NULL,
            title TEXT,             -- short description
            desc  TEXT,             -- long description

            UNIQUE (name, path)
        )''')

        db.execute('''CREATE TABLE tag (
            id    INTEGER PRIMARY KEY,
            name  TEXT UNIQUE
        )''')

        db.execute('''CREATE TABLE rtag (
            res_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,

            PRIMARY KEY (res_id, tag_id),
            FOREIGN KEY (res_id) REFERENCES resource (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tag      (id) ON DELETE CASCADE
        )''')

        db.commit()
        db.close()

