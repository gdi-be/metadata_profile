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
    return url_pattern.sub(replace, text.replace('\n', '<br>'))

def format_value(val):
    if isinstance(val, dict):
        active_items = [f"{k}" for k, v in val.items() if v is True]
        return ", ".join(active_items) if active_items else "-"
    return linkify(str(val)) if val is not None and val != "" else "-"

def generate_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_path = os.path.join(base_dir, 'tables/mde_metadatenprofil-berlin_git0.1.yaml')
    output_path = os.path.join(base_dir, 'index.html')
    
    if not os.path.exists(yaml_path):
        sys.exit(2)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Alle Spalten ermitteln
    all_columns = []
    for section_item in data:
        for field in section_item.get('fields', []):
            for key in field.keys():
                if key not in all_columns:
                    all_columns.append(key)

    # REINES HTML & CSS - Keine Skripte, keine externen Abhängigkeiten
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
            overflow-x: auto; /* Erlaubt horizontales Scrollen nur bei extrem kleinen Bildschirmen */
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
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
        /* Visuell saubere Trennzeilen für Sektionen über die gesamte Breite */
        .section-row {{
            background-color: #e5e7eb;
            font-weight: bold;
            font-size: 14px;
            color: #1f2937;
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
        
        # Sektions-Überschrift als Zeile über die volle Spaltenbreite einfügen
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

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html()
