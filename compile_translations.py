#!/usr/bin/env python
"""
Compile .po translation files to .mo format using polib
This script serves as an alternative to GNU gettext's msgfmt command
"""

import os
import polib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / 'locale'

def compile_messages():
    """Compile all .po files to .mo files"""
    if not LOCALE_DIR.exists():
        print(f"Locale directory not found: {LOCALE_DIR}")
        return
    
    compiled_count = 0
    for po_file in LOCALE_DIR.glob('*/LC_MESSAGES/*.po'):
        try:
            mo_file = po_file.with_suffix('.mo')
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"✓ Compiled: {po_file.relative_to(BASE_DIR)} → {mo_file.relative_to(BASE_DIR)}")
            compiled_count += 1
        except Exception as e:
            print(f"✗ Error compiling {po_file}: {e}")
    
    print(f"\n✓ Successfully compiled {compiled_count} translation files")

if __name__ == '__main__':
    compile_messages()
