import os, base64

base = r'c:\Users\post\Desktop\Dateien_KI\Wetterbuch'
embedded = {}

for year in sorted(os.listdir(base)):
    ypath = os.path.join(base, year)
    if not os.path.isdir(ypath) or not year.isdigit(): 
        continue
    
    embedded[year] = {}
    for fname in sorted(os.listdir(ypath)):
        if not fname.upper().endswith('.SEQ'): 
            continue
        
        with open(os.path.join(ypath, fname), 'rb') as f:
            data = base64.b64encode(f.read()).decode('ascii')
        
        # Detect month from filename
        up = fname.upper()
        months = ['JANUAR','FEBRUAR','MAERZ','APRIL','MAI','JUNI','JULI','AUGUST','SEPTEMBE','OKTOBER','NOVEMBER','DEZEMBER']
        month_idx = -1
        for i, m in enumerate(months):
            if up.startswith(m):
                month_idx = i
                break
        
        if month_idx >= 0:
            embedded[year][str(month_idx)] = data

# Output as JavaScript
print('const EMBEDDED_DATA = {')
for year in sorted(embedded.keys(), key=int):
    print(f'  "{year}": {{')
    for m in sorted(embedded[year].keys(), key=int):
        print(f'    {m}: "{embedded[year][m]}",')
    print('  },')
print('};')
