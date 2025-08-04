# Layout Composition Patterns - SimpleSim Design System

## Desktop Layouts, Component Composition, and Page Templates

### **Layout Philosophy**

#### **Desktop-First Approach**
SimpleSim is optimized for desktop workflow at 1024px+ screen widths with progressive enhancement for smaller screens.

#### **Grid-Based Foundation**
All layouts use a consistent 12-column grid system with standard breakpoints and predictable spacing.

#### **Component Composition**
Layouts are assembled from reusable, composable components that maintain consistency across the application.

---

## **Grid System**

### **Grid Specifications**
```typescript
interface GridSystem {
  columns: 12
  gutters: {
    xs: '16px'  // 0-640px
    sm: '24px'  // 641-768px  
    md: '32px'  // 769-1024px
    lg: '40px'  // 1025-1440px
    xl: '48px'  // 1441px+
  }
  maxWidth: {
    sm: '640px'
    md: '768px' 
    lg: '1024px'
    xl: '1280px'
    xxl: '1536px'
  }
  breakpoints: {
    sm: '640px'
    md: '768px'
    lg: '1024px'
    xl: '1280px'
    xxl: '1536px'
  }
}
```

### **Container Patterns**
```typescript
interface ContainerTypes {
  // Full width container
  fluid: {
    width: '100%'
    padding: 'gutter-size'
    maxWidth: 'none'
  }
  
  // Centered container with max width
  constrained: {
    width: '100%'
    padding: 'gutter-size'
    maxWidth: '1280px'
    margin: '0 auto'
  }
  
  // Content-width container
  content: {
    width: '100%'
    padding: 'gutter-size'
    maxWidth: '768px'
    margin: '0 auto'
  }
}
```

---

## **Application Shell Layout**

### **Shell Structure**
```typescript
interface ApplicationShell {
  structure: {
    header: {
      height: '64px'
      position: 'fixed'
      zIndex: 1000
      background: 'white'
      borderBottom: '1px solid gray-200'
    }
    contextBar: {
      height: '56px'
      position: 'sticky'
      top: '64px'
      background: 'gray-50'
      borderBottom: '1px solid gray-200'
    }
    main: {
      paddingTop: '120px' // header + context bar
      minHeight: 'calc(100vh - 120px)'
      background: 'white'
    }
    footer: {
      height: '48px'
      background: 'gray-50'
      borderTop: '1px solid gray-200'
      marginTop: 'auto'
    }
  }
}
```

### **Header Composition**
```typescript
interface HeaderLayout {
  structure: 'logo | navigation | spacer | actions | user-menu'
  
  components: {
    logo: {
      width: '200px'
      flexShrink: 0
    }
    navigation: {
      flex: '1'
      maxWidth: '600px'
      display: 'flex'
      gap: '32px'
    }
    spacer: {
      flex: '1'
    }
    actions: {
      display: 'flex'
      gap: '16px'
      alignItems: 'center'
    }
    userMenu: {
      width: '200px'
      flexShrink: 0
      textAlign: 'right'
    }
  }
}
```

### **Context Bar Layout**
```typescript
interface ContextBarLayout {
  structure: 'breadcrumb | spacer | filters | actions'
  
  components: {
    breadcrumb: {
      flex: '1'
      minWidth: '200px'
    }
    spacer: {
      flex: '1'
    }
    filters: {
      display: 'flex'
      gap: '12px'
      alignItems: 'center'
    }
    actions: {
      display: 'flex'
      gap: '8px'
      alignItems: 'center'
    }
  }
}
```

---

## **Page Layout Templates**

### **1. Dashboard Layout**
```typescript
interface DashboardLayout {
  structure: {
    type: 'dashboard'
    grid: '12-column'
    areas: [
      'kpi-row: 12 columns',
      'charts-row: 8 columns + 4 columns',
      'table-row: 12 columns'
    ]
  }
  
  composition: {
    kpiRow: {
      display: 'grid'
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))'
      gap: '24px'
      marginBottom: '32px'
    }
    chartsRow: {
      display: 'grid'
      gridTemplateColumns: '2fr 1fr'
      gap: '24px'
      marginBottom: '32px'
    }
    tableRow: {
      display: 'block'
    }
  }
  
  responsive: {
    mobile: {
      kpiRow: 'single column'
      chartsRow: 'stack vertically'
      tableRow: 'horizontal scroll'
    }
  }
}
```

