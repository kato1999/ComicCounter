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


#拡張子に応じたファイルを返すための準備
CONTENT_TYPE = defaultdict(lambda: 'application/octed-stream')
CONTENT_TYPE.update({
        '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json',
        '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif',
        '.css':'text/css'
    }
)



def application(environ,start_response):
    
    #拡張子の取得
    filepath = '.' + environ['PATH_INFO']
    extention = pathlib.Path( filepath ).suffix
    

    # 「GET (HTML以外のファイル)」であればファイルの中身をそのまま返す(.icoは無視)
    # 拡張子がリスト内にあるかどうかで判定
    extention_li = [".css", ".jpeg", ".jpg", ".png", ".txt"]
    if ( extention in extention_li):
        headers = [('Content-type', CONTENT_TYPE[extention])]
        if (filepath!="./favicon.ico"):
            with open(filepath,mode='br') as file:
                data = file.read()

            start_response('200 OK', headers)
            return [bytes(data)]


    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)

    # ==============
    # SQLへの追加操作
    # ==============
    if ('v1' in form) and (filepath=="./add"):
        # フォームデータから各フィールド値を取得
        title = form.getvalue("v1", "0")
        author = form.getvalue("v2", "0")
        company = form.getvalue("v3", "0")
        year = form.getvalue("v4", "0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

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

        # 一旦別ページ(manage.html)に飛ばす。
        # リロードした際に重複して追加されるのを防ぐ
        with open("manage.html",mode="r") as file:
            html = file.read()
            html = html.encode('utf-8')
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
        return [html]



    # ============
    # SQLの削除操作
    # ==============
    if (filepath=="./delete"):
        # nameは1で固定してある。
        # valueはSQLに保存してある管理番号(number)と同一
        delete_number = form.getlist("1")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str
        
        print(delete_number)
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



    # HTML（共通ヘッダ部分）
    with open("index.html",mode="r") as file:
        html = file.read()
    content = ""

    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str


    # ============
    # SQLの検索操作
    # ==============
    if (filepath=="./search"):
        search_list = [False for _ in range(4)]
        sql = 'select * from books where author =? and company=?'

        if ('v1' in form):
            search_list[0] = form.getvalue("v1", "0")
        if ('v2' in form):
            search_list[1] = form.getvalue("v2", "0")
        if ('v3' in form):
            search_list[2] = form.getvalue("v3", "0")
        if ('v4' in form):
            search_list[3] = form.getvalue("v4", "0")
    
        
        cur.execute(sql,(search_list[1],search_list[2]))
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


    else:
        # SQL文（select）の作成
        sql = 'select * from books'

        # SQL文の実行とその結果のHTML形式への変換
        for row in cur.execute(sql):
            content +=  '<tr>\n'\
                        '<td class="td1"><input type="checkbox"   name="1" value="'+ str(row[0]) +'"></td>\n'
            for i in range(1, len(row)-2):
                if not(row[i] is None):
                    content +=  '<td>'+str(row[i])+'</td>\n'
                else:
                    content +=  '<td>未定義</td>\n'
            content += '</tr>\n'


    # カーソルと接続を閉じる
    cur.close()
    con.close()


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

