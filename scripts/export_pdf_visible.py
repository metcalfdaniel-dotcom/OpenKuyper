#!/usr/bin/env python3
"""
Automated PDF export using VISIBLE browser with Paged.js support.
This script:
1. Starts a local HTTP server to avoid CORS issues
2. Opens a visible browser window
3. Waits for Paged.js to complete rendering
4. Generates PDFs using browser's print function
"""

import os
import sys
import time
import asyncio
import http.server
import socketserver
import threading
from playwright.async_api import async_playwright

EDITIONS_DIR = "/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"
PORT = 8765

VOLUMES = {
    "Vol1_Part1": "archive/Antirevolutionary_Politics_Vol1_Part1.html",
    "Vol1_Part2": "archive/Antirevolutionary_Politics_Vol1_Part2.html",
    "Vol2_Part1": "archive/Antirevolutionary_Politics_Vol2_Part1.html",
    "Vol2_Part2": "archive/Antirevolutionary_Politics_Vol2_Part2.html",
    "Vol3": "Antirevolutionary_Politics_Vol3_Master_Index.html"
}

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that doesn't print every request"""
    def log_message(self, format, *args):
        pass  # Suppress logging

def start_server():
    """Start HTTP server in background thread"""
    os.chdir(EDITIONS_DIR)
    handler = QuietHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"🌐 Starting HTTP server on http://localhost:{PORT}")
    
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(2)  # Give server time to start
    return httpd

async def export_pdf_with_browser(vol_key, browser):
    """Export a single volume to PDF using visible browser"""
    filename = VOLUMES.get(vol_key)
    if not filename:
        print(f"Error: Unknown volume {vol_key}")
        return False

    output_pdf = filename.replace('.html', '.pdf')
    output_path = os.path.join(EDITIONS_DIR, output_pdf)
    
    print(f"\n{'='*60}")
    print(f"📖 Exporting {vol_key}")
    print(f"   Source: {filename}")
    print(f"   Target: {output_pdf}")
    print(f"{'='*60}")
    
    # Create new page
    page = await browser.new_page()
    
    # Navigate to the HTML file via local server
    url = f'http://localhost:{PORT}/{filename}'
    print(f"🔗 Loading: {url}")
    
    try:
        await page.goto(url, wait_until='load', timeout=60000)
        print("✓ Page loaded")
        
        # Wait for Paged.js to start
        await asyncio.sleep(2)
        
        # Wait for the completion indicator (checking the HUD element)
        print("⏳ Waiting for Paged.js to render (this may take 3-5 minutes)...")
        try:
            # Wait for the HUD to show completion message
            await page.wait_for_function(
                """() => {
                    const hud = document.getElementById('render-hud');
                    return hud && hud.textContent.includes('READY FOR PDF EXPORT');
                }""",
                timeout=600000  # 10 minutes max
            )
            print("✓ Paged.js rendering complete!")
            
            # Get the page count
            page_count = await page.evaluate(
                "document.querySelectorAll('.pagedjs_page').length"
            )
            print(f"📄 Document has {page_count} pages")
            
        except Exception as e:
            print(f"⚠ Timeout or error waiting for Paged.js: {e}")
            print("   Continuing anyway...")
        
        # Give it a moment to settle
        await asyncio.sleep(2)
        
        # Generate PDF
        print("🖨️  Generating PDF...")
        await page.pdf(
            path=output_path,
            format='Letter',
            print_background=True,
            prefer_css_page_size=True,
            margin={
                'top': '0',
                'right': '0',
                'bottom': '0',
                'left': '0'
            }
        )
        
        # Verify the file was created
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ SUCCESS! PDF created: {size_mb:.2f} MB")
            await page.close()
            return True
        else:
            print(f"❌ ERROR: PDF not created")
            await page.close()
            return False
            
    except Exception as e:
        print(f"❌ ERROR during export: {e}")
        await page.close()
        return False

async def main():
    """Main export function"""
    print("\n" + "="*60)
    print("🚀 AUTOMATED PDF EXPORT - VISIBLE BROWSER MODE")
    print("="*60)
    
    # Start HTTP server
    httpd = start_server()
    
    try:
        # Launch browser in VISIBLE mode (headless=False)
        async with async_playwright() as p:
            print("🌐 Launching browser (visible mode)...")
            browser = await p.chromium.launch(
                headless=False,  # VISIBLE BROWSER
                args=['--start-maximized']
            )
            
            # Determine which volumes to export
            if len(sys.argv) > 1 and sys.argv[1] == "all":
                volumes_to_export = list(VOLUMES.keys())
            elif len(sys.argv) > 1:
                volumes_to_export = [sys.argv[1]]
            else:
                volumes_to_export = list(VOLUMES.keys())
            
            print(f"\n📚 Exporting {len(volumes_to_export)} volume(s)")
            
            # Export each volume
            success_count = 0
            for i, vol_key in enumerate(volumes_to_export, 1):
                print(f"\n{'▶'*3} Volume {i}/{len(volumes_to_export)} {'◀'*3}")
                success = await export_pdf_with_browser(vol_key, browser)
                if success:
                    success_count += 1
                    print(f"✓ {vol_key} complete")
                else:
                    print(f"✗ {vol_key} failed")
                
                # Small delay between volumes
                if i < len(volumes_to_export):
                    print("\n⏸️  Pausing 3 seconds before next volume...")
                    await asyncio.sleep(3)
            
            # Summary
            print("\n" + "="*60)
            print(f"📊 EXPORT COMPLETE: {success_count}/{len(volumes_to_export)} successful")
            print("="*60)
            
            await browser.close()
            
    finally:
        print("\n🛑 Shutting down HTTP server...")
        httpd.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
