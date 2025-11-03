import sqlite3

def database():
    # =====================
    # 1. DATABASE KURULUMU
    # =====================
    conn = sqlite3.connect("speech_eval_small.db")
    c = conn.cursor()

    # Prompts tablosu: hedef cümleler
    c.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expected_text TEXT
    )
    """)

    # Recordings tablosu: sonuçlar
    c.execute("""
    CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt_id INTEGER,
        file_path TEXT,
        recognized_text TEXT,
        score INTEGER,
        ratio INTEGER,
        partial INTEGER,
        token_sort INTEGER,
        passed BOOLEAN,
        feedback TEXT,
        FOREIGN KEY(prompt_id) REFERENCES prompts(id)
    )
    """)
    conn.commit()

    # ==============================
    # 3. PROMPT EKLEME (10 CÜMLE)
    # ==============================
    sentences = [
        "Tower, November 1 2 3 Alfa Bravo ready for departure runway 18.",
        "Climb and maintain flight level 350.",
        "Request descent to flight level 200.",
        "Cleared for takeoff runway 27 left.",
        "Contact ground on 121.9.",
        "Maintain present heading and altitude.",
        "Descend and maintain 3000 feet.",
        "Cleared to land runway 18 right.",
        "Turn left heading 090.",
        "Report established on the localizer."
    ]

    # Eğer tabloda hiç prompt yoksa ekle
    c.execute("SELECT COUNT(*) FROM prompts")
    count = c.fetchone()[0]
    if count == 0:
        for s in sentences:
            c.execute("INSERT INTO prompts (expected_text) VALUES (?)", (s,))
        conn.commit()
        print("10 örnek cümle eklendi ✅")
    else:
        print("Prompts zaten var, ekleme yapılmadı.") 
 
database()