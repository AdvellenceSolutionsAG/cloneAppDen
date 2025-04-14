import streamlit as st
import os
import json
import subprocess

# --- Mapping für Anzeige ---
ENTITY_LABELS = {
    "exartikel": "Artikel",
    "extradeitem": "Trade Item",
    "exlieferantenartikel": "Lieferantenartikel",
    "exverkaufskond": "Verkaufskondition",
    "exeinkaufskond": "Einkaufskondition"
}

# --- Hilfsfunktionen ---
def get_matching_clone_configs(entity_type):
    folder = "config/clone"
    configs = []
    for fname in os.listdir(folder):
        if fname.endswith(".json") and fname.startswith(entity_type):
            path = os.path.join(folder, fname)
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            display = config.get("display_name", fname.replace(".json", ""))
            configs.append({"filename": fname.replace(".json", ""), "display_name": display})
    return configs

# --- URL-Parameter lesen ---
params = st.query_params
identifier = params.get("identifier", "")
entity_type = params.get("entity_type", "")

# --- Titel und Logo anzeigen ---
st.image("assets/logo.png", width=200)
st.title("🔁 MDM Clone App")

# --- Identifier und Typ anzeigen (Read-only) ---
st.text_input("🧬 Entitätstyp", value=ENTITY_LABELS.get(entity_type, entity_type), disabled=True)
st.text_input("🆔 Identifier", value=identifier, disabled=True)

# --- Passende Clone-Konfigurationen laden ---
if entity_type:
    available_configs = get_matching_clone_configs(entity_type)
else:
    available_configs = []

config_display_names = [c["display_name"] for c in available_configs]
config_filename_map = {c["display_name"]: c["filename"] for c in available_configs}

selected_display = st.selectbox("🧩 Klon-Konfiguration wählen", config_display_names)
selected_config = config_filename_map.get(selected_display)

# --- Lieferanteneingabe, wenn "Lieferantenwechsel" im Displaynamen steht ---
supplier_nr = None
if "Lieferantenwechsel" in selected_display:
    supplier_nr = st.text_input("🏷 Neue Lieferantennummer eingeben", placeholder="z. B. 102000")

# --- Klonen starten ---
if st.button("🚀 Klonen starten"):
    if not identifier or not entity_type or not selected_config:
        st.error("Bitte stelle sicher, dass alle Parameter korrekt übergeben wurden.")
    elif "Lieferantenwechsel" in selected_display and not supplier_nr:
        st.error("Bitte gib die neue Lieferantennummer ein.")
    else:
        # Befehl aufbauen
        command = f"python main.py --clone {selected_config} --articlenr {identifier}"
        if supplier_nr:
            command += f" --supplier {supplier_nr}"

        st.text(f"Führe aus: {command}")

        with st.spinner("Bitte warten – Klonvorgang läuft..."):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            st.code(result.stdout)
            if result.stderr:
                st.error(result.stderr)

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Made with ❤️ by <strong>Advellence Solutions AG</strong></div>", unsafe_allow_html=True)
