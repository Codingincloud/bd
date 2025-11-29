# BDIMS System Diagrams

Complete set of system diagrams for the Blood Donor Information Management System (BDIMS).

## 📁 Contents

This folder contains 5 comprehensive diagrams documenting the BDIMS architecture:

### 1. **ER Diagram** (`er_diagram.drawio`)
- **Type**: Entity Relationship Diagram
- **Entities**: 11 database entities
- **Shows**: Complete database schema with all relationships, primary keys, foreign keys, and attributes
- **Entities Include**: User, Donor, AdminProfile, DonationHistory, DonationRequest, DonationCenter, Hospital, BloodInventory, EmergencyRequest, EmergencyResponse, HealthMetrics, Notifications

### 2. **Context Diagram** (`context_diagram.drawio`)
- **Type**: Level 0 Data Flow Diagram
- **Shows**: System boundaries and external entity interactions
- **External Entities**: Donor, Administrator, Blood Bank Staff, Hospital, Nominatim API, PostgreSQL Database, Email Service
- **Data Flows**: 15+ input/output flows showing system interactions

### 3. **Data Flow Diagram** (`dataflow_diagram.drawio`)
- **Type**: Level 1 DFD
- **Processes**: 10 major system processes
- **Data Stores**: 10 database stores
- **Shows**: Detailed data flow between processes, external entities, and data stores
- **Processes Include**:
  1. User Authentication
  2. Donor Management
  3. Donation Request Processing
  4. Blood Inventory Management
  5. Emergency Request Handling
  6. Health Metrics Tracking
  7. Location Services
  8. Reporting & Analytics
  9. Notification System
  10. Blood Center Management

### 4. **Use Case Diagram** (`usecase_diagram.drawio`)
- **Type**: UML Use Case Diagram
- **Actors**: 4 (Guest, Donor, Administrator, Nominatim API)
- **Use Cases**: 30+ functional requirements
- **Shows**: System functionality from user perspective with relationships (include, extend)

**Donor Use Cases**: Registration, Login, Profile Management, Location Update, Schedule Donation, View History, Check Eligibility, Add Health Metrics, Emergency Response, Compatibility Check, Find Centers

**Admin Use Cases**: Manage Donors, Add/Edit/Delete Donors, Search Donors, Manage Inventory, Update Stock, Create Emergency Requests, Manage Requests, Approve/Reject, Generate Reports, View Analytics, Track Locations, Manage Centers, Send Notifications

### 5. **Flowchart** (`flowchart.drawio`)
- **Type**: Process Flowchart
- **Process**: Complete Donation Request Workflow
- **Steps**: 25+ process steps
- **Shows**: Detailed step-by-step flow from registration to donation approval
- **Includes**: Decision points, error handling, alternate paths

## 🚀 How to Use

### Option 1: View Online (Recommended)
1. Open `index.html` in your browser
2. Click "Open in Draw.io" for any diagram
3. View, edit, or export the diagram

### Option 2: Desktop Application
1. Download [Draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases)
2. Open the `.drawio` files directly
3. Edit and export as needed

### Option 3: Direct Web Access
Visit: https://app.diagrams.net/
- Click "Open Existing Diagram"
- Upload the `.drawio` file
- View/Edit/Export

## 💾 Export Options

Each diagram can be exported to:
- **PNG** - For presentations and documents (recommended for reports)
- **JPEG** - Smaller file size, good for web
- **SVG** - Vector format, scales perfectly
- **PDF** - For printing and professional documentation
- **XML** - Editable Draw.io format (source files)

### To Export:
1. Open diagram in Draw.io
2. Go to **File → Export as**
3. Choose format (PNG/JPEG/SVG/PDF)
4. Set quality/resolution
5. Click Export

## 🎨 Diagram Color Coding

### ER Diagram
- **Blue**: User entity
- **Green**: Donor entity
- **Orange**: Admin entity
- **Purple**: History/Metrics entities
- **Yellow**: Request entities
- **Red/Pink**: Emergency & Hospital entities
- **Gray**: Data attributes

### Context Diagram
- **Blue**: Central BDIMS system
- **Green**: Donor (external entity)
- **Orange**: Administrator
- **Yellow**: Staff
- **Red**: Hospital
- **Light Blue**: API services
- **Purple**: Database

### DFD Level 1
- **Blue**: Authentication process
- **Green**: Donor management
- **Orange**: Request processing
- **Red**: Inventory/Emergency
- **Purple**: Health tracking
- **Cyan**: Location services
- **Dark**: Analytics/Reporting

### Use Case Diagram
- **Light Blue**: Authentication use cases
- **Green**: Donor use cases
- **Orange**: Admin use cases
- **Yellow**: Request use cases

### Flowchart
- **Green**: Start/End
- **Light Blue**: Process steps
- **Purple**: Input/Registration
- **Orange**: Authentication
- **Cyan**: Information display
- **Yellow**: Decision points
- **Red**: Rejection/Error paths
- **Light Green**: Approval paths

## 📊 Diagram Statistics

| Diagram | Entities/Actors/Steps | Relationships/Flows | Complexity |
|---------|----------------------|---------------------|------------|
| ER Diagram | 11 entities | 20+ relationships | High |
| Context Diagram | 7 external entities | 15+ data flows | Medium |
| DFD Level 1 | 10 processes, 10 stores | 25+ flows | High |
| Use Case Diagram | 4 actors | 30+ use cases | High |
| Flowchart | 25+ steps | 35+ flows | High |

## 🔧 Technical Details

- **Format**: Draw.io XML (`.drawio`)
- **Compatibility**: Draw.io Desktop, draw.io web app, diagrams.net
- **Standards**: UML 2.5, DFD conventions, ER notation
- **Resolution**: Vector-based (scalable to any size)
- **Editable**: Yes, fully editable source files

## 📝 Diagram Maintenance

### Version Control
All diagram files are tracked in Git. To update:
1. Open the `.drawio` file
2. Make changes
3. Save the file
4. Commit with descriptive message

### Naming Convention
- `er_diagram.drawio` - Entity Relationship
- `context_diagram.drawio` - Level 0 DFD
- `dataflow_diagram.drawio` - Level 1 DFD
- `usecase_diagram.drawio` - Use Cases
- `flowchart.drawio` - Process Flow

## 🎓 Academic Use

These diagrams are designed for:
- ✅ Final Year Project Report
- ✅ Thesis Documentation
- ✅ Presentations
- ✅ Technical Documentation
- ✅ System Design Proposals

All diagrams follow academic standards and best practices for software engineering documentation.

## 👥 Team

**BDIMS Development Team**
- Bishal Shrestha (790310)
- Chirayu Shrestha (790311)
- Pappu Yadav (790324)
- Prashant Ghimire (790328)

**Supervised by**: Er. Anish Baral  
**Institution**: Khwopa Engineering College, Purbanchal University

## 📄 License

These diagrams are part of the BDIMS project and are provided for educational purposes.

---

**Last Updated**: November 29, 2025  
**Version**: 1.0  
**Status**: Complete ✅
