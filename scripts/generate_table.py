import yaml
import os
import sys
import re

def linkify(text):
    """Erkennt URLs im Text und wandelt sie in anklickbare HTML-Links um."""
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
    """Formatiert verschachtelte Strukturen lesbar."""
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

    # Spaltennamen dynamisch sammeln (ohne 'section', da dies die Zwischenüberschrift wird)
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

    total_columns = len(all_columns)

    # HTML Grundgerüst mit dynamischer Höhen-Anpassung
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDE Metadatenprofil</title>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        /* Flexbox auf dem Body, um die volle Fensterhöhe dynamisch zu nutzen */
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden; /* Verhindert den globalen Scrollbalken der Website */
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            color: #333333;
            background-color: #f9fafb;
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
            padding: 20px;
        }}
        .header-area {{
            flex: 0 0 auto; /* Feste Höhe für Header */
            margin-bottom: 15px;
        }}
        .container {{
            flex: 1 1 auto; /* Nimmt den restlichen verfügbaren Platz ein */
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden; /* Zwingt DataTables innerhalb der Box zu bleiben */
        }}
        h1 {{
            font-size: 22px;
            color: #111827;
            margin: 0 0 5px 0;
        }}
        
        /* DataTables Schrift- und Layoutanpassungen */
        table.dataTable, table.dataTable th, table.dataTable td,
        .dataTables_wrapper, .dataTables_filter input, .dataTables_length select {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            font-size: 13px !important;
        }}
        
        /* Wichtig für das Scroll-Erlebnis: Setzt den Scroll-Container auf maximale Höhe */
        .dataTables_scrollBody {{
            flex: 1 1 auto !important;
            height: auto !important;
            max-height: none !important;
        }}
        .dataTables_wrapper {{
            display: flex;
            flex-direction: column;
            height: 100%;
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
        
        /* Styling für die Sektions-Zwischenüberschriften */
        .section-row {{
            background-color: #e5e7eb !important;
            font-weight: bold;
            font-size: 14px !important;
            color: #1f2937;
        }}
        .section-row td {{
            padding: 12px 10px !important;
            border-bottom: 2px solid #d1d5db !important;
        }}
    </style>
</head>
<body>

<div class="header-area">
    <h1>Metadatenprofil</h1>
    <p style="color: #6b7280; margin: 0; font-size: 13px;">Vollständige, dynamische Tabellenansicht aller Profilfelder.</p>
</div>

<div class="container">
    <table id="mdeTable" class="display stripe row-border" style="width:100%">
        <thead>
            <tr>
                {"".join([f"<th>{col.replace('_', ' ').title()}</th>" for col in all_columns])}
            </tr>
        </thead>
        <tbody>
"""

    # Zeilen befüllen – Sektionen werden als Trennzeilen eingezogen
    for section_item in data:
        section_title = section_item.get('section', 'Allgemein')
        fields = section_item.get('fields', [])
        
        # Zwischenüberschrift für die Sektion einfügen (erstreckt sich über alle Spalten)
        html_content += f'            <tr class="section-row"><td colspan="{total_columns}">{section_title}</td></tr>\n'
        
        for field in fields:
            html_content += "            <tr>\n"
            for col in all_columns:
                val = field.get(col, "")
                formatted_val = format_value(val)
                html_content += f'                <td>{formatted_val}</td>\n'
            html_content += "            </tr>\n"

    html_content += """
        </tbody>
    </table>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

<script>
$(document).ready(function() {
    var table = $('#mdeTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/de-DE.json"
        },
        "pageLength": -1, // Zeigt standardmäßig alle Zeilen, da wir nun scrollen
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Alle"]],
        "stateSave": true,
        "order": [], // Behält die YAML-Reihenfolge bei
        "scrollY": "calc(100vh - 190px)", // Berechnet die genaue Höhe abzüglich Header/Padding
        "scrollX": true, // Aktiviert horizontales Scrollen falls nötig
        "scrollCollapse": true,
        "paging": true
    });
});
</script>

</body>
</html>
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle mit Zwischenüberschriften und fixer Scroll-Höhe gebaut!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
