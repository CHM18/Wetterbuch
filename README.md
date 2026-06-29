# Wetterbuch.html - Modern web-version of the C64 Wetterbuch

** To browse the data from 1985-1998, just open Wetterbuch.html in a webbrowser **

# WETTERBU.PRG — Commodore 64 Weather Diary ("Wetterbuch")

**Written by Günter and Ch. Maier, 1992. Requires Simons BASIC cartridge.**

---

## Data Structures (lines 50–86)

| Array | Purpose |
|---|---|
| `T1%(366)`, `T2%(366)` | Daily minimum/maximum temperature for up to 366 days |
| `WE%(366)` | Daily weather code — a **bitmask** (bit 0=sunny, 1=partly cloudy, 2=overcast, 3=rain, 4=thunderstorm, 5=hail, 6=snow, 7=fog) |
| `NREG%(366)` | Daily rainfall in mm |
| `NSCH%(366)` | Daily snowfall/hail in cm |
| `MAX%(12,2)`, `MIN%(12,2)` | Monthly temperature records + the day they occurred |
| `WZ%(12,7)` | Count of each weather type per month |
| `MW(12)` | Monthly mean temperature |

---

## Main Menu (lines 165–370) — 6 options

1. **Load data from disk** (`GOSUB READMON`)
2. **Enter new data** (`GOSUB DATEIN`)
3. **View a month's data** (`GOSUB DATAUS`)
4. **Statistics** (`GOSUB STAT`)
5. **Save data to disk** (`GOSUB SAVEYEAR`)
6. **Quit**

---

## Key Procedures

**`PROC CHANGEYEAR` (5000)** — asks for the 4-digit year, detects leap years (366 vs 365 days), sets the title string.

**`PROC DATEIN` (2000)** — day-by-day data entry loop:
- Prompts for month and day with validation
- User picks 1–8 weather types (stored as bitmask, multiple per day allowed)
- Enters min and max temperature
- If rain/thunderstorm: enters mm of rain
- If snow/hail: enters cm of accumulation
- F1=next day · F3=view chart · F5=correct · F7=menu

**`PROC DATAUS` (6030)** — per-day graphical view in **HIRES mode**:
- Activates sprites showing weather icons for the day
- Draws bar charts: min-temp / max-temp / rain / snow for that day
- Shows horizontal scale lines at monthly min/max

**`PROC STAT` (7010)** — Monthly or Annual statistics:

| Procedure | What it draws |
|---|---|
| `PROC TEMPSTAT` (7133) | Line graph of daily min & max temp + mean for one month |
| `PROC NSCHSTAT` (7510) | Bar chart of daily rain (mm) and snow (cm) for one month |
| `PROC WETSTAT` (7710) | **Pie chart** of weather-type days for one month |
| `PROC JTEMPSTAT` (8208) | Annual temp graph — one point per month (min/max/mean lines) |
| `PROC JNSCHSTAT` (8510) | Annual precipitation bar chart per month |
| `PROC JWETSTAT` (8810) | Annual weather-type pie chart |

---

## Disk I/O (lines 9030–9700)

- **`PROC SAVEMON`** — saves one month as a CBM sequential file named e.g. `JANUAR1992` (5 numbers per day + monthly summary)
- **`PROC READMON`** — reads all 12 month files back into memory
- **`PROC SAVEYEAR`** — loops through all 12 months calling SAVEMON

These produce exactly the `.SEQ` files in the `1985/`–`1998/` folders.

---

## Sprites (lines 12000–21000)

Eight custom sprites are defined using `DINSTR` (Simons BASIC dot-matrix sprite editor using B/C/D pixel characters). They represent weather phenomena (sun rays, clouds, rain, lightning, snow, fog) and are animated on screen during data entry and display using `MMOB` (multicolor sprite move).

---

## Summary

This is a **complete weather-station diary application** for the C64. You enter daily weather observations (temperatures, weather type, precipitation) over a full year. The program saves each month as a sequential disk file, and can display the data as high-resolution bar charts, line graphs, and pie charts — all using Simons BASIC's built-in graphics commands. The `.SEQ` files in this workspace are the actual recorded weather data from 1985 through 1998.

---

## Decoded Source

The tokenized BASIC program (`WETTERBU.PRG`) was decoded using `decode_prg.py`.
The decoded listing is available in `WETTERBU_decoded.txt`.

### Using `decode_prg.py` to Decode C64 BASIC Programs

This Python script decodes tokenized Commodore 64 BASIC programs (`.PRG` files) into readable source code.

**Usage:**
```bash
python decode_prg.py <input.PRG> [output.txt]
```

