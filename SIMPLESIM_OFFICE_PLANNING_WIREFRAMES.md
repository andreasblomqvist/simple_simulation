# SimpleSim Office Planning Interface Wireframes

Based on UX research analysis of Planacy and current SimpleSim usage patterns. These wireframes address the 5-tab complexity issue and integrate office expenses into unified business planning.

## 1. PRIMARY WIREFRAME: Dashboard-Centric Planning Workspace (Recommended)

```
┌─ SimpleSim ──────────────────────────────────────────────────────────────────────────────────────┐
│ [☰] [Dashboard] [Scenarios] [Reports] [Settings]           [🔍 Search] [👤 User] [⚙️] [🌙]    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ Business Planning Dashboard ────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│ ┌─ Office Context ──────────────────────────────────────────────────────────────────────────────┐ │
│ │ 📍 [London Office ▼]    📅 [2025 Q1-Q4 ▼]    📊 [Monthly View ▼]    [Create Scenario] [Export] │ │
│ │                                                                                              │ │
│ │ 💰 Total Budget: £2.4M  |  👥 Current FTE: 45  |  📈 Growth Target: +15%  |  ⚡ Modified    │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Planning Grid ──────────────────────────────────────────────────────────────────────────────┐ │
│ │                     │ Jan │ Feb │ Mar │ Apr │ May │ Jun │ Jul │ Aug │ Sep │ Oct │ Nov │ Dec │ │ │
│ │ ├─ WORKFORCE ────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤ │ │
│ │ │ ▼ Consultant       │     │     │     │     │     │     │     │     │     │     │     │     │ │ │
│ │ │   ├─ A Level   [+] │  8  │  8  │  9  │  9  │ 10  │ 10  │ 11  │ 11  │ 12  │ 12  │ 13  │ 13  │ │ │
│ │ │   ├─ B Level   [+] │  5  │  5  │  5  │  6  │  6  │  7  │  7  │  8  │  8  │  9  │  9  │ 10  │ │ │
│ │ │   └─ C Level   [+] │  2  │  2  │  2  │  2  │  3  │  3  │  3  │  3  │  4  │  4  │  4  │  4  │ │ │
│ │ │ ▼ Senior Cons.     │     │     │     │     │     │     │     │     │     │     │     │     │ │ │
│ │ │   ├─ A Level   [+] │  3  │  3  │  3  │  4  │  4  │  4  │  5  │  5  │  5  │  6  │  6  │  6  │ │ │
│ │ │   └─ B Level   [+] │  2  │  2  │  2  │  2  │  2  │  3  │  3  │  3  │  3  │  3  │  4  │  4  │ │ │
│ │ │ ▲ Operations   [+] │  4  │  4  │  4  │  4  │  5  │  5  │  5  │  5  │  6  │  6  │  6  │  6  │ │ │
│ │ ├─ SALARIES ─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤ │ │
│ │ │ ▲ Consultant       │185K │188K │194K │200K │210K │215K │225K │230K │242K │248K │258K │265K │ │ │
│ │ │ ▲ Senior Cons.     │125K │127K │130K │135K │140K │143K │150K │153K │160K │165K │172K │175K │ │ │
│ │ │ ▲ Operations       │ 48K │ 48K │ 49K │ 50K │ 52K │ 53K │ 54K │ 55K │ 58K │ 59K │ 61K │ 62K │ │ │
│ │ ├─ EXPENSES ─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤ │ │
│ │ │ ▲ Office Rent      │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ │ │
│ │ │ ▲ Tech & Software  │ 12K │ 12K │ 13K │ 13K │ 14K │ 14K │ 15K │ 15K │ 16K │ 16K │ 17K │ 17K │ │ │
│ │ │ ▲ Travel & Client  │  8K │  9K │ 11K │ 12K │ 15K │ 18K │ 20K │ 18K │ 16K │ 14K │ 12K │ 10K │ │ │
│ │ │ ▲ Training         │  3K │  2K │  4K │  6K │  8K │  5K │  3K │  7K │  9K │  4K │  2K │  5K │ │ │
│ │ └─ TOTALS ──────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤ │ │
│ │   📊 Total Cost     │233K │236K │247K │256K │270K │280K │293K │301K │318K │326K │339K │347K │ │ │
│ │   👥 Total FTE      │ 24  │ 24  │ 25  │ 27  │ 30  │ 32  │ 34  │ 35  │ 38  │ 40  │ 42  │ 43  │ │ │
│ │   💷 Cost per FTE   │9.7K │9.8K │9.9K │9.5K │9.0K │8.8K │8.6K │8.6K │8.4K │8.2K │8.1K │8.1K │ │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Quick Actions & Insights ───────────────────────────────────────────────────────────────────┐ │
│ │ 📈 YoY Growth: +18% FTE, +24% Revenue     🎯 Utilization: 87% (Target: 85%)                 │ │
│ │                                                                                              │ │
│ │ [Copy from Previous Month] [Apply Growth %] [Bulk Salary Adjust] [Import from Excel]        │ │
│ │                                                                                              │ │
│ │ 🚨 Alerts: Q3 hiring spike may stress recruitment | 💡 Suggest: Gradual Q2-Q3 ramp          │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

INTERACTION FLOWS:
► Office Dropdown: Switch context, maintains grid data per office
► Month Cells: Click to edit, Enter to confirm, Esc to cancel
► Role Rows: Click [+] to add position, [-] to remove, drag to reorder
► Section Collapse: Click ▼/▲ to show/hide sections (Workforce/Salaries/Expenses)
► Hover States: Cell highlights, shows YoY comparison tooltip
► Create Scenario: Pre-populates with current grid data
► Export: Excel/PDF with formatting preserved
```

