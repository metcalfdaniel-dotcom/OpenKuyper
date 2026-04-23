package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// ─── Data Structures ─────────────────────────────────────────────────────────

type ChapterInfo struct {
	Volume    int    `json:"volume"`
	Number    int    `json:"number"`
	Slug      string `json:"slug"`
	Title     string `json:"title"`
	StartPage int    `json:"start_page"`
	EndPage   int    `json:"end_page"`
}

type ChapterMap struct {
	Volume   int           `json:"volume"`
	Chapters []ChapterInfo `json:"chapters"`
}

type AlignmentReport struct {
	Chapter          string   `json:"chapter"`
	DutchParagraphs  int      `json:"dutch_paragraphs"`
	EngParagraphs    int      `json:"eng_paragraphs"`
	DutchSections    int      `json:"dutch_sections"`
	EngSections      int      `json:"eng_sections"`
	ParagraphRatio   float64  `json:"paragraph_ratio"`
	MissingSections  []string `json:"missing_sections"`
	ExtraSections    []string `json:"extra_sections"`
	PageMarkersDutch int      `json:"page_markers_dutch"`
	PageMarkersEng   int      `json:"page_markers_eng"`
	Pass             bool     `json:"pass"`
	Issues           []string `json:"issues"`
}

// ─── Chapter Definitions ─────────────────────────────────────────────────────

var vol1Chapters = []ChapterInfo{
	{Volume: 1, Number: 1, Slug: "introduction", Title: "Introduction", StartPage: 11, EndPage: 36},
	{Volume: 1, Number: 2, Slug: "concept-of-state", Title: "The Concept of the State", StartPage: 37, EndPage: 50},
	{Volume: 1, Number: 3, Slug: "essence-of-state", Title: "The Essence of the State", StartPage: 51, EndPage: 70},
	{Volume: 1, Number: 4, Slug: "transition-modern-era", Title: "Transition to the Modern Era", StartPage: 71, EndPage: 85},
	{Volume: 1, Number: 5, Slug: "constitution", Title: "The Constitution", StartPage: 86, EndPage: 110},
	{Volume: 1, Number: 6, Slug: "the-land", Title: "The Land", StartPage: 111, EndPage: 130},
	{Volume: 1, Number: 7, Slug: "supreme-authority", Title: "The Supreme Authority", StartPage: 131, EndPage: 155},
	{Volume: 1, Number: 8, Slug: "sovereignty", Title: "The Sovereignty", StartPage: 156, EndPage: 180},
	{Volume: 1, Number: 9, Slug: "purpose-of-state", Title: "The Purpose of the State", StartPage: 181, EndPage: 0},
}

var vol2Chapters = []ChapterInfo{
	{Volume: 2, Number: 1, Slug: "introduction", Title: "Introduction", StartPage: 1, EndPage: 20},
	{Volume: 2, Number: 2, Slug: "suffrage", Title: "Suffrage", StartPage: 21, EndPage: 40},
	{Volume: 2, Number: 3, Slug: "representation", Title: "Representation", StartPage: 41, EndPage: 55},
	{Volume: 2, Number: 4, Slug: "council-state", Title: "Council of State and Ministers", StartPage: 56, EndPage: 75},
	{Volume: 2, Number: 5, Slug: "second-chamber", Title: "The Second Chamber", StartPage: 76, EndPage: 95},
	{Volume: 2, Number: 6, Slug: "accounting-office", Title: "General Accounting Office", StartPage: 96, EndPage: 110},
	{Volume: 2, Number: 7, Slug: "first-chamber", Title: "The First Chamber", StartPage: 111, EndPage: 125},
	{Volume: 2, Number: 8, Slug: "provinces", Title: "Administration of the Provinces", StartPage: 126, EndPage: 145},
	{Volume: 2, Number: 9, Slug: "municipalities", Title: "Municipal Government", StartPage: 146, EndPage: 165},
	{Volume: 2, Number: 10, Slug: "army-navy", Title: "Army and Navy", StartPage: 166, EndPage: 185},
	{Volume: 2, Number: 11, Slug: "colonies", Title: "The Colonies", StartPage: 186, EndPage: 205},
	{Volume: 2, Number: 12, Slug: "foreign-affairs", Title: "Foreign Affairs", StartPage: 206, EndPage: 220},
	{Volume: 2, Number: 13, Slug: "justice", Title: "Justice", StartPage: 221, EndPage: 240},
	{Volume: 2, Number: 14, Slug: "finances", Title: "The Finances", StartPage: 241, EndPage: 260},
	{Volume: 2, Number: 15, Slug: "public-propriety", Title: "The Public Propriety", StartPage: 261, EndPage: 275},
	{Volume: 2, Number: 16, Slug: "public-health", Title: "Care for Public Health", StartPage: 276, EndPage: 295},
	{Volume: 2, Number: 17, Slug: "public-works", Title: "Public Works", StartPage: 296, EndPage: 310},
	{Volume: 2, Number: 18, Slug: "poor-relief", Title: "Poor Relief", StartPage: 311, EndPage: 325},
	{Volume: 2, Number: 19, Slug: "church-state", Title: "Church and State", StartPage: 326, EndPage: 350},
	{Volume: 2, Number: 20, Slug: "education", Title: "Education", StartPage: 351, EndPage: 370},
	{Volume: 2, Number: 21, Slug: "labor", Title: "Labor", StartPage: 371, EndPage: 390},
	{Volume: 2, Number: 22, Slug: "party-policy", Title: "Party Policy at the Ballot Box", StartPage: 391, EndPage: 0},
}

