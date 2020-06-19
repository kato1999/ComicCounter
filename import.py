#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pathlib
from collections import defaultdict

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
dbname = 'database.db'
#dbname = ':memory:'

# テーブルの作成
con = sqlite3.connect(dbname)
cur = con.cursor()
create_table = 'create table if not exists books(title text, year int, month int, date int, company text, author text)'
cur.execute(create_table)
con.commit()
cur.close()
con.close()