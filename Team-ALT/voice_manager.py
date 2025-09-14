# voice_manager.py

import speech_recognition as sr
import edge_tts
import tempfile
import os

# Choose a French voice
VOICE = "fr-FR-HenriNeural"  # change if you prefer another voice

class VoiceManager:
    def __init__(self):
        pass

    # --- NOUVELLE VERSION DE LA FONCTION LISTEN ---
  
    def listen(self, language: str = "fr-FR", pause_threshold: float = 1.5, phrase_time_limit: int = 15) -> str:
        r = sr.Recognizer()
        r.pause_threshold = pause_threshold
        
        # --- AJOUTS POUR LA SENSIBILITÉ ---
        # Un seuil d'énergie plus bas rend le micro plus sensible.
        # Vous pouvez expérimenter avec des valeurs entre 50 et 4000.
        r.energy_threshold = 300  
        r.dynamic_energy_threshold = False # On désactive l'ajustement dynamique pour forcer notre valeur

        try:
            with sr.Microphone() as source:
                # L'ajustement au bruit ambiant est moins crucial quand on fixe le seuil manuellement
                # r.adjust_for_ambient_noise(source, duration=0.5) 
                audio = r.listen(source, timeout=5, phrase_time_limit=phrase_time_limit)
        except Exception as e:
            print("Microphone error:", e)
            return "" 

        try:
            text = r.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return "" # C'est normal si le micro n'a rien capté
        except sr.RequestError as e:
            print("Speech API error:", e)
            return ""

    async def tts_to_file(self, text: str, voice: str = VOICE, rate: str = "+0%") -> str:
        """
        Generate TTS asynchronously and return path to mp3 file.
        Caller should read the file and then delete it.
        """
        if not text:
            return None
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(tmp_path)
            return tmp_path
        except Exception as e:
            print("TTS error:", e)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise