#!/usr/bin/env python3
"""
100% HANDS-FREE PDF Export using WeasyPrint.
No browser, no JavaScript, no waiting - pure Python rendering.

WeasyPrint is a professional-grade PDF generator that:
- Runs completely headless with zero interaction
- Supports CSS Paged Media (like Paged.js but native)
- Requires no browser or JavaScript
- Can run overnight unattended
"""

import os
import sys
from weasyprint import HTML, CSS
from pathlib import Path

EDITIONS_DIR = "/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"

VOLUMES = {
    "Vol1_Part1": "archive/Antirevolutionary_Politics_Vol1_Part1.html",
    "Vol1_Part2": "archive/Antirevolutionary_Politics_Vol1_Part2.html",
    "Vol2_Part1": "archive/Antirevolutionary_Politics_Vol2_Part1.html",
    "Vol2_Part2": "archive/Antirevolutionary_Politics_Vol2_Part2.html",
    "Vol3": "Antirevolutionary_Politics_Vol3_Master_Index.html"
}

# Additional CSS for print optimization
PRINT_CSS = """
@page {
    size: letter;
    margin: 1in 0.85in 1in 1.25in;
}

/* Ensure proper font loading */
body {
    font-family: 'Crimson Pro', Georgia, serif;
}

/* Remove the render HUD for PDF */
#render-hud {
    display: none !important;
}
"""

def export_pdf(vol_key):
    """Export a single volume to PDF using WeasyPrint"""
    filename = VOLUMES.get(vol_key)
    if not filename:
        print(f"❌ Error: Unknown volume {vol_key}")
        print(f"Available volumes: {', '.join(VOLUMES.keys())}")
        return False

    input_path = os.path.join(EDITIONS_DIR, filename)
    output_pdf = filename.replace('.html', '.pdf')
    output_path = os.path.join(EDITIONS_DIR, output_pdf)
    
    print(f"\n{'='*60}")
    print(f"📖 Exporting {vol_key}")
    print(f"   Source: {filename}")
    print(f"   Target: {output_pdf}")
    print(f"{'='*60}")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Input file not found: {input_path}")
        return False
    
    try:
        print(f"🔧 Rendering HTML to PDF...")
        
        # Load HTML file
        html = HTML(filename=input_path)
        
        # Add print optimization CSS
        css = CSS(string=PRINT_CSS)
        
        # Generate PDF
        print(f"📄 Generating PDF (this may take 1-3 minutes)...")
        html.write_pdf(output_path, stylesheets=[css])
        
        # Verify output
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ SUCCESS! PDF created: {size_mb:.2f} MB")
            return True
        else:
            print(f"❌ ERROR: PDF not created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during export: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main export function"""
    print("\n" + "="*60)
    print("🚀 HANDS-FREE PDF EXPORT - WeasyPrint")
    print("   No browser required - 100% automated")
    print("="*60)
    
    # Determine which volumes to export
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        volumes_to_export = list(VOLUMES.keys())
    elif len(sys.argv) > 1:
        volumes_to_export = [sys.argv[1]]
    else:
        print("Usage: python3 export_pdf_weasyprint.py [Vol1_Part1|Vol1_Part2|Vol2_Part1|Vol2_Part2|Vol3|all]")
        sys.exit(1)
    
    print(f"\n📚 Exporting {len(volumes_to_export)} volume(s)")
    
    # Export each volume
    success_count = 0
    failed_volumes = []
    
    for i, vol_key in enumerate(volumes_to_export, 1):
        print(f"\n{'▶'*3} Volume {i}/{len(volumes_to_export)} {'◀'*3}")
        success = export_pdf(vol_key)
        
        if success:
            success_count += 1
            print(f"✓ {vol_key} complete")
        else:
            failed_volumes.append(vol_key)
            print(f"✗ {vol_key} failed")
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 EXPORT COMPLETE")
    print(f"   ✅ Successful: {success_count}/{len(volumes_to_export)}")
    if failed_volumes:
        print(f"   ❌ Failed: {', '.join(failed_volumes)}")
    print("="*60)

if __name__ == "__main__":
    main()
