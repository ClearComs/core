

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import tempfile
import os
import numpy as np
import time
import sys
import subprocess
import shutil

# --- Optional deps (handle missing gracefully) ---
try:
    import pyttsx3
except Exception as e:
    pyttsx3 = None

try:
    import sounddevice as sd
    from scipy.io.wavfile import write as wav_write
except Exception as e:
    sd = None
    wav_write = None

# Fuzzy for metrics + fallback compare
try:
    from fuzzywuzzy import fuzz
except Exception as e:
    fuzz = None

# User's existing modules
try:
    from Active_STT import speech as stt_speech   # expects: text = stt_speech(audio_path)
except Exception as e:
    stt_speech = None

# Try to import user's compare function
user_compare = None
try:
    from compare import compare_texts as user_compare
except Exception as e:
    try:
        # Some users might have named it 'compare'
        from compare import compare as user_compare
    except Exception:
        user_compare = None

DB_PATH = "speech_eval_small.db"
DEFAULT_TTS_VOICE = "com.apple.speech.synthesis.voice.Alex"  # macOS
DEFAULT_TTS_RATE = 150  # slower for clarity
RECORD_SECONDS = 5       # fixed-duration recording
FUZZY_PASS_THRESHOLD = 85  # used if user's compare() doesn't return a pass flag


# -----------------------------
# Database helpers
# -----------------------------
def load_prompts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, expected_text FROM prompts ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows  # list[(id, text)]


