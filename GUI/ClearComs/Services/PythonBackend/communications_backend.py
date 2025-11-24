import os
import sys
import sqlite3
import tempfile
import subprocess
import shutil
import json

import whisper
from fuzzywuzzy import fuzz
import sounddevice as sd
from scipy.io.wavfile import write as wav_write
import pyttsx3


# =========================
# settings
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "speech_eval_small.db")
WHISPER_MODEL_NAME = "base"
RECORD_SECONDS = 5          # defoult recordig time
SAMPLE_RATE = 44100
PASS_THRESHOLD = 80         # compare_texts passing treshold


# =========================
# Compare function
# =========================
def compare_texts(target: str, user: str):
    target_norm = target.lower().strip()
    user_norm   = user.lower().strip()

    ratio = fuzz.ratio(target_norm, user_norm)
    partial = fuzz.partial_ratio(target_norm, user_norm)
    token_sort = fuzz.token_sort_ratio(target_norm, user_norm)

    score = int((ratio + partial + token_sort) / 3)
    passed = score >= PASS_THRESHOLD

    return {
        "score": score,
        "ratio": ratio,
        "partial": partial,
        "token_sort": token_sort,
        "passed": 1 if passed else 0,
        "feedback": "Good work, keep up!" if passed else "You have to practice more"
    }


# =========================
# DB helper
# =========================
def get_prompt_by_id(prompt_id: int) -> str | None:
    """prompts tablosundan expected_text döndürür."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT expected_text FROM prompts WHERE id = ?", (prompt_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def save_recording(prompt_id: int,
                   file_path: str,
                   recognized_text: str,
                   cmp: dict) -> None:
    """recordings tablosuna sonuç yazar."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO recordings
        (prompt_id, file_path, recognized_text, score, ratio, partial, token_sort, passed, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prompt_id,
            file_path,
            recognized_text,
            cmp.get("score"),
            cmp.get("ratio"),
            cmp.get("partial"),
            cmp.get("token_sort"),
            cmp.get("passed"),
            cmp.get("feedback"),
        ),
    )
    conn.commit()
    conn.close()


# =========================
# TTS
# =========================
def _init_tts_engine():
    """pyttsx3 engine init (macOS için nsss driver tercih eder)."""
    try:
        if sys.platform == "darwin":
            engine = pyttsx3.init(driverName="nsss")
            # defoult alex speech sound:
            try:
                engine.setProperty("voice", "com.apple.speech.synthesis.voice.Alex")
            except Exception:
                pass
        else:
            engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        return engine
    except Exception as e:
        raise RuntimeError(f"TTS init failed: {e}")


def speak_text(text: str) -> None:
    """Verilen metni sesli okur (pyttsx3, gerekirse sistem fallback)."""
    # first try pyttsx3
    try:
        engine = _init_tts_engine()
        engine.say(text)
        engine.runAndWait()
        return
    except Exception:
        pass

    #if pyttsx3 fails
    try:
        if sys.platform == "darwin":
            subprocess.run(["say", text], check=False)
        elif sys.platform.startswith("win"):
            safe = text.replace("'", "\\'")
            cmd = (
                "Add-Type -AssemblyName System.Speech; "
                f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')"
            )
            subprocess.run(["powershell", "-Command", cmd], check=False)
        else:
            if shutil.which("spd-say"):
                subprocess.run(["spd-say", text], check=False)
            elif shutil.which("espeak"):
                subprocess.run(["espeak", text], check=False)
            else:
                raise RuntimeError("No TTS backend available")
    except Exception as e:
        raise RuntimeError(f"TTS failed: {e}")


def play_prompt(prompt_id: int) -> dict:
    """
    DB’den prompt metnini çekip TTS ile okur.
    C# tarafı için özet bir dict döndürür.
    """
    text = get_prompt_by_id(prompt_id)
    if not text:
        return {"error": "prompt_not_found", "prompt_id": prompt_id}

    speak_text(text)
    return {
        "prompt_id": prompt_id,
        "prompt_text": text,
    }


# =========================
# recording + Whisper STT
# =========================
def record_audio(duration: int = RECORD_SECONDS,
                 samplerate: int = SAMPLE_RATE) -> str:
    """Mikrofondan ses kaydeder, geçici .wav dosyasının yolunu döndürür."""
    data = sd.rec(int(duration * samplerate),
                  samplerate=samplerate,
                  channels=1,
                  dtype="int16")
    sd.wait()

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_write(tmp.name, samplerate, data)
    return tmp.name


_whisper_model_cache = None


def load_whisper_model():
    """Whisper modelini cache’leyerek yükler."""
    global _whisper_model_cache
    if _whisper_model_cache is None:
        _whisper_model_cache = whisper.load_model(WHISPER_MODEL_NAME)
    return _whisper_model_cache


def speech_to_text(audio_path: str) -> str:
    """Whisper ile ses dosyasını çözümler ve metni döndürür."""
    model = load_whisper_model()
    result = model.transcribe(audio_path, language="en")
    return result["text"]


# =========================
# main evaluation function
# =========================
def record_and_evaluate(prompt_id: int,
                        duration: int = RECORD_SECONDS) -> dict:
    """
    1) prompt metnini DB’den çeker
    2) mikrofondan ses kaydı alır
    3) Whisper ile çözümler
    4) compare_texts ile kıyaslar
    5) recordings tablosuna yazar
    6) sonucu dict olarak döndürür
    """
    expected = get_prompt_by_id(prompt_id)
    if not expected:
        return {"error": "prompt_not_found", "prompt_id": prompt_id}

    # recording
    audio_path = record_audio(duration=duration)

    # STT
    user_text = speech_to_text(audio_path)

    # compare
    cmp = compare_texts(expected, user_text)

    # save to DB
    save_recording(prompt_id, audio_path, user_text, cmp)

    # output for C# or CLI
    result = {
        "prompt_id": prompt_id,
        "audio_path": audio_path,
        "prompt_text": expected,
        "recognized_text": user_text,
        "score": cmp["score"],
        "ratio": cmp["ratio"],
        "partial": cmp["partial"],
        "token_sort": cmp["token_sort"],
        "passed": cmp["passed"],
        "feedback": cmp["feedback"],
    }
    return result


# =========================
# Basic CLI interface
# =========================
def main():
    """
    Konsoldan kullanım:
        python clearcoms_backend.py play_prompt 1
        python clearcoms_backend.py record_and_evaluate 1
    Sonuçları JSON olarak print eder.
    """
    if len(sys.argv) < 3:
        # Hata durumunda da JSON dönelim ki C# tarafı şaşırmasın
        print(json.dumps({"error": "usage", "message": "Usage: python clearcoms_backend.py <play_prompt|record_and_evaluate> <prompt_id>"}))
        return 1

    cmd = sys.argv[1]
    try:
        prompt_id = int(sys.argv[2])
    except ValueError:
        print(json.dumps({"error": "invalid_prompt_id", "raw": sys.argv[2]}))
        return 1

    if cmd == "play_prompt":
        out = play_prompt(prompt_id)
    elif cmd == "record_and_evaluate":
        out = record_and_evaluate(prompt_id)
    else:
        out = {"error": "unknown_command", "command": cmd}

    # C# tarafı için GERÇEK JSON çıktı (tek satır)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