### **2. List View Layout**
```typescript
interface ListViewLayout {
  structure: {
    type: 'list'
    grid: '12-column'
    areas: [
      'filters-bar: 12 columns',
      'content-area: 12 columns'
    ]
  }
  
  composition: {
    filtersBar: {
      display: 'flex'
      justifyContent: 'space-between'
      alignItems: 'center'
      padding: '16px 0'
      borderBottom: '1px solid gray-200'
      marginBottom: '24px'
    }
    contentArea: {
      display: 'flex'
      flexDirection: 'column'
      gap: '16px'
    }
  }
  
  variants: {
    withSidebar: {
      contentArea: {
        display: 'grid'
        gridTemplateColumns: '280px 1fr'
        gap: '32px'
      }
    }
    cardGrid: {
      contentArea: {
        display: 'grid'
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))'
        gap: '24px'
      }
    }
  }
}
```

### **3. Detail View Layout**
```typescript
interface DetailViewLayout {
  structure: {
    type: 'detail'
    grid: '12-column'
    areas: [
      'header-section: 12 columns',
      'content-section: 8 columns + 4 columns sidebar'
    ]
  }
  
  composition: {
    headerSection: {
      display: 'flex'
      justifyContent: 'space-between'
      alignItems: 'flex-start'
      padding: '24px 0'
      borderBottom: '1px solid gray-200'
      marginBottom: '32px'
    }
    contentSection: {
      display: 'grid'
      gridTemplateColumns: '1fr 320px'
      gap: '40px'
    }
  }
  
  responsive: {
    tablet: {
      contentSection: 'stack vertically, sidebar becomes full width'
    }
  }
}
```

### **4. Form Layout**
```typescript
interface FormLayout {
  structure: {
    type: 'form'
    grid: '12-column'
    areas: [
      'form-header: 12 columns',
      'form-content: 8 columns centered'
    ]
  }
  
  composition: {
    formHeader: {
      textAlign: 'center'
      padding: '32px 0'
      borderBottom: '1px solid gray-200'
      marginBottom: '40px'
    }
    formContent: {
      maxWidth: '600px'
      margin: '0 auto'
      padding: '0 24px'
    }
  }
  
  fieldLayouts: {
    singleColumn: {
      display: 'flex'
      flexDirection: 'column'
      gap: '24px'
    }
    twoColumn: {
      display: 'grid'
      gridTemplateColumns: '1fr 1fr'
      gap: '24px'
    }
    fieldGroup: {
      display: 'flex'
      flexDirection: 'column'
      gap: '16px'
      padding: '24px'
      border: '1px solid gray-200'
      borderRadius: '8px'
    }
  }
}
```

### **5. Editor Layout**
```typescript
interface EditorLayout {
  structure: {
    type: 'editor'
    grid: 'custom-areas'
    areas: [
      'toolbar: full width',
      'content: full width, scrollable'
    ]
  }
  
  composition: {
    toolbar: {
      position: 'sticky'
      top: '120px' // below header + context bar
      background: 'white'
      borderBottom: '1px solid gray-200'
      padding: '12px 0'
      zIndex: 10
    }
    content: {
      padding: '24px'
      minHeight: 'calc(100vh - 200px)'
    }
  }
  
  variants: {
    splitView: {
      content: {
        display: 'grid'
        gridTemplateColumns: '1fr 1fr'
        gap: '1px'
        background: 'gray-200'
      }
    }
    withPreview: {
      content: {
        display: 'grid'
        gridTemplateColumns: '1fr 400px'
        gap: '24px'
      }
    }
  }
}
```

---

## **Component Composition Patterns**

