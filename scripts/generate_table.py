import yaml
import os
import sys

def generate_html():
    # Ermittelt das tatsächliche Wurzelverzeichnis des Repositories
    # (Egal ob das Skript aus /scripts/ oder dem Hauptordner gestartet wird)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    yaml_path = os.path.join(base_dir, 'tables/mde_metadatenprofil-berlin_git0.1.yaml')
    output_path = os.path.join(base_dir, 'index.html')
    
    # Präzise Fehlermeldung, falls die Datei fehlt
    if not os.path.exists(yaml_path):
        print(f"❌ FEHLER: Die Datei wurde nicht gefunden unter: {yaml_path}", file=sys.stderr)
        print(f"Gesuchter Ordnerinhalt: {os.listdir(os.path.dirname(yaml_path))}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ FEHLER beim Parsen der YAML-Datei: {e}", file=sys.stderr)
        sys.exit(3)

# HTML-Struktur mit der exakt gleichen DataTables-Bibliothek
    html_content = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDE Metadatenprofil</title>
    
    <!-- CSS für das Tabellen-Framework (DataTables) -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; background-color: #f9fafb; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h1 { color: #1e3a8a; margin-top: 0; }
        .font-mono { font-family: monospace; font-size: 12px; }
        .badge { background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        .br-pre { white-space: pre-line; }
    </style>
</head>
<body>

<div class="container">
    <h1>Metadatenprofil (Automatisch generiert aus YAML)</h1>
    <p style="color: #6b7280; margin-bottom: 20px;">Dieses Profil wird direkt aus der versionierten Git-YAML erzeugt.</p>

    <table id="mdeTable" class="display stripe" style="width:100%">
        <thead>
            <tr>
                <th>Sektion</th>
                <th>ID</th>
                <th>Feldname [key]</th>
                <th>Anzeige-Titel [label]</th>
                <th>Kardinalität</th>
                <th>Art des Feldes</th>
                <th>Funktionsweise</th>
                <th>Codelisten / Vorbelegungen</th>
                <th>Export zu ISO</th>
            </tr>
        </thead>
        <tbody>
"""

    # Flachklopfen der hierarchischen YAML-Struktur für die Tabelle
    for section_item in data:
        section_title = section_item.get('section', 'Allgemein')
        fields = section_item.get('fields', [])
        
        for field in fields:
            # Buttons als kleine Häkchen-Liste für die Infospalte aufbereiten
            btns = field.get('buttons', {})
            btn_list = []
            if btns.get('help'): btn_list.append("Hilfe")
            if btns.get('copy'): btn_list.append("Kopieren")
            if btns.get('adopt'): btn_list.append("Übernahme")
            if btns.get('template'): btn_list.append("Vorlage")
            if btns.get('delete'): btn_list.append("Löschen")
            btn_str = f"<br><small style='color:#6b7280;'>Buttons: {', '.join(btn_list)}</small>" if btn_list else ""

            # Werte auslesen und Zeilenumbrüche für HTML vorbereiten
            f_id = field.get('id', '')
            f_key = field.get('key', '')
            label = field.get('label', '')
            mult = field.get('multiplicity', '')
            f_type = field.get('field_type', '')
            desc = field.get('description', '').replace('\n', '<br>') + btn_str
            codelist = field.get('codelists_defaults', '').replace('\n', '<br>')
            iso = field.get('iso_export', '')

            html_content += f"""
            <tr>
                <td style="font-weight:600; color:#2563eb;">{section_title}</td>
                <td class="font-mono">{f_id}</td>
                <td class="font-mono" style="color:#4b5563;">{f_key}</td>
                <td><strong>{label}</strong></td>
                <td style="text-align:center;">{mult}</td>
                <td><span class="badge">{f_type}</span></td>
                <td style="font-size:13px;" class="br-pre">{desc}</td>
                <td class="font-mono br-pre" style="color:#6d28d9; font-size:11px;">{codelist}</td>
                <td style="font-size:12px; color:#4b5563;">{iso}</td>
            </tr>"""

    # JS-Bibliotheken einbinden (jQuery + DataTables)
    html_content += """
        </tbody>
    </table>
</div>

<!-- Einbinden der exakt gleichen JavaScript-Bibliotheken -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

<script>
$(document).ready(function() {
    // Initialisierung der Tabelle mit deutscher Übersetzung
    $('#mdeTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/de-DE.json"
        },
        "pageLength": 25,
        "stateSave": true, // Merkt sich Filterung/Sortierung beim Neuladen
        "order": [[ 0, "asc" ]] // Sortierung standardmäßig nach Sektion
    });
});
</script>

</body>
</html>
"""

    # Und hier schreiben wir die index.html ebenfalls sauber ins Hauptverzeichnis
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle via DataTables erfolgreich im Hauptverzeichnis gebaut!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