// ─── Forbidden Terms ─────────────────────────────────────────────────────────

var forbiddenTerms = []string{
	"values", "lifestyle", "social construct", "mindset",
	"narrative", "identity politics", "social justice",
}

var preferredTerms = map[string]string{
	"worldview": "life-system / life-and-world view",
	"values":    "principles / convictions",
}

// ─── Main ────────────────────────────────────────────────────────────────────

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(0)
	}

	switch os.Args[1] {
	case "extract":
		cmdExtract(os.Args[2:])
	case "align":
		cmdAlign(os.Args[2:])
	case "quality":
		cmdQuality(os.Args[2:])
	case "substack":
		cmdSubstack(os.Args[2:])
	case "assemble":
		cmdAssemble(os.Args[2:])
	case "help", "--help", "-h":
		printUsage()
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n\n", os.Args[1])
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println(`Kuyper Translation Pipeline

Usage: pipeline <command> [arguments]

Commands:
  extract <volume>              Extract chapters from FULL.md into manuscript/
  align <chapter-dir>           Check Dutch/English alignment for a chapter
  quality <chapter-dir>         Run quality gate on a chapter
  substack <chapter-dir>        Export a chapter to Substack format
  assemble <volume>             Assemble all refined chapters into a volume

Examples:
  pipeline extract 1
  pipeline align manuscript/volume_1/ch01-introduction
  pipeline quality manuscript/volume_1/ch01-introduction
  pipeline substack manuscript/volume_1/ch01-introduction
  pipeline assemble 1`)
}

// ─── Command: extract ────────────────────────────────────────────────────────

