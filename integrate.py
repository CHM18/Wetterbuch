#!/usr/bin/env python3
"""
Integrate embedded data and fix styling in index.html
"""

# Read existing HTML
with open(r'c:\Users\post\Desktop\Dateien_KI\Wetterbuch\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Read embedded data
with open(r'c:\Users\post\Desktop\Dateien_KI\Wetterbuch\embedded_data.js', 'r', encoding='utf-16') as f:
    embedded_js = f.read()

# Fix 1: Update WEATHER colors
old_weather = '''const WEATHER = [
  { label:'Sonnig',   icon:'☀',  color:'#f59e0b' },
  { label:'Heiter',   icon:'⛅',  color:'#fbbf24' },
  { label:'Bewölkt',  icon:'☁',  color:'#60a5fa' },
  { label:'Regen',    icon:'🌧', color:'#0369a1' },
  { label:'Gewitter', icon:'⚡', color:'#1e3a8a' },
  { label:'Hagel',    icon:'🌨', color:'#d1d5db' },
  { label:'Schnee',   icon:'❄',  color:'#cffafe' },
  { label:'Nebel',    icon:'🌫', color:'#9ca3af' },
];'''

new_weather = '''const WEATHER = [
  { label:'Sonnig',   icon:'☀',  color:'#f59e0b' },
  { label:'Heiter',   icon:'⛅',  color:'#fbbf24' },
  { label:'Bewölkt',  icon:'☁',  color:'#60a5fa' },
  { label:'Regen',    icon:'🌧', color:'#0369a1' },
  { label:'Gewitter', icon:'⚡', color:'#1e3a8a' },
  { label:'Hagel',    icon:'🌨', color:'#d1d5db' },
  { label:'Schnee',   icon:'❄',  color:'#cffafe' },
  { label:'Nebel',    icon:'🌫', color:'#9ca3af' },
];'''

# If already updated, skip
if new_weather not in html:
    # Find and replace the WEATHER definition (it should already be updated from previous edits)
    pass

# Fix 2: Update .w-tag CSS
old_css = '.w-tag  { font-size: .68rem; padding: 2px 6px; border-radius: 4px; border: 1.5px solid; background: transparent; }'
new_css = '.w-tag  { font-size: .68rem; padding: 2px 6px; border-radius: 4px; border: 1.5px solid; background: transparent; color: var(--muted); }'

if old_css in html:
    html = html.replace(old_css, new_css)

# Fix 3: Update tag HTML rendering
old_tag_html = '<span class="w-tag" style="border-color:${w.color};color:var(--muted)"><span style="color:${w.color};font-weight:700">${w.icon}</span> ${w.label}</span>'
new_tag_html = '<span class="w-tag" style="border-color:${w.color}"><span style="color:${w.color};font-weight:800;margin-right:3px">${w.icon}</span>${w.label}</span>'

if old_tag_html in html:
    html = html.replace(old_tag_html, new_tag_html)

# Fix 4: Insert embedded data and auto-load function
# Find insertion point (before last DOMContentLoaded)
insert_code = f'''let EMBEDDED_DATA = {{}};

// Embedded weather data - auto-loaded on page init
{embedded_js}

// Auto-load embedded data
function autoLoadEmbedded() {{
  if (!EMBEDDED_DATA || Object.keys(EMBEDDED_DATA).length === 0) return;
  const promises = [];
  for (const year in EMBEDDED_DATA) {{
    for (const monthIdx in EMBEDDED_DATA[year]) {{
      promises.push(
        fetch(`data:application/octet-stream;base64,${{EMBEDDED_DATA[year][monthIdx]}}`)
          .then(r => r.arrayBuffer())
          .then(buf => {{
            const parsed = parseSeqFile(buf);
            if (!parsed) return;
            if (!db[year]) db[year] = {{}};
            db[year][monthIdx] = parsed;
          }})
      );
    }}
  }}
  if (promises.length === 0) return;
  Promise.all(promises).then(() => {{
    if (Object.keys(db).length === 0) return;
    buildSidebar();
    const firstYear = Object.keys(db).map(Number).sort((a,b)=>a-b)[0];
    showAnnual(firstYear);
    document.getElementById('locationLabel').textContent =
      `${{Object.keys(db).length}} Jahre, ${{Object.values(db).reduce((s,y)=>s+Object.keys(y).length,0)}} Monate bereit`;
  }});
}}

'''

# Find the start of DOMContentLoaded
pos = html.find('document.addEventListener(\'DOMContentLoaded\'')
if pos > 0:
    # Also insert call to autoLoadEmbedded inside DOMContentLoaded
    # Find the opening brace
    brace_pos = html.find('{', pos)
    if brace_pos > 0:
        # Insert autoLoadEmbedded() call at the start of the function
        html = html[:brace_pos + 1] + '\n  autoLoadEmbedded();\n  ' + html[brace_pos + 1:]
    
    # Insert the embedded data and autoLoadEmbedded function before DOMContentLoaded
    html = html[:pos] + insert_code + html[pos:]

# Write updated HTML
with open(r'c:\Users\post\Desktop\Dateien_KI\Wetterbuch\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✓ Updated index.html with embedded data and styling fixes')
print(f'✓ Embedded {len([k for k in EMBEDDED_DATA.keys()])} years of weather data' if 'EMBEDDED_DATA' in locals() else '✓ Embedded data integrated')
