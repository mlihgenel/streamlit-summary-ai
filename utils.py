import os
import json
import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s -%(filename)s",
    level=logging.INFO
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
TOPICS_FILE = os.path.join(DATA_DIR, "topics.json")

def load_topics():
    logging.info("Geçmiş konular yükleniyor")
    if os.path.exists(TOPICS_FILE):
        try:
            with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                logging.info("Kayıtlar yüklendi")
                return json.load(f)
        except Exception:
            logging.warning("Geçmiş kayıtlar yüklenemedi")
            return []
    return []

def save_topics(topics):
    try:
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
            logging.info("Kayıtlar kaydedildi")
    except:
        logging.error("Kayıtlar kaydedilemedi")
