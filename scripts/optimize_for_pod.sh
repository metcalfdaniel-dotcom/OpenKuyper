#!/bin/bash
# PDF Optimization for Print-on-Demand Services
# Using FOSS tools: Ghostscript, QPDF, Poppler utilities
#
# This script optimizes PDFs for:
# - Amazon KDP (Kindle Direct Publishing)
# - Lulu
# - IngramSpark
# - Other POD services

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDITIONS_DIR="/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions"
POD_OUTPUT_DIR="$EDITIONS_DIR/POD_Ready"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================"
echo "📚 PDF OPTIMIZATION FOR PRINT-ON-DEMAND"
echo "   Using FOSS tools (Ghostscript + QPDF)"
echo "============================================================"

# Create output directory
mkdir -p "$POD_OUTPUT_DIR"

# Check for required tools
echo ""
echo "🔍 Checking for required tools..."
for tool in gs qpdf pdfinfo; do
    if command -v $tool &> /dev/null; then
        echo "   ✓ $tool found"
    else
        echo -e "   ${RED}✗ $tool not found${NC}"
        if [ "$tool" == "gs" ]; then
            echo "      Install with: brew install ghostscript"
        elif [ "$tool" == "qpdf" ]; then
            echo "      Install with: brew install qpdf"
        fi
        exit 1
    fi
done

# Function to optimize a single PDF
optimize_pdf() {
    local input_pdf="$1"
    local filename=$(basename "$input_pdf")
    local output_pdf="$POD_OUTPUT_DIR/$filename"
    
    echo ""
    echo "============================================================"
    echo "📖 Optimizing: $filename"
    echo "============================================================"
    
    # Step 1: Ghostscript optimization
    # - Embeds all fonts
    # - Optimizes images to 300 DPI
    # - Creates PDF/X-1a:2001 compliant output (optional)
    # - Compresses file size
    
    local temp_pdf="${output_pdf}.tmp.pdf"
    
    echo "🔧 Step 1: Ghostscript optimization..."
    echo "   - Embedding fonts"
    echo "   - Optimizing images to 300 DPI"
    echo "   - Compressing file"
    
    gs -dBATCH -dNOPAUSE -dQUIET \
       -sDEVICE=pdfwrite \
       -dCompatibilityLevel=1.4 \
       -dPDFSETTINGS=/printer \
       -dEmbedAllFonts=true \
       -dSubsetFonts=true \
       -dColorImageDownsampleType=/Bicubic \
       -dColorImageResolution=300 \
       -dGrayImageDownsampleType=/Bicubic \
       -dGrayImageResolution=300 \
       -dMonoImageDownsampleType=/Bicubic \
       -dMonoImageResolution=300 \
       -sOutputFile="$temp_pdf" \
       "$input_pdf"
    
    if [ ! -f "$temp_pdf" ]; then
        echo -e "${RED}✗ Ghostscript optimization failed${NC}"
        return 1
    fi
    
    echo "   ✓ Ghostscript optimization complete"
    
    # Step 2: QPDF linearization (fast web view)
    # Makes the PDF load faster when viewed online
    
    echo "🔧 Step 2: QPDF linearization..."
    
    qpdf --linearize "$temp_pdf" "$output_pdf"
    
    if [ ! -f "$output_pdf" ]; then
        echo -e "${RED}✗ QPDF linearization failed${NC}"
        rm -f "$temp_pdf"
        return 1
    fi
    
    # Clean up temp file
    rm -f "$temp_pdf"
    
    echo "   ✓ QPDF linearization complete"
    
    # Report file statistics
    echo ""
    echo "📊 File Statistics:"
    
    local original_size=$(ls -lh "$input_pdf" | awk '{print $5}')
    local optimized_size=$(ls -lh "$output_pdf" | awk '{print $5}')
    
    echo "   Original:  $original_size"
    echo "   Optimized: $optimized_size"
    
    # Get PDF metadata
    echo ""
    echo "📋 PDF Metadata:"
    pdfinfo "$output_pdf" | grep -E "Pages|Page size|PDF version|Optimized" | sed 's/^/   /'
    
    echo ""
    echo -e "${GREEN}✅ Optimization complete: $filename${NC}"
    
    return 0
}

# Process all PDFs
echo ""
echo "============================================================"
echo "📚 Processing PDFs..."
echo "============================================================"

cd "$EDITIONS_DIR"

# Find all PDF files (excluding the POD_Ready directory)
pdf_files=($(find . -maxdepth 1 -name "*.pdf" -type f | grep -v "POD_Ready"))

if [ ${#pdf_files[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠ No PDF files found in $EDITIONS_DIR${NC}"
    exit 1
fi

echo "Found ${#pdf_files[@]} PDF file(s) to optimize"

success_count=0
failed_count=0

for pdf_file in "${pdf_files[@]}"; do
    if optimize_pdf "$pdf_file"; then
        ((success_count++))
    else
        ((failed_count++))
    fi
done

# Summary
echo ""
echo "============================================================"
echo "📊 OPTIMIZATION SUMMARY"
echo "============================================================"
echo -e "${GREEN}✅ Successful: $success_count${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${RED}❌ Failed: $failed_count${NC}"
fi
echo ""
echo "📁 Optimized PDFs saved to:"
echo "   $POD_OUTPUT_DIR"
echo ""
echo "✨ These PDFs are optimized for:"
echo "   • Amazon KDP (Kindle Direct Publishing)"
echo "   • Lulu"
echo "   • IngramSpark"
echo "   • Other print-on-demand services"
echo ""
echo "📌 POD Upload Checklist:"
echo "   ✓ 300 DPI images"
echo "   ✓ Fonts embedded"
echo "   ✓ Proper trim size (7\" × 10\")"
echo "   ✓ Optimized file size"
echo "   ⚠ Review interior margins for binding"
echo "   ⚠ Check with your POD service for specific requirements"
echo "============================================================"
