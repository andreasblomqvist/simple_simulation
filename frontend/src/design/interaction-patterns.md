# Interaction Patterns - SimpleSim Design System

## Micro-Interactions, Hover States, and UI Behavior Patterns

### **Core Interaction Principles**

#### **1. Immediate Feedback**
Every user action receives immediate visual acknowledgment within 100ms.

#### **2. Predictable Behavior**
Similar interactions behave consistently across the entire application.

#### **3. Reduced Cognitive Load**
Interactions guide users toward successful task completion without confusion.

#### **4. Graceful Degradation**
Interactions work progressively, with fallbacks for reduced capabilities.

---

## **Button Interactions**

### **Primary Button States**
```typescript
interface ButtonStates {
  default: {
    background: 'primary-500'
    color: 'white'
    border: 'none'
    shadow: 'sm'
    transition: 'all 150ms ease'
  }
  hover: {
    background: 'primary-600'
    shadow: 'md'
    transform: 'translateY(-1px)'
    transition: 'all 150ms ease'
  }
  active: {
    background: 'primary-700'
    shadow: 'sm'
    transform: 'translateY(0px)'
    transition: 'all 100ms ease'
  }
  disabled: {
    background: 'gray-300'
    color: 'gray-500'
    cursor: 'not-allowed'
    shadow: 'none'
    transform: 'none'
  }
  loading: {
    background: 'primary-500'
    color: 'transparent'
    cursor: 'wait'
    content: 'spinner-animation'
  }
}
```

### **Secondary Button States**
```typescript
interface SecondaryButtonStates {
  default: {
    background: 'transparent'
    color: 'primary-600'
    border: '1px solid primary-300'
    transition: 'all 150ms ease'
  }
  hover: {
    background: 'primary-50'
    border: '1px solid primary-400'
    transform: 'translateY(-1px)'
  }
  active: {
    background: 'primary-100'
    border: '1px solid primary-500'
    transform: 'translateY(0px)'
  }
}
```

### **Destructive Button States**
```typescript
interface DestructiveButtonStates {
  default: {
    background: 'error-500'
    color: 'white'
    requiresConfirmation: true
  }
  hover: {
    background: 'error-600'
    shadow: 'md'
    showWarningIcon: true
  }
  confirmation: {
    background: 'error-700'
    text: 'Click again to confirm'
    countdown: '3 seconds'
  }
}
```

---

## **Form Interactions**

### **Input Field States**
```typescript
interface InputFieldStates {
  default: {
    border: '1px solid gray-300'
    background: 'white'
    placeholder: 'gray-400'
    transition: 'all 200ms ease'
  }
  focus: {
    border: '2px solid primary-500'
    boxShadow: '0 0 0 3px primary-100'
    outline: 'none'
    background: 'white'
  }
  error: {
    border: '2px solid error-500'
    boxShadow: '0 0 0 3px error-100'
    background: 'error-25'
    showErrorIcon: true
  }
  success: {
    border: '2px solid success-500'
    boxShadow: '0 0 0 3px success-100'
    showSuccessIcon: true
  }
  disabled: {
    background: 'gray-100'
    color: 'gray-500'
    cursor: 'not-allowed'
    border: '1px solid gray-200'
  }
}
```

### **Real-Time Validation**
```typescript
interface ValidationBehavior {
  onBlur: {
    timing: 'When user leaves field'
    behavior: 'Validate and show errors immediately'
    visual: 'Error state with message below field'
  }
  onType: {
    timing: 'After 500ms pause in typing'
    behavior: 'Show success state when valid'
    visual: 'Success icon and green border'
  }
  onSubmit: {
    timing: 'When form is submitted'
    behavior: 'Focus first error field'
    visual: 'Scroll to error and highlight'
  }
}
```

### **Auto-Save Behavior**
```typescript
interface AutoSaveBehavior {
  trigger: {
    timing: '2 seconds after last change'
    conditions: 'Field is valid and has changed'
  }
  feedback: {
    visual: 'Subtle "Saved" indicator appears briefly'
    duration: '2 seconds fade out'
    location: 'Adjacent to saved field'
  }
  error: {
    visual: 'Warning icon with retry option'
    behavior: 'Allow manual save attempt'
    message: 'Auto-save failed. Click to retry.'
  }
}
```

---

## **Table Interactions**

### **Row Interactions**
```typescript
interface TableRowStates {
  default: {
    background: 'white'
    borderBottom: '1px solid gray-200'
  }
  hover: {
    background: 'primary-25'
    cursor: 'pointer'
    transition: 'background 150ms ease'
  }
  selected: {
    background: 'primary-50'
    borderLeft: '3px solid primary-500'
    showActions: true
  }
  editing: {
    background: 'warning-25'
    border: '2px solid warning-300'
    showSaveCancel: true
  }
}
```

