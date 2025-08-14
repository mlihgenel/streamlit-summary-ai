import os
import logging
import json
import google.generativeai as gen_ai
from dotenv import load_dotenv

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s -%(filename)s",
    level=logging.INFO
)

load_dotenv()

# Model Oluşturma
try:
    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
        logging.info("API KEY alındı")
    except:
        logging.error("API KEY bulunamadı")
    
    gen_ai.configure(api_key=GOOGLE_API_KEY)
    model_name = "gemini-1.5-flash" # hızlı cevap veren model olduğu için 

    model = gen_ai.GenerativeModel(model_name=model_name)
    logging.info("Model oluşturuldu")
except:
    logging.warning("Model oluşturulamadı")

def get_response(text):
    prompt = f"""
    Aşağıdaki metni analiz et ve şu formatta bir JSON nesnesi döndür:
    {{
        "title": "Metin için kısa ve ilgi çekici bir başlık",
        "summary": "Metnin detaylı bir özeti",
        "keywords": "Virgülle ayrılmış 3 anahtar kelime",
        "feedback_suggestion": "Metindeki konularla ilgili yapıcı bir geri bildirim ve pratik öneriler"
    }}

    Metin:
    ---
    {text}
    ---
    """
    try:
        response = model.generate_content(prompt)
        # Modelin döndürebileceği markdown formatını temizle
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        logging.info(f"Model yanıt üretti ({get_response.__name__})")
        return json.loads(cleaned_response)
    except Exception as e:
        logging.error(f"Model yanıtı işlenemedi veya üretilemedi ({get_response.__name__}): {e}")
        return None
