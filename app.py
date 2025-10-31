from flask import Flask, render_template_string, request
import os
import psycopg2

# Flask uygulaması
app = Flask(__name__)

# Render'dan otomatik gelen DATABASE_URL veya varsayılan bağlantı
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hello_cloud_2_user:Vg1m8zx1Wm4amlq86oZmgrHlCJ8obDlx@dpg-d3tjhpmr433s73do2ir0-a.oregon-postgres.render.com/hello_cloud_2"
)

# HTML şablonu
HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>Buluttan Selam</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
      background: linear-gradient(to right, #dfe9f3, #ffffff);
    }
    h1 { color: #333; }
    p { color: #555; }
    form { margin: 20px auto; }
    input {
      margin: 10px;
      font-size: 16px;
      padding: 8px;
      border-radius: 5px;
      border: 1px solid #ccc;
    }
    button {
      padding: 10px 15px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
    button:hover {
      background: #45a049;
    }
    ul {
      list-style: none;
      padding: 0;
    }
    li {
      background: white;
      margin: 5px auto;
      width: 220px;
      padding: 8px;
      border-radius: 5px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <h1>☁️ Buluttan Selam ☁️</h1>
  <p>Adını yaz, selamını bırak 💬</p>

  <form method="POST">
    <input type="text" name="isim" placeholder="Adını yaz" required>
    <button type="submit">Gönder</button>
  </form>

  <h3>Son 10 Ziyaretçi</h3>
  <ul>
    {% for ad in isimler %}
      <li>{{ ad }}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""

# Veritabanı bağlantı fonksiyonu
def connect_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL tanımlı değil.")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Ana sayfa (GET & POST)
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                # Tabloyu oluştur (yoksa)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ziyaretciler (
                        id SERIAL PRIMARY KEY,
                        isim TEXT NOT NULL
                    )
                """)
                
                # Form gönderildiyse, ismi kaydet
                if request.method == "POST":
                    isim = (request.form.get("isim") or "").strip()
                    if isim:
                        cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
                        conn.commit()
                
                # Son 10 ismi al
                cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC LIMIT 10")
                isimler = [row[0] for row in cur.fetchall()]
                
        return render_template_string(HTML, isimler=isimler)
    
    except Exception as e:
        return f"<h3>İç hata: {e}</h3>", 500


# Uygulama başlangıcı
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
