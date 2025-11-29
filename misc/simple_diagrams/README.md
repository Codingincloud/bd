# BDIMS Simple Diagrams

## Overview

This folder contains five essential system diagrams for the **Blood Donation Information Management System (BDIMS)** project, designed in a clean, minimalistic **black-and-white style** specifically for academic presentations, reports, and technical documentation.

## Design Principles

All diagrams follow these strict design guidelines:

✅ **Simple & Clean** - No unnecessary complexity or decorations  
✅ **Black & White Only** - Black outlines on white background  
✅ **No Line Crossings** - All connections are carefully routed to avoid intersections  
✅ **Standard Symbols** - Following UML and DFD conventions  
✅ **Consistent Spacing** - Professional layout with adequate whitespace  
✅ **Print-Ready** - Optimized for both screen and paper  

## Diagrams Included

### 1. Context Diagram (Level 0)
**File:** `context_diagram.drawio`

A Level 0 Data Flow Diagram showing the BDIMS system as a single central process surrounded by external entities.

**Key Features:**
- 1 central system bubble
- 6 external entities (Donor, Administrator, Hospital, Donation Center, Database, Nominatim API)
- 12 labeled data flows
- Clear input (solid lines) and output (dashed lines) distinction

**Usage:** System overview, showing boundaries and external interactions

---

### 2. Data Flow Diagram (Level 1)
**File:** `dfd_level1.drawio`

Detailed breakdown showing internal processes and data stores within BDIMS.

**Key Features:**
- 10 major processes (Authentication, Registration, Request Management, etc.)
- 10 data stores (User Data, Donor Profiles, Donation Requests, etc.)
- 4 external entities
- 25+ data flows with clear read/write operations

**Usage:** Technical documentation, process analysis, database design context

---

### 3. Entity-Relationship Diagram
**File:** `er_diagram.drawio`

Complete database schema showing all entities, attributes, and relationships.

**Key Features:**
- 11 entities (User, Donor, AdminProfile, DonationRequest, DonationHistory, etc.)
- All attributes listed with data types
- Primary Keys (PK) and Foreign Keys (FK) clearly marked
- 13 relationships with cardinality (1:1, 1:N)
- Clean layout with no overlapping relationship lines

**Usage:** Database design, schema documentation, technical specifications

---

### 4. System Flowchart
**File:** `flowchart.drawio`

Step-by-step process flow for the complete donation request workflow.

**Key Features:**
- Vertical layout for easy reading
- Standard flowchart symbols (ellipses for start/end, rectangles for processes, diamonds for decisions)
- 14 process steps
- 4 decision points (Registered?, Valid Credentials?, Eligible?, Approved?)
- Error handling and loop-back paths
- Two end points (rejection and success paths)

**Usage:** Process documentation, user journey mapping, training materials

---

### 5. Use Case Diagram
**File:** `usecase_diagram.drawio`

Functional requirements showing all system actors and their interactions.

**Key Features:**
- 4 actors (Guest, Donor, Administrator, Hospital)
- 28 use cases covering all system functionality
- System boundary clearly marked
- 5 include relationships showing dependencies
- Straight lines with no crossings
- Actors positioned on left and right sides

**Usage:** Requirements documentation, functional specification, system scope definition

---

## File Format

All diagrams are saved in **Draw.io XML format (.drawio)**:
- **Editable** - Full control over layout, colors, text
- **Open Source** - Free to use and modify
- **Cross-Platform** - Works on Windows, Mac, Linux, Web
- **Exportable** - Can export to PNG, JPEG, SVG, PDF, HTML

---

## How to Use

