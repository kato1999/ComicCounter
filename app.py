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
create_table = 'create table if not exists books(number int, title text, count int, comment text)'
cur.execute(create_table)
con.commit()
cur.close()
con.close()


# ファイルの中身をそのまま返す処理
def return_file(filepath, extention, start_response):
    #拡張子に応じたファイルを返すための準備
    CONTENT_TYPE = defaultdict(lambda: 'application/octed-stream')
    CONTENT_TYPE.update({
            '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json',
            '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif',
            '.css':'text/css'
        }
    )

    headers = [('Content-type', CONTENT_TYPE[extention])]
    with open(filepath,mode='br') as file:
        data = file.read()
        
    start_response('200 OK', headers)
    return [bytes(data)]



# SQLへの追加操作
def insert_sql(form, start_response):
    # フォームデータから各フィールド値を取得
    title = form.getvalue("v1", "0")
    count = form.getvalue("v2", "0")
    comment = form.getvalue("v3", "0")

    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # 現在最大の管理番号+1を次の管理番号にする。(消去操作のために用意)
    sql = 'select max(number) from books'
    cur.execute(sql)
    num = cur.fetchall()

    # データがない場合には現在の管理番号を0に設定する。
    if num[0][0] is None:
        num = [[0]]

    sql = 'insert into books (number, title, count, comment) values (?,?,?,?)'
    cur.execute(sql, (int(num[0][0])+1, title , count, comment))
    con.commit()

    cur.close()
    con.close()

    # 一旦別ページ(manage.html)に飛ばす。
    # リロードした際に重複して追加されるのを防ぐ
    with open("manage.html",mode="r") as file:
        html = file.read()
        html = html.encode('utf-8')
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
    ('Content-Length', str(len(html))) ])
    return [html]



# SQL内のデータの削除操作
def delete_sql(form, start_response):
    # nameは1で固定してある。
    # valueはSQLに保存してある管理番号(number)と同一
    delete_number = form.getlist("1")

    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    
    for i in delete_number:
        sql = 'delete from books where number = ?'
        cur.execute(sql, (i,))
        con.commit()
    cur.close()
    con.close()

    # 一旦別ページ(manage.html)に飛ばす。
    # リロードした際に重複して削除されるのを防ぐ
    with open("manage.html",mode="r") as file:
        html = file.read()
        html = html.encode('utf-8')
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
    ('Content-Length', str(len(html))) ])
    return [html]



# SQLの検索操作
def select_sql(form, start_response):
    content = ""

    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    search_list = [False for _ in range(4)]
    sql = 'select * from books where title =?'

    if ('v1' in form):
        search_list[0] = form.getvalue("v1", "0")

    cur.execute(sql,(search_list[1],))
    list1 = cur.fetchall()

    for row in list1:
        content +=  '<tr>\n'\
                    '<td class="td1"><input type="checkbox" name="1" value="'+ str(row[0]) +'"></td>\n'
        for i in range(1, len(row)-2):
            if not(row[i] is None):
                content +=  '<td>'+str(row[i])+'</td>\n'
            else:
                content +=  '<td>未定義</td>\n'
        content += '</tr>\n'
    cur.close()
    con.close()

    return content



def default():
    content = ""
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    sql = 'select * from books'

    # SQL文の実行とその結果のHTML形式への変換
    # 表の横幅(%)
    for row in cur.execute(sql):
        content +=  '<tr>\n'\
                    '<td class="td1 box"><input type="checkbox" name="1" value="'+ str(row[0]) +'"></td>\n'
        for i in range(1, len(row)):
            if not(row[i] is None):
                content +=  '<td class="td'+ str(i+1) +'">'+ str(row[i]) +'</td>\n'
            else:
                content +=  '<td>未定義</td>\n'
        content += '</tr>\n'
    cur.close()
    con.close()

    return content



def application(environ,start_response):
    # ファイル名取得
    filepath = '.' + environ['PATH_INFO']


    # .html以外の拡張子をもつファイルをGETされた場合の処理
    # ファイルの中身をそのまま返す(拡張子がない場合と.icoも対象外)
    extention = pathlib.Path( filepath ).suffix
    extention_li = [".html", "", ".ico"]
    if not(extention in extention_li):
        return return_file(filepath, extention, start_response)


    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)

    # SQLへの追加操作
    if (filepath=="./insert"):
        return insert_sql(form, start_response)

    # SQLの削除操作
    elif (filepath=="./delete"):
        return delete_sql(form,start_response)

    # SQLの検索操作
    elif (filepath=="./search"):
        content = select_sql(form, start_response)

    # localhostに直接アクセスした場合の処理
    else:
        content = default()

    # HTML（共通ヘッダ部分）
    with open("index.html",mode="r") as file:
        html = file.read()

    html = html.format(body1 = content , title = "本の情報")
    html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]


# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python3 test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，http://localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる．
#  コマンドライン引数にポート番号を指定（python3 test_wsgi.py ポート番号）した場合は，
#  http://localhost:ポート番号 にアクセスする．
from wsgiref import simple_server
if __name__ == '__main__':
    port = 8080
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    server = simple_server.make_server('', port, application)
    server.serve_forever()

