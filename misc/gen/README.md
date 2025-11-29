# BDIMS Final Report - LaTeX Documentation

This folder contains the complete LaTeX source files for the **Blood Donor Information Management System (BDIMS)** final report.

## 📁 Contents

### Main Files
- `main.tex` - Main document with document class, packages, and structure
- `title.tex` - Title page with project details
- `bonafide.tex` - Bonafide certificate

### Chapter Files
- `chapter1_introduction.tex` - Background, Problem Statement, Objectives, Scope
- `chapter2_literature_review.tex` - Existing Systems, Technologies, Research
- `chapter3_system_analysis.tex` - Feasibility Study, Requirements Analysis
- `chapter4_system_design.tex` - Architecture, Database Design, DFD, ER Diagram
- `chapter5_implementation.tex` - Technology Stack, Code Implementation
- `chapter6_testing.tex` - Testing Strategy, Test Cases, Results
- `chapter7_conclusion.tex` - Summary, Limitations, Future Enhancements

### Supporting Files
- `appendix.tex` - User Manual, Installation Guide, Code Samples
- `references.bib` - Bibliography in BibTeX format
- `compile.bat` - Windows batch script for compilation
- `images/` - Folder for diagrams and screenshots (empty - add your images here)

## 🔧 Prerequisites

To compile this LaTeX document, you need:

1. **LaTeX Distribution:**
   - **Windows:** MiKTeX (https://miktex.org/) or TeX Live
   - **Mac:** MacTeX (https://www.tug.org/mactex/)
   - **Linux:** TeX Live (install via package manager)

2. **Required Packages:** (usually auto-installed by MiKTeX/TeX Live)
   - inputenc, geometry, graphicx, hyperref
   - setspace, titlesec, fancyhdr
   - booktabs, multirow, amsmath
   - listings, xcolor, enumitem, longtable
   - biblatex with biber backend

## 📝 Compilation Instructions

### Method 1: Using the Batch Script (Windows)

Simply double-click `compile.bat` or run in command prompt:
```batch
compile.bat
```

The script will:
1. Run pdflatex (first pass)
2. Run biber for bibliography
3. Run pdflatex (second pass)
4. Run pdflatex (third pass for TOC)
5. Clean up auxiliary files
6. Open the generated PDF

### Method 2: Manual Compilation

Run these commands in sequence:

```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

### Method 3: Using LaTeX Editor

Open `main.tex` in your LaTeX editor:
- **Overleaf:** Upload all files, compile online
- **TeXstudio:** Open main.tex, press F5 to compile
- **TeXmaker:** Open main.tex, use Quick Build (F1)
- **VS Code with LaTeX Workshop:** Open folder, compile automatically

## 🖼️ Adding Images

1. Place image files in the `images/` folder
2. Supported formats: PNG, JPG, PDF
3. Reference in LaTeX:
   ```latex
   \begin{figure}[h]
   \centering
   \includegraphics[width=0.8\textwidth]{images/your_image.png}
   \caption{Your Caption}
   \label{fig:your_label}
   \end{figure}
   ```

## 📊 Recommended Images to Add

For a complete report, consider adding:

1. **System Architecture Diagram** (Chapter 4)
2. **ER Diagram** (Chapter 4)
3. **Data Flow Diagram** (Chapter 4)
4. **Use Case Diagram** (Chapter 4)
5. **Screenshots:**
   - Homepage
   - Donor Dashboard
   - Interactive Map
   - Health Metrics Form
   - Donation History
   - Admin Dashboard
   - Inventory Management
   - Emergency Request

## 🎨 Customization

### Changing Team Details

Edit `title.tex` and `bonafide.tex`:
- Team member names and roll numbers
- Supervisor name
- Date

### Modifying Content

Each chapter is in a separate file for easy editing:
- Open the relevant `chapterX_*.tex` file
- Make your changes
- Save and recompile

### Adjusting Formatting

In `main.tex`, you can modify:
- Page margins: `\usepackage[top=1in,bottom=1in,left=1.5in,right=1in]{geometry}`
- Line spacing: `\onehalfspacing` (change to `\doublespacing` if needed)
- Font size: `\documentclass[12pt,a4paper]{report}` (change 12pt to 10pt or 11pt)

## 📖 Document Structure

The report follows standard academic format:

```
Front Matter (Roman numerals)
├── Title Page (i)
├── Bonafide Certificate (ii)
├── Acknowledgement (iii)
├── Abstract (iv)
├── Table of Contents (v)
├── List of Figures (vi)
├── List of Tables (vii)
└── List of Abbreviations (viii)

Main Content (Arabic numerals)
├── Chapter 1: Introduction (1)
├── Chapter 2: Literature Review
├── Chapter 3: System Analysis
├── Chapter 4: System Design
├── Chapter 5: Implementation
├── Chapter 6: Testing
├── Chapter 7: Conclusion
├── References
└── Appendix
```

## ⚠️ Common Issues and Solutions

### Issue: "File not found" error
**Solution:** Ensure all `.tex` files are in the same directory as `main.tex`

### Issue: Bibliography not appearing
**Solution:** 
1. Make sure `references.bib` exists
2. Run biber: `biber main`
3. Recompile with pdflatex twice

### Issue: Images not displaying
**Solution:**
1. Check image path is correct
2. Ensure image file exists in `images/` folder
3. Use forward slashes: `images/diagram.png`

### Issue: Package not found
**Solution:** 
- MiKTeX: Will auto-install on first compilation
- TeX Live: Run `tlmgr install <package-name>`

### Issue: Compilation takes too long
**Solution:** 
1. Close PDF viewer before recompiling
2. Delete auxiliary files: `*.aux`, `*.log`, etc.
3. Use draft mode: `\documentclass[12pt,a4paper,draft]{report}`

## 📄 Output

Successful compilation produces:
- **main.pdf** - The final report (ready for printing/submission)
- Auxiliary files (*.aux, *.log, etc.) - Can be deleted after compilation

## 🖨️ Printing Guidelines

For professional printing:
1. **Paper:** A4 size (210mm × 297mm)
2. **Margins:** Left 1.5", Others 1" (as configured)
3. **Binding:** Spine binding (left margin allows for this)
4. **Color:** Black & white with color charts/diagrams
5. **Pages:** Print double-sided to save paper

## 📞 Support

For LaTeX help:
- **Overleaf Documentation:** https://www.overleaf.com/learn
- **LaTeX Stack Exchange:** https://tex.stackexchange.com/
- **LaTeX Wikibook:** https://en.wikibooks.org/wiki/LaTeX

## 📝 Version History

- **v1.0** (2025-11-29): Initial complete report with all 7 chapters
  - Comprehensive content covering entire BDIMS project
  - All sections complete and ready for submission
  - Based on actual project implementation

## ✅ Checklist Before Submission

- [ ] All team member names and roll numbers correct
- [ ] Supervisor name correct
- [ ] Date updated to submission date
- [ ] All images added and displaying correctly
- [ ] Table of contents generated properly
- [ ] Page numbers correct
- [ ] No compilation errors or warnings
- [ ] Bibliography entries complete
- [ ] Spell-check completed
- [ ] PDF opens without issues
- [ ] Printed copy reviewed

## 📜 License

This documentation is part of an academic project for educational purposes.

---

**Generated for:** Blood Donor Information Management System (BDIMS)  
**Institution:** Khwopa Engineering College, Bhaktapur  
**Program:** Bachelor of Engineering in Computer Engineering  
**Semester:** Fifth Semester, 2025
