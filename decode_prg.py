import struct
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════
# C64 BASIC V2 & SIMONS BASIC TOKEN TABLES
# ═══════════════════════════════════════════════════════

# Standard C64 BASIC V2 tokens
tokens = {
    0x80:"END", 0x81:"FOR", 0x82:"NEXT", 0x83:"DATA", 0x84:"INPUT#", 0x85:"INPUT",
    0x86:"DIM", 0x87:"READ", 0x88:"LET", 0x89:"GOTO", 0x8A:"RUN", 0x8B:"IF",
    0x8C:"RESTORE", 0x8D:"GOSUB", 0x8E:"RETURN", 0x8F:"REM", 0x90:"STOP",
    0x91:"ON", 0x92:"WAIT", 0x93:"LOAD", 0x94:"SAVE", 0x95:"VERIFY", 0x96:"DEF",
    0x97:"POKE", 0x98:"PRINT#", 0x99:"PRINT", 0x9A:"CONT", 0x9B:"LIST", 0x9C:"CLR",
    0x9D:"CMD", 0x9E:"SYS", 0x9F:"OPEN", 0xA0:"CLOSE", 0xA1:"GET", 0xA2:"NEW",
    0xA3:"TAB(", 0xA4:"TO", 0xA5:"FN", 0xA6:"SPC(", 0xA7:"THEN", 0xA8:"NOT",
    0xA9:"STEP", 0xAA:"+", 0xAB:"-", 0xAC:"*", 0xAD:"/", 0xAE:"^",
    0xAF:"AND", 0xB0:"OR", 0xB1:">", 0xB2:"=", 0xB3:"<", 0xB4:"SGN",
    0xB5:"INT", 0xB6:"ABS", 0xB7:"USR", 0xB8:"FRE", 0xB9:"POS", 0xBA:"SQR",
    0xBB:"RND", 0xBC:"LOG", 0xBD:"EXP", 0xBE:"COS", 0xBF:"SIN", 0xC0:"TAN",
    0xC1:"ATN", 0xC2:"PEEK", 0xC3:"LEN", 0xC4:"STR$", 0xC5:"VAL", 0xC6:"ASC",
    0xC7:"CHR$", 0xC8:"LEFT$", 0xC9:"MID$", 0xCA:"RIGHT$", 0xCB:"GO"
}

# Simons BASIC extended tokens (preceded by 0x64)
simons = {
    0x01:"HIRES",    0x02:"PLOT",     0x03:"LINE",     0x04:"BLOCK",
    0x05:"FCHR",     0x06:"FCOL",     0x07:"FILL",     0x08:"REC",
    0x09:"ROT",      0x0A:"DRAW",     0x0B:"CHAR",     0x0C:"HI COL",
    0x0D:"INV",      0x0E:"FRAC",     0x0F:"MOVE",     0x10:"PLACE",
    0x11:"UPB",      0x12:"UPW",      0x13:"LEFTW",    0x14:"LEFTB",
    0x15:"DOWNB",    0x16:"DOWNW",    0x17:"RIGHTB",   0x18:"RIGHTW",
    0x19:"MULTI",    0x1A:"COLOUR",   0x1B:"MMOB",     0x1C:"BFLASH",
    0x1D:"MOB SET",  0x1E:"MUSIC",    0x1F:"FLASH",    0x20:"REPEAT",
    0x21:"PLAY",     0x22:"DO",       0x23:"PRINT",    0x24:"EXIT",
    0x25:"EXITIF",   0x26:"UNTIL",    0x27:"WHILE",    0x28:"AT(",
    0x29:"CASE",     0x2A:"ENDCASE",  0x2B:"OF",       0x2C:"WAVE",
    0x2D:"VOLUME",   0x2E:"PUT",      0x2F:"FETCH",    0x30:"AT(",
    0x31:"PROC",     0x32:"GOTO",     0x33:"GOSUB",    0x34:"ENDPROC",
    0x35:"DISC",     0x36:"HELP",     0x37:"FETCH",    0x38:"FN",
    0x39:"CALL",     0x3A:"EXEC",     0x3B:"PROCEDURE",0x3C:"PROC",
    0x3D:"LOCAL",    0x3E:"LOOP",     0x3F:"RCOMP",    0x40:"ELSE",
    0x41:"RETINSTR", 0x42:"PRINTUSING",0x43:"USING",   0x44:"CAT",
    0x45:"ERASE",    0x46:"COPY",     0x47:"FIND",     0x48:"OPTION",
    0x49:"AUTO",     0x4A:"OLD",      0x4B:"JOY",      0x4C:"MOD",
    0x4D:"DIV",      0x4E:"ALL",      0x4F:"DIN",      0x50:"RESET",
    0x51:"CALL",     0x52:"ON KEY",   0x53:"DISABLE",  0x54:"RESUME",
    0x55:"DLOAD",    0x56:"CHRSN",    0x57:"SPRDEF",   0x58:"PASTE",
    0x59:"TURBO",    0x5A:"EXPAND",   0x5B:"SCROLL",   0x5C:"COLOUR",
    0x5D:"CENTRE",   0x5E:"PRINT#",   0x5F:"DSAVE",    0x60:"DELETE",
    0x61:"INSTR",    0x62:"DINSTR",   0x63:"STAMP",    0x64:"CSET",
    0x65:"SPRPLOT",  0x66:"AT",       0x67:"DEC",      0x68:"HEX$",
    0x69:"ERR$",     0x6A:"NUM",      0x6B:"ON",       0x6C:"RCOMP",
    0x6D:"INSTR",    0x6E:"ELSE",     0x6F:"ANGL",     0x70:"RANGE",
    0x71:"TEST",     0x72:"CLOSE",    0x73:"SIZE",      0x74:"BSTR$",
    0x75:"CONT",     0x76:"WINDOW",   0x77:"DISPLAY",  0x78:"SPEED",
    0x79:"PROC",     0x7A:"EXEC",     0x7B:"ON",
}

