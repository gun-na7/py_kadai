from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 写真の保存先
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# uploadsフォルダがなければ作る
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# DBを作成
# =========================
def init_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            photo TEXT,
            location TEXT,
            memo TEXT
        )
    """)

    con.commit()
    con.close()


# =========================
# 一覧表示
# =========================
@app.route("/")
def index():

    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = cur.fetchall()

    con.close()

    return render_template("index.html", posts=posts)


# =========================
# 入力フォーム
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        # フォームから取得
        title = request.form.get("title")
        location = request.form.get("location")
        memo = request.form.get("memo")

        # 写真を取得
        photo = request.files.get("photo")

        filename = ""

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        # DBへ登録
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
            INSERT INTO posts
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

        return redirect(url_for("index"))

    return render_template("add.html")


# =========================
# 起動
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)