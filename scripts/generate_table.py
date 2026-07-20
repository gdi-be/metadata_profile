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
        badge_html = '<div class="button-badge-container">'
        target_buttons = ['help', 'copy', 'adopt', 'template', 'delete']
        
        labels = {
            'help': 'Hilfe',
            'copy': 'Kopieren',
            'adopt': 'Übernehmen',
            'template': 'Template',
            'delete': 'Löschen'
        }
        
        for key in target_buttons:
            state = val.get(key, False)
            label = labels.get(key, key)
            
            if state is True:
                badge_html += f'<span class="btn-indicator indicator-true" title="{label}: Ja">&#10004;</span>'
            else:
                badge_html += f'<span class="btn-indicator indicator-false" title="{label}: Nein">&#10008;</span>'
                
        badge_html += '</div>'
        return badge_html
    
    if val is True:
        return '<span class="status-icon icon-true" title="Ja">&#10004;</span>'
    if val is False:
        return '<span class="status-icon icon-false" title="Nein">&#10008;</span>'
        
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
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
            color: #333333;
            background-color: #f9fafb;
            padding: 20px;
            margin: 0;
        }}
        h1 {{ font-size: 22px; margin: 0 0 5px 0; color: #111827; }}
        
        .table-container {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-top: 15px;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            table-layout: fixed; /* Zwingt den Browser zur Einhaltung der prozentualen Dynamik */
        }}
        
        th, td {{
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
            word-break: break-word;
        }}
        
        th {{
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 600;
        }}
        
        .section-row {{
            background-color: #e5e7eb;
            font-weight: bold;
            font-size: 14px;
            color: #1f2937;
        }}
        
        .section-row td {{
            padding: 12px 10px;
        }}
        
        .button-badge-container {{
            display: inline-flex;
            gap: 4px;
            justify-content: center;
            vertical-align: middle;
        }}

        .btn-indicator {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            cursor: help;
        }}

        .indicator-true {{
            background-color: #ecfdf5;
            color: #10b981;
            border: 1px solid #a7f3d0;
        }}

        .indicator-false {{
            background-color: #fef2f2;
            color: #ef4444;
            border: 1px solid #fecaca;
        }}

        .status-icon {{
            font-size: 14px;
            font-weight: bold;
        }}
        .icon-true {{ color: #10b981 !important; }}
        .icon-false {{ color: #ef4444 !important; }}

        /* DYNAMISCHE PROZENT-AUFTEILUNG FÜR 100% MONITOR-AUSNUTZUNG */
        table th:nth-child(1), table td:nth-child(1) {{ width: 30px; }}   /* id (starr klein) */
        table th:nth-child(2), table td:nth-child(2) {{ width: 10%; }}   /* key */
        table th:nth-child(3), table td:nth-child(3) {{ width: 10%; }}   /* label */
        table th:nth-child(4), table td:nth-child(4) {{ width: 5%; }}    /* multiplicity */
        table th:nth-child(5), table td:nth-child(5) {{ width: 7%; }}    /* field_type */
        table th:nth-child(6), table td:nth-child(6) {{ width: 8%; }}    /* type */
        table th:nth-child(7), table td:nth-child(7) {{ width: 8%; }}    /* role */
        table th:nth-child(8), table td:nth-child(8) {{ width: 8%; }}    /* iso_export */
        table th:nth-child(9), table td:nth-child(9) {{ width: 7%; }}    /* other_channels */
        table th:nth-child(10), table td:nth-child(10) {{ width: 22%; }} /* description (atmet dynamisch) */
        table th:nth-child(11), table td:nth-child(11) {{ width: 15%; }} /* codelists_defaults (atmet dynamisch) */
        
        /* Die 12. Spalte ("buttons") bleibt fest versiegelt gegen Ausbrüche */
        table th:nth-child(12), table td:nth-child(12) {{
            width: 120px; 
            text-align: center;
        }}
    </style>
</head>
<body>

<h1>Metadatenprofil</h1>
<p style="color: #6b7280; margin: 0;">Statische Dokumentation aller Profilfelder.</p>

<div class="table-container">
    <table>
        <thead>
            <tr>
                {"".join([f"<th>{col.replace('_', ' ').title()}</th>" for col in all_columns])}
            </tr>
        </thead>
        <tbody>
"""

    for section_item in data:
        section_title = section_item.get('section') or section_item.get('Sektion') or 'Allgemein'
        fields = section_item.get('fields', [])
        
        colspan_value = len(all_columns)
        html_content += f'            <tr class="section-row"><td colspan="{colspan_value}">{section_title}</td></tr>\n'
        
        for field in fields:
            html_content += "            <tr>\n"
            for col in all_columns:
                val = field.get(col, "")
                html_content += f'                <td>{format_value(val)}</td>\n'
            html_content += "            </tr>\n"

    html_content += """
        </tbody>
    </table>
</div>

</body>
</html>
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML-Tabelle mit elastischer Breite erfolgreich generiert!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
