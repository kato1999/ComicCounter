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
create_table = 'create table if not exists books(number int, title text, company text, author text, year int, month int, date int )'
cur.execute(create_table)
con.commit()
cur.close()
con.close()



# データベース接続とカーソル生成
con = sqlite3.connect(dbname)
cur = con.cursor()
con.text_factory = str

with open("aozora.csv") as file:
    mm = file.readlines()
    for data in mm:
        li = data.split(",")
        title = li[1]
        company = li[8]
        author = li[6]
        year = li[3].replace("/","")

        # 現在最大の管理番号+1を次の管理番号にする。
        # 現在最大の管理番号の取得
        sql = 'select max(number) from books'
        cur.execute(sql)
        num = cur.fetchall()

        # データがない場合には最大の管理番号を0にする。
        if num[0][0] is None:
            num = [[0]]
        print(num)

        # SQL文（insert）の作成と実行
        sql = 'insert into books (number, title , company, author, year, month, date) values (?,?,?,?,?,?,?)'
        cur.execute(sql, (int(num[0][0])+1, title ,company,author,int(year),0,0))
        con.commit()

cur.close()
con.close()

