from flask import Flask, render_template, request, redirect
import sqlite3
import os
import uuid

app = Flask(__name__)

# 設定
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# データベース接続
def get_db():

    con = sqlite3.connect("database.db")

    return con


# テーブル作成
def init_db():

    con = get_db()

    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            photo TEXT,
            location TEXT,
            memo TEXT
        )
    """)

    con.commit()
    con.close()


# 参照 SELECT
@app.route("/")
def index():

    con = get_db()
    cursor = con.cursor()

    # データを取得
    cursor.execute("""
        SELECT id, title, photo, location, memo
        FROM memories
        ORDER BY id DESC
    """)

    posts = cursor.fetchall()
    con.close()

    return render_template(
        "index.html",
        posts=posts
    )


# 登録 INSERT
@app.route("/add", methods=["GET", "POST"])
def add():

    # GETの場合
    if request.method == "GET":

        return render_template("add.html")


    # フォームからデータ取得

    title = request.form.get("title")
    location = request.form.get("location")
    memo = request.form.get("memo")
    photo = request.files.get("photo")

    # 写真を保存
    filename = ""

    if photo and photo.filename:

        extension = os.path.splitext(
            photo.filename
        )[1]

        filename = str(uuid.uuid4()) + extension

        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    # INSERT
    con = get_db()
    cursor = con.cursor()

    cursor.execute("""
        INSERT INTO memories
        (title, photo, location, memo)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        filename,
        location,
        memo
    ))

    con.commit()
    con.close()

    # 一覧画面へ
    return redirect("/")


# 修正 UPDATE
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    con = get_db()
    cursor = con.cursor()


    # 修正するデータをSELECT

    if request.method == "GET":

        cursor.execute("""
            SELECT id, title, photo, location, memo
            FROM memories
            WHERE id = ?
        """, (id,))

        post = cursor.fetchone()

        con.close()


        if post is None:
            return "データがありません"

        return render_template(
            "edit.html",
            post=post
        )


    # POST → UPDATE

    title = request.form.get("title")
    location = request.form.get("location")
    memo = request.form.get("memo")

    # 写真
    photo = request.files.get("photo")

    if photo and photo.filename:

        extension = os.path.splitext(
            photo.filename
        )[1]

        filename = str(uuid.uuid4()) + extension

        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        # 写真も更新
        cursor.execute("""
            UPDATE memories

            SET
                title = ?,
                photo = ?,
                location = ?,
                memo = ?

            WHERE id = ?
        """, (
            title,
            filename,
            location,
            memo,
            id
        ))


    else:

        # 写真を変更しない場合
        cursor.execute("""
            UPDATE memories

            SET
                title = ?,
                location = ?,
                memo = ?

            WHERE id = ?
        """, (
            title,
            location,
            memo,
            id
        ))


    con.commit()
    con.close()

    return redirect("/")


# 削除 DELETE
@app.route("/delete/<int:id>")
def delete(id):

    con = get_db()
    cursor = con.cursor()

    # DELETE
    cursor.execute("""
        DELETE FROM memories
        WHERE id = ?
    """, (id,))

    con.commit()
    con.close()

    return redirect("/")


# アプリ起動
if __name__ == "__main__":
    init_db()
    app.run('0.0.0.0', 8000, debug=True)