func cmdExtract(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: pipeline extract <volume>")
		os.Exit(1)
	}

	volNum := 0
	fmt.Sscanf(args[0], "%d", &volNum)
	if volNum < 1 || volNum > 2 {
		fmt.Fprintf(os.Stderr, "Error: volume must be 1 or 2\n")
		os.Exit(1)
	}

	baseDir := "."
	dutchFile := filepath.Join(baseDir, "editions", fmt.Sprintf("Kuyper_Antirevolutionary_Politics_Vol%d_Dutch.md", volNum))
	englishFile := filepath.Join(baseDir, "editions", fmt.Sprintf("Kuyper_Antirevolutionary_Politics_Vol%d_FULL.md", volNum))

	for _, f := range []string{dutchFile, englishFile} {
		if _, err := os.Stat(f); os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "Error: source file not found: %s\n", f)
			os.Exit(1)
		}
	}

	dutchContent, _ := os.ReadFile(dutchFile)
	englishContent, _ := os.ReadFile(englishFile)

	var chapters []ChapterInfo
	if volNum == 1 {
		chapters = vol1Chapters
	} else {
		chapters = vol2Chapters
	}

	manuscriptDir := filepath.Join(baseDir, "manuscript", fmt.Sprintf("volume_%d", volNum))
	os.MkdirAll(manuscriptDir, 0755)

	extracted := 0
	for _, ch := range chapters {
		chDir := filepath.Join(manuscriptDir, fmt.Sprintf("ch%02d-%s", ch.Number, ch.Slug))
		os.MkdirAll(chDir, 0755)

		dutchChapter := extractByPage(string(dutchContent), ch.StartPage, ch.EndPage)
		engChapter := extractByPage(string(englishContent), ch.StartPage, ch.EndPage)

		// Write dutch_source.md
		dutchPath := filepath.Join(chDir, "dutch_source.md")
		if _, err := os.Stat(dutchPath); os.IsNotExist(err) {
			os.WriteFile(dutchPath, []byte(dutchChapter), 0644)
			fmt.Printf("  ✓ %s/dutch_source.md (%d bytes)\n", chDir, len(dutchChapter))
		} else {
			fmt.Printf("  ⊘ %s/dutch_source.md (exists, skipping)\n", chDir)
		}

		// Write english_draft.md
		draftPath := filepath.Join(chDir, "english_draft.md")
		if _, err := os.Stat(draftPath); os.IsNotExist(err) {
			os.WriteFile(draftPath, []byte(engChapter), 0644)
			fmt.Printf("  ✓ %s/english_draft.md (%d bytes)\n", chDir, len(engChapter))
		} else {
			fmt.Printf("  ⊘ %s/english_draft.md (exists, skipping)\n", chDir)
		}

		// Create english_refined.md from draft if missing
		refinedPath := filepath.Join(chDir, "english_refined.md")
		if _, err := os.Stat(refinedPath); os.IsNotExist(err) {
			os.WriteFile(refinedPath, []byte(engChapter), 0644)
		}

		extracted++
	}

	// Write chapter map
	chapterMap := ChapterMap{Volume: volNum, Chapters: chapters}
	mapPath := filepath.Join(baseDir, "pipeline", fmt.Sprintf("chapter_map_vol%d.json", volNum))
	mapJSON, _ := json.MarshalIndent(chapterMap, "", "  ")
	os.WriteFile(mapPath, mapJSON, 0644)

	fmt.Printf("\n✓ Chapter map: %s\n", mapPath)
	fmt.Printf("✓ Extracted %d chapters for Volume %d\n", extracted, volNum)
}

func extractByPage(content string, startPage, endPage int) string {
	lines := strings.Split(content, "\n")
	var result []string
	inChapter := false
	pageRe := regexp.MustCompile(`—- Page (\d+) —-`)

	for _, line := range lines {
		matches := pageRe.FindStringSubmatch(line)
		if len(matches) > 1 {
			var pageNum int
			fmt.Sscanf(matches[1], "%d", &pageNum)
			if pageNum == startPage {
				inChapter = true
			}
			if inChapter && endPage > 0 && pageNum > endPage {
				break
			}
		}
		if inChapter {
			result = append(result, line)
		}
	}
	return strings.Join(result, "\n")
}

// ─── Command: align ──────────────────────────────────────────────────────────

func cmdAlign(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: pipeline align <chapter-dir>")
		os.Exit(1)
	}

	chapterDir := args[0]
	dutchPath := filepath.Join(chapterDir, "dutch_source.md")
	engPath := filepath.Join(chapterDir, "english_draft.md")

	for _, f := range []string{dutchPath, engPath} {
		if _, err := os.Stat(f); os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "Error: file not found: %s\n", f)
			os.Exit(1)
		}
	}

	dutchContent, _ := os.ReadFile(dutchPath)
	engContent, _ := os.ReadFile(engPath)

	report := analyzeAlignment(chapterDir, string(dutchContent), string(engContent))
	printAlignmentReport(report)

	// Write report file
	reportPath := filepath.Join(chapterDir, "alignment_report.md")
	writeAlignmentReport(reportPath, report)
	fmt.Printf("\n📄 Report: %s\n", reportPath)

	if !report.Pass {
		os.Exit(1)
	}
}

