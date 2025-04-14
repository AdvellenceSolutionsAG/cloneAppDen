import streamlit as st
import os
import json
import subprocess

# --- Mapping für lesbare Entitätstypen ---
# Technische Bezeichnungen (exartikel, ...) werden für die UI lesbar gemacht
ENTITY_LABELS = {
    "exartikel": "Artikel",
    "extradeitem": "Trade Item",
    "exlieferantenartikel": "Lieferantenartikel",
    "exverkaufskond": "Verkaufskondition",
    "exeinkaufskond": "Einkaufskondition"
}

# --- Hilfsfunktion: Filtert alle passenden Clone-Konfigs für einen Entitätstyp ---
def get_matching_clone_configs(entity_type):
    folder = "config/clone"
    configs = []

    for fname in os.listdir(folder):
        # Nur JSON-Dateien, die mit dem Entitätstyp beginnen
        if fname.endswith(".json") and fname.startswith(entity_type):
            path = os.path.join(folder, fname)
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Anzeige-Name (display_name aus der Datei, sonst Dateiname)
            display = config.get("display_name", fname.replace(".json", ""))
            configs.append({
                "filename": fname.replace(".json", ""),
                "display_name": display
            })

    return configs

# --- URL-Parameter lesen (z. B. ?entity_type=exartikel&identifier=1234) ---
params = st.query_params
identifier = params.get("identifier", "")
entity_type = params.get("entity_type", "")

# --- UI: Logo und Titel ---
st.image("assets/logo.png", width=200)
st.title("🔁 MDM Clone App")

# --- UI: Identifier und Entitätstyp anzeigen (Read-only) ---
st.text_input("🧬 Entitätstyp", value=ENTITY_LABELS.get(entity_type, entity_type), disabled=True)
st.text_input("🆔 Identifier", value=identifier, disabled=True)

# --- Passende Clone-Konfigurationen laden und Auswahl anzeigen ---
if entity_type:
    available_configs = get_matching_clone_configs(entity_type)
else:
    available_configs = []

# Anzeige-Namen und technische Dateinamen zuordnen
config_display_names = [c["display_name"] for c in available_configs]
config_filename_map = {c["display_name"]: c["filename"] for c in available_configs}

# --- Konfiguration auswählen ---
selected_display = st.selectbox("🧩 Klon-Konfiguration wählen", config_display_names)
selected_config = config_filename_map.get(selected_display)

# --- Button: Klonprozess starten ---
if st.button("🚀 Klonen starten"):
    if not identifier or not entity_type or not selected_config:
        st.error("Bitte stelle sicher, dass alle Parameter korrekt übergeben wurden.")
    else:
        # Main-Skript als Subprozess ausführen
        command = f"python main.py --clone {selected_config} --articlenr {identifier}"
        st.text(f"Führe aus: {command}")

        with st.spinner("Bitte warten – Klonvorgang läuft..."):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            # Ausgabe anzeigen
            st.code(result.stdout)

            if result.stderr:
                st.error(result.stderr)

# --- Footer mit Branding ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Made with ❤️ by <strong>Advellence Solutions AG</strong></div>",
    unsafe_allow_html=True
)
