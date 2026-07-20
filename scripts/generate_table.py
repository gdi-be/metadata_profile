import yaml
import os
import sys
import re

def linkify(text):
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    url_pattern = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)')
    
    def replace(match):
        url = match.group(0)
        href = url if url.startswith('http') else 'http://' + url
        return f'<a href="{href}" target="_blank" style="color: #2563eb; text-decoration: underline;">{url}</a>'
    
    html_ready = text.replace('\n', '<br>')
    return url_pattern.sub(replace, html_ready)

def format_value(val):
    if isinstance(val, dict):
        active_items = [f"{k}" for k, v in val.items() if v is True]
        return ", ".join(active_items) if active_items else "-"
    if val is None or val == "":
        return "-"
    return linkify(str(val))

def generate_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_path = os.path.join(base_dir, 'tables/mde_metadatenprofil-berlin_git0.1.yaml')
    output_path = os.path.join(base_dir, 'index.html')
    
    if not os.path.exists(yaml_path):
        print(f"❌ FEHLER: Datei fehlt unter: {yaml_path}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ FEHLER beim Parsen der YAML-Datei: {e}", file=sys.stderr)
        sys.exit(3)

    # Spalten sammeln (Sektion wird die ganz normale erste Spalte)
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDE Metadatenprofil</title>
    
    <!-- Reine Core-DataTables CSS ohne fehleranfällige Plugins -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
            color: #333333;
            background-color: #f9fafb;
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
            padding: 20px;
        }}
        .header-area {{
            flex: 0 0 auto;
            margin-bottom: 15px;
        }}
        /* Der umgebende Container füllt den Bildschirm elastisch aus */
        .container {{
            flex: 1 1 auto;
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            max-width: 100%;
        }}
        h1 {{
            font-size: 22px;
            color: #111827;
            margin: 0 0 5px 0;
        }}
        
        /* Die responsive Box füllt den Rest des Containers und scrollt sauber */
        .table-responsive {{
            flex: 1 1 auto;
            overflow: auto;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            width: 100%;
        }}
        
        /* FIX: Zwingt die Tabelle, exakt die Containerbreite zu respektieren */
        table.dataTable {{
            margin: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            table-layout: fixed; /* Hält Kopf und Körper im exakt gleichen Breitenraster */
            border-collapse: collapse;
        }}
        
        table.dataTable, table.dataTable th, table.dataTable td,
        .dataTables_wrapper, .dataTables_filter input, .dataTables_length select {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-size: 13px !important;
        }}
        
        /* MODERNES FIXIEREN DES TABELLENKOPFS PER CSS */
        table.dataTable thead th {{
            position: sticky;
            top: 0;
            z-index: 10;
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb !important;
            padding: 10px;
            text-align: left;
            white-space: normal;
            word-break: break-word;
        }}
        
        /* Zellenbegrenzung und automatischer Textumbruch */
        table.dataTable tbody td {{
            padding: 10px;
            vertical-align: top;
            white-space: normal;
            word-break: break-word;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        /* Hebt die Sektions-Spalte optisch dezent hervor */
        table.dataTable tbody td.section-cell {{
            font-weight: 500;
            color: #6b7280;
            background-color: #f9fafb;
        }}
    </style>
</head>
<body>

<div class="header-area">
    <h1>Metadatenprofil</h1>
    <p style="color: #6b7280; margin: 0; font-size: 13px;">Vollständige, dynamische Tabellenansicht aller Profilfelder.</p>
</div>

<div class="container">
    <div class="table-responsive">
        <table id="mdeTable" class="display stripe row-border" style="width:100%">
            <thead>
                <tr>
                    <th style="width: 15%;">Sektion</th>
                    {"".join([f"<th>{col.replace('_', ' ').title()}</th>" for col in all_columns])}
                </tr>
            </thead>
            <tbody>
"""

    # Befüllen der Zeilen
    for section_item in data:
        section_title = section_item.get('section') or section_item.get('Sektion') or 'Allgemein'
        fields = section_item.get('fields', [])
        
        for field in fields:
            html_content += "            <tr>\n"
            html_content += f'                <td class="section-cell">{section_title}</td>\n'
                
            for col in all_columns:
                val = field.get(col, "")
                formatted_val = format_value(val)
                html_content += f'                <td>{formatted_val}</td>\n'
            html_content += "            </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

<script>
$(document).ready(function() {
    $('#mdeTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/de-DE.json"
        },
        "pageLength": -1, // Da CSS das Scrollen übernimmt, zeigen wir standardmäßig alle Zeilen
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Alle"]],
        "stateSave": true,
        "order": [], // Garantiert, dass die originale YAML-Sortierung erhalten bleibt
        "autoWidth": false,
        "scrollY": false,
        "scrollX": false
    });
});
</script>

</body>
</html>
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle erfolgreich und sauber generiert!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
