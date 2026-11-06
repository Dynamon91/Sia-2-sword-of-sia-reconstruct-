"""Render the declared weighted project estimate; no elapsed-time prediction."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'docs/progress.json').read_text())
assert sum(r['weight'] for r in data['areas'])==100
assert all(0<=r['earned']<=r['weight'] for r in data['areas'])
value=sum(r['earned'] for r in data['areas'])
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="76" viewBox="0 0 600 76" role="img" aria-label="Avanzamento stimato del progetto: {value}%">
<rect width="600" height="76" rx="10" fill="#0b1829"/>
<text x="18" y="25" fill="#ffffff" font-family="sans-serif" font-size="16">Lady Sia 2 · WORK IN PROGRESS · {value}% stimato</text>
<rect x="18" y="40" width="564" height="18" rx="9" fill="#314156"/>
<rect x="18" y="40" width="{564*value/100}" height="18" rx="9" fill="#48c78e"/>
</svg>'''
(root/'docs/progress.svg').write_text(svg+'\n')
rows=['# Avanzamento complessivo','',f'**{value}% — stima editoriale ponderata, aggiornata il {data["updated"]}.**','', 'Non misura il tempo rimanente né la percentuale di pixel originali recuperati. I pesi sono una convenzione di pianificazione e potranno essere rivisti se cambia lo scopo. Un riferimento video archiviato non conta come livello implementato.','', '| Parte | Punti acquisiti / peso | Stato verificato |','|---|---:|---|']
for r in data['areas']:rows.append(f'| {r["name"]} | {r["earned"]} / {r["weight"]} | {r["evidence"]} |')
rows+=['','Aggiornare docs/progress.json solo dopo risultati verificati, poi eseguire `python3 tools/update_progress.py`. Audio sperimentale non integrato e materiali di riferimento non equivalgono a contenuti finiti.']
(root/'docs/PROGRESS.md').write_text('\n'.join(rows)+'\n')
print(f'Progress estimate: {value}%')

# Keep README and detailed progress synchronized from the same data.
readme=root/'README.md'
text=readme.read_text()
start=text.index('<!-- PROJECT_PROGRESS -->')
end=text.index('<!-- /PROJECT_PROGRESS -->',start)+len('<!-- /PROJECT_PROGRESS -->')
block=f"""<!-- PROJECT_PROGRESS -->
![Avanzamento complessivo stimato: {value}%](docs/progress.svg)

**Progetto completo: circa {value}%** — stima ponderata, non misura del tempo rimanente. [Criteri e stato delle singole parti](docs/PROGRESS.md).
<!-- /PROJECT_PROGRESS -->"""
readme.write_text(text[:start]+block+text[end:])

# PNG companion for chat clients without inline SVG support.
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(900,114),'#0b1829');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
draw.text((27,16),f'Lady Sia 2 · WORK IN PROGRESS · {value}% stimato',font=font,fill='white')
draw.rounded_rectangle((27,60,873,87),radius=13,fill='#314156')
if value:draw.rounded_rectangle((27,60,27+846*value/100,87),radius=13,fill='#48c78e')
im.save(root/'docs/progress.png')
