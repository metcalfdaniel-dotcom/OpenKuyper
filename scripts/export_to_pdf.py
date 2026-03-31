
import os
import subprocess
import time
import sys

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EDITIONS_DIR = "/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"
BASE_URL = "file://" + EDITIONS_DIR

VOLUMES = {
    "Vol1_Part1": "archive/Antirevolutionary_Politics_Vol1_Part1.html",
    "Vol1_Part2": "archive/Antirevolutionary_Politics_Vol1_Part2.html",
    "Vol2_Part1": "archive/Antirevolutionary_Politics_Vol2_Part1.html",
    "Vol2_Part2": "archive/Antirevolutionary_Politics_Vol2_Part2.html",
    "Vol3": "Antirevolutionary_Politics_Vol3_Master_Index.html"
}

def export_pdf(vol_key):
    filename = VOLUMES.get(vol_key)
    if not filename:
        print(f"Error: Unknown volume {vol_key}")
        print(f"Available volumes: {', '.join(VOLUMES.keys())}")
        return

    output_pdf = filename.replace('.html', '.pdf')
    url = f"{BASE_URL}/{filename}"
    
    print(f"--- Exporting {vol_key} to PDF ---")
    print(f"Source: {url}")
    print(f"Target: {output_pdf}")
    
    # We use Google Chrome in headless mode.
    # Note: For Paged.js to work in headless mode, we often need a delay or to tell Chrome to wait.
    # However, Chrome's --print-to-pdf doesn't have a built-in 'wait for JS' flag that works well with Paged.js
    # so we use a virtual time budget which forces Chrome to run the event loop.
    
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",  # Allow local file access for paged.js
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=300000", # Wait up to 5 minutes for Paged.js
        "--no-pdf-header-footer",
        "--enable-logging",
        "--v=1",
        f"--print-to-pdf={os.path.join(EDITIONS_DIR, output_pdf)}",
        url
    ]
    
    try:
        print("Running headless Chrome (this may take 1-5 minutes)...")
        # subprocess.run with capture_output=True captures stdout and stderr
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if the file was actually created
        if os.path.exists(os.path.join(EDITIONS_DIR, output_pdf)):
            print(f"✅ Success! PDF generated: {output_pdf}")
        else:
            print(f"❌ Error: Chrome process exited but {output_pdf} was not found.")
            print("Chrome stderr output:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during PDF generation (Process Exit Code {e.returncode})")
        print("Standard error stream:")
        print(e.stderr)
        print("Standard output stream:")
        print(e.stdout)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    if not os.path.exists(CHROME_PATH):
        print(f"Error: Google Chrome not found at {CHROME_PATH}")
        sys.exit(1)
        
    if len(sys.argv) < 2:
        print("Usage: python3 export_to_pdf.py [Vol1|Vol2|Vol3|all]")
        sys.exit(1)
        
    target = sys.argv[1]
    if target == "all":
        for k in VOLUMES:
            export_pdf(k)
    else:
        export_pdf(target)