func analyzeAlignment(chapterDir, dutch, english string) AlignmentReport {
	report := AlignmentReport{Chapter: filepath.Base(chapterDir)}

	report.DutchParagraphs = countParagraphs(dutch)
	report.EngParagraphs = countParagraphs(english)
	if report.DutchParagraphs > 0 {
		report.ParagraphRatio = float64(report.EngParagraphs) / float64(report.DutchParagraphs)
	}

	dutchSections := extractSections(dutch)
	engSections := extractSections(english)
	report.DutchSections = len(dutchSections)
	report.EngSections = len(engSections)

	dutchSet := make(map[string]bool)
	for _, s := range dutchSections {
		dutchSet[s] = true
	}
	engSet := make(map[string]bool)
	for _, s := range engSections {
		engSet[s] = true
	}

	for _, s := range dutchSections {
		if !engSet[s] {
			report.MissingSections = append(report.MissingSections, s)
		}
	}
	for _, s := range engSections {
		if !dutchSet[s] {
			report.ExtraSections = append(report.ExtraSections, s)
		}
	}

	pageRe := regexp.MustCompile(`—- Page \d+ —-`)
	report.PageMarkersDutch = len(pageRe.FindAllString(dutch, -1))
	report.PageMarkersEng = len(pageRe.FindAllString(english, -1))

	if report.ParagraphRatio < 0.3 {
		report.Issues = append(report.Issues, fmt.Sprintf("English is only %.0f%% of Dutch — possible major omissions", report.ParagraphRatio*100))
	}
	if report.ParagraphRatio > 3.0 {
		report.Issues = append(report.Issues, fmt.Sprintf("English is %.0f%% of Dutch — possible duplication", report.ParagraphRatio*100))
	}
	if len(report.MissingSections) > 0 {
		report.Issues = append(report.Issues, fmt.Sprintf("%d section(s) missing in English", len(report.MissingSections)))
	}
	if report.DutchSections > 0 && report.EngSections == 0 {
		report.Issues = append(report.Issues, "No sections found in English — extraction may have failed")
	}

	report.Pass = len(report.Issues) == 0
	return report
}

func countParagraphs(content string) int {
	// Count actual paragraphs: blocks of non-empty text separated by blank lines
	// This handles both line-broken text (Dutch) and flowing text (English)
	blocks := strings.Split(content, "\n\n")
	count := 0
	pageRe := regexp.MustCompile(`^—- Page \d+ —-$`)
	sectionRe := regexp.MustCompile(`^§\s*\d+`)
	headerRe := regexp.MustCompile(`^#{1,6}\s`)

	for _, block := range blocks {
		block = strings.TrimSpace(block)
		if block == "" {
			continue
		}
		// Skip blocks that are only page markers or headers
		lines := strings.Split(block, "\n")
		hasContent := false
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" || pageRe.MatchString(line) || sectionRe.MatchString(line) || headerRe.MatchString(line) {
				continue
			}
			hasContent = true
			break
		}
		if hasContent {
			count++
		}
	}
	return count
}

func extractSections(content string) []string {
	sectionRe := regexp.MustCompile(`§\s*(\d+)`)
	matches := sectionRe.FindAllStringSubmatch(content, -1)
	var sections []string
	seen := make(map[string]bool)
	for _, m := range matches {
		if len(m) > 1 && !seen[m[1]] {
			sections = append(sections, m[1])
			seen[m[1]] = true
		}
	}
	return sections
}

func printAlignmentReport(r AlignmentReport) {
	fmt.Printf("\n=== Alignment Report: %s ===\n\n", r.Chapter)
	fmt.Printf("Paragraphs:  Dutch=%d  English=%d  Ratio=%.1f%%\n", r.DutchParagraphs, r.EngParagraphs, r.ParagraphRatio*100)
	fmt.Printf("Sections:    Dutch=%d  English=%d\n", r.DutchSections, r.EngSections)
	fmt.Printf("Page markers: Dutch=%d  English=%d\n", r.PageMarkersDutch, r.PageMarkersEng)

	if len(r.MissingSections) > 0 {
		fmt.Printf("\n⚠️  Missing English sections: %s\n", strings.Join(r.MissingSections, ", "))
	}
	if len(r.ExtraSections) > 0 {
		fmt.Printf("\n⚠️  Extra English sections: %s\n", strings.Join(r.ExtraSections, ", "))
	}

	fmt.Printf("\n")
	if r.Pass {
		fmt.Println("✅ PASS")
	} else {
		fmt.Println("❌ FAIL:")
		for _, issue := range r.Issues {
			fmt.Printf("  • %s\n", issue)
		}
	}
}

