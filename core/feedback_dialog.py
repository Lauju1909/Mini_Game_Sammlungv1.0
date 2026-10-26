import threading
import urllib.request
import datetime
import tkinter as tk
from tkinter import ttk
import core.localization as localization

def send_feedback_async(app_key, version, sender, message, audio_manager=None, callback=None):
    def worker():
        try:
            url = "https://ntfy.sh/lauju_app_feedback"
            payload = f"App: {app_key}\nVersion: {version}\nAbsender: {sender}\nDatum: {datetime.datetime.utcnow().isoformat()}\nNachricht:\n{message}".encode("utf-8")
            req = urllib.request.Request(url, data=payload, method="POST")
            req.add_header("Title", f"Feedback: {app_key} von {sender}".encode("utf-8"))
            req.add_header("Tags", f"{app_key},desktop,speech_balloon".encode("utf-8"))
            with urllib.request.urlopen(req, timeout=10) as resp:
                success = (resp.status == 200)
        except Exception as e:
            print("Feedback sending failed:", e)
            success = False

        if callback:
            callback(success)
        elif audio_manager:
            lang = localization.get_language()
            if success:
                msg = "Feedback erfolgreich an Lauju gesendet! Vielen Dank." if lang == "de" else "Feedback successfully sent to Lauju! Thank you."
                try:
                    audio_manager.play_sound("fanfare")
                except Exception:
                    pass
                audio_manager.speak(msg, priority=2)
            else:
                msg = "Fehler beim Senden des Feedbacks. Bitte Internetverbindung prüfen." if lang == "de" else "Error sending feedback. Please check your internet connection."
                try:
                    audio_manager.play_sound("bump")
                except Exception:
                    pass
                audio_manager.speak(msg, priority=2)

    threading.Thread(target=worker, daemon=True).start()

def open_feedback_dialog(app_key="minigames", version="1.2.0", audio_manager=None):
    def run_gui():
        try:
            root = tk.Tk()
            lang = localization.get_language()
            title = "Feedback & Ideen an Lauju" if lang == "de" else "Feedback & Ideas to Lauju"
            root.title(title)
            root.geometry("480x380")
            root.attributes("-topmost", True)
            root.resizable(False, False)

            frame = ttk.Frame(root, padding=16)
            frame.pack(fill=tk.BOTH, expand=True)

            lbl_sender = ttk.Label(frame, text="Dein Name / Alias (optional):" if lang == "de" else "Your Name / Alias (optional):")
            lbl_sender.pack(anchor=tk.W, pady=(0, 4))

            ent_sender = ttk.Entry(frame, width=40)
            ent_sender.pack(fill=tk.X, pady=(0, 12))
            ent_sender.focus_set()

            lbl_text = ttk.Label(frame, text="Deine Nachricht / Spiel-Idee / Fehlerbericht:" if lang == "de" else "Your message / game idea / bug report:")
            lbl_text.pack(anchor=tk.W, pady=(0, 4))

            txt_message = tk.Text(frame, height=8, width=40, wrap=tk.WORD, font=("Segoe UI", 10))
            txt_message.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

            lbl_status = ttk.Label(frame, text="")
            lbl_status.pack(anchor=tk.W, pady=(0, 8))

            def on_send():
                sender = ent_sender.get().strip() or "Anonym"
                msg = txt_message.get("1.0", tk.END).strip()
                if not msg:
                    lbl_status.config(text="Bitte zuerst eine Nachricht eingeben!" if lang == "de" else "Please enter a message first!", foreground="red")
                    if audio_manager:
                        audio_manager.speak("Bitte zuerst eine Nachricht eingeben!" if lang == "de" else "Please enter a message first!")
                    return

                lbl_status.config(text="Wird gesendet..." if lang == "de" else "Sending...", foreground="blue")
                btn_send.config(state=tk.DISABLED)

                def on_done(success):
                    def update_ui():
                        if success:
                            lbl_status.config(text="✅ Erfolgreich gesendet! Danke." if lang == "de" else "✅ Sent successfully! Thank you.", foreground="green")
                            if audio_manager:
                                try:
                                    audio_manager.play_sound("fanfare")
                                except Exception:
                                    pass
                                audio_manager.speak("Feedback erfolgreich an Lauju übermittelt! Vielen Dank." if lang == "de" else "Feedback sent successfully! Thank you.")
                            root.after(1500, root.destroy)
                        else:
                            lbl_status.config(text="❌ Fehler beim Senden." if lang == "de" else "❌ Error sending.", foreground="red")
                            btn_send.config(state=tk.NORMAL)
                            if audio_manager:
                                audio_manager.speak("Fehler beim Senden." if lang == "de" else "Error sending.")
                    root.after(0, update_ui)

                send_feedback_async(app_key, version, sender, msg, audio_manager, on_done)

            btn_box = ttk.Frame(frame)
            btn_box.pack(fill=tk.X)

            btn_send = ttk.Button(btn_box, text="📤 Absenden" if lang == "de" else "📤 Submit", command=on_send)
            btn_send.pack(side=tk.LEFT, padx=(0, 8))

            btn_cancel = ttk.Button(btn_box, text="Abbrechen" if lang == "de" else "Cancel", command=root.destroy)
            btn_cancel.pack(side=tk.LEFT)

            root.bind("<Escape>", lambda e: root.destroy())
            root.mainloop()
        except Exception as e:
            print("Feedback dialog error:", e)

    threading.Thread(target=run_gui, daemon=True).start()
    if audio_manager:
        audio_manager.speak("Feedback-Fenster geöffnet. Bitte gib deine Nachricht ein." if localization.get_language() == "de" else "Feedback window opened. Please enter your message.")
