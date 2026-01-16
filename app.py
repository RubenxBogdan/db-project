from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DB_FILE = 'todos.db'  # <- benutze deine vorhandene Datenbank

# Startseite
@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if request.method == "POST":
        text = request.form["text"].strip()
        if text != "":
            c.execute("INSERT INTO todos (text) VALUES (?)", (text,))
            conn.commit()
        return redirect("/")

    c.execute("SELECT id, text FROM todos")
    items = c.fetchall()
    conn.close()
    return render_template("index.html", items=items)

# Eintrag löschen
@app.route("/delete/<int:item_id>")
def delete(item_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM todos WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect("/")

# App starten
if __name__ == "__main__":
    app.run(debug=True)
