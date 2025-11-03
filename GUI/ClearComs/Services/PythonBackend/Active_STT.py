import whisper
import sqlite3
from fuzzywuzzy import fuzz
from compare import compare_texts
import os

def speech(x,prompt_id):
    # ==============================
    # 4. RECORDINGLERİ TEST ETME
    # ==============================
    conn = sqlite3.connect("speech_eval_small.db")
    c = conn.cursor()

    model = whisper.load_model("small")
    audio_file=x
    # Ses dosyasını çözümle
    result = model.transcribe(audio_file, language="en")
    user_text = result["text"]
    print (user_text)

    # DB’den hedef cümleyi çek
    c.execute("SELECT expected_text FROM prompts WHERE id = ?", (prompt_id,))
    target = c.fetchone()[0]

    # Kıyaslama
    cmp = compare_texts(target, user_text)

    # DB’ye kaydet
    c.execute("""INSERT INTO recordings
           (prompt_id, file_path, recognized_text, score, ratio, partial, token_sort, passed, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (prompt_id, audio_file, user_text, cmp["score"], cmp["ratio"],
         cmp["partial"], cmp["token_sort"], cmp["passed"], cmp["feedback"]))
    conn.commit()

    print(f"[OK] Prompt {prompt_id}")
    print("Beklenen   :", target)
    print("Kullanıcı :", user_text)
    print("Sonuç     :", cmp)
    print("-" * 40)
    return result


    conn.close()
