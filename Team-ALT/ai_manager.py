# ai_manager.py
import os
from dotenv import load_dotenv
from groq import Groq

SYSTEM_PROMPT = """
Tu es Sport Buddy, un coach sportif francophone.
Utilise le tutoiement. Sois amical, motivant et extrêmement concis (1-2 phrases très courtes).
Ne pose qu'une seule question à la fois.
Pense à toujours rappeler l'importance de l'échauffement au début et des étirements à la fin.
Si l'utilisateur signale une douleur, dis-lui d'arrêter immédiatement l'exercice et de consulter un médecin.
"""
class AIManager:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in .env")
        self.client = Groq(api_key=api_key)
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def get_response(self, user_input: str, max_tokens: int = 200) -> str:
        if not user_input:
            return ""
        # Append user message
        self.history.append({"role": "user", "content": user_input})
        try:
            resp = self.client.chat.completions.create(
                messages=self.history,
                model="llama-3.1-8b-instant",
                temperature=0.2,
                max_tokens=max_tokens,
            )
            ai_text = resp.choices[0].message.content.strip()
            # store full reply in history for context
            self.history.append({"role": "assistant", "content": ai_text})
            # Return first 1-2 sentences (enforced concision)
            sentences = [s.strip() for s in ai_text.replace("\n", " ").split(".") if s.strip()]
            short = ". ".join(sentences[:2])
            if short and not short.endswith("."):
                short += "."
            return short or ai_text or "Sorry, I couldn't generate a response."
        except Exception as e:
            return "Sorry, technical error: " + str(e)
