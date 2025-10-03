import whisper
import sqlite3
from fuzzywuzzy import fuzz
from compare import compare_texts
import os

# Sabit test klasörünün yolu
TEST_DIR = "/Users/yagizcetin/Downloads/test"

def get_audio_path(filename: str) -> str:
    """Test klasöründen dosya yolu döndürür"""
    return os.path.join(TEST_DIR, filename)
    print("Path:", file_path)
    print("Var mı?", os.path.exists(file_path))
def speech():
    # ==============================
    # 4. RECORDINGLERİ TEST ETME
    # ==============================
    conn = sqlite3.connect("speech_eval_small.db")
    c = conn.cursor()

    model = whisper.load_model("large")

    # recording1.mp3 → prompt_id 1, recording2.mp3 → prompt_id 2 ...
    for prompt_id in range(1, 11):
        p_id= "rec"+str(prompt_id)+".m4a"
        audio_file = get_audio_path(p_id)
        print("Path:", audio_file)
        print("Var mı?", os.path.exists(audio_file))
        try:
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

        except Exception as e:
            print(f"[HATA] Prompt {prompt_id} işlenemedi ({audio_file})")
            print("Gerçek hata:", repr(e))
            continue

    conn.close()
