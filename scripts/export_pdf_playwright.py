#!/usr/bin/env python3
"""
Alternative PDF export using Playwright with proper Paged.js support.
Playwright has better headless support for complex JavaScript rendering.
"""

import os
import sys
import asyncio
from playwright.async_api import async_playwright

EDITIONS_DIR = "/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"

VOLUMES = {
    "Vol1_Part1": "archive/Antirevolutionary_Politics_Vol1_Part1.html",
    "Vol1_Part2": "archive/Antirevolutionary_Politics_Vol1_Part2.html",
    "Vol2_Part1": "archive/Antirevolutionary_Politics_Vol2_Part1.html",
    "Vol2_Part2": "archive/Antirevolutionary_Politics_Vol2_Part2.html",
    "Vol3": "Antirevolutionary_Politics_Vol3_Master_Index.html"
}

async def export_pdf(vol_key):
    filename = VOLUMES.get(vol_key)
    if not filename:
        print(f"Error: Unknown volume {vol_key}")
        print(f"Available volumes: {', '.join(VOLUMES.keys())}")
        return False

    output_pdf = filename.replace('.html', '.pdf')
    file_path = os.path.join(EDITIONS_DIR, filename)
    output_path = os.path.join(EDITIONS_DIR, output_pdf)
    
    print(f"\n--- Exporting {vol_key} to PDF ---")
    print(f"Source: {file_path}")
    print(f"Target: {output_path}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the file
        await page.goto(f'file://{file_path}')
        
        # Wait for Paged.js to complete rendering
        # Look for the completion indicator in the HTML
        print("Waiting for Paged.js to render...")
        try:
            await page.wait_for_selector('.pagedjs_done', timeout=300000)  # 5 minutes
            print("✓ Paged.js rendering complete")
        except:
            print("⚠ Timeout waiting for Paged.js (continuing anyway)")
        
        # Generate PDF
        print("Generating PDF...")
        await page.pdf(
            path=output_path,
            format='Letter',
            print_background=True,
            prefer_css_page_size=True
        )
        
        await browser.close()
        
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Success! PDF generated: {output_pdf} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"❌ Error: PDF not created")
            return False

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 export_pdf_playwright.py [Vol1_Part1|Vol1_Part2|Vol2_Part1|Vol2_Part2|Vol3|all]")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == "all":
        for vol_key in VOLUMES:
            success = await export_pdf(vol_key)
            if not success:
                print(f"Failed to export {vol_key}, stopping.")
                break
    else:
        await export_pdf(target)

if __name__ == "__main__":
    asyncio.run(main())