func writeAlignmentReport(path string, r AlignmentReport) {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("# Alignment Report: %s\n\n", r.Chapter))
	sb.WriteString(fmt.Sprintf("- **Dutch paragraphs:** %d\n", r.DutchParagraphs))
	sb.WriteString(fmt.Sprintf("- **English paragraphs:** %d\n", r.EngParagraphs))
	sb.WriteString(fmt.Sprintf("- **Paragraph ratio:** %.1f%%\n", r.ParagraphRatio*100))
	sb.WriteString(fmt.Sprintf("- **Dutch sections:** %d\n", r.DutchSections))
	sb.WriteString(fmt.Sprintf("- **English sections:** %d\n", r.EngSections))
	sb.WriteString(fmt.Sprintf("- **Status:** %s\n\n", map[bool]string{true: "✅ PASS", false: "❌ FAIL"}[r.Pass]))

	if len(r.MissingSections) > 0 {
		sb.WriteString("## Missing English Sections\n\n")
		for _, s := range r.MissingSections {
			sb.WriteString(fmt.Sprintf("- § %s\n", s))
		}
		sb.WriteString("\n")
	}
	if len(r.ExtraSections) > 0 {
		sb.WriteString("## Extra English Sections\n\n")
		for _, s := range r.ExtraSections {
			sb.WriteString(fmt.Sprintf("- § %s\n", s))
		}
		sb.WriteString("\n")
	}
	if len(r.Issues) > 0 {
		sb.WriteString("## Issues\n\n")
		for _, issue := range r.Issues {
			sb.WriteString(fmt.Sprintf("- %s\n", issue))
		}
	}
	os.WriteFile(path, []byte(sb.String()), 0644)
}

// ─── Command: quality ────────────────────────────────────────────────────────

func cmdQuality(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: pipeline quality <chapter-dir>")
		os.Exit(1)
	}

	chapterDir := args[0]
	engPath := filepath.Join(chapterDir, "english_refined.md")
	dutchPath := filepath.Join(chapterDir, "dutch_source.md")

	if _, err := os.Stat(engPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "Error: english_refined.md not found in %s\n", chapterDir)
		os.Exit(1)
	}

	engContent, _ := os.ReadFile(engPath)
	content := string(engContent)
	chapterName := filepath.Base(chapterDir)

	var issues []string

	// 1. Alignment check (if dutch_source exists)
	if _, err := os.Stat(dutchPath); err == nil {
		dutchContent, _ := os.ReadFile(dutchPath)
		r := analyzeAlignment(chapterDir, string(dutchContent), content)
		// Only flag alignment issues for section mismatches, not paragraph ratio
		// (refined version may have different paragraph structure)
		if len(r.MissingSections) > 0 {
			issues = append(issues, fmt.Sprintf("%d section(s) missing in English", len(r.MissingSections)))
		}
	}

	// 2. Terminology consistency
	termIssues := checkTerminology(content)
	issues = append(issues, termIssues...)

	// 3. Forbidden terms
	forbiddenIssues := checkForbiddenTerms(content)
	issues = append(issues, forbiddenIssues...)

	// 4. Section header integrity
	sectionRe := regexp.MustCompile(`§\s*\d+`)
	sections := sectionRe.FindAllString(content, -1)
	if len(sections) == 0 {
		issues = append(issues, "No section headers (§) found — chapter may be incomplete")
	}

	// 5. Minimum length
	if len(content) < 500 {
		issues = append(issues, fmt.Sprintf("Chapter is only %d bytes — suspiciously short", len(content)))
	}

	// 6. Page markers (warning, not fail — they can be stripped later)
	pageRe := regexp.MustCompile(`—- Page \d+ —-`)
	pageMarkers := pageRe.FindAllString(content, -1)
	if len(pageMarkers) > 0 {
		fmt.Printf("  ⚠️  %d page markers present (will be stripped during Substack export)\n", len(pageMarkers))
	}

	// Print report
	fmt.Printf("\n=== Quality Gate: %s ===\n\n", chapterName)
	fmt.Printf("Sections found: %d\n", len(sections))
	fmt.Printf("Content length: %d bytes\n", len(content))

	if len(issues) == 0 {
		fmt.Println("\n✅ PASS — Chapter is ready for publication")
	} else {
		fmt.Printf("\n❌ FAIL — %d issue(s):\n", len(issues))
		for _, issue := range issues {
			fmt.Printf("  • %s\n", issue)
		}
	}

	// Write report
	reportPath := filepath.Join(chapterDir, "quality_report.md")
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("# Quality Gate Report: %s\n\n", chapterName))
	sb.WriteString(fmt.Sprintf("- **Sections:** %d\n", len(sections)))
	sb.WriteString(fmt.Sprintf("- **Content length:** %d bytes\n", len(content)))
	sb.WriteString(fmt.Sprintf("- **Status:** %s\n\n", map[bool]string{true: "✅ PASS", false: "❌ FAIL"}[len(issues) == 0]))
	if len(issues) > 0 {
		sb.WriteString("## Issues\n\n")
		for _, issue := range issues {
			sb.WriteString(fmt.Sprintf("- %s\n", issue))
		}
	}
	os.WriteFile(reportPath, []byte(sb.String()), 0644)
	fmt.Printf("\n📄 Report: %s\n", reportPath)

	if len(issues) > 0 {
		os.Exit(1)
	}
}

