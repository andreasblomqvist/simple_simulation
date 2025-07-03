# SimpleSim UI Guidelines

## Purpose

This document defines the canonical UI and layout rules for all pages and components in the SimpleSim project. All developers and AI assistants **must** follow these guidelines to ensure a clean, consistent, and professional user experience.

---

## 1. Layout Principles
- **Main container:** Use a single Ant Design `<Card style={{ margin: 32 }}>` as the page container.
- **Alignment:** All content is left-aligned inside the Card.
- **Spacing:** No extra max-width wrappers or background divs. The Card controls layout.
- **Padding:** Use Card's default padding. Avoid extra padding/margin unless absolutely necessary.

**Example:**
```tsx
<Card style={{ margin: 32 }}>
  <Title level={2}>Page Title</Title>
  {/* Content here */}
</Card>
```

---

## 2. Headings
- **One main heading per page** (`<Title level={2}>`).
- **Section headings:** Use `<Title level={3/4}>` or `<h3>`, but do not repeat headings inside nested components.
- **No duplicate headers:** Only the page should render the main heading, not child components.

---

## 3. Content Structure
- **No nested Cards or Panels.** Only one Card per page.
- **Tables, forms, and buttons** are always inside the main Card.
- **Section wrappers:** Use `<div>` or `<section>` for logical grouping, not for layout.

---

## 4. Buttons and Actions
- **Group actions** at the bottom or top of the Card, not floating or scattered.
- **Consistent spacing** between buttons (e.g., `<Space>` or `style={{ marginRight: 8 }}`).

---

## 5. Color, Background, and Typography
- **Background:** Use the app's default background; do not override inside pages.
- **Text color:** Use Ant Design defaults unless otherwise specified.
- **Font sizes/weights:** Use Ant Design Typography components for headings and text.

---

## 6. Component Usage
- **Card:** Only for the main page container.
- **Table:** Use Ant Design Table, full width inside Card.
- **Tabs:** Place inside Card if needed, with section content below.
- **Empty states:** Use Ant Design's `<Empty />` for no data.
- **Loading:** Use `<Spin />` centered in the Card.

---

## 7. Code Examples

**Page Skeleton:**
```tsx
<Card style={{ margin: 32 }}>
  <Title level={2}>System Configuration</Title>
  {/* Sections, tables, actions here */}
</Card>
```

**Section with Table and Actions:**
```tsx
<Title level={3}>Progression Config</Title>
<Table ... />
<Space style={{ marginTop: 24 }}>
  <Button type="primary">Save</Button>
  <Button>Reset</Button>
</Space>
```

---

## 8. Do & Don't

**Do:**
- Use a single Card per page
- Keep all content left-aligned
- Only one main heading per page
- Group actions together
- Use Ant Design components for consistency

**Don't:**
- Nest Cards, Panels, or Boxes
- Repeat headings in both parent and child components
- Add extra wrappers for layout
- Scatter buttons or actions
- Override background or add unnecessary chrome

---

## 9. Canonical Examples
- **SystemConfig.tsx** and **ScenarioRunner.tsx** (after cleanup) are the reference implementations for layout and structure.

---

## 10. Enforcement
- All new UI work **must** follow these guidelines.
- If you see a violation, refactor to match this guide.
- AI assistants must reference and apply these rules for every UI-related task. 