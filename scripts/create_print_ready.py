#!/usr/bin/env python3
"""
Create print-ready HTML files by removing Paged.js dependency.
These files can be opened directly in any browser and printed via Cmd+P.

The existing CSS @page rules are already in place, so the browser's
native print engine will handle pagination beautifully.
"""

import os
import re
from pathlib import Path

EDITIONS_DIR = "/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"

VOLUMES = {
    "Vol1_Part1": "archive/Antirevolutionary_Politics_Vol1_Part1.html",
    "Vol1_Part2": "archive/Antirevolutionary_Politics_Vol1_Part2.html",
    "Vol2_Part1": "archive/Antirevolutionary_Politics_Vol2_Part1.html",
    "Vol2_Part2": "archive/Antirevolutionary_Politics_Vol2_Part2.html",
    "Vol3": "Antirevolutionary_Politics_Vol3_Master_Index.html"
}

def strip_pagedjs(html_content):
    """Remove Paged.js scripts and HUD, keep CSS @page rules"""
    
    # Remove the Paged.js script tag
    html_content = re.sub(
        r'<script src="paged\.polyfill\.js"></script>',
        '',
        html_content,
        flags=re.IGNORECASE
    )
    
    # Remove the Paged.js configuration script
    html_content = re.sub(
        r'<script>.*?window\.PagedConfig.*?</script>',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Remove the mutation observer script
    html_content = re.sub(
        r'<script>.*?const observer = new MutationObserver.*?</script>',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Remove the render HUD div
    html_content = re.sub(
        r'<div id="render-hud">.*?</div>',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Remove HUD-related CSS
    html_content = re.sub(
        r'#render-hud \{.*?\}',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Remove body margin adjustment for HUD
    html_content = re.sub(
        r'body \{ margin-top: 50px !important; \}',
        '',
        html_content
    )
    
    # Remove pagedjs margin CSS
    html_content = re.sub(
        r'\.pagedjs_margin-top.*?\}',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Remove @media print HUD rule
    html_content = re.sub(
        r'@media print \{.*?#render-hud.*?\}',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Add a note that this is the print-ready version
    # (Removed per user request - no instruction box needed)
    
    return html_content

def create_print_version(vol_key):
    """Create a print-ready version of a volume"""
    filename = VOLUMES.get(vol_key)
    if not filename:
        print(f"❌ Error: Unknown volume {vol_key}")
        return False
    
    input_path = os.path.join(EDITIONS_DIR, filename)
    
    # Create output filename
    output_filename = filename.replace('.html', '_PRINT.html')
    output_path = os.path.join(EDITIONS_DIR, output_filename)
    
    print(f"\n{'='*60}")
    print(f"📖 Creating print-ready version: {vol_key}")
    print(f"   Source: {filename}")
    print(f"   Output: {output_filename}")
    print(f"{'='*60}")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Input file not found: {input_path}")
        return False
    
    try:
        # Read original file
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔧 Removing Paged.js dependencies...")
        
        # Strip Paged.js
        print_ready_html = strip_pagedjs(html_content)
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(print_ready_html)
        
        # Verify output
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            print(f"✅ SUCCESS! Print-ready file created: {size_kb:.1f} KB")
            print(f"   📁 Location: {output_path}")
            return True
        else:
            print(f"❌ ERROR: Output file not created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Create print-ready versions of all volumes"""
    print("\n" + "="*60)
    print("🖨️  CREATING PRINT-READY HTML FILES")
    print("   Browser-native printing (no Paged.js)")
    print("="*60)
    
    success_count = 0
    failed_volumes = []
    
    for i, vol_key in enumerate(VOLUMES.keys(), 1):
        print(f"\n{'▶'*3} Volume {i}/{len(VOLUMES)} {'◀'*3}")
        success = create_print_version(vol_key)
        
        if success:
            success_count += 1
            print(f"✓ {vol_key} ready for printing")
        else:
            failed_volumes.append(vol_key)
            print(f"✗ {vol_key} failed")
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 CONVERSION COMPLETE")
    print(f"   ✅ Successful: {success_count}/{len(VOLUMES)}")
    if failed_volumes:
        print(f"   ❌ Failed: {', '.join(failed_volumes)}")
    print("\n📌 Next Steps:")
    print("   1. Open each *_PRINT.html file in Chrome/Safari")
    print("   2. Press Cmd+P to print")
    print("   3. Save as PDF")
    print("   4. Done!")
    print("="*60)

if __name__ == "__main__":
    main()
