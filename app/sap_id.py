import requests
import os
import json
import re


def get_new_sap_artikelnummer(mdm_identifier: str) -> str:
    """
    Holt eine neue Artikelnummer aus SAP, indem:
    1. Ein Token geholt wird
    2. Ein Attributwert aus exartikel gelesen wird
    3. Ein weiterer MDM-Wert abgefragt wird (arefxnummernkreis über refxartikelartsap)
    4. Mit diesem Wert eine neue Artikelnummer bei SAP geholt wird
    """

    # 1. Token holen (Beispiel: über Client Credentials)
    token_url = os.getenv("SAP_TOKEN_URL")
    auth_header = {"Authorization": os.getenv("SAP_TOKEN_AUTH")}
    token_response = requests.get(token_url, headers=auth_header)
    token_response.raise_for_status()
    token = token_response.json().get("access_token")

    if not token:
        raise Exception("Token konnte nicht abgefragt werden.")

    bearer_header = {"Authorization": f"Bearer {token}"}

    # 2. MDM Call: axartikelartsap aus exartikel lesen
    mdm_url = os.getenv("API_URL_GET")
    mdm_headers = {
        "Content-Type": "application/json",
        "x-rdp-clientId": os.getenv("RDP_CLIENT_ID"),
        "x-rdp-userId": os.getenv("RDP_USER_ID"),
        "x-rdp-useremail": os.getenv("RDP_USER_EMAIL"),
        "auth-client-id": os.getenv("RDP_CLIENT_ID"),
        "auth-client-secret": os.getenv("RDP_CLIENT_SECRET")
    }

    mdm_payload_art = {
        "params": {
            "query": {
                "filters": {
                    "typesCriterion": ["exartikel"],
                    "attributesCriterion": [
                        {
                            "axartikelnrsap": {
                                "exacts": mdm_identifier,
                                "type": "_STRING",
                                "valueContexts": [{"source": "internal", "locale": "de-DE"}]
                            }
                        }
                    ]
                }
            },
            "fields": {
                "attributes": ["axartikelartsap"],
                "relationships": [],
                "relationshipAttributes": []
            }
        }
    }

    mdm_response = requests.post(mdm_url, headers=mdm_headers, json=mdm_payload_art)
    mdm_response.raise_for_status()
    mdm_data = mdm_response.json()

    attributes = mdm_data.get("response", {}).get("entities", [{}])[0].get("data", {}).get("attributes", {})
    artikelart = attributes.get("axartikelartsap", {}).get("values", [{}])[0].get("value")

    if not artikelart:
        raise Exception("Artikelart nicht gefunden.")

    # 3. MDM Call: Nummernkreis über Artikelart referenziert
    mdm_payload_ref = {
        "params": {
            "query": {
                "filters": {
                    "typesCriterion": ["refxartikelartsap"],
                    "attributesCriterion": [
                        {
                            "value": {
                                "exacts": str(artikelart),
                                "type": "_STRING",
                                "valueContexts": [{"source": "internal", "locale": "de-DE"}]
                            }
                        }
                    ]
                }
            },
            "fields": {
                "attributes": ["arefxnummernkreis"],
                "relationships": [],
                "relationshipAttributes": []
            }
        }
    }

    nummernkreis_response = requests.post(mdm_url, headers=mdm_headers, json=mdm_payload_ref)
    nummernkreis_response.raise_for_status()
    nummernkreis_data = nummernkreis_response.json()

    nummernkreis = nummernkreis_data.get("response", {}).get("entities", [{}])[0] \
        .get("data", {}).get("attributes", {}).get("arefxnummernkreis", {}).get("values", [{}])[0].get("value")

    if not nummernkreis:
        raise Exception("Nummernkreis konnte nicht aus MDM gelesen werden.")

    # 4. SAP Call mit Nummernkreis
    sap_id_url = os.getenv("SAP_ID_URL_TEMPLATE").replace("{nummernkreis}", str(nummernkreis))
    sap_response = requests.get(sap_id_url, headers=bearer_header)
    sap_response.raise_for_status()
    raw_sap_id = sap_response.text.strip()  # Beispiel: "00000001401096"

    # Entferne führende Nullen via Regex
    sap_id = re.sub(r"^0+", "", raw_sap_id)

    if not sap_id:
        raise Exception("SAP ID konnte nicht geholt oder war leer.")

    return sap_id