### **Card Composition**
```typescript
interface CardComposition {
  structure: 'header | body | footer'
  
  variants: {
    basic: {
      padding: '24px'
      border: '1px solid gray-200'
      borderRadius: '8px'
      background: 'white'
    }
    elevated: {
      padding: '24px'
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      borderRadius: '8px'
      background: 'white'
    }
    bordered: {
      padding: '24px'
      border: '2px solid primary-200'
      borderRadius: '8px'  
      background: 'primary-25'
    }
  }
  
  composition: {
    header: {
      display: 'flex'
      justifyContent: 'space-between'
      alignItems: 'center'
      marginBottom: '16px'
      paddingBottom: '16px'
      borderBottom: '1px solid gray-200'
    }
    body: {
      flex: '1'
    }
    footer: {
      display: 'flex'
      justifyContent: 'flex-end'
      gap: '12px'
      marginTop: '24px'
      paddingTop: '16px'
      borderTop: '1px solid gray-200'
    }
  }
}
```

### **Panel Composition**
```typescript
interface PanelComposition {
  structure: 'panel-header | panel-content'
  
  variants: {
    collapsible: {
      header: {
        cursor: 'pointer'
        userSelect: 'none'
        showChevron: true
      }
      content: {
        overflow: 'hidden'
        transition: 'max-height 200ms ease'
      }
    }
    fixed: {
      header: {
        cursor: 'default'
      }
      content: {
        display: 'block'
      }
    }
  }
  
  composition: {
    panelHeader: {
      display: 'flex'
      justifyContent: 'space-between'
      alignItems: 'center'
      padding: '16px 20px'
      background: 'gray-50'
      borderBottom: '1px solid gray-200'
      fontWeight: '600'
    }
    panelContent: {
      padding: '20px'
    }
  }
}
```

### **Table Composition**
```typescript
interface TableComposition {
  structure: 'table-header | table-body | table-footer'
  
  composition: {
    tableContainer: {
      border: '1px solid gray-200'
      borderRadius: '8px'
      overflow: 'hidden'
    }
    tableHeader: {
      background: 'gray-50'
      borderBottom: '1px solid gray-200'
      position: 'sticky'
      top: '0'
      zIndex: 1
    }
    tableBody: {
      background: 'white'
    }
    tableFooter: {
      background: 'gray-50'
      borderTop: '1px solid gray-200'
      padding: '12px 16px'
    }
  }
  
  cellTypes: {
    data: {
      padding: '12px 16px'
      textAlign: 'left'
      verticalAlign: 'middle'
    }
    numeric: {
      padding: '12px 16px'
      textAlign: 'right'
      fontFamily: 'mono'
    }
    action: {
      padding: '8px'
      textAlign: 'center'
      width: '80px'
    }
  }
}
```

---

## **Spacing and Rhythm**

### **Vertical Rhythm**
```typescript
interface VerticalRhythm {
  baselineGrid: '8px'
  
  spacing: {
    xs: '4px'   // 0.5 × baseline
    sm: '8px'   // 1 × baseline  
    md: '16px'  // 2 × baseline
    lg: '24px'  // 3 × baseline
    xl: '32px'  // 4 × baseline
    xxl: '48px' // 6 × baseline
    xxxl: '64px' // 8 × baseline
  }
  
  usage: {
    componentGaps: 'md (16px)'
    sectionGaps: 'xl (32px)'
    pageGaps: 'xxl (48px)'
    containerPadding: 'lg (24px)'
    cardPadding: 'lg (24px)'
    modalPadding: 'xl (32px)'
  }
}
```

### **Horizontal Spacing**
```typescript
interface HorizontalSpacing {
  contentPadding: {
    mobile: '16px'
    tablet: '24px'
    desktop: '32px'
    wide: '40px'
  }
  
  componentGaps: {
    tight: '8px'
    normal: '16px'
    loose: '24px'
    extraLoose: '32px'
  }
  
  buttonSpacing: {
    internal: '16px 24px' // padding
    external: '8px'       // gap between buttons
  }
}
```

---

## **Layout Components**

### **Stack Component**
```typescript
interface StackComponent {
  purpose: 'Vertical layout with consistent spacing'
  
  props: {
    gap: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
    align: 'start' | 'center' | 'end' | 'stretch'
    justify: 'start' | 'center' | 'end' | 'space-between'
  }
  
  usage: `
    <Stack gap="lg" align="center">
      <Heading>Page Title</Heading>
      <Text>Description</Text>
      <Button>Primary Action</Button>
    </Stack>
  `
}
```