### **Cell Editing Pattern**
```typescript
interface CellEditingBehavior {
  singleClick: {
    action: 'Select row'
    visual: 'Highlight entire row'
  }
  doubleClick: {
    action: 'Enter edit mode'
    visual: 'Replace cell content with input field'
    focus: 'Auto-focus input and select all text'
  }
  keyboardTrigger: {
    key: 'Enter or F2'
    action: 'Enter edit mode for focused cell'
  }
  saveActions: {
    enter: 'Save and move to next row'
    tab: 'Save and move to next cell'
    escape: 'Cancel and revert changes'
  }
}
```

### **Bulk Selection**
```typescript
interface BulkSelectionBehavior {
  headerCheckbox: {
    unchecked: 'Select all visible rows'
    checked: 'Deselect all rows'
    indeterminate: 'Some rows selected, click to select all'
  }
  rowSelection: {
    click: 'Toggle row selection'
    shiftClick: 'Select range from last selected to current'
    ctrlClick: 'Add/remove from selection'
  }
  bulkActions: {
    trigger: 'Show when > 0 rows selected'
    position: 'Context bar above table'
    actions: ['Edit selected', 'Delete selected', 'Export selected']
  }
}
```

---

## **Navigation Interactions**

### **Tab Navigation**
```typescript
interface TabBehavior {
  default: {
    background: 'transparent'
    borderBottom: '2px solid transparent'
    color: 'gray-600'
    cursor: 'pointer'
  }
  hover: {
    color: 'primary-600'
    borderBottom: '2px solid primary-200'
  }
  active: {
    color: 'primary-700'
    borderBottom: '2px solid primary-500'
    fontWeight: '600'
  }
  disabled: {
    color: 'gray-400'
    cursor: 'not-allowed'
    showTooltip: 'Reason why disabled'
  }
}
```

### **Context Switching**
```typescript
interface ContextSwitchingBehavior {
  trigger: {
    element: 'Dropdown next to page title'
    shortcut: 'Cmd+Shift+O (for office switching)'
  }
  display: {
    maxItems: 10
    grouping: 'By type (Recent, Favorites, All)'
    search: 'Fuzzy search with keyboard navigation'
  }
  selection: {
    mouse: 'Click to switch context'
    keyboard: 'Arrow keys + Enter'
    recent: 'Show recently accessed contexts first'
  }
}
```

---

## **Modal and Dialog Interactions**

### **Modal Behavior**
```typescript
interface ModalBehavior {
  opening: {
    animation: 'Fade in background, scale up modal'
    duration: '200ms ease-out'
    focus: 'Auto-focus first interactive element'
  }
  closing: {
    triggers: ['Escape key', 'Click backdrop', 'Close button']
    animation: 'Scale down modal, fade out background'
    duration: '150ms ease-in'
  }
  keyboard: {
    tab: 'Cycle through modal elements only'
    escape: 'Close modal'
    enter: 'Activate default action (usually Save/OK)'
  }
}
```

### **Confirmation Dialogs**
```typescript
interface ConfirmationBehavior {
  destructive: {
    title: 'Clear action description'
    description: 'Explain consequences'
    primaryButton: {
      text: 'Specific action (e.g., "Delete Office")'
      color: 'error'
      requiresDelay: '2 seconds before enabling'
    }
    secondaryButton: {
      text: 'Cancel'
      color: 'neutral'
      autoFocus: true
    }
  }
  nonDestructive: {
    primaryButton: {
      text: 'Confirm action'
      color: 'primary'
      autoFocus: true
    }
  }
}
```

---

## **Loading and Progress Interactions**

### **Loading States**
```typescript
interface LoadingBehavior {
  immediate: {
    trigger: '< 100ms operations'
    visual: 'No loading indicator'
  }
  short: {
    trigger: '100ms - 2s operations'
    visual: 'Spinner on triggering element'
    behavior: 'Disable element during loading'
  }
  medium: {
    trigger: '2s - 10s operations'
    visual: 'Progress bar with percentage'
    behavior: 'Show estimated time remaining'
  }
  long: {
    trigger: '> 10s operations'
    visual: 'Progress bar + status messages'
    behavior: 'Allow cancellation'
  }
}
```

### **Skeleton Loading**
```typescript
interface SkeletonBehavior {
  usage: 'For content areas while data loads'
  animation: 'Subtle shimmer effect'
  shape: 'Approximates final content layout'
  timing: 'Show after 200ms delay to avoid flash'
}
```

---

## **Drag and Drop Interactions**

### **Drag Behavior**
```typescript
interface DragBehavior {
  dragStart: {
    visual: 'Reduce opacity to 70%'
    cursor: 'grabbing'
    ghost: 'Semi-transparent copy follows cursor'
  }
  dragOver: {
    validTarget: {
      background: 'primary-100'
      border: '2px dashed primary-400'
      cursor: 'copy'
    }
    invalidTarget: {
      cursor: 'not-allowed'
      showIndicator: 'Red X or prohibition sign'
    }
  }
  drop: {
    success: {
      animation: 'Brief green flash'
      feedback: 'Success toast notification'
    }
    failure: {
      animation: 'Shake effect'
      feedback: 'Error message with reason'
    }
  }
}
```

---

## **Search and Filter Interactions**