## 2. ALTERNATIVE WIREFRAME: Simplified Spreadsheet-Style Interface

```
┌─ SimpleSim Business Planning ────────────────────────────────────────────────────────────────────┐
│ [☰] [Dashboard] [Scenarios] [Reports] [Settings]           [🔍 Search] [👤 User] [⚙️] [🌙]    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ Planning Workspace ─────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│ 📍 London Office  │  📅 2025  │  [Monthly] [Quarterly] [Yearly]  │  [💾 Save] [📤 Export] [⚙️]    │
│                                                                                                  │
│ ┌─ Spreadsheet View ──────────────────────────────────────────────────────────────────────────┐ │
│ │     A              B     C     D     E     F     G     H     I     J     K     L     M    N │ │
│ │  1  Category/Role │ Jan │ Feb │ Mar │ Apr │ May │ Jun │ Jul │ Aug │ Sep │ Oct │ Nov │ Dec │Tot│ │
│ │  ├──────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼───┤ │
│ │  2  🔵 HEADCOUNT    │     │     │     │     │     │     │     │     │     │     │     │     │   │ │
│ │  3  Consultant A    │  8  │  8  │  9  │  9  │ 10  │ 10  │ 11  │ 11  │ 12  │ 12  │ 13  │ 13  │126│ │
│ │  4  Consultant B    │  5  │  5  │  5  │  6  │  6  │  7  │  7  │  8  │  8  │  9  │  9  │ 10  │ 85│ │
│ │  5  Consultant C    │  2  │  2  │  2  │  2  │  3  │  3  │  3  │  3  │  4  │  4  │  4  │  4  │ 36│ │
│ │  6  Sr. Consultant A│  3  │  3  │  3  │  4  │  4  │  4  │  5  │  5  │  5  │  6  │  6  │  6  │ 54│ │
│ │  7  Sr. Consultant B│  2  │  2  │  2  │  2  │  2  │  3  │  3  │  3  │  3  │  3  │  4  │  4  │ 33│ │
│ │  8  Operations      │  4  │  4  │  4  │  4  │  5  │  5  │  5  │  5  │  6  │  6  │  6  │  6  │ 60│ │
│ │  9  🟢 SALARIES     │     │     │     │     │     │     │     │     │     │     │     │     │   │ │
│ │ 10  Consultant      │185K │188K │194K │200K │210K │215K │225K │230K │242K │248K │258K │265K │2.7M│ │
│ │ 11  Sr. Consultant  │125K │127K │130K │135K │140K │143K │150K │153K │160K │165K │172K │175K │1.8M│ │
│ │ 12  Operations      │ 48K │ 48K │ 49K │ 50K │ 52K │ 53K │ 54K │ 55K │ 58K │ 59K │ 61K │ 62K │660K│ │
│ │ 13  🟡 EXPENSES     │     │     │     │     │     │     │     │     │     │     │     │     │   │ │
│ │ 14  Office Rent     │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │ 25K │300K│ │
│ │ 15  Technology      │ 12K │ 12K │ 13K │ 13K │ 14K │ 14K │ 15K │ 15K │ 16K │ 16K │ 17K │ 17K │168K│ │
│ │ 16  Travel          │  8K │  9K │ 11K │ 12K │ 15K │ 18K │ 20K │ 18K │ 16K │ 14K │ 12K │ 10K │163K│ │
│ │ 17  Training        │  3K │  2K │  4K │  6K │  8K │  5K │  3K │  7K │  9K │  4K │  2K │  5K │ 58K│ │
│ │ ├──────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼───┤ │
│ │ 18  💰 TOTAL COST   │406K │415K │436K │451K │484K │506K │531K │544K │581K │591K │619K │634K │6.2M│ │
│ │ 19  👥 TOTAL FTE    │ 24  │ 24  │ 25  │ 27  │ 30  │ 32  │ 34  │ 35  │ 38  │ 40  │ 42  │ 43  │ 394│ │
│ │ 20  📊 COST/FTE     │16.9K│17.3K│17.4K│16.7K│16.1K│15.8K│15.6K│15.5K│15.3K│14.8K│14.7K│14.7K│   │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Formula Bar & Tools ────────────────────────────────────────────────────────────────────────┐ │
│ │ fx │ =SUM(B3:B8)                                              [📋] [📈] [🔄] [🎯] [⚠️]     │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Scenario Actions ───────────────────────────────────────────────────────────────────────────┐ │
│ │ [Create Scenario from Plan] [Compare with Actuals] [Export to Excel] [Share with Team]       │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

INTERACTION FLOWS:
► Spreadsheet Navigation: Arrow keys, Tab, Enter like Excel
► Cell Editing: Double-click or F2 to edit, supports formulas
► Row/Column Operations: Right-click for insert/delete/format
► Color Coding: Blue (headcount), Green (salaries), Yellow (expenses)
► Formula Support: Basic SUM, AVERAGE, growth calculations
► Export Integration: Maintains Excel compatibility
```

