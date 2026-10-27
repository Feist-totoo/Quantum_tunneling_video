from pathlib import Path

path = Path(r"C:\Users\liuzh\.codex\visualizations\2026\08\06\019fd5cf-c08c-7421-a0d8-c19bdfd3f45a\animation-layout-board.html")
text = path.read_text(encoding="utf-8")

replacements = {
    'id="alb-y" type="range" min="-20" max="140"': 'id="alb-y" type="range" min="-100" max="1000"',
    'id="alb-size" type="range" min="0" max="120"': 'id="alb-size" type="range" min="0" max="2000"',
    'title:{x:50,y:48,size:8,opacity:100}, sun:{x:50,y:117,size:108,opacity:100}': 'title:{x:50,y:48,size:3,opacity:100}, sun:{x:50,y:900,size:900,opacity:100}',
    'title:{x:50,y:24,size:3.8,opacity:100}, sun:{x:50,y:80,size:76,opacity:100}': 'title:{x:50,y:24,size:1.4,opacity:100}, sun:{x:50,y:410,size:400,opacity:100}',
    'title:{x:50,y:8,size:1.1,opacity:0}, sun:{x:50,y:52,size:52,opacity:100}': 'title:{x:50,y:8,size:.2,opacity:0}, sun:{x:50,y:52,size:52,opacity:100}',
    "function loadPreset(){ state=clonePreset(presetSelect.value); selected=presetSelect.value.startsWith('temperature')?'axis':'title'; render(); }": "function loadPreset(){ state=clonePreset(presetSelect.value); selectObject(presetSelect.value.startsWith('temperature')?'axis':'title'); }",
    'function selectObject(key){selected=key;render();}': "function selectObject(key){ selected=key; yInput.max=key==='sun'?1000:140; sizeInput.max=key==='sun'?2000:(key==='title'?20:120); render(); }",
    "state[selected].y=Math.max(-20,Math.min(140,(event.clientY-drag.rect.top)/drag.rect.height*100-drag.dy));render();": "const maxY=selected==='sun'?1000:140; state[selected].y=Math.max(-100,Math.min(maxY,(event.clientY-drag.rect.top)/drag.rect.height*100-drag.dy));render();",
}

for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f"Missing expected fragment: {old[:80]}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print(path)