func checkTerminology(content string) []string {
	var issues []string

	// Check for lowercase variants of required terms
	requiredTerms := map[string][]string{
		"Sphere Sovereignty": {"sphere sovereignty", "Sphere sovereignty"},
		"Common Grace":       {"common grace", "Common grace"},
		"The Antithesis":     {"the antithesis"},
		"Ordinances of God":  {"ordinances of god", "Ordinances of god"},
		"The Magistrate":     {"the magistrate"},
		"Palingenesis":       {"palingenesis"},
	}

	for correct, variants := range requiredTerms {
		for _, variant := range variants {
			pattern := regexp.MustCompile(`(?i)\b` + regexp.QuoteMeta(variant) + `\b`)
			if pattern.MatchString(content) {
				issues = append(issues, fmt.Sprintf("'%s' found — should be '%s'", variant, correct))
			}
		}
	}

	return issues
}

func checkForbiddenTerms(content string) []string {
	var issues []string
	contentLower := strings.ToLower(content)

	for _, term := range forbiddenTerms {
		if strings.Contains(contentLower, term) {
			alt := preferredTerms[term]
			msg := fmt.Sprintf("Forbidden term '%s' found", term)
			if alt != "" {
				msg += fmt.Sprintf(" — use '%s' instead", alt)
			}
			issues = append(issues, msg)
		}
	}

	return issues
}

// ─── Command: substack ───────────────────────────────────────────────────────

func cmdSubstack(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: pipeline substack <chapter-dir>")
		os.Exit(1)
	}

	chapterDir := args[0]
	engPath := filepath.Join(chapterDir, "english_refined.md")

	if _, err := os.Stat(engPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "Error: english_refined.md not found in %s\n", chapterDir)
		os.Exit(1)
	}

	content, _ := os.ReadFile(engPath)
	chapterName := filepath.Base(chapterDir)

	// Parse chapter metadata from directory name
	// e.g., "ch01-introduction" → vol from parent, number=1, slug="introduction"
	parentDir := filepath.Base(filepath.Dir(chapterDir)) // "volume_1" or "volume_2"
	volNum := 1
	if strings.Contains(parentDir, "volume_2") {
		volNum = 2
	}

	chapterNum := 0
	slug := chapterName
	fmt.Sscanf(chapterName, "ch%02d-%s", &chapterNum, &slug)

	// Find chapter title from chapter map
	title := chapterName
	mapPath := filepath.Join("pipeline", fmt.Sprintf("chapter_map_vol%d.json", volNum))
	if mapData, err := os.ReadFile(mapPath); err == nil {
		var cm ChapterMap
		if err := json.Unmarshal(mapData, &cm); err == nil {
			for _, ch := range cm.Chapters {
				if ch.Number == chapterNum {
					title = ch.Title
					break
				}
			}
		}
	}

	// Process content for Substack
	substackContent := formatForSubstack(string(content), volNum, chapterNum, title)

	// Create substack output directory
	substackDir := filepath.Join("substack")
	os.MkdirAll(substackDir, 0755)

	// Write Substack markdown
	outFile := filepath.Join(substackDir, fmt.Sprintf("vol%d-ch%02d-%s.md", volNum, chapterNum, slug))
	os.WriteFile(outFile, []byte(substackContent), 0644)
	fmt.Printf("✓ Substack export: %s\n", outFile)

	// Write preview HTML
	previewFile := filepath.Join(substackDir, fmt.Sprintf("vol%d-ch%02d-%s-preview.html", volNum, chapterNum, slug))
	previewHTML := generatePreviewHTML(substackContent, volNum, chapterNum, title)
	os.WriteFile(previewFile, []byte(previewHTML), 0644)
	fmt.Printf("✓ Preview HTML: %s\n", previewFile)

	// Write checklist
	checklistFile := filepath.Join(substackDir, fmt.Sprintf("vol%d-ch%02d-%s-checklist.md", volNum, chapterNum, slug))
	checklist := generateChecklist(volNum, chapterNum, title, slug)
	os.WriteFile(checklistFile, []byte(checklist), 0644)
	fmt.Printf("✓ Checklist: %s\n", checklistFile)
}