### Option 1: View and Edit Online (Recommended)
1. Go to [https://app.diagrams.net/](https://app.diagrams.net/)
2. Click "Open Existing Diagram"
3. Select any `.drawio` file from this folder
4. Edit, export, or print as needed

### Option 2: Desktop Application
1. Download Draw.io Desktop from [diagrams.net](https://www.diagrams.net/)
2. Install the application (available for Windows, Mac, Linux)
3. Open any `.drawio` file directly in the app
4. Edit and save changes

### Option 3: Direct Web Access
1. Open `index.html` in any web browser
2. Click on any diagram card
3. Use "Download" to save locally or "Open in Draw.io" for online editing

---

## Exporting for Reports/Presentations

### To Export as PNG (High Quality Image):
1. Open diagram in Draw.io
2. Go to **File → Export as → PNG**
3. Settings:
   - Zoom: **100%** (or higher for better quality)
   - Border Width: **10px** (adds margin)
   - Transparent Background: **No** (keep white background)
   - Resolution: **300 DPI** (for printing)
4. Click **Export**

### To Export as PDF (Print Quality):
1. Open diagram in Draw.io
2. Go to **File → Export as → PDF**
3. Settings:
   - Page View: **Diagram** (fits to page)
   - Include: **All Pages** (if multi-page)
   - Quality: **100%**
4. Click **Export**

### To Export as SVG (Vector Graphics):
1. Open diagram in Draw.io
2. Go to **File → Export as → SVG**
3. Settings:
   - Size: **Diagram** (original size)
   - Links: **Open in same window**
4. Click **Export**
5. **Best for:** LaTeX documents, scalable graphics

### To Export as JPEG:
1. Open diagram in Draw.io
2. Go to **File → Export as → JPEG**
3. Settings same as PNG
4. Click **Export**

---

## Including in LaTeX Reports

```latex
\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\textwidth]{context_diagram.png}
    \caption{Context Diagram - BDIMS System Boundaries}
    \label{fig:context}
\end{figure}
```

Or for SVG (using `svg` package):
```latex
\usepackage{svg}

\begin{figure}[h]
    \centering
    \includesvg[width=0.8\textwidth]{context_diagram.svg}
    \caption{Context Diagram - BDIMS System Boundaries}
    \label{fig:context}
\end{figure}
```

---

## Diagram Statistics

| Diagram | Type | Complexity | Entities/Processes | Relationships/Flows |
|---------|------|------------|-------------------|---------------------|
| Context Diagram | DFD Level 0 | Low | 6 external entities | 12 data flows |
| Data Flow Diagram | DFD Level 1 | High | 10 processes, 10 stores | 25+ flows |
| ER Diagram | Database Schema | High | 11 entities | 13 relationships |
| Flowchart | Process Flow | Medium | 14 steps | 4 decisions |
| Use Case Diagram | UML | Medium | 4 actors | 28 use cases |

---

## Technical Specifications

- **Format:** Draw.io XML (.drawio)
- **Color Scheme:** Black (#000000) on White (#FFFFFF)
- **Font:** Sans-serif (Arial/Helvetica equivalent)
- **Line Width:** 2px for major elements, 1.5px for connections
- **Canvas Sizes:**
  - Context Diagram: 1200×900px
  - DFD Level 1: 1400×1200px
  - ER Diagram: 1400×1400px
  - Flowchart: 900×1600px (vertical)
  - Use Case Diagram: 1400×1200px

---

## Version Control

**Version:** 1.0  
**Last Updated:** November 29, 2025  
**Status:** ✅ Complete - All 5 diagrams finalized

### Revision History:
- **v1.0** (Nov 29, 2025) - Initial release with all 5 diagrams

---

## Maintenance Guidelines

### To Update Diagrams:
1. Open the `.drawio` file in Draw.io
2. Make your changes
3. **Important:** Maintain the black-and-white style
4. Ensure no lines cross each other
5. Save the file (File → Save or Ctrl+S)
6. Update the "Last Updated" date in this README

### Best Practices:
- ✅ Keep consistent spacing between elements
- ✅ Use standard symbols (don't create custom shapes)
- ✅ Label all connections clearly
- ✅ Test print/export before finalizing
- ✅ Save backup copies before major changes

---

## Troubleshooting

**Q: Diagram looks blurry when exported?**  
A: Increase the zoom level to 200% or set DPI to 300 when exporting PNG.

**Q: Lines appear crossed when I edit?**  
A: Use waypoints (click on line, drag the diamond points) to route around other elements.

**Q: Can't open in Draw.io web app?**  
A: Make sure the file has `.drawio` extension. Try drag-and-drop instead of "Open File".

**Q: Want to change colors?**  
A: Select element → Right panel → Style tab → Change Fill/Stroke colors. But remember: keep it black & white!

---

## Academic Use

These diagrams are designed specifically for:
- ✅ Final defense presentations
- ✅ Mid-term reports
- ✅ Technical documentation
- ✅ Project proposals
- ✅ Research papers
- ✅ Thesis/dissertation documents

**Recommended Sections:**
- **Context Diagram** → System Overview, Introduction
- **DFD Level 1** → System Design, Architecture
- **ER Diagram** → Database Design, Data Management
- **Flowchart** → Process Description, Methodology
- **Use Case Diagram** → Functional Requirements, Scope

---

## License

These diagrams are part of the BDIMS project and are intended for academic purposes. Feel free to modify and adapt for your needs.

---

## Contact & Support

For questions about these diagrams or the BDIMS project:
- Review the `index.html` file for interactive access
- Check the main project documentation in `misc/final_defense_report/`
- Refer to the QA preparation guide in `misc/documentation/`

---

## Quick Reference

### Diagram Selection Guide:

**Need to show system boundaries?** → Use **Context Diagram**  
**Need to explain processes?** → Use **DFD Level 1**  
**Need to show database structure?** → Use **ER Diagram**  
**Need to explain workflow?** → Use **Flowchart**  
**Need to show features?** → Use **Use Case Diagram**

---

**Last Updated:** November 29, 2025  
**Prepared By:** BDIMS Development Team  
**Institution:** Khwopa College of Engineering  