def save_recording(prompt_id, file_path, recognized_text, score=None,
                   ratio=None, partial=None, token_sort=None, passed=None, feedback=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO recordings (
            prompt_id, file_path, recognized_text, score, ratio, partial, token_sort, passed, feedback
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (prompt_id, file_path, recognized_text, score, ratio, partial, token_sort, passed, feedback))
    conn.commit()
    conn.close()


# -----------------------------
# Speech helpers
# -----------------------------
def speak_text_mac(text, rate=DEFAULT_TTS_RATE, voice=DEFAULT_TTS_VOICE):
    if pyttsx3 is None:
        raise RuntimeError("pyttsx3 not installed. Try: pip install pyttsx3")
    engine = pyttsx3.init(driverName='nsss')
    if voice:
        try:
            engine.setProperty('voice', voice)
        except Exception:
            pass
    try:
        engine.setProperty('rate', rate)
    except Exception:
        pass
    engine.say(text)
    engine.runAndWait()


def speak_text(text, rate=DEFAULT_TTS_RATE, voice=DEFAULT_TTS_VOICE):
    """Cross-platform TTS wrapper.
    Tries pyttsx3 with an appropriate driver first, then falls back to system commands:
      - macOS: `say`
      - Windows: PowerShell / System.Speech
      - Linux: `spd-say` or `espeak`
    """
    # Try pyttsx3 if available
    if pyttsx3 is not None:
        try:
            driver = None
            if sys.platform == "darwin":
                driver = 'nsss'
            elif sys.platform.startswith("win"):
                driver = 'sapi5'
            else:
                # many Linux setups use espeak
                driver = 'espeak'

            # init engine with chosen driver when possible
            try:
                engine = pyttsx3.init(driverName=driver)
            except Exception:
                engine = pyttsx3.init()

            if voice:
                try:
                    engine.setProperty('voice', voice)
                except Exception:
                    pass
            try:
                engine.setProperty('rate', rate)
            except Exception:
                pass

            engine.say(text)
            engine.runAndWait()
            return
        except Exception:
            # fall through to system-level fallback
            pass

    # Fallback to system commands
    try:
        if sys.platform == "darwin":
            # macOS built-in `say`
            subprocess.run(["say", text], check=False)
            return
        elif sys.platform.startswith("win"):
            # Use PowerShell's System.Speech
            # Escape single quotes in text
            safe = text.replace("'", "\\'")
            cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')"
            subprocess.run(["powershell", "-Command", cmd], check=False)
            return
        else:
            # Linux: try spd-say then espeak
            if shutil.which("spd-say"):
                subprocess.run(["spd-say", text], check=False)
                return
            elif shutil.which("espeak"):
                subprocess.run(["espeak", text], check=False)
                return
            else:
                raise RuntimeError("No TTS backend available: install pyttsx3 or spd-say/espeak")
    except Exception as e:
        raise RuntimeError(f"TTS failed: {e}")


def speak_text_mac(text):
    """Backward-compatible wrapper kept for callers that expect speak_text_mac.
    It delegates to the cross-platform speak_text implementation.
    """
    return speak_text(text)


def record_audio(duration=5, samplerate=44100):
    # Eğer kullanıcıya uygun input yoksa default device seçilir
    try:
        devices = sd.query_devices()
        default_input = sd.default.device[0]  # mevcut default input index
        default_output = sd.default.device[1]  # mevcut default output index
        print("Varsayılan input/output:", default_input, default_output)
    except Exception as e:
        print("Cihaz listesi alınamadı:", e)
        default_input = None
        default_output = None

    # Default device bırakıyoruz → sounddevice kendi seçiyor
    sd.default.device = (default_input, default_output)

    print("Recording with device:", sd.default.device)
    data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_write(tmp.name, samplerate, data)
    return tmp.name


def compare_fallback(expected: str, recognized: str):
    """
    If user's compare function is unavailable or returns an unexpected format,
    compute fuzzy metrics here and decide pass/fail with a threshold.
    Returns: dict(score, ratio, partial, token_sort, passed, feedback)
    """
    if fuzz is None:
        # minimal fallback if fuzzywuzzy not installed
        passed = int(expected.strip().lower() == recognized.strip().lower())
        return dict(score=100 if passed else 0, ratio=None, partial=None, token_sort=None,
                    passed=passed, feedback=None)

    e = expected.strip().lower()
    r = recognized.strip().lower()
    ratio = fuzz.ratio(e, r)
    partial = fuzz.partial_ratio(e, r)
    token_sort = fuzz.token_sort_ratio(e, r)
    score = max(ratio, partial, token_sort)
    passed = 1 if score >= FUZZY_PASS_THRESHOLD else 0
    # Optional quick feedback
    if passed:
        feedback = "Good match."
    else:
        feedback = f"Low similarity (score={score}). Try clearer pronunciation."
    return dict(score=score, ratio=ratio, partial=partial, token_sort=token_sort, passed=passed, feedback=feedback)


def run_compare(expected: str, recognized: str):
    """
    Try user's compare() first; interpret the result flexibly.
    Fallback to our fuzzy-based evaluator if needed.
    Normalize expected/recognized before comparing.
    """
    # Always compute fuzzy metrics for DB even if user's compare returns only pass/fail
    metrics = compare_fallback(expected, recognized)

    if user_compare is None:
        return metrics

    try:
        res = user_compare(expected, recognized)
    except Exception:
        return metrics

    # Try to interpret 'res' smartly
    # Case A: dict with fields
    if isinstance(res, dict):
        # Merge any known keys
        out = dict(metrics)  # start with fuzzy metrics we computed
        for k in ["score", "ratio", "partial", "token_sort", "passed", "feedback"]:
            if k in res and res[k] is not None:
                out[k] = res[k]
        return out

    # Case B: bool/int (0/1)
    if isinstance(res, (bool, int)):
        out = dict(metrics)
        out["passed"] = int(res)
        # keep fuzzy metrics for score/ratio etc.
        return out

    # Case C: tuple/list like (passed, score, ratio, ...)
    if isinstance(res, (tuple, list)) and len(res) > 0:
        out = dict(metrics)
        # best guess: first item = pass flag
        try:
            out["passed"] = int(res[0])
        except Exception:
            pass
        # if second item looks like score
        if len(res) > 1 and isinstance(res[1], (int, float)):
            out["score"] = int(res[1])
        return out

    # Unknown return type → fallback
    return metrics


# -----------------------------
# GUI
# -----------------------------
class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcards - Speech Trainer")
        self.prompts = load_prompts()
        if not self.prompts:
            messagebox.showwarning("Uyarı", "Veritabanında hiç prompt yok.")
            self.prompts = [(0, "No prompts found.")]
        self.index = 0

        # Styles
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        container = ttk.Frame(root, padding=20)
        container.pack(fill="both", expand=True)

        self.card_label = ttk.Label(container, text="", font=("Arial", 24), wraplength=800, anchor="center", justify="center")
        self.card_label.pack(pady=(22, 20))  # üstten 50px boşluk

        self.card_label = ttk.Label(container, text="", font=("Arial", 24), wraplength=800, anchor="center", justify="center")
        self.card_label.pack(pady=(0, 10), fill="x")

        self.result_label = ttk.Label(container, text="", font=("Arial", 14), foreground="#333", wraplength=800, anchor="center", justify="center")
        self.result_label.pack(pady=(4, 16), fill="x")

        btns = ttk.Frame(container)
        btns.pack()

        self.prev_btn = ttk.Button(btns, text="◀ Previous", command=self.show_prev)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.speak_btn = ttk.Button(btns, text="🔊 Listen", command=self.speak_current)
        self.speak_btn.grid(row=0, column=1, padx=5)

        self.record_btn = ttk.Button(btns, text="🎙 Record", command=self.record_and_evaluate)
        self.record_btn.grid(row=0, column=2, padx=5)

        self.next_btn = ttk.Button(btns, text="Next ▶", command=self.show_next)
        self.next_btn.grid(row=0, column=3, padx=5)

        self.status = ttk.Label(container, text="Ready", font=("Arial", 10))
        self.status.pack(pady=(12, 0))

        self.show_card()

    # Navigation
    def show_card(self):
        pid, text = self.prompts[self.index]
        self.card_label.config(text=text)
        self.result_label.config(text="")
        self.status.config(text=f"ID: {pid}   Card {self.index+1}/{len(self.prompts)}")

    def show_prev(self):
        if self.index > 0:
            self.index -= 1
            self.show_card()

    def show_next(self):
        if self.index < len(self.prompts) - 1:
            self.index += 1
            self.show_card()

    # TTS
    def speak_current(self):
        _, text = self.prompts[self.index]
        def _run():
            try:
                self._set_busy(True, "Processing...")
                speak_text(text)
            except Exception as e:
                messagebox.showerror("TTS Error", str(e))
            finally:
                self._set_busy(False, "Ready")
        threading.Thread(target=_run, daemon=True).start()

    # Record + STT + Compare
    def record_and_evaluate(self):
        if stt_speech is None:
            messagebox.showerror("STT Hatası", "STT modülü bulunamadı veya import edilemedi. STT.py içindeki 'speech(path)' fonksiyonunu doğrulayın.")
            return

        pid, expected = self.prompts[self.index]

        def _run():
            try:
                self._set_busy(True, f"Recording ({RECORD_SECONDS} sn)...")
                audio_path = record_audio(RECORD_SECONDS)
                self._set_busy(True, "running STT...")
                recognized = stt_speech(audio_path,pid)
                if not isinstance(recognized, str):
                    # Try to pull text if they returned dict-like
                    try:
                        recognized = recognized.get("text")  # e.g. whisper returns dict sometimes
                    except Exception:
                        recognized = str(recognized)

                self._set_busy(True, "Comparing...")
                cmp_res = run_compare(expected, recognized)

                # Save into DB
                save_recording(
                    prompt_id=pid,
                    file_path=audio_path,
                    recognized_text=recognized,
                    score=cmp_res.get("score"),
                    ratio=cmp_res.get("ratio"),
                    partial=cmp_res.get("partial"),
                    token_sort=cmp_res.get("token_sort"),
                    passed=cmp_res.get("passed"),
                    feedback=cmp_res.get("feedback"),
                )

                # Update UI
                verdict = cmp_res.get("passed")
                emoji = "✅ Correct" if verdict == 1 else "❌ Wrong"
                ratio = cmp_res.get("ratio")
                partial = cmp_res.get("partial")
                token_sort = cmp_res.get("token_sort")
                score = cmp_res.get("score")

                details = f"📝 What you said: {recognized}\n\n{emoji} | Skor: {score} | ratio={ratio}, partial={partial}, token_sort={token_sort}"
                if cmp_res.get("feedback"):
                    details += f"\n💡 {cmp_res['feedback']}"
                self.result_label.config(text=details)
                self.status.config(text="Kaydedildi ✔")

            except Exception as e:
                messagebox.showerror("Hata", str(e))
            finally:
                self._set_busy(False, "Hazır")

        threading.Thread(target=_run, daemon=True).start()

    def _set_busy(self, busy: bool, text: str):
        self.status.config(text=text)
        state = "disabled" if busy else "normal"
        for btn in (self.prev_btn, self.speak_btn, self.record_btn, self.next_btn):
            btn.config(state=state)


def main():
    root = tk.Tk()
    root.title("Flashcards - Speech Trainer")

    # Ekran boyutlarını al
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Pencere boyutu
    width = 750
    height = 400

    # Ortalamak için x ve y
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Geometri ayarla
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Pencereyi yeniden boyutlandırmaya izin ver (istersen kapatabilirsin)
    root.resizable(True, True)

    app = FlashcardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
