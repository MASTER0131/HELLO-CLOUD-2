from flask import Flask, render_template_string, request
import os
import psycopg2

app = Flask(_name_)
DATABASE_URL = os.getenv("DATABASE_URL", "KENDI DATABASE URLNIZ")

HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>Buluttan Selam</title>
  <style>
    body {font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #eef2f3;}
    h1 {color: #333;}
    form {margin: 20px auto;}
    input {margin: 10px; font-size: 16px; padding: 8px;}
    button {padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer;}
    ul {list-style: none; padding: 0;}
    li {background: white; margin: 5px auto; width: 220px; padding: 8px; border-radius: 5px;}
  </style>
</head>
<body>
  <h1>Buluttan Selam</h1>
  <p>adını yaz , selamını bırak</p>

  <form method="POST">
    <input type="text" name="isim" placeholder="Adını yaz" required>
    <button type="submit">Gönder</button>
  </form>

  <h3>Ziyaretçiler</h3>
  <ul>
    {% for ad in isimler %}
      <li>{{ ad }}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""

def connect_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL tanımlı değil.")
    return psycopg2.connect(DATABASE_URL)

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        # Her istekte tabloyu garanti et
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ziyaretciler (
                        id SERIAL PRIMARY KEY,
                        isim TEXT NOT NULL
                    )
                """)
                if request.method == "POST":
                    isim = (request.form.get("isim") or "").strip()
                    if isim:
                        cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
                cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC LIMIT 10")
                isimler = [row[0] for row in cur.fetchall()]
        return render_template_string(HTML, isimler=isimler)
    except Exception as e:
        return f"İç hata: {e}", 500

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)
