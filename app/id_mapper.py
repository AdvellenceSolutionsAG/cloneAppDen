# Module importieren
import uuid  # Für das Generieren neuer UUIDs
from collections import defaultdict  # Für verschachtelte Dictionaries mit Standardwerten
from app.sap_id import get_new_sap_artikelnummer  # SAP-Artikelnummernservice



def assign_new_ids_and_update_relations(entities, identifier):
    """
    Weist allen Entitäten neue IDs zu (bei exartikel = neue SAP-ID) und aktualisiert ihre Relationen.
    
    Parameter:
        entities (list): Die exportierten Entitäten, die geklont werden sollen.
        identifier (str): Ursprünglicher Identifier (z. B. Artikelnummer), wird für SAP verwendet.
    
    Rückgabe:
        cloned (list): Liste der bearbeiteten Entitäten mit neuen IDs und ggf. angepassten Relationen.
        id_map (dict): Mapping von alten zu neuen IDs je Entitätstyp.
        new_sap_id (str|None): Die neu generierte SAP-ID, falls vorhanden.
    """

    id_map = defaultdict(dict)  # Dict nach Typ gruppiert: exartikel → {alte_id: neue_id, ...}
    cloned = []  # Liste der final bearbeiteten Entitäten
    new_sap_id = None  # Wird nur bei exartikel vergeben


    for ent in entities:
        typ = ent["type"]
        old_id = ent["id"]

        if typ == "exartikel":
            # Bei Artikeln eine echte SAP-ID holen (inkl. MDM-Abfrage etc.)
            new_id = get_new_sap_artikelnummer(identifier)
            new_sap_id = new_id
        else:
            # Bei allen anderen Typen eine zufällige UUID verwenden
            new_id = str(uuid.uuid4())

        id_map[typ][old_id] = new_id  # Mapping speichern

    for ent in entities:
        typ = ent["type"]
        old_id = ent["id"]
        new_id = id_map[typ][old_id]

        # Neue ID zuweisen & Name entfernen (z. B. aus Naming-Regeln ableiten)
        ent["id"] = new_id
        ent.pop("name", None)

        if new_sap_id:
            ent.setdefault("data", {}).setdefault("attributes", {})["axartikelnrsap"] = {
                "values": [{
                    "id": "1_0_0",
                    "value": new_sap_id,
                    "locale": "de-DE",
                    "source": "internal"
                }]
            }


        for rels in ent.get("data", {}).get("relationships", {}).values():
            for rel in rels:
                rel_to = rel.get("relTo")
                if rel_to:
                    t, i = rel_to["type"], rel_to["id"]
                    if i in id_map[t]:
                        rel_to["id"] = id_map[t][i]

        cloned.append(ent)

    return cloned, id_map, new_sap_id