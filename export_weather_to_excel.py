#!/usr/bin/env python3
"""
Export Wetterbuch weather data to Excel file with monthly summaries.
Creates an Excel file with yearly and monthly weather statistics.
"""

import struct
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Weather type names and icons
WEATHER_TYPES = [
    ('Sonne', '☀'),
    ('Heiter', '🌤'),
    ('Bewölkt', '☁'),
    ('Regen', '💧'),
    ('Gewitter', '⚡'),
    ('Hagel', '🧊'),
    ('Schnee', '❄'),
    ('Nebel', '🌫'),
]

MONTHS_DE = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
]

MONTH_PREFIXES = {
    'JANUAR': 0, 'FEBRUAR': 1, 'MAERZ': 2, 'APRIL': 3,
    'MAI': 4, 'JUNI': 5, 'JULI': 6, 'AUGUST': 7,
    'SEPTEMBER': 8, 'OKTOBER': 9, 'NOVEMBER': 10, 'DEZEMBER': 11,
}

def detect_month_from_filename(filename):
    """Extract month index from filename."""
    up = filename.upper()
    for prefix, idx in MONTH_PREFIXES.items():
        if up.startswith(prefix):
            return idx
    return -1

def parse_seq_file(buffer):
    """Parse SEQ file containing weather data."""
    try:
        text = buffer.decode('latin1', errors='ignore')
    except:
        return None
    
    # C64 PRINT# separates values with CR (0x0D)
    parts = text.split('\r')
    parts = [s.strip() for s in parts if s.strip()]
    
    if len(parts) < 16:
        return None
    
    try:
        summary_raw = [int(p) for p in parts[-16:]]
        day_raw = [int(p) for p in parts[:-16]]
    except ValueError:
        return None
    
    days = []
    for i in range(0, len(day_raw) - 4, 5):
        days.append({
            'minTemp': day_raw[i],
            'maxTemp': day_raw[i + 1],
            'weather': day_raw[i + 2],
            'rain': day_raw[i + 3],
            'snow': day_raw[i + 4],
        })
    
    # If summary is all zeros (incomplete save), recompute from daily data
    if all(v == 0 for v in summary_raw[:8]) and days:
        summary_raw = compute_summary(days)
    
    return {
        'days': days,
        'summary': {
            'maxTemp': summary_raw[0],
            'minTemp': summary_raw[2],
            'maxRain': summary_raw[4],
            'maxSnow': summary_raw[6],
            'weatherCounts': summary_raw[8:16],
        }
    }

def compute_summary(days):
    """Compute monthly summary from daily data."""
    max_temp, min_temp = -999, 999
    max_rain, max_snow = 0, 0
    weather_counts = [0] * 8
    
    for day in days:
        max_temp = max(max_temp, day['maxTemp'])
        min_temp = min(min_temp, day['minTemp'])
        max_rain = max(max_rain, day['rain'])
        max_snow = max(max_snow, day['snow'])
        
        # Count weather types from bitmask
        for bit in range(8):
            if day['weather'] & (1 << bit):
                weather_counts[bit] += 1
    
    return [max_temp, 0, min_temp, 0, max_rain, 0, max_snow, 0] + weather_counts

def get_weather_mask(summary):
    """Get bitmask of which weather types occurred in the month."""
    weather_counts = summary.get('weatherCounts', [0] * 8)
    mask = 0
    for i, count in enumerate(weather_counts):
        if count > 0:
            mask |= (1 << i)
    return mask

def export_to_excel(output_file='Wetterdaten.xlsx'):
    """Export all weather data to Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Wetterbuch'
    
    # Set column widths
    ws.column_dimensions['A'].width = 8   # Jahr
    ws.column_dimensions['B'].width = 12  # Monat
    for col in range(3, 11):  # Weather icons
        ws.column_dimensions[get_column_letter(col)].width = 5
    ws.column_dimensions['K'].width = 10  # Min Temp
    ws.column_dimensions['L'].width = 10  # Max Temp
    ws.column_dimensions['M'].width = 12  # Regen(mm)
    ws.column_dimensions['N'].width = 12  # Schnee(cm)
    
    # Define styles
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Write header row
    headers = ['Jahr', 'Monat'] + [name for name, _ in WEATHER_TYPES] + ['Min Temp', 'Max Temp', 'Regen(mm)', 'Schnee(cm)']
    ws.append(headers)
    
    # Format header row
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = border
    
    # Freeze the header row
    ws.freeze_panes = 'A2'
    
    # Collect data for all years and months
    data_rows = []
    
    for year in range(1985, 1999):
        year_dir = Path(f'{year}')
        if not year_dir.exists():
            continue
        
        # Collect month files
        month_files = {}
        for seq_file in year_dir.glob('*.SEQ'):
            month_idx = detect_month_from_filename(seq_file.name)
            if month_idx >= 0:
                month_files[month_idx] = seq_file
        
        # Process each month
        for month_idx in range(12):
            if month_idx not in month_files:
                continue
            
            seq_path = month_files[month_idx]
            
            # Read and parse the file
            try:
                with open(seq_path, 'rb') as f:
                    buffer = f.read()
                parsed = parse_seq_file(buffer)
                if not parsed:
                    continue
                
                summary = parsed['summary']
                weather_mask = get_weather_mask(summary)
                
                # Build row
                row = [year, MONTHS_DE[month_idx]]
                
                # Weather icons (columns 3-10)
                for bit in range(8):
                    if weather_mask & (1 << bit):
                        row.append(WEATHER_TYPES[bit][1])
                    else:
                        row.append('')
                
                # Temperature and precipitation
                row.extend([
                    summary['minTemp'],
                    summary['maxTemp'],
                    summary['maxRain'],
                    summary['maxSnow'],
                ])
                
                data_rows.append(row)
                
            except Exception as e:
                print(f'Error processing {seq_path}: {e}')
                continue
    
    # Write data rows
    for row_data in data_rows:
        ws.append(row_data)
    
    # Format data rows
    for row_idx in range(2, len(data_rows) + 2):
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = border
            cell.alignment = center_align
            
            # Format numbers
            if col_idx in [1, 11, 12, 13, 14]:  # Year and numeric columns
                cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Save the workbook
    wb.save(output_file)
    print(f'✅ Excel file created: {output_file}')
    print(f'   Total rows: {len(data_rows)} months from 14 years')

if __name__ == '__main__':
    export_to_excel('Wetterdaten.xlsx')