func formatForSubstack(content string, volNum, chapterNum int, title string) string {
	lines := strings.Split(content, "\n")
	var result []string

	// Add series header
	result = append(result, fmt.Sprintf("*Antirevolutionary Politics, Vol. %d, Chapter %d*", volNum, chapterNum))
	result = append(result, "")

	pageRe := regexp.MustCompile(`^—- Page \d+ —-$`)
	sectionRe := regexp.MustCompile(`^§\s*(\d+)\.\s*(.*)`)

	for _, line := range lines {
		// Strip page markers
		if pageRe.MatchString(line) {
			continue
		}

		// Convert § headers to H3
		if matches := sectionRe.FindStringSubmatch(line); len(matches) > 0 {
			result = append(result, fmt.Sprintf("### § %s. %s", matches[1], matches[2]))
			continue
		}

		// Convert chapter headers to H2
		chapRe := regexp.MustCompile(`^(?:CHAPTER|Chapter)\s+([IVXLCDM]+)\.?\s*(.*)`)
		if matches := chapRe.FindStringSubmatch(line); len(matches) > 0 {
			result = append(result, fmt.Sprintf("## Chapter %s: %s", matches[1], matches[2]))
			continue
		}

		result = append(result, line)
	}

	return strings.Join(result, "\n")
}

func generatePreviewHTML(content string, volNum, chapterNum int, title string) string {
	// Convert markdown to simple HTML for preview
	html := strings.ReplaceAll(content, "&", "&amp;")
	html = strings.ReplaceAll(html, "<", "&lt;")
	html = strings.ReplaceAll(html, ">", "&gt;")

	// Simple markdown → HTML
	lines := strings.Split(html, "\n")
	var htmlLines []string
	htmlLines = append(htmlLines, "<!DOCTYPE html><html><head><meta charset='utf-8'>")
	htmlLines = append(htmlLines, "<style>")
	htmlLines = append(htmlLines, "body { font-family: Georgia, serif; max-width: 680px; margin: 40px auto; line-height: 1.7; color: #333; }")
	htmlLines = append(htmlLines, "h2 { font-family: system-ui; border-bottom: 2px solid #8b2222; padding-bottom: 8px; margin-top: 40px; }")
	htmlLines = append(htmlLines, "h3 { font-family: system-ui; margin-top: 30px; color: #555; }")
	htmlLines = append(htmlLines, "em { color: #8b2222; }")
	htmlLines = append(htmlLines, "blockquote { border-left: 3px solid #ccc; padding-left: 16px; margin-left: 0; color: #666; font-style: italic; }")
	htmlLines = append(htmlLines, "</style></head><body>")
	htmlLines = append(htmlLines, fmt.Sprintf("<h1>Chapter %d: %s</h1>", chapterNum, title))

	inBlockquote := false
	for _, line := range lines {
		if strings.HasPrefix(line, "### ") {
			if inBlockquote {
				htmlLines = append(htmlLines, "</blockquote>")
				inBlockquote = false
			}
			htmlLines = append(htmlLines, fmt.Sprintf("<h3>%s</h3>", line[4:]))
		} else if strings.HasPrefix(line, "## ") {
			if inBlockquote {
				htmlLines = append(htmlLines, "</blockquote>")
				inBlockquote = false
			}
			htmlLines = append(htmlLines, fmt.Sprintf("<h2>%s</h2>", line[3:]))
		} else if strings.HasPrefix(line, "*") && strings.HasSuffix(line, "*") {
			htmlLines = append(htmlLines, fmt.Sprintf("<p><em>%s</em></p>", line[1:len(line)-1]))
		} else if strings.HasPrefix(line, "> ") {
			if !inBlockquote {
				htmlLines = append(htmlLines, "<blockquote>")
				inBlockquote = true
			}
			htmlLines = append(htmlLines, line[2:])
		} else if line == "" {
			if inBlockquote {
				htmlLines = append(htmlLines, "</blockquote>")
				inBlockquote = false
			}
		} else {
			if inBlockquote {
				htmlLines = append(htmlLines, "</blockquote>")
				inBlockquote = false
			}
			htmlLines = append(htmlLines, fmt.Sprintf("<p>%s</p>", line))
		}
	}

	htmlLines = append(htmlLines, "</body></html>")
	return strings.Join(htmlLines, "\n")
}