**Arguments:**
- `<input.PRG>` — Path to the tokenized BASIC program file (required)
- `[output.txt]` — Path to the output text file (optional; default: input filename with `.txt` extension)

**Examples:**
```bash
# Decode WETTERBU.PRG → WETTERBU.txt (same directory)
python decode_prg.py WETTERBU.PRG

# Decode WETTERBU.PRG with custom output name
python decode_prg.py WETTERBU.PRG decoded_listing.txt

# Decode SIMONS_B.PRG (Simons BASIC cartridge ROM)
python decode_prg.py SIMONS_B.PRG SIMONS_decoded.txt
```

**Features:**
- Decodes both standard **C64 BASIC V2** tokens and **Simons BASIC** extended tokens
- Converts PETSCII character encoding to ASCII
- Preserves line numbers and structure
- Works with any Commodore 64 BASIC program (`.PRG` files)

**Requirements:**
- Python 3.6+
- No external dependencies (uses only standard library: `struct`, `sys`, `pathlib`)

---

## Helper Files (Development & Debugging)

### `embed_data.py`
**Purpose:** Generates embedded weather data for the web application.

Reads all 168 `.SEQ` files (12 months × 14 years from 1985–1998) from the year directories, encodes them as base64 strings, and outputs a JavaScript file with an `EMBEDDED_DATA` object containing all data embedded as text.

**Usage:**
```bash
python embed_data.py
```

**Output:**
- `embedded_data.js` — JavaScript object with structure:
  ```javascript
  const EMBEDDED_DATA = {
    "1985": { 0: "base64...", 1: "base64...", ... },
    "1986": { ... },
    ...
  }
  ```
- Allows the web app to load weather data instantly without separate file downloads
- Total embedded size: ~347 KB (14 years × 12 months of weather data)

---

### `integrate.py`
**Purpose:** Integrates embedded data into the web application.

Reads `embedded_data.js` and `index.html`, merges the weather data into the main HTML file, and ensures all JavaScript is properly initialized.

**Usage:**
```bash
python integrate.py
```

**Operations:**
1. Reads `embedded_data.js` with proper UTF-16 encoding handling
2. Inserts the `EMBEDDED_DATA` object into `index.html`
3. Adds the `autoLoadEmbedded()` function for automatic data loading
4. Updates CSS styling for weather tags and icons
5. Outputs the complete self-contained web application

**Requirements:**
- Python 3.6+
- Must be run after `embed_data.py` generates the data file

---

### `_debug_script.js`
**Purpose:** Temporary debugging file for JavaScript validation.

Extracted from `index.html` during development to validate the main JavaScript block for syntax errors using Node.js.

**Usage (manual validation):**
```bash
node --check _debug_script.js
```

**When created:**
- Generated during debugging to isolate the main script block
- Used to identify and fix JavaScript parsing errors
- Not needed for production; can be safely deleted

**Status:** Temporary/debug file — safe to ignore or delete.

---

### `analyze_braces.py`
**Purpose:** Analyzes JavaScript brace balance and syntax structure.

Counts opening/closing braces, parentheses, and brackets in the main script block to identify mismatched or stray braces that cause syntax errors.

**Usage:**
```bash
python analyze_braces.py
```

**Output:**
- Balance count: `Opens: X, Closes: Y, Balance: X-Y`
- Line-by-line balance tracking to identify where mismatch occurs
- Last 30 lines showing cumulative brace balance progression
- Helps locate unclosed functions or stray braces

**When useful:**
- When `node --check` reports "Unexpected end of input" or "}' at line X"
- To understand the structure of large JavaScript blocks
- To verify all functions are properly closed

**Status:** Temporary/debug file — safe to ignore or delete.

---

### `check_syntax.py`
**Purpose:** General Python syntax validator and code analyzer.

Utility script for checking Python file syntax and structure during development.

**Usage:**
```bash
python check_syntax.py
```

**Status:** Temporary/debug file — safe to ignore or delete.

---

## Notes on Helper Files

These files were created during the development and debugging process:

- **Development phase:** `embed_data.py` and `integrate.py` were used to create the initial version
- **Debugging phase:** `_debug_script.js`, `analyze_braces.py`, and `check_syntax.py` were created to diagnose and fix JavaScript syntax errors
- **Production:** Only `index.html`, `decode_prg.py`, and `embed_data.py` are needed going forward
- **Git:** The `.gitignore` file excludes these helper files from version control to keep the repository clean

To regenerate the web app after modifying data:
1. Ensure all `.SEQ` files are in their year directories (`1985/`, `1986/`, etc.)
2. Run `python embed_data.py` to regenerate embedded data
3. Run `python integrate.py` to update `index.html`
4. Open `index.html` in a web browser

