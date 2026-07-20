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
    # Spezifische Behandlung für das 'buttons'-Dictionary aus der YAML
    if isinstance(val, dict):
        badge_html = '<div class="button-badge-container">'
        # Jedes Button-Symbol erhält ein individuelles Icon und eine Erklärung beim Drüberfahren (title)
        icons = {
            'help': ('?', '#3b82f6', 'Hilfe'),
            'copy': ('📋', '#6b7280', 'Kopieren'),
            'adopt': ('💾', '#8b5cf6', 'Übernehmen'),
            'template': ('📄', '#f59e0b', 'Template'),
            'delete': ('🗑️', '#ef4444', 'Löschen')
        }
        
        # Sortierte oder feste Reihenfolge ausgeben
        for key in ['help', 'copy', 'adopt', 'template', 'delete']:
            if key in val:
                state = val[key]
                icon_char, color, label = icons.get(key, ('•', '#6b7280', key))
                if state is True:
                    badge_html += f'<span class="btn-badge title-true" style="border-color: {color}; color: {color};" title="{label}: Aktiv">{icon_char}</span>'
                else:
                    badge_html += f'<span class="btn-badge title-false" title="{label}: Deaktiviert">✘</span>'
        badge_html += '</div>'
        return badge_html
    
    # Allgemeine Fallbacks für Standard-Boolean-Werte
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

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Alle dynamischen Datenspalten präzise sammeln
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

    # REINES HTML & CSS - Exakt auf 12 Spalten abgestimmt
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
            table-layout: fixed;
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
            width: 100% !important;
        }}
        
        /* Inline Status-Icons */
        .status-icon {{
            font-size: 14px;
            font-weight: bold;
        }}
        .icon-true {{ color: #10b981; }}
        .icon-false {{ color: #ef4444; }}

        /* Kompakte Buttons-Badges */
        .button-badge-container {{
            display: flex;
            gap: 4px;
            justify-content: center;
        }}
        .btn-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border: 1px solid;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            cursor: help;
        }}
        .title-false {{
            border-color: #e5e7eb;
            color: #d1d5db;
        }}

        /* PRÄZISE CODESPALTIERUNG FÜR DIE 12 SPALTEN (Zählung von links nach rechts) */
        table th:nth-child(1), table td:nth-child(1) {{ width: 3%; }}   /* id */
        table th:nth-child(2), table td:nth-child(2) {{ width: 12%; }}  /* key */
        table th:nth-child(3), table td:nth-child(3) {{ width: 12%; }}  /* label */
        table th:nth-child(4), table td:nth-child(4) {{ width: 5%; }}   /* multiplicity */
        table th:nth-child(5), table td:nth-child(5) {{ width: 6%; }}   /* field_type */
        table th:nth-child(6), table td:nth-child(6) {{ width: 8%; }}   /* type */
        table th:nth-child(7), table td:nth-child(7) {{ width: 7%; }}   /* role */
        table th:nth-child(8), table td:nth-child(8) {{ width: 8%; }}   /* iso_export */
        table th:nth-child(9), table td:nth-child(9) {{ width: 7%; }}   /* other_channels */
        table th:nth-child(10), table td:nth-child(10) {{ width: 20%; }} /* description (Viel Platz) */
        table th:nth-child(11), table td:nth-child(11) {{ width: 11%; }} /* codelists_defaults */
        
        /* Die 12. Spalte ("buttons") wird maximal komprimiert und zentriert */
        table th:nth-child(12), table td:nth-child(12) {{
            width: 1%;
            white-space: nowrap;
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
        print("✅ HTML-Tabelle erfolgreich generiert und perfekt mit YAML abgeglichen!")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben der index.html: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    generate_html()