### **Grid Component**
```typescript
interface GridComponent {
  purpose: 'CSS Grid layout with responsive columns'
  
  props: {
    columns: number | 'auto-fit' | 'auto-fill'
    gap: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
    minItemWidth: string // for auto-fit/auto-fill
  }
  
  usage: `
    <Grid columns="auto-fit" minItemWidth="300px" gap="lg">
      <Card>Item 1</Card>
      <Card>Item 2</Card>
      <Card>Item 3</Card>
    </Grid>
  `
}
```

### **Container Component**
```typescript
interface ContainerComponent {
  purpose: 'Consistent page-level containers'
  
  props: {
    size: 'fluid' | 'constrained' | 'content'
    padding: boolean
  }
  
  usage: `
    <Container size="constrained" padding>
      <PageContent />
    </Container>
  `
}
```

---

## **Responsive Behavior**

### **Breakpoint Strategy**
```typescript
interface ResponsiveStrategy {
  approach: 'mobile-first with desktop optimization'
  
  behavior: {
    desktop: {
      range: '1024px+'
      layout: 'full multi-column layouts'
      navigation: 'horizontal navigation bar'
      interactions: 'hover states, complex interactions'
    }
    tablet: {
      range: '768px-1023px'
      layout: 'simplified multi-column'
      navigation: 'horizontal with possible overflow'
      interactions: 'touch-friendly sizing'
    }
    mobile: {
      range: '0-767px'
      layout: 'single column, stacked'
      navigation: 'hamburger menu'
      interactions: 'large touch targets'
    }
  }
}
```

### **Component Responsive Patterns**
```typescript
interface ResponsivePatterns {
  // Grid becomes stack on mobile
  gridToStack: {
    desktop: 'display: grid; grid-template-columns: repeat(3, 1fr)'
    mobile: 'display: flex; flex-direction: column'
  }
  
  // Hide elements on smaller screens
  progressiveDisclosure: {
    desktop: 'display: flex'
    tablet: 'display: none' // hide secondary actions
    mobile: 'display: none'
  }
  
  // Resize text for readability
  fluidTypography: {
    desktop: 'font-size: 1.5rem'
    tablet: 'font-size: 1.25rem'
    mobile: 'font-size: 1.125rem'
  }
}
```

---

## **Layout Utilities**

### **CSS Utility Classes**
```css
/* Spacing utilities */
.space-y-sm > * + * { margin-top: 8px; }
.space-y-md > * + * { margin-top: 16px; }
.space-y-lg > * + * { margin-top: 24px; }

/* Flexbox utilities */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }

/* Grid utilities */
.grid { display: grid; }
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
.col-span-6 { grid-column: span 6; }

/* Container utilities */
.container { max-width: 1280px; margin: 0 auto; padding: 0 32px; }
.container-fluid { width: 100%; padding: 0 32px; }
```

### **Layout Testing**
```typescript
interface LayoutTesting {
  visualRegression: 'Screenshot testing at different breakpoints'
  accessibility: 'Keyboard navigation and screen reader testing'
  performance: 'Layout shift and rendering performance'
  crossBrowser: 'Layout consistency across browsers'
}
```

---

## **Implementation Guidelines**

### **Component Library Structure**
```
components/
├── layout/
│   ├── Container.tsx
│   ├── Stack.tsx
│   ├── Grid.tsx
│   └── Spacer.tsx
├── templates/
│   ├── DashboardTemplate.tsx
│   ├── ListViewTemplate.tsx
│   ├── DetailViewTemplate.tsx
│   ├── FormTemplate.tsx
│   └── EditorTemplate.tsx
└── shell/
    ├── ApplicationShell.tsx
    ├── Header.tsx
    ├── ContextBar.tsx
    └── Footer.tsx
```

### **Usage Patterns**
1. **Start with template** - Choose appropriate page template
2. **Apply layout components** - Use Stack, Grid, Container for structure  
3. **Add content components** - Cards, Tables, Forms within layout
4. **Test responsiveness** - Verify behavior at all breakpoints
5. **Validate accessibility** - Ensure keyboard navigation works

### **Performance Considerations**
- **CSS Grid** preferred over Flexbox for complex layouts
- **Sticky positioning** for headers and toolbars
- **Container queries** for component-level responsive design
- **Layout shifting** prevention with explicit dimensions