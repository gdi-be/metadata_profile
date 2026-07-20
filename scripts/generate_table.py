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

    # Spaltennamen dynamisch sammeln. 
    # WICHTIG: Wir setzen 'Sektion' als allererste Spalte fest, damit DataTables sauber danach gruppieren kann!
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

# HTML Grundgerüst mit flexibler Breiten- und Höhenanpassung
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDE Metadatenprofil</title>
    
    <!-- DataTables CSS + RowGroup CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/rowgroup/1.4.1/css/rowGroup.dataTables.min.css">
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            color: #333333;
            background-color: #f9fafb;
            padding: 20px;
            margin: 0;
        }}
        .header-area {{
            margin-bottom: 15px;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-width: 100%;
            box-sizing: border-box;
        }}
        h1 {{
            font-size: 22px;
            color: #111827;
            margin: 0 0 5px 0;
        }}
        
        /* Einheitliche Schriftarten */
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
        
        /* Feste maximale Breite für Zellen, damit sie bei Textmassen umbrechen */
        table.dataTable tbody td {{
            padding: 10px;
            vertical-align: top;
            max-width: 250px;
            white-space: normal; /* Erlaubt Textumbrüche */
            word-break: break-word; /* Bricht lange Wörter */
        }}
        
        /* Sektions-Zwischenüberschriften */
        table.dataTable tr.dtrg-group th {{
            background-color: #e5e7eb !important;
            font-weight: bold !important;
            font-size: 14px !important;
            color: #1f2937 !important;
            text-align: left !important;
            padding: 12px 10px !important;
            border-bottom: 2px solid #d1d5db !important;
        }}
        
        /* Verhindert, dass die Tabelle den Container sprengt */
        .dataTables_wrapper {{
            width: 100% !important;
            overflow: hidden;
        }}
    </style>
</head>
<body>

<div class="header-area">
    <h1>Metadatenprofil</h1>
    <p style="color: #6b7280; margin: 0; font-size: 13px;">Vollständige, dynamische Tabellenansicht aller Profilfelder.</p>
</div>

<div class="container">
    <table id="mdeTable" class="display stripe row-border cell-border" style="width:100%">
        <thead>
            <tr>
                <th>Sektion</th>
                {"".join([f"<th>{col.replace('_', ' ').title()}</th>" for col in all_columns])}
            </tr>
        </thead>
        <tbody>
"""

    for section_item in data:
        section_title = section_item.get('section', 'Allgemein')
        fields = section_item.get('fields', [])
        
        for field in fields:
            html_content += "            <tr>\n"
            html_content += f'                <td>{section_title}</td>\n'
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
<script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/rowgroup/1.4.1/js/dataTables.rowGroup.min.js"></script>

<script>
$(document).ready(function() {
    var table = $('#mdeTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/de-DE.json"
        },
        "pageLength": 25, // Nutzen wir Pagination statt "-1" (alle), um die Performance und das Scrollen zu schonen
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Alle"]],
        "stateSave": true,
        "order": [],
        "columnDefs": [
            { "visible": false, "targets": 0 }
        ],
        "rowGroup": {
            "dataSrc": 0
        },
        "autoWidth": false, // Zwingt DataTables, die Breitenberechnung dynamisch zu machen
        "scrollX": true,    // Aktiviert den horizontalen Scrollbalken innerhalb des Containers
        "scrollCollapse": true
    });
    
    // Passt die Spaltenbreiten beim Laden und bei Fenster-Resizing automatisch an
    setTimeout(function() {
        table.columns.adjust().draw();
    }, 150);
});
</script>

</body>
</html>
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle mit fehlerfreiem RowGroup-Layout gebaut!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
