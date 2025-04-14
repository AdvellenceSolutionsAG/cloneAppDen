# Importiere requests für HTTP-Anfragen und Hilfsfunktion für Payload-Erstellung
import requests
from utils.helpers import load_and_customize_payload


def fetch_entities(identifier, entity_configs, env_config, template_path):
    """
    Lädt Entitäten vom MDM-System basierend auf der übergebenen Konfiguration.

    Diese Funktion baut für jede konfigurierte Entität (z.B. exartikel, exlieferantenartikel etc.)
    einen Payload dynamisch auf und ruft die MDM-API ab.

    Parameter:
        identifier (str): Artikelnummer oder generischer Identifier (z.B. axartikelnrsap)
        entity_configs (list): Liste von Dicts mit Entity-Typen und Attributkonfigurationen
        env_config (dict): Umgebungskonfiguration (API-Endpunkte, Header)
        template_path (str): Pfad zur JSON-Payload-Vorlage

    Rückgabe:
        list: Alle abgerufenen Entitäten in einem Array
    """

    all_entities = []  # Hier werden alle gefundenen Entitäten gesammelt

    for cfg in entity_configs:
        # Baue dynamischen Payload basierend auf Template + Konfiguration
        payload = load_and_customize_payload(
            template_path=template_path,
            entity_type=cfg["typ"],
            artikelnummer=identifier,
            attributes=cfg["attributes"],
            relationships=cfg["relationships"],
            relationship_attributes=cfg["relationship_attributes"]
        )

        # Sende POST-Request an die MDM-API mit konfigurierten Headern
        response = requests.post(env_config["url_get"], json=payload, headers=env_config["headers_get"])
        response.raise_for_status()  # Bei HTTP-Fehler wird Ausnahme geworfen
        result = response.json()

        # Extrahiere Entitäten aus der Antwortstruktur
        entities = result.get("response", {}).get("entities", [])

        if entities:
            print(f"[OK] {cfg['typ']}: {len(entities)} Eintrag(e) gefunden.")
            all_entities.extend(entities)  # Füge gefundene Entitäten der Gesamtliste hinzu
        else:
            print(f"[HINWEIS] {cfg['typ']}: Kein Eintrag gefunden.")

    return all_entities
