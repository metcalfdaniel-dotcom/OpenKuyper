#!/usr/bin/env node
/**
 * FULLY AUTOMATED PDF EXPORT using Puppeteer
 * This script runs completely hands-free and can run overnight.
 * 
 * It uses the simplified *_PRINT.html files (no Paged.js) and
 * generates PDFs using Chromium's native print engine.
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const EDITIONS_DIR = '/Users/danielmetcalf/PARA/1. Projects/Kuyper Translation/01_Editions';

const VOLUMES = {
    'Vol1_Part1': 'archive/Antirevolutionary_Politics_Vol1_Part1_PRINT.html',
    'Vol1_Part2': 'archive/Antirevolutionary_Politics_Vol1_Part2_PRINT.html',
    'Vol2_Part1': 'archive/Antirevolutionary_Politics_Vol2_Part1_PRINT.html',
    'Vol2_Part2': 'archive/Antirevolutionary_Politics_Vol2_Part2_PRINT.html',
    'Vol3': 'Antirevolutionary_Politics_Vol3_Master_Index_PRINT.html'
};

async function exportPDF(page, volKey, filename) {
    const inputPath = path.join(EDITIONS_DIR, filename);
    const outputPDF = filename.replace('_PRINT.html', '.pdf');
    const outputPath = path.join(EDITIONS_DIR, outputPDF);

    console.log('\n' + '='.repeat(60));
    console.log(`📖 Exporting ${volKey}`);
    console.log(`   Source: ${filename}`);
    console.log(`   Target: ${outputPDF}`);
    console.log('='.repeat(60));

    if (!fs.existsSync(inputPath)) {
        console.error(`❌ Error: Input file not found: ${inputPath}`);
        return false;
    }

    try {
        // Navigate to the HTML file
        const fileUrl = `file://${inputPath}`;
        console.log('🔗 Loading page...');
        await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 60000 });

        console.log('✓ Page loaded');

        // Give it a moment to render
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log('🖨️  Generating PDF...');

        // Generate PDF with proper settings
        await page.pdf({
            path: outputPath,
            format: 'Letter',
            printBackground: true,
            preferCSSPageSize: true,
            margin: {
                top: '0',
                right: '0',
                bottom: '0',
                left: '0'
            }
        });

        // Verify the file was created
        if (fs.existsSync(outputPath)) {
            const stats = fs.statSync(outputPath);
            const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
            console.log(`✅ SUCCESS! PDF created: ${sizeMB} MB`);
            console.log(`   📁 ${outputPath}`);
            return true;
        } else {
            console.error(`❌ ERROR: PDF not created`);
            return false;
        }

    } catch (error) {
        console.error(`❌ ERROR during export: ${error.message}`);
        return false;
    }
}

async function main() {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 AUTOMATED PDF EXPORT - Puppeteer');
    console.log('   100% hands-free, runs unattended');
    console.log('='.repeat(60));

    let browser;
    try {
        console.log('\n🌐 Launching browser...');
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        console.log('✓ Browser ready\n');

        const volumeKeys = Object.keys(VOLUMES);
        console.log(`📚 Exporting ${volumeKeys.length} volumes\n`);

        let successCount = 0;
        const failedVolumes = [];

        for (let i = 0; i < volumeKeys.length; i++) {
            const volKey = volumeKeys[i];
            const filename = VOLUMES[volKey];

            console.log(`${'▶'.repeat(3)} Volume ${i + 1}/${volumeKeys.length} ${'◀'.repeat(3)}`);

            const success = await exportPDF(page, volKey, filename);

            if (success) {
                successCount++;
                console.log(`✓ ${volKey} complete`);
            } else {
                failedVolumes.push(volKey);
                console.log(`✗ ${volKey} failed`);
            }

            // Small delay between volumes
            if (i < volumeKeys.length - 1) {
                console.log('\n⏸️  Pausing 2 seconds...');
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        // Summary
        console.log('\n' + '='.repeat(60));
        console.log('📊 EXPORT COMPLETE');
        console.log(`   ✅ Successful: ${successCount}/${volumeKeys.length}`);
        if (failedVolumes.length > 0) {
            console.log(`   ❌ Failed: ${failedVolumes.join(', ')}`);
        }
        console.log('='.repeat(60));

    } catch (error) {
        console.error(`\n❌ Fatal error: ${error.message}`);
        process.exit(1);
    } finally {
        if (browser) {
            console.log('\n🛑 Closing browser...');
            await browser.close();
        }
    }
}

main();
