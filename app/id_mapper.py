import uuid
from collections import defaultdict
from app.sap_id import get_new_sap_artikelnummer


def assign_new_ids_and_update_relations(entities, identifier):
    id_map = defaultdict(dict)
    cloned = []
    new_sap_id = None

    for ent in entities:
        typ = ent["type"]
        old_id = ent["id"]

        if typ == "exartikel":
            new_id = get_new_sap_artikelnummer(identifier)
            new_sap_id = new_id
        else:
            new_id = str(uuid.uuid4())

        id_map[typ][old_id] = new_id

    for ent in entities:
        typ = ent["type"]
        old_id = ent["id"]
        new_id = id_map[typ][old_id]
        ent["id"] = new_id
        ent.pop("name", None)

        if new_sap_id:
            ent.setdefault("data", {}).setdefault("attributes", {})["axartikelnrsap"] = {
                "values": [{"id": "1_0_0", "value": new_sap_id, "locale": "de-DE", "source": "internal"}]
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