## 3. MULTI-OFFICE WIREFRAME: Executive Aggregated View

```
┌─ SimpleSim Executive Dashboard ──────────────────────────────────────────────────────────────────┐
│ [☰] [Dashboard] [Scenarios] [Reports] [Settings]           [🔍 Search] [👤 User] [⚙️] [🌙]    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ Multi-Office Business Planning ─────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│ ┌─ Office Selection & Summary ─────────────────────────────────────────────────────────────────┐ │
│ │ 🌍 [All Offices ▼] │ 📅 [2025 ▼] │ 📊 [Quarterly ▼] │ [Create Global Scenario] [Export All] │ │
│ │                                                                                              │ │
│ │ ☑️ London (45 FTE)  ☑️ New York (78 FTE)  ☑️ Singapore (32 FTE)  ☑️ Frankfurt (28 FTE)     │ │
│ │                                                                                              │ │
│ │ 💰 Global Budget: $12.8M  |  👥 Total FTE: 183  |  📈 Planned Growth: +22%                │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Aggregated Planning Grid ──────────────────────────────────────────────────────────────────┐ │
│ │                          │  Q1 2025  │  Q2 2025  │  Q3 2025  │  Q4 2025  │   Total    │ │ │
│ │ ├────────────────────────┼───────────┼───────────┼───────────┼───────────┼────────────┤ │ │
│ │ │ 🏢 LONDON              │           │           │           │           │            │ │ │
│ │ │ ├─ Consultants         │    45     │    48     │    52     │    55     │    200     │ │ │
│ │ │ ├─ Senior Consultants  │    18     │    20     │    22     │    24     │     84     │ │ │
│ │ │ ├─ Operations          │    12     │    13     │    14     │    15     │     54     │ │ │
│ │ │ └─ Quarterly Cost      │  $1.2M    │  $1.3M    │  $1.4M    │  $1.5M    │   $5.4M   │ │ │
│ │ │                        │           │           │           │           │            │ │ │
│ │ │ 🏢 NEW YORK            │           │           │           │           │            │ │ │
│ │ │ ├─ Consultants         │    72     │    76     │    82     │    85     │    315     │ │ │
│ │ │ ├─ Senior Consultants  │    28     │    30     │    33     │    36     │    127     │ │ │
│ │ │ ├─ Operations          │    18     │    19     │    21     │    22     │     80     │ │ │
│ │ │ └─ Quarterly Cost      │  $2.1M    │  $2.2M    │  $2.4M    │  $2.5M    │   $9.2M   │ │ │
│ │ │                        │           │           │           │           │            │ │ │
│ │ │ 🏢 SINGAPORE           │           │           │           │           │            │ │ │
│ │ │ ├─ Consultants         │    28     │    30     │    32     │    35     │    125     │ │ │
│ │ │ ├─ Senior Consultants  │    12     │    13     │    15     │    16     │     56     │ │ │
│ │ │ ├─ Operations          │     8     │     9     │    10     │    11     │     38     │ │ │
│ │ │ └─ Quarterly Cost      │  $0.8M    │  $0.9M    │  $1.0M    │  $1.1M    │   $3.8M   │ │ │
│ │ │                        │           │           │           │           │            │ │ │
│ │ │ 🏢 FRANKFURT           │           │           │           │           │            │ │ │
│ │ │ ├─ Consultants         │    22     │    24     │    26     │    28     │    100     │ │ │
│ │ │ ├─ Senior Consultants  │    10     │    11     │    12     │    13     │     46     │ │ │
│ │ │ ├─ Operations          │     6     │     7     │     8     │     8     │     29     │ │ │
│ │ │ └─ Quarterly Cost      │  $0.7M    │  $0.8M    │  $0.9M    │  $0.9M    │   $3.3M   │ │ │
│ │ ├────────────────────────┼───────────┼───────────┼───────────┼───────────┼────────────┤ │ │
│ │ │ 🌍 GLOBAL TOTALS       │           │           │           │           │            │ │ │
│ │ │ ├─ Total FTE           │   239     │   254     │   275     │   289     │   1,057    │ │ │
│ │ │ ├─ Total Cost          │  $4.8M    │  $5.2M    │  $5.7M    │  $6.0M    │  $21.7M   │ │ │
│ │ │ ├─ Average Cost/FTE    │ $20.1K    │ $20.5K    │ $20.7K    │ $20.8K    │  $20.5K   │ │ │
│ │ │ └─ Growth Rate         │   +8%     │   +6%     │   +8%     │   +5%     │   +27%    │ │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
│ ┌─ Regional Insights & Actions ────────────────────────────────────────────────────────────────┐ │
│ │ 📊 Cost Distribution: NY 42% | London 25% | Singapore 18% | Frankfurt 15%                   │ │
│ │                                                                                              │ │
│ │ ⚠️  Alerts: NY Q3 hiring aggressive | 💡 Opportunity: Frankfurt cost efficiency best        │ │
│ │                                                                                              │ │
│ │ [Drill Down to Office] [Compare Regions] [Export Regional Report] [Create Variance Alert]   │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

INTERACTION FLOWS:
► Office Checkboxes: Toggle office inclusion in aggregated view
► Drill Down: Click office name to view detailed monthly grid
► Regional Compare: Side-by-side office comparison modal
► Export Options: Global summary or individual office reports
► Alert System: Cross-office variance and trend detection
► Scenario Creation: Global scenario with office-specific parameters
```

