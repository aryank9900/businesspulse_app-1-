# BusinessPulse — Business Analytics Platform

> A premium, AI-powered business analytics dashboard for live sales pitches to local business owners.

---

## What It Does

Enter a few simple business numbers and instantly generate:
- **Executive Dashboard** with 8 animated KPI cards
- **7 Beautiful Charts** (bar, line, pie, doughnut, grouped bar, weekly trend)
- **AI Business Insights** (7 actionable recommendations)
- **Business Health Score** (0–100 with animated ring)
- **PDF Export** + Print + Dark/Light Mode

---

## Quick Start

### Windows
```
Double-click start_windows.bat
```

### Mac / Linux
```bash
chmod +x start_mac_linux.sh
./start_mac_linux.sh
```

### Manual
```bash
pip install flask flask-sqlalchemy
python app.py
```
Then open: **http://localhost:5000**

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python Flask                      |
| Database   | SQLite via SQLAlchemy             |
| Frontend   | HTML5, CSS3, Bootstrap 5          |
| Charts     | Chart.js 4.4                      |
| Icons      | Font Awesome 6.5                  |
| Fonts      | Inter + Plus Jakarta Sans (Google)|
| PDF Export | html2pdf.js                       |

---

## Application Flow

```
Landing Page (Form Input)
        ↓
POST /generate (Flask processes data)
        ↓
AI Analytics Engine
  ├── Profit / Margin / Revenue calculations
  ├── Business Health Score (0–100)
  ├── 7 AI Insights (business-type aware)
  ├── Expense breakdown by business type
  ├── Weekly & Monthly projections
  └── All chart data
        ↓
Dashboard (localStorage → rendered instantly)
  ├── 8 KPI Cards (animated counters)
  ├── 7 Chart.js Charts
  ├── AI Insights Panel
  ├── Health Score Ring
  ├── Performance Bars
  └── Metrics Table
```

---

## Supported Business Types

Cafe · Restaurant · Biryani Shop · Bakery · Grocery Store · Medical Store · Clothing Store · Mobile Shop · Salon · Hardware Shop · Juice Center · Supermarket · Electronics Store · Pharmacy · Sweet Shop

Each type gets **custom expense categories** (e.g., a restaurant gets Raw Materials/Staff/Rent/Utilities/Packaging/Misc).

---

## Features

- ✅ Animated KPI counters
- ✅ 7 professional charts
- ✅ AI-powered business insights
- ✅ Business Health Score with SVG ring
- ✅ Dark / Light mode toggle
- ✅ PDF export (A3 landscape)
- ✅ Print-friendly layout
- ✅ Fully responsive (mobile-ready)
- ✅ SQLite persistence (history saved)
- ✅ Auto currency formatting (₹ INR)
- ✅ Business-type-aware analytics
- ✅ Sidebar navigation
- ✅ No internet required (except CDN fonts)

---

## Project Structure

```
businesspulse/
├── app.py                  # Flask backend + analytics engine
├── requirements.txt        # Python dependencies
├── start_windows.bat       # One-click Windows launcher
├── start_mac_linux.sh      # One-click Mac/Linux launcher
├── README.md               # This file
├── businesspulse.db        # SQLite database (auto-created)
└── templates/
    ├── index.html          # Landing page with form
    └── dashboard.html      # Dashboard with all charts
```

---

## Pitch Script

1. Open http://localhost:5000
2. Ask the owner:
   - "What's your business name?"
   - "How much revenue did you make today?"
   - "What were your expenses?"
   - "How many customers came in?"
   - "What's your best-selling item?"
3. Fill in the form (takes ~30 seconds)
4. Click **"Generate My Dashboard"**
5. Watch the WOW reaction 🎯

---

Built with ❤️ for live business pitches.
