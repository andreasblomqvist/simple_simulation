# Button Component Migration Guide

## Enhanced Button Features (Phase 1 Foundation)

The Button component has been enhanced with comprehensive design system features while maintaining full backward compatibility.

## New Features Added

### 1. Enhanced Variants
- **Primary**: Main call-to-action buttons with elevation effects
- **Secondary**: Outline buttons with subtle hover states  
- **Ghost**: Minimal buttons for secondary actions
- **Destructive**: For dangerous actions with error colors
- **Outline**: Neutral outlined buttons
- **Link**: Text-only buttons with underline on hover
- **Default**: Backward compatibility alias for primary

### 2. Comprehensive Size System
- **xs**: `h-7 px-2 text-xs` - Compact interfaces
- **sm**: `h-8 px-3 text-sm` - Table actions, toolbars
- **md**: `h-10 px-4 text-sm` - Standard buttons (default)
- **lg**: `h-11 px-6 text-base` - Hero sections, important CTAs
- **xl**: `h-12 px-8 text-lg` - Landing pages, major actions
- **icon**: `h-10 w-10` - Icon-only buttons
- **default**: Backward compatibility alias for md

### 3. Icon Support
```tsx
// Left icon
<Button icon={<Plus />} iconPosition="left">Add Item</Button>

// Right icon  
<Button icon={<ExternalLink />} iconPosition="right">Open</Button>

// Icon only
<Button size="icon"><Settings /></Button>
```

### 4. Loading States
```tsx
<Button loading={isSubmitting}>Save Changes</Button>
```
- Shows spinner animation
- Maintains button dimensions
- Disables interaction
- Preserves original text (hidden during loading)

### 5. Enhanced Properties
```tsx
interface ButtonProps {
  loading?: boolean           // Show loading spinner
  icon?: React.ReactNode     // Icon element
  iconPosition?: 'left' | 'right'  // Icon placement
  fullWidth?: boolean        // 100% width
  rounded?: boolean          // Fully rounded corners
  // ... all existing props maintained
}
```

### 6. Advanced Interaction States
- **Hover**: Elevation changes, color transitions, subtle transform
- **Active**: Press feedback with reduced elevation
- **Focus**: Accessible focus rings using design tokens
- **Disabled**: Proper visual feedback and cursor changes
- **Loading**: Wait cursor and spinner animation

## Backward Compatibility

✅ **Existing code continues to work without changes**

```tsx
// These still work exactly as before:
<Button>Default Button</Button>
<Button variant="default">Legacy Default</Button>
<Button size="default">Legacy Size</Button>
<Button variant="outline">Outline Button</Button>
```

## Design System Integration

### Colors
All colors use design tokens from `design-tokens.css`:
- Primary buttons: `--color-primary-500/600/700`
- Error buttons: `--color-error-500/600/700`  
- Text colors: `--color-gray-*` scale
- Focus rings: Design system compliant

### Animations
- Transitions: `150ms` for interactions, `200ms` for state changes
- Easing: CSS custom properties for consistent motion
- Hover elevation: `-translate-y-0.5` for tactile feedback
- Focus: Accessible focus rings with proper contrast

### Accessibility
- Proper ARIA attributes (`aria-disabled`)
- Focus management with keyboard navigation
- Screen reader support for loading states
- Color contrast compliance (WCAG 2.1 AA)
- Focus rings meet accessibility standards

## Testing

Visit `/button-demo` to see all button features in action:
- All variants and sizes
- Loading state demonstrations  
- Icon positioning examples
- Interactive state previews
- Theme compatibility testing
- Common usage pattern examples

## Performance

- No breaking changes to existing performance
- Lucide React icons are tree-shakable
- CSS classes are optimized with Tailwind
- Loading spinners use efficient CSS animations
- Design tokens enable runtime theme switching

## Migration Recommendations

### For New Development
```tsx
// Preferred for new code
<Button variant="primary" size="lg" icon={<Plus />}>
  Create Scenario
</Button>

// Instead of generic
<Button>Create Scenario</Button>
```

### Component Updates (Optional)
1. Replace `variant="default"` with `variant="primary"` 
2. Replace `size="default"` with `size="md"`
3. Add appropriate icons for better UX
4. Use loading states for async actions

### Design System Alignment
- Use semantic variants (primary/secondary vs default)
- Consistent sizing across similar UI contexts
- Appropriate icons for actions (Plus for create, etc.)
- Loading states for all async operations

## Future Enhancements (Phase 2+)
- Destructive confirmation patterns
- Advanced animation presets
- Button groups and toolbars
- Keyboard shortcuts integration
- Toast notification integration for actions

The enhanced Button component serves as the foundation for the unified SimpleSim design system while ensuring zero disruption to existing functionality.