import copy
import uuid
import requests


def handle_supplier_switch(entities, identifier, supplier_nr, env_config):
    """
    Führt den Lieferantenwechsel-Prozess aus:
    - Holt die ID des neuen Lieferanten
    - Erstellt neue Relationen zu diesem Lieferanten im Artikel
    - Klont existierende Lieferantenartikel + zugehörige Trade Items
    - Verknüpft geklonte Trade Items mit Artikel + neuem Lieferantenartikel

    Rückgabe:
        Liste aller betroffenen Entitäten (Original + neue)
    """

    # 1. Neue Lieferanten-ID via API-Call abfragen
    payload = {
        "params": {
            "query": {
                "filters": {
                    "typesCriterion": ["exlieferant"],
                    "attributesCriterion": [
                        {
                            "axlieferantennr": {
                                "exacts": [supplier_nr],
                                "type": "_STRING",
                                "valueContexts": [{
                                    "source": "internal",
                                    "locale": "de-DE"
                                }]
                            }
                        }
                    ]
                }
            },
            "fields": {
                "attributes": [
                    "axnameeins"
                ],
                "relationships": [],
                "relationshipAttributes": []
            }
        }
    }

    response = requests.post(env_config["url_get"], json=payload, headers=env_config["headers_get"])
    response.raise_for_status()
    data = response.json()

    try:
        supplier_id = data["response"]["entities"][0]["id"]
    except (KeyError, IndexError):
        raise Exception("Lieferanten-ID konnte nicht gefunden werden.")
    
    supplier_name = data["response"]["entities"][0]["data"]["attributes"].get("axnameeins", {}).get("values", [{}])[0].get("value")

    print(f"[INFO] Neue Lieferanten-ID: {supplier_id}")

    # Initiale Daten extrahieren
    artikel_entity = next((e for e in entities if e.get("type") == "exartikel"), None)
    alte_lieferantenartikel = [e for e in entities if e.get("type") == "exlieferantenartikel"]
    alte_tradeitems = [e for e in entities if e.get("type") == "extradeitem"]

    if not artikel_entity:
        raise Exception("exartikel nicht vorhanden in Konfiguration – erforderlich für Lieferantenwechsel.")

    # SAP-ID vom Artikel extrahieren
    sap_id_value = artikel_entity.get("data", {}).get("attributes", {}).get("axartikelnrsap", {}).get("values", [{}])[0].get("value")
    article_id = artikel_entity.get("data", {}).get("attributes", {}).get("axidentifier", {}).get("values", [{}])[0].get("value")
    article_name = artikel_entity.get("data", {}).get("attributes", {}).get("axmdmname", {}).get("values", [{}])[0].get("value")

    # 2. Neue Lieferantenrelation am Artikel setzen
    artikel_entity = copy.deepcopy(artikel_entity)
    artikel_entity.setdefault("data", {}).setdefault("relationships", {}).setdefault("relxliefzuart", []).append({
        "id": "1_0_0",
        "relTo": {"id": supplier_id, "type": "exlieferant"},
        "properties": {
            "direction": "both",
            "relationshipType": "relxliefzuart"
        },
        "attributes": {
            "arelxregellieferant": {
                "values": [{
                    "id": "1_0_0",
                    "value": False,
                    "locale": "de-DE"
                }]
            }
        }
    })

    neue_entities = []
    artikel_entity["id"] = article_id
    artikel_entity["name"] = article_name

    for alt_lieferantenartikel in alte_lieferantenartikel:
        # 3. Neuer Lieferantenartikel
        neuer_lieferantenartikel = copy.deepcopy(alt_lieferantenartikel)
        neuer_lieferantenartikel["id"] = f"{sap_id_value}-{supplier_nr}"
        neuer_lieferantenartikel.pop("name", f"{sap_id_value}-{supplier_name}-{supplier_nr}")

        # Neue Lieferanteninfo setzen
        attrs = neuer_lieferantenartikel.setdefault("data", {}).setdefault("attributes", {})
        attrs["axlieferantennr"] = {"values": [{"id": "1_0_0", "value": supplier_nr, "locale": "de-DE", "source": "internal"}]}
        attrs["axnameeins"] = {"values": [{"id": "1_0_0", "value": supplier_name, "locale": "de-DE", "source": "internal"}]}
        attrs["axartikelnrsap"] = {"values": [{"id": "1_0_0", "value": sap_id_value, "locale": "de-DE", "source": "internal"}]}
        attrs["axmdmname"] = {"values": [{"id": "1_0_0", "value": f"{sap_id_value}-{supplier_name}-{supplier_nr}", "locale": "de-DE", "source": "internal"}]}
        attrs["axidentifier"] = {"values": [{"id": "1_0_0", "value": f"{sap_id_value}-{supplier_nr}", "locale": "de-DE", "source": "internal"}]}

        # Bestehende Lieferanten-Relationen bereinigen
        neuer_lieferantenartikel.setdefault("data", {}).setdefault("relationships", {})["relxliefzuliefart"] = []
        
        # Neue Relation zum Lieferanten
        neuer_lieferantenartikel.setdefault("data", {}).setdefault("relationships", {}).setdefault("relxliefzuliefart", []).append({
            "id": "1_0_0",
            "relTo": {"id": supplier_id, "type": "exlieferant"}
        })

        # 4. Neue Trade Items klonen
        neue_tradeitem_ids = []
        original_tradeitem_ids = alt_lieferantenartikel.get("data", {}).get("relationships", {}).get("relxtradeitemzuliefartikel", [])

        for rel in original_tradeitem_ids:
            trade_item_id = rel.get("relTo", {}).get("id")
            if not trade_item_id:
                continue

            original_trade_item = next((t for t in alte_tradeitems if t.get("id") == trade_item_id), None)
            if not original_trade_item:
                continue

            new_trade_item = copy.deepcopy(original_trade_item)
            new_trade_item["id"] = str(uuid.uuid4())
            new_trade_item.pop("name", None)

            new_trade_item.setdefault("data", {}).setdefault("relationships", {}).setdefault("relxtradeitemzuart", []).append({
                "id": "1_0_0",
                "relTo": {"id": identifier, "type": "exartikel"},
                "properties": {"relationshipType": "relxtradeitemzuart"}
            })
            
            # Artikelnummer auf neue Trade Item schreiben
            new_trade_item.setdefault("data", {}).setdefault("attributes", {})["axartikelnrsap"] = {
                "values": [{"id": "1_0_0", "value": sap_id_value, "locale": "de-DE", "source": "internal"}]
            }
            
            # Lieferanten Name auf neue Trade Item schreiben
            new_trade_item.setdefault("data", {}).setdefault("attributes", {})["axnameeins"] = {
                "values": [{"id": "1_0_0", "value": supplier_name, "locale": "de-DE", "source": "internal"}]
            }

            # Lieferanten Nummer auf neue Trade Item schreiben
            new_trade_item.setdefault("data", {}).setdefault("attributes", {})["axlieferantennr"] = {
                "values": [{"id": "1_0_0", "value": supplier_nr, "locale": "de-DE", "source": "internal"}]
            }

            neue_tradeitem_ids.append({"id": "1_0_0", "relTo": {"id": new_trade_item["id"], "type": "extradeitem"}})
            neue_entities.append(new_trade_item)

        # Neue Trade Item Relationen hinzufügen
        neuer_lieferantenartikel.setdefault("data", {}).setdefault("relationships", {}).setdefault("relxtradeitemzuliefartikel", []).extend(neue_tradeitem_ids)

        # 5. Neue Relation zum Artikel
        artikel_entity.setdefault("data", {}).setdefault("relationships", {}).setdefault("relxartikelzulieferantenartikel", []).append({
            "id": "1_0_0",
            "relTo": {"id": neuer_lieferantenartikel["id"], "type": "exlieferantenartikel"}
        })

        neue_entities.append(neuer_lieferantenartikel)

    # Finaler Output: ursprünglicher Artikel (aktualisiert) + alle neuen Entitäten (Lieferantenartikel & Trade Items)
    result = [artikel_entity] + [e for e in entities if e["type"] not in ["exartikel", "exlieferantenartikel", "extradeitem"]] + neue_entities
    return result