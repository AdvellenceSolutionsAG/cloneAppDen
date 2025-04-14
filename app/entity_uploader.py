# Importiere notwendige Module
import requests  # Für HTTP-Anfragen
import uuid      # Für das Erzeugen einer eindeutigen ID für den Dateinamen
import os        # Für Dateipfade

def upload_entities(entities, env_config, sync_config):
    """
    Lädt die geklonten Entitäten als Datei per HTTP PUT in das Zielsystem hoch (Blob Import).

    Parameter:
        entities (list): Die zu sendenden Entitäten (werden nicht direkt verwendet, da sie bereits gespeichert sind)
        env_config (dict): Ziel-Umgebungskonfiguration mit Upload-URL und Headern
        sync_config (dict): Synchronisationskonfiguration (z. B. clone_config für Dateibenennung)
    """

    # Erzeuge einen eindeutigen Dateinamen basierend auf der Konfiguration + zufälliger UUID
    filename = f"{sync_config['clone_config']}-{uuid.uuid4()}.json"

    # Speicherort der hochzuladenden Datei
    path = os.path.join("data", "get_entities.json")

    # Öffne Datei im Binärmodus (für PUT-Upload)
    with open(path, "rb") as f:
        # Ersetze Platzhalter "Filename" in der URL mit dem tatsächlichen Namen
        url = env_config["url"].replace("Filename", filename)

        print(f"[INFO] Upload-URL: {url}")  # Info für Nachvollziehbarkeit

        # Sende PUT-Request mit Dateiinhalt
        response = requests.put(url, headers=env_config["headers"], data=f)

        # Wenn Upload fehlschlägt, wird hier eine Exception geworfen
        response.raise_for_status()

        print("[SUCCESS] Upload erfolgreich abgeschlossen.")
