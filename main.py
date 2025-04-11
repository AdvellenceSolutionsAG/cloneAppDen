# main.py

import argparse
import os
from dotenv import load_dotenv
from utils.helpers import load_json
from utils.env_config import get_env_config
from app.clone_runner import run_clone_process
from utils.logging_config import configure_logging
import logging

# --- Logging konfigurieren ---
configure_logging()

# --- Argumente parsen ---
parser = argparse.ArgumentParser(description="MDM Clone App")
parser.add_argument("--clone", dest="clone_config", required=True, help="CloneConfig-Datei (z.B. exartikel_STANDARD)")
parser.add_argument("--articlenr", dest="articlenr", required=True, help="Artikelnummer oder Identifier")
args = parser.parse_args()

# --- Umgebungsvariablen laden ---
load_dotenv()

# --- Konstanten & Pfade ---
CLONE_DIR = "config/clone"
DATA_DIR = "data"
TEMPLATE_PATH = "payloads/template.json"

# --- Konfigurationen laden ---
sync_config_path = os.path.join(CLONE_DIR, f"{args.clone_config}.json")
sync_config = load_json(sync_config_path)
sync_config["clone_config"] = args.clone_config  # für Filename im Upload

env_config = get_env_config()
identifier = args.articlenr

# --- Klon-Vorgang starten ---
new_sap_id, entity_type = run_clone_process(identifier, sync_config, env_config, TEMPLATE_PATH, DATA_DIR)

# --- Ausgabe bei SAP-ID Generierung ---
if new_sap_id:
    base_url = os.getenv("BASE_URL")
    if base_url:
        link = f"{base_url}/entity-manage?id={new_sap_id}&type={entity_type}"
        print(f"\n[INFO] Neue SAP-Artikelnummer: {new_sap_id}")
        print(f"\n[INFO] Artikel wird erstellt: {link}")
    else:
        print(f"\n[INFO] Neue SAP-Artikelnummer: {new_sap_id}")
