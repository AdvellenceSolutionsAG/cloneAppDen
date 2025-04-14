# main.py – Einstiegspunkt der MDM Clone App

import argparse
import os
from dotenv import load_dotenv
from utils.helpers import load_json
from utils.env_config import get_env_config
from app.clone_runner import run_clone_process
from utils.logging_config import configure_logging
import logging

# --- Logging konfigurieren ---
# Initialisiert das Logging mit einheitlichem Format (wird aus utils geladen)
# configure_logging()

# --- Kommandozeilenargumente definieren und parsen ---
parser = argparse.ArgumentParser(description="MDM Clone App")
parser.add_argument(
    "--clone",
    dest="clone_config",
    required=True,
    help="Name der Clone-Konfiguration (z. B. exartikel_STANDARD)"
)
parser.add_argument(
    "--articlenr",
    dest="articlenr",
    required=True,
    help="Artikelnummer oder Identifier zur Verarbeitung"
)
parser.add_argument(
    "--supplier",
    dest="supplier",
    required=False,
    help="(Optional) Neue Lieferantennummer für Lieferantenwechsel-Prozess"
)
args = parser.parse_args()

# --- Umgebungsvariablen laden (.env Datei) ---
# Ermöglicht Zugriff auf API-URLs, Tokens etc. über os.getenv(...)
load_dotenv()

# --- Konstanten und Pfade definieren ---
CLONE_DIR = "config/clone"             # Pfad zu den Clone-Konfigurationen
DATA_DIR = "data"                      # Speicherort für JSON-Daten
TEMPLATE_PATH = "payloads/template.json"  # Template für API-Requests

# --- Konfigurationsdateien laden ---
# Lade die gewählte Clone-Konfiguration
sync_config_path = os.path.join(CLONE_DIR, f"{args.clone_config}.json")
sync_config = load_json(sync_config_path)

# Merke den technischen Namen der Konfiguration (für Upload-Filenamen)
sync_config["clone_config"] = args.clone_config

# Umgebungskonfiguration laden (API-URLs, Header)
env_config = get_env_config()

# Artikelnummer/Identifier über Argument
identifier = args.articlenr
supplier_nr = args.supplier

# --- Starte Klonprozess ---
# Ruft die gesamte Business-Logik auf und erhält ggf. eine neue SAP-ID zurück
new_sap_id, entity_type = run_clone_process(
    identifier,
    sync_config,
    env_config,
    TEMPLATE_PATH,
    DATA_DIR,
    supplier_nr=supplier_nr
)

# --- Ausgabe bei erfolgreicher SAP-ID Generierung ---
# Wenn eine neue SAP-ID erzeugt wurde, gib den Link zur neuen Entität aus
if new_sap_id:
    base_url = os.getenv("BASE_URL")
    if base_url:
        link = f"{base_url}/entity-manage?id={new_sap_id}&type={entity_type}"
        print(f"\n[INFO] Neue SAP-Artikelnummer: {new_sap_id}")
        print(f"\n[INFO] Artikel wird erstellt: {link}")
    else:
        print(f"\n[INFO] Neue SAP-Artikelnummer: {new_sap_id}")
