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

    return refresh(start_response)




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

    return refresh(start_response)



def change_sql(form, start_response):
    # フォームデータから各フィールド値を取得
    num = form.getvalue("v0", "0")
    title = form.getvalue("v1", "0")
    count = form.getvalue("v2", "0")
    comment = form.getvalue("v3", "0")

    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    
    sql = 'update books set title=?, count=?, comment=? where number=?'
    cur.execute(sql, (title, count, comment, num))
    con.commit()
    cur.close()
    con.close()

    return refresh(start_response)



# SQLの検索操作
def select_sql(form):
    content = ""

    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    sql = 'select * from books where title like ?'

    search = form.getvalue("v1", "0")
    search = "%"+search+"%"

    cur.execute(sql,(search,))
    list1 = cur.fetchall()

    for row in list1:
        content +=  '<tr>\n'\
                    '<td class="td1 box"><input type="checkbox" name="1" value="'+ str(row[0]) +'"></td>\n'
        for i in range(1, len(row)):
            content +=  '<td class="td'+ str(i+1) +'">'+ str(row[i]) +'</td>\n'
        content += '<td class="td5"><a href="change?v1=' + str(row[0]) + '">変更</a></td>\n'
        content += '</tr>\n'
    cur.close()
    con.close()

    show_all = "<a href='manage.html'>検索結果をクリア</a>"
    sub1 = "検索結果"
    sub2 = "本の追加"
    chck1 = "checked='checked'"
    chck2 = ""
    btn1 = '<input type="submit" class="button add_btn" formaction="insert" value="登録">'

    with open("index.html",mode="r") as file:
        html = file.read()
    html = html.format(body1 = content , title = "本の情報", show_all=show_all,
                sub1=sub1, sub2=sub2, value0="", value1="", value2="", value3="",
                checked1=chck1, checked2=chck2,btn1=btn1 )

    return html



#値を変更するための画面を表示
def change(form):
    content = ""

    # nameは1で固定してある。
    # valueはSQLに保存してある管理番号(number)と同一
    number = form.getvalue("v1")

    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    
    sql = 'select * from books where number = ?'
    cur.execute(sql, (number,))
    list1 = cur.fetchall()

    value1 = list1[0][1]
    value2 = list1[0][2]
    value3 = list1[0][3]

    sql = 'select * from books'

    # SQL文の実行とその結果のHTML形式への変換
    # 表の横幅(%)
    for row in cur.execute(sql):
        content +=  '<tr>\n'\
                    '<td class="td1 box"><input type="checkbox" name="1" value="'+ str(row[0]) +'"></td>\n'
        for i in range(1, len(row)):
            content +=  '<td class="td'+ str(i+1) +'">'+ str(row[i]) +'</td>\n'
        content += '<td class="td5"><a href="change?v1=' + str(row[0]) + '">変更</a></td>\n'
        content += '</tr>\n'

    cur.close()
    con.close()

    show_all = ""
    sub1 = "本の一覧"
    sub2 = "本情報の変更"
    chck1 = ""
    chck2 = "checked='checked'"
    btn1 = '<input type="submit" class="button add_btn" formaction="change_sql" value="変更">'

    with open("index.html",mode="r") as file:
        html = file.read()
    html = html.format(body1 = content , title = "本の情報", show_all=show_all,
                sub1=sub1, sub2=sub2, value0=list1[0][0], value1=value1, value2=value2, value3=value3,
                checked1=chck1, checked2=chck2, btn1=btn1)
    return html



# 一旦別ページ(manage.html)に飛ばす。
# リロードした際に重複して追加・削除されるのを防ぐ
def refresh(start_response):
    with open("manage.html",mode="r") as file:
        html = file.read()
        html = html.encode('utf-8')

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]



# localhostにアクセスしたときの処理
# 本の一覧を表示
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
            content +=  '<td class="td'+ str(i+1) +'">'+ str(row[i]) +'</td>\n'
        content += '<td class="td5"><a href="change?v1=' + str(row[0]) + '">変更</a></td>\n'
        content += '</tr>\n'
    cur.close()
    con.close()

    show_all = ""
    sub1 = "本の一覧"
    sub2 = "本の追加"
    chck1 = "checked='checked'"
    chck2 = ""
    btn1 = '<input type="submit" class="button add_btn" formaction="insert" value="登録">'

    with open("index.html",mode="r") as file:
        html = file.read()
    html = html.format(body1=content , title="本の情報", show_all=show_all,
                sub1=sub1, sub2=sub2, value0="", value1="", value2="", value3="",
                checked1=chck1, checked2=chck2, btn1=btn1 )

    return html



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

    # SQLの値変更
    elif (filepath=="./change_sql"):
        return change_sql(form,start_response)

    elif (filepath=="./manage.html"):
        return refresh(start_response)

    # SQLの検索操作
    elif (filepath=="./search"):
        html = select_sql(form)

    # 値を変更するための画面を生成
    elif (filepath=="./change"):
        html = change(form)

    # localhostに直接アクセスした場合の処理
    else:
        html = default()
 
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