## 4. MOBILE/RESPONSIVE WIREFRAME: Tablet/Compact View

```
┌─ SimpleSim Mobile ───────────────────────────────────────────────────┐
│ [☰] SimpleSim                                     [🔍] [👤] [⚙️]    │
└──────────────────────────────────────────────────────────────────────┘

┌─ Business Planning (Mobile) ─────────────────────────────────────────┐
│                                                                      │
│ ┌─ Context Bar ────────────────────────────────────────────────────┐ │
│ │ 📍 London Office ▼                                              │ │
│ │ 📅 2025 Q1 ▼         📊 Monthly ▼         [Create Scenario]     │ │
│ │                                                                  │ │
│ │ 💰 £2.4M Budget  👥 45 FTE  📈 +15% Growth                     │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─ Planning Cards (Stacked) ───────────────────────────────────────┐ │
│ │ ┌─ 👥 WORKFORCE ──────────────────────────────────────────────┐ │ │
│ │ │                Jan │ Feb │ Mar │                           │ │ │
│ │ │ Consultant A    8   │  8  │  9  │ [▲] [▼] [Edit All]      │ │ │
│ │ │ Consultant B    5   │  5  │  5  │                         │ │ │
│ │ │ Consultant C    2   │  2  │  2  │                         │ │ │
│ │ │ Sr. Consultant  5   │  5  │  5  │                         │ │ │
│ │ │ Operations      4   │  4  │  4  │                         │ │ │
│ │ │                                                           │ │ │
│ │ │ Total FTE      24   │ 24  │ 25  │ [+ Add Role]            │ │ │
│ │ └───────────────────────────────────────────────────────────────┘ │ │
│ │                                                                  │ │
│ │ ┌─ 💰 SALARIES ────────────────────────────────────────────────┐ │ │
│ │ │                Jan │ Feb │ Mar │                           │ │ │
│ │ │ Consultant    185K │188K │194K │ [Bulk Adjust +3%]       │ │ │
│ │ │ Sr. Consultant125K │127K │130K │                         │ │ │
│ │ │ Operations     48K │ 48K │ 49K │                         │ │ │
│ │ │                                                           │ │ │
│ │ │ Total Salary  358K │363K │373K │ [View Details]          │ │ │
│ │ └───────────────────────────────────────────────────────────────┘ │ │
│ │                                                                  │ │
│ │ ┌─ 🏢 EXPENSES ─────────────────────────────────────────────────┐ │ │
│ │ │                Jan │ Feb │ Mar │                           │ │ │
│ │ │ Office Rent    25K │ 25K │ 25K │ [Fixed]                 │ │ │
│ │ │ Technology     12K │ 12K │ 13K │                         │ │ │
│ │ │ Travel          8K │  9K │ 11K │                         │ │ │
│ │ │ Training        3K │  2K │  4K │                         │ │ │
│ │ │                                                           │ │ │
│ │ │ Total Expenses 48K │ 48K │ 53K │ [+ Add Category]        │ │ │
│ │ └───────────────────────────────────────────────────────────────┘ │ │
│ │                                                                  │ │
│ │ ┌─ 📊 SUMMARY ──────────────────────────────────────────────────┐ │ │
│ │ │ Total Cost:   406K │415K │436K │                           │ │ │
│ │ │ Cost per FTE: 16.9K│17.3K│17.4K│                           │ │ │
│ │ │ YoY Growth:    +8% │ +9% │+12% │                           │ │ │
│ │ └───────────────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─ Actions ────────────────────────────────────────────────────────┐ │
│ │ [📤 Export] [📋 Copy Previous] [🔄 Sync] [⚙️ Settings]          │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌─ Month Detail Modal (When cell tapped) ─────────────────────────────┐
│ Consultant A - January 2025              [✕]                       │
│                                                                      │
│ Current FTE: [8    ] ▲▼                                             │
│ Previous:    7 FTE (+1)                                             │
│ Planned:     9 FTE (Feb)                                            │
│                                                                      │
│ Monthly Salary: £15,400                                             │
│ Recruitment Cost: £2,100                                            │
│ Training Budget: £500                                               │
│                                                                      │
│ [Apply to All Months] [Copy to Next] [Cancel] [Save]               │
└──────────────────────────────────────────────────────────────────────┘

INTERACTION FLOWS:
► Vertical Card Stack: Scroll through sections (Workforce/Salaries/Expenses)
► Tap Cell: Opens detailed edit modal with context
► Swipe Gestures: Navigate between months within sections
► Bulk Actions: Edit All/Bulk Adjust for efficiency
► Quick Filters: Show only changed values, hide fixed costs
► Context Persistence: Maintains office/period selection across views
```