func generateChecklist(volNum, chapterNum int, title, slug string) string {
	return fmt.Sprintf(`# Publishing Checklist: Vol %d, Ch %02d — %s

## Pre-Publication
- [ ] Quality gate passed (run: pipeline quality manuscript/volume_%d/ch%02d-%s)
- [ ] Alignment check passed (run: pipeline align manuscript/volume_%d/ch%02d-%s)
- [ ] Human review completed
- [ ] Substack formatting verified (open: substack/vol%d-ch%02d-%s-preview.html)
- [ ] Opening hook compelling
- [ ] Theological terminology verified against GLOSSARY.md

## Publication
- [ ] Copy substack/vol%d-ch%02d-%s.md into Substack editor
- [ ] Set title: "Kuyper on %s"
- [ ] Set subtitle: "Antirevolutionary Politics, Vol. %d, Chapter %d"
- [ ] Add tags: abraham-kuyper, neo-calvinism, political-theology, sphere-sovereignty, reformed
- [ ] Preview in Substack
- [ ] Publish

## Post-Publication
- [ ] Record Substack URL: ________________
- [ ] Share on social media
- [ ] Update review/PROGRESS.md
- [ ] Cross-reference with sources.neocalvinism.org
`, volNum, chapterNum, title, volNum, chapterNum, slug, volNum, chapterNum, slug, volNum, chapterNum, slug, volNum, chapterNum, slug, volNum, chapterNum, title, volNum, chapterNum)
}

// ─── Command: assemble ───────────────────────────────────────────────────────

func cmdAssemble(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: pipeline assemble <volume>")
		os.Exit(1)
	}

	volNum := 0
	fmt.Sscanf(args[0], "%d", &volNum)
	if volNum < 1 || volNum > 2 {
		fmt.Fprintf(os.Stderr, "Error: volume must be 1 or 2\n")
		os.Exit(1)
	}

	// Read chapter map
	mapPath := filepath.Join("pipeline", fmt.Sprintf("chapter_map_vol%d.json", volNum))
	mapData, err := os.ReadFile(mapPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading chapter map: %v\n", err)
		fmt.Fprintf(os.Stderr, "Run 'pipeline extract %d' first to generate the chapter map.\n", volNum)
		os.Exit(1)
	}

	var cm ChapterMap
	json.Unmarshal(mapData, &cm)

	manuscriptDir := filepath.Join("manuscript", fmt.Sprintf("volume_%d", volNum))
	var chapters []string

	for _, ch := range cm.Chapters {
		chDir := filepath.Join(manuscriptDir, fmt.Sprintf("ch%02d-%s", ch.Number, ch.Slug))
		refinedPath := filepath.Join(chDir, "english_refined.md")

		if _, err := os.Stat(refinedPath); os.IsNotExist(err) {
			fmt.Printf("  ⚠️  Missing: %s (skipping)\n", refinedPath)
			continue
		}

		content, _ := os.ReadFile(refinedPath)
		// Strip page markers from refined content
		pageRe := regexp.MustCompile(`—- Page \d+ —-\n?`)
		cleaned := pageRe.ReplaceAllString(string(content), "")
		chapters = append(chapters, cleaned)
		fmt.Printf("  ✓ %s (%d bytes)\n", refinedPath, len(cleaned))
	}

	// Assemble
	var assembled strings.Builder
	assembled.WriteString("---\n")
	assembled.WriteString(fmt.Sprintf("title: \"Antirevolutionary Politics: Volume %d\"\n", volNum))
	assembled.WriteString("author: \"Abraham Kuyper\"\n")
	assembled.WriteString("translator: \"Daniel Metcalf\"\n")
	assembled.WriteString(fmt.Sprintf("volume: %d\n", volNum))
	assembled.WriteString("---\n\n")

	for _, ch := range chapters {
		assembled.WriteString(ch)
		assembled.WriteString("\n\n")
	}

	// Write output
	outDir := "editions"
	os.MkdirAll(outDir, 0755)
	outFile := filepath.Join(outDir, fmt.Sprintf("Kuyper_Antirevolutionary_Politics_Vol%d_ASSEMBLED.md", volNum))
	os.WriteFile(outFile, []byte(assembled.String()), 0644)

	fmt.Printf("\n✓ Assembled %d chapters → %s (%d bytes)\n", len(chapters), outFile, len(assembled.String()))
}