# ═══════════════════════════════════════════════════════
# PETSCII TO ASCII CONVERSION
# ═══════════════════════════════════════════════════════

def petscii(b):
    """Convert PETSCII byte to printable ASCII."""
    if 0x20 <= b <= 0x5F:
        return chr(b)
    if 0x60 <= b <= 0x7E:
        return chr(b)
    if 0xC1 <= b <= 0xDA:
        return chr(b - 0x80)  # shifted letters -> uppercase
    if b == 0x0D:
        return '\n'
    return f'[{b:02X}]'

# ═══════════════════════════════════════════════════════
# PARSING & DECODING
# ═══════════════════════════════════════════════════════

def decode_prg(input_file, output_file=None):
    """
    Decode a Commodore 64 BASIC tokenized PRG file to readable BASIC source.
    
    Args:
        input_file: Path to .PRG file
        output_file: Path to output .TXT file (default: input with .txt extension)
    """
    # Determine output path
    if output_file is None:
        output_file = Path(input_file).with_suffix('.txt')
    
    # Read PRG file
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}", file=sys.stderr)
        return False
    
    if len(data) < 2:
        print(f"ERROR: File too small: {input_file}", file=sys.stderr)
        return False
    
    # Parse BASIC program
    pos = 2  # skip 2-byte load address
    lines = []
    
    while pos + 3 < len(data):
        next_ptr, = struct.unpack_from('<H', data, pos)
        if next_ptr == 0:
            break
        line_num, = struct.unpack_from('<H', data, pos+2)
        pos += 4
        
        text = ""
        in_string = False
        
        while pos < len(data) and data[pos] != 0:
            b = data[pos]
            if b == 0x22:  # Quote character
                in_string = not in_string
                text += '"'
                pos += 1
                continue
            if in_string:
                text += petscii(b)
                pos += 1
                continue
            if b == 0x64:  # Simons BASIC prefix
                pos += 1
                sb = data[pos]
                text += simons.get(sb, f'{{SB:{sb:02X}}}')
            elif b >= 0x80:
                text += tokens.get(b, f'{{{b:02X}}}')
            else:
                text += petscii(b)
            pos += 1
        
        pos += 1  # skip null terminator
        lines.append(f"{line_num} {text}")
    
    # Write output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except IOError as e:
        print(f"ERROR: Could not write to {output_file}: {e}", file=sys.stderr)
        return False
    
    # Print summary
    print(f"✓ Decoded {len(lines)} lines from {Path(input_file).name}")
    print(f"✓ Written to {Path(output_file).name}")
    return True

# ═══════════════════════════════════════════════════════
# COMMAND-LINE INTERFACE
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: decode_prg.py <input.PRG> [output.txt]", file=sys.stderr)
        print()
        print("Decode a Commodore 64 BASIC tokenized PRG file to readable source code.")
        print()
        print("Arguments:")
        print("  input.PRG     Path to tokenized BASIC program file")
        print("  output.txt    Path to output text file (default: input with .txt extension)")
        print()
        print("Examples:")
        print("  python decode_prg.py WETTERBU.PRG")
        print("  python decode_prg.py WETTERBU.PRG decoded_listing.txt")
        sys.exit(1)
    
    input_prg = sys.argv[1]
    output_txt = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = decode_prg(input_prg, output_txt)
    sys.exit(0 if success else 1)
