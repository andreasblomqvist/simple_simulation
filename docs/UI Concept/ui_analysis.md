# UI Analysis: Organization Simulation System

## Current UI Overview
The current UI for the organization simulation system, built with Ant Design components, presents various input fields and controls for configuring simulation parameters. It is divided into several logical sections, but the overall layout appears somewhat cluttered, and the relationships between certain controls could be made clearer.

## Levers and Settings Analysis

### 1. Levers Section
- **Levers (Dropdown):** Allows selection of different simulation levers (e.g., 'Recruitment'). This likely changes the context for the 'Levels' and 'Value' fields.
- **Levels (Dropdown):** Specifies the organizational level or category associated with the selected 'Lever' (e.g., 'AM', 'A', 'AC', 'C', 'S/C', 'AM', 'M', 'S/M', 'P/P').
- **Value (Input Field):** Numerical input for the chosen 'Lever' and 'Level' combination (e.g., '2.5 %').
- **Monthly: X% (Text):** Displays the monthly value, likely derived from the 'Value' input.

### 2. Time Period Section
- **Time Period (Dropdown):** Likely selects the granularity of the time period (e.g., 'Monthly').
- **Month (Input Field):** Specifies a particular month for the simulation.
- **Apply to all months (Checkbox):** If checked, the settings apply across all months of the simulation duration.

### 3. Configuration Section
- **Apply to all offices (Checkbox):** If checked, the settings apply to all offices.
- **Office Journey (Dropdown):** Unclear purpose without more context, but likely relates to a specific office's progression or type.
- **Specific Offices (Dropdown):** Allows selection of particular offices if 'Apply to all offices' is unchecked.

### 4. Simulation Parameters
- **Simulation Duration (Input Field):** Sets the total duration of the simulation in months (e.g., '24 Months').
- **Price Increase (%) (Input Field):** Percentage increase in price (e.g., '3.0 %').
- **Salary Increase (%) (Input Field):** Percentage increase in salary (e.g., '3.0 %').
- **Unplanned Absence (%) (Input Field):** Percentage of unplanned absence (e.g., '5.0 %').
- **Monthly Working Hours (Input Field):** Number of monthly working hours (e.g., '166.4').
- **Other Expense (Input Field):** Additional expenses (e.g., '100000').

## Pain Points and Opportunities for Simplification

1.  **Cluttered Input Area:** The main configuration area feels dense with many input fields. Grouping related parameters more visually could improve clarity.
2.  **Lever/Level/Value Relationship:** While grouped, the interaction of selecting a 'Lever', then a 'Level', and then inputting a 'Value' could be streamlined. Perhaps a more dynamic form that adjusts based on 'Lever' selection.
3.  **Time Period and Office Scope:** The 'Time Period' and 'Office' related settings are somewhat separated from the main 'Levers' section. Integrating these scope-defining parameters more closely with the levers they affect could be beneficial.
4.  **Action Buttons Redundancy:** There are multiple 'Apply' and 'Run Simulation' buttons. It's unclear if 'Apply' is needed before 'Run Simulation' or if 'Run Simulation' implicitly applies changes. A single, clear 


action button that clearly initiates the simulation with all current settings would be better.
5.  **Visual Hierarchy:** The current layout lacks a strong visual hierarchy, making it difficult to quickly grasp the most important controls or the flow of interaction.

## Opportunities for Simplification

1.  **Tabbed or Collapsible Sections:** Grouping related controls into tabbed or collapsible sections (e.g., "Simulation Levers," "Time & Scope," "Global Parameters") could reduce visual clutter.
2.  **Dynamic Forms:** When a user selects a "Lever," the "Levels" and "Value" fields could dynamically appear or change, reducing the number of visible fields when not relevant.
3.  **Clearer Action Flow:** A single, prominent "Run Simulation" button that implicitly applies all current settings would simplify the user experience. "Load Config Data" and "Reset to Config" could be secondary actions.
4.  **Visual Grouping:** Use Ant Design's `Card`, `Collapse`, or `Tabs` components to visually group related inputs and create a clearer hierarchy.
5.  **Inline Help/Tooltips:** For complex fields like "Office Journey," providing inline help or tooltips could clarify their purpose without adding permanent clutter.

This analysis will serve as the foundation for designing a simpler and more intuitive UI.

