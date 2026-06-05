#!/usr/bin/env python
import subprocess
import json
import sys

try:
    result = subprocess.run(
        ['python3', '/home/tarik/.local/bin/eco_flow.py', '--json'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("🐛")
        sys.exit(0)

    data = json.loads(result.stdout.strip())
    text = (
        f" {' - ' if data.get('decharge_ac_active') else ''}"
        f"{'  ' + data.get('puissance_sortie') + ' - ' if data.get('puissance_sortie') else ''}"
        f"󰂄 {data.get('niveau_de_charge', '?')} - "
        f"  {data.get('puissance_solaire', '?')} - "
        f" {data.get('temperature', '?')} "
    )
    tooltip_lines = [f"{k}: {v}" for k, v in data.items()]
    tooltip = "\n".join(tooltip_lines)
    print(text)
    #print(json.dumps(text))

except Exception as e:
    print(json.dumps({
        "text": "🐛",
        "tooltip": f"Erreur: {str(e)}"
    }))
