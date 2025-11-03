import sqlite3
import pyttsx3

# 1. TTS motorunu başlat
engine = pyttsx3.init(driverName='nsss')
voices = engine.getProperty('voices')
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
engine.setProperty('rate', 180)

def speak_text(text):
    """Verilen metni sesli oku"""
    engine.say(text)
    engine.runAndWait()

def get_prompt_by_id(prompt_id):
    """Database'den id'ye göre prompt getir"""
    conn = sqlite3.connect("speech_eval_small.db")
    c = conn.cursor()
    c.execute("SELECT expected_text FROM prompts WHERE id=?", (prompt_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]  # sadece metni döndür
    return None

# 2. Örnek kullanım
prompt_id = 1  # mesela id=1 olan yazıyı seç
text = get_prompt_by_id(prompt_id)

if text:
    print(f"[DB’den gelen yazı]: {text}")
    speak_text(text)
else:
    print("Bu ID için kayıt bulunamadı.")
