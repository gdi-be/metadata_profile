import yaml
import os
import sys
import re

def linkify(text):
    """Erkennt URLs im Text und wandelt sie in anklickbare HTML-Links um."""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    # Regex für URLs
    url_pattern = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)')
    
    def replace(match):
        url = match.group(0)
        href = url if url.startswith('http') else 'http://' + url
        return f'<a href="{href}" target="_blank" style="color: #2563eb; text-decoration: underline;">{url}</a>'
    
    # Zeilenumbrüche für HTML vorbereiten und Links ersetzen
    html_ready = text.replace('\n', '<br>')
    return url_pattern.sub(replace, html_ready)

def format_value(val):
    """Formatiert verschachtelte Strukturen (wie Buttons) lesbar."""
    if isinstance(val, dict):
        # Zeigt z.B. Aktivierte Buttons übersichtlich an
        active_items = [f"{k}" for k, v in val.items() if v is True]
        return ", ".join(active_items) if active_items else "-"
    if val is None or val == "":
        return "-"
    return linkify(str(val))

def generate_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_path = os.path.join(base_dir, 'metadatenprofil.yaml')
    output_path = os.path.join(base_dir, 'index.html')
    
    if not os.path.exists(yaml_path):
        print(f"❌ FEHLER: Datei fehlt unter: {yaml_path}", file=sys.stderr)
        sys.exit(2)

    try:
        # Benutze safe_load, um die Reihenfolge der Listen strikt einzuhalten
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ FEHLER beim Parsen der YAML-Datei: {e}", file=sys.stderr)
        sys.exit(3)

    # 1. Alle einzigartigen Spaltennamen dynamisch sammeln, um kein Feld zu verlieren
    # (Wir halten uns an die Reihenfolge, in der sie das erste Mal auftauchen)
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

    # HTML Grundgerüst mit einheitlicher Schriftart und Schriftgröße (Inter / Sans-Serif)
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDE Metadatenprofil</title>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        /* Einheitliche Schriftart und Basis-Größe für die gesamte Seite */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            line-height: 1.5;
            color: #333333;
            background-color: #f9fafb;
            padding: 20px;
        }}
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 22px;
            color: #111827;
            margin-top: 0;
            margin-bottom: 5px;
        }}
        /* Erzwingt exakt dieselbe Schriftart/-größe für die Tabelle und DataTables-Elemente */
        table.dataTable, table.dataTable th, table.dataTable td,
        .dataTables_wrapper, .dataTables_filter input, .dataTables_length select {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            font-size: 13px !important;
        }}
        table.dataTable thead th {{
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb !important;
            padding: 10px;
        }}
        table.dataTable tbody td {{
            padding: 10px;
            vertical-align: top;
            max-width: 300px;
            word-wrap: break-word;
        }}
        .section-badge {{
            font-weight: 600;
            color: #0056b3;
        }}
    </style>
</head>
<body>

<div class="container">
    <h1>Metadatenprofil</h1>
    <p style="color: #6b7280; margin-bottom: 20px; font-size: 13px;">Vollständige, dynamische Tabellenansicht aller Profilfelder.</p>

    <table id="mdeTable" class="display stripe row-border" style="width:100%">
        <thead>
            <tr>
                <th>Sektion</th>
                {"".join([f"<th>{col.replace('_', ' ').title()}</th>" for col in all_columns])}
            </tr>
        </thead>
        <tbody>
"""

    # 2. Zeilen befüllen – Streng nach der Reihenfolge der YAML
    for section_item in data:
        section_title = section_item.get('section', 'Allgemein')
        fields = section_item.get('fields', [])
        
        for field in fields:
            html_content += "            <tr>\n"
            html_content += f'                <td class="section-badge">{section_title}</td>\n'
            
            # Jede Spalte dynamisch auslesen (verhindert das Vergessen von Feldern)
            for col in all_columns:
                val = field.get(col, "")
                formatted_val = format_value(val)
                html_content += f'                <td>{formatted_val}</td>\n'
                
            html_content += "            </tr>\n"

    # JS-Bibliotheken einbinden
    html_content += """
        </tbody>
    </table>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

<script>
$(document).ready(function() {
    $('#mdeTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/de-DE.json"
        },
        "pageLength": 25,
        "stateSave": true,
        "order": [] // Deaktiviert die automatische Vorsortierung, behält die YAML-Reihenfolge bei!
    });
});
</script>

</body>
</html>
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle erfolgreich und formtreu im Hauptverzeichnis gebaut!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