### **Search Behavior**
```typescript
interface SearchBehavior {
  input: {
    placeholder: 'Search scenarios, offices, results...'
    minLength: 2
    debounce: '300ms'
  }
  results: {
    instant: 'Show results as user types'
    grouping: 'Group by content type'
    highlighting: 'Highlight matching terms'
    emptyState: 'Suggest alternative searches'
  }
  keyboard: {
    arrowKeys: 'Navigate through results'
    enter: 'Select highlighted result'
    escape: 'Clear search and close results'
  }
}
```

### **Filter Interactions**
```typescript
interface FilterBehavior {
  application: {
    timing: 'Apply immediately on selection'
    visual: 'Show active filters as removable chips'
    feedback: 'Update result count in real-time'
  }
  clearing: {
    individual: 'X button on each filter chip'
    all: 'Clear all filters button'
    confirmation: 'None required for filters'
  }
  combinations: {
    behavior: 'Filters are additive (AND logic)'
    visual: 'Show relationship between filters'
  }
}
```

---

## **Notification and Feedback Patterns**

### **Toast Notifications**
```typescript
interface ToastBehavior {
  success: {
    duration: '4 seconds'
    color: 'success'
    icon: 'checkmark'
    action: 'Optional undo action'
  }
  error: {
    duration: 'Persistent until dismissed'
    color: 'error'
    icon: 'alert-circle'
    action: 'Required dismiss button'
  }
  warning: {
    duration: '6 seconds'
    color: 'warning'
    icon: 'alert-triangle'
    action: 'Optional action button'
  }
  info: {
    duration: '5 seconds'
    color: 'primary'
    icon: 'info'
    action: 'Optional learn more link'
  }
}
```

### **Inline Validation Messages**
```typescript
interface InlineValidationBehavior {
  error: {
    position: 'Below field'
    color: 'error-600'
    icon: 'alert-circle'
    animation: 'Slide down + fade in'
  }
  success: {
    position: 'Icon in field'
    color: 'success-500'
    icon: 'checkmark'
    animation: 'Scale in'
  }
  warning: {
    position: 'Below field'
    color: 'warning-600'
    icon: 'alert-triangle'
    animation: 'Slide down + fade in'
  }
}
```

---

## **Accessibility Interactions**

### **Keyboard Navigation**
```typescript
interface KeyboardBehavior {
  tab: {
    order: 'Logical visual order'
    indicators: 'Clear focus indicators'
    skip: 'Skip links for repetitive navigation'
  }
  shortcuts: {
    global: {
      'Cmd+K': 'Global search'
      'Cmd+N': 'New scenario'
      'Cmd+S': 'Save current work'
      'Esc': 'Close modal/cancel action'
    }
    contextual: {
      'Enter': 'Activate primary action'
      'Space': 'Select/toggle'
      'Arrow keys': 'Navigate within components'
    }
  }
}
```

### **Screen Reader Interactions**
```typescript
interface ScreenReaderBehavior {
  announcements: {
    pageLoad: 'Announce page title and primary heading'
    dynamicContent: 'Announce when content changes'
    errors: 'Announce errors immediately'
    success: 'Announce successful actions'
  }
  landmarks: {
    navigation: 'Mark navigation areas'
    main: 'Mark main content area'
    search: 'Mark search functionality'
    forms: 'Label all form sections'
  }
}
```

---

## **Animation and Transition Guidelines**

### **Motion Principles**
```typescript
interface MotionPrinciples {
  purposeful: 'Every animation serves a functional purpose'
  performant: 'Use CSS transforms for smooth 60fps animations'
  respectful: 'Honor reduced motion preferences'
  subtle: 'Enhance without distracting'
}
```

### **Standard Durations**
```typescript
interface AnimationDurations {
  immediate: '0ms'      // State changes like focus
  fast: '100ms'         // Hover effects, button presses
  normal: '200ms'       // Modal open/close, panel expansion
  slow: '400ms'         // Page transitions, complex animations
  very_slow: '600ms+'   // Only for decorative or onboarding
}
```

### **Easing Functions**
```typescript
interface EasingFunctions {
  ease_out: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' // Default for entrances
  ease_in: 'cubic-bezier(0.55, 0.06, 0.68, 0.19)'  // For exits
  ease_in_out: 'cubic-bezier(0.26, 0.08, 0.25, 1)' // For bi-directional
}
```

---

## **Implementation Guidelines**

### **CSS Custom Properties for States**
```css
:root {
  --transition-fast: 100ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 400ms ease;
  
  --shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-active: 0 2px 4px rgba(0, 0, 0, 0.12);
  
  --focus-ring: 0 0 0 3px var(--primary-100);
}
```

### **React Interaction Hooks**
```typescript
// Custom hooks for consistent interactions
const useHoverState = () => { /* implementation */ }
const useFocusState = () => { /* implementation */ }
const useLoadingState = () => { /* implementation */ }
const useKeyboardShortcuts = () => { /* implementation */ }
```

### **Testing Interaction Patterns**
- **Visual regression testing** for all interactive states
- **Keyboard navigation testing** for accessibility compliance  
- **Performance testing** for animation smoothness
- **User testing** for interaction intuitiveness