## Key Design Decisions & Integration Points

### Information Architecture
1. **Context First**: Office and time period selection drives all data
2. **Progressive Disclosure**: Summary → Categories → Details → Monthly granularity  
3. **Unified Expenses**: Office costs integrated within business planning workflow
4. **Scenario Integration**: Direct handoff from planning grid to scenario creation

### Navigation Simplification
- **Eliminates 5-tab complexity**: Single planning workspace
- **Context-driven views**: Office selection changes entire interface context
- **Integrated expenses**: No separate tab, expenses within planning grid
- **Scenario handoff**: Pre-populated scenario creation from current plan

### Professional Styling Cues (from Planacy)
- **Spreadsheet familiarity**: Grid-based layout with clear column headers
- **Hierarchical data**: Role categories with expandable levels
- **Financial formatting**: Currency with K/M notation, right-aligned numbers
- **Color coding**: Consistent colors for different data types
- **Formula support**: Basic calculations visible and editable

### Responsive Strategy
- **Desktop-first**: Optimized for 1024px+ planning workflows
- **Tablet adaptation**: Card-based stacking for touch interaction
- **Mobile consideration**: Essential functionality in constrained space
- **Cross-device sync**: Seamless handoff between desktop planning and mobile review

### SimpleSim Integration
- **Scenario workflow**: Planning grid → Create Scenario → Run Simulation → View Results
- **Data continuity**: Office configuration drives default values
- **Role hierarchy**: Maintains leveled vs flat role distinction
- **Export compatibility**: Excel format preserves formulas and formatting