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
create_table = 'create table if not exists users (id int, name varchar(64))'
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

    # localhost または index.html 
    # HTML（共通ヘッダ部分）
    with open("index.html",mode="r") as file:
        html = file.read()
    content = ""

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

        # HTML（入力フォーム部分）
        content +=  '<div class="form1">\n' \
                    '<form>\n' \
                    '学生番号（整数） <input type="text" name="v1"><br>\n' \
                    '氏名　（文字列） <input type="text" name="v2"><br>\n' \
                    '<input type="submit" value="登録">\n' \
                    '</form>\n' \
                    '</div>\n'
    else:
        # 入力フォームの内容が空でない場合

        # フォームデータから各フィールド値を取得
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        # SQL文（insert）の作成と実行
        sql = 'insert into users (id, name) values (?,?)'
        cur.execute(sql, (int(v1),v2))
        con.commit()

        # SQL文（select）の作成
        sql = 'select * from users'

        # SQL文の実行とその結果のHTML形式への変換
        content +=  '<div class="ol1">\n' \
                    '<ol>\n'
        for row in cur.execute(sql):
            content += '<li>' + str(row[0]) + ',' + row[1] + '</li>\n'
        content +=  '</ol>\n' \
                    '</div>\n' \
                    '<a href="/">登録ページに戻る</a>\n'
                

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

