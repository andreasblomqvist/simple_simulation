# Component API Specifications

## Design System Component Architecture

### **Component Hierarchy Philosophy**

```typescript
// Base Component Pattern
interface BaseComponentProps {
  className?: string
  children?: ReactNode
  testId?: string
  'aria-label'?: string
}

// Composable Pattern - Build complex components from simple ones
// Example: DataTable = Table + TableHeader + TableBody + TableRow + TableCell
```

### **Component Categories**

1. **Primitives** - Basic building blocks (Button, Input, Text)
2. **Composites** - Combined primitives (Form, Modal, DataTable) 
3. **Layouts** - Structural components (Container, Grid, Stack)
4. **Patterns** - Complete UI patterns (PageHeader, ActionBar, StatsGrid)

## Primitive Components

### **Button Component**

```typescript
interface ButtonProps extends BaseComponentProps {
  // Visual variants
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  
  // States
  loading?: boolean
  disabled?: boolean
  
  // Content
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
  children: ReactNode
  
  // Behavior
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void
  type?: 'button' | 'submit' | 'reset'
  
  // Advanced
  fullWidth?: boolean
  rounded?: boolean
}

// Usage Examples
<Button variant="primary" size="lg" loading={isSubmitting}>
  Create Scenario
</Button>

<Button variant="ghost" icon={<Settings />} iconPosition="left">
  Configure
</Button>

<Button variant="destructive" onClick={handleDelete}>
  Delete Office
</Button>
```

### **Input Component**

```typescript
interface InputProps extends BaseComponentProps {
  // Field definition
  type?: 'text' | 'email' | 'password' | 'number' | 'search' | 'tel' | 'url'
  name?: string
  value?: string | number
  defaultValue?: string | number
  
  // Behavior
  onChange?: (value: string, event: ChangeEvent<HTMLInputElement>) => void
  onBlur?: (event: FocusEvent<HTMLInputElement>) => void
  onFocus?: (event: FocusEvent<HTMLInputElement>) => void
  
  // Validation
  required?: boolean
  error?: string
  success?: string
  
  // Appearance
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'filled' | 'borderless'
  
  // Content
  placeholder?: string
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
  
  // States
  disabled?: boolean
  readonly?: boolean
  loading?: boolean
  
  // Constraints
  min?: number
  max?: number
  step?: number
  pattern?: string
  maxLength?: number
}

// Usage Examples
<Input 
  type="number"
  value={fte}
  onChange={(value) => setFte(Number(value))}
  placeholder="Full-time employees"
  error={validation.fte}
  min={0}
  max={999}
/>

<Input 
  type="search"
  placeholder="Search offices..."
  icon={<Search />}
  iconPosition="left"
/>
```

### **Select Component**

```typescript
interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
  description?: string
}

interface SelectProps extends BaseComponentProps {
  // Options
  options: SelectOption[]
  value?: string | number
  defaultValue?: string | number
  
  // Behavior
  onChange?: (value: string | number, option: SelectOption) => void
  onOpen?: () => void
  onClose?: () => void
  
  // Appearance
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'filled'
  
  // Content
  placeholder?: string
  icon?: ReactNode
  
  // States
  disabled?: boolean
  loading?: boolean
  error?: string
  
  // Features
  searchable?: boolean
  clearable?: boolean
  multiple?: boolean
  maxHeight?: number
}

// Usage Examples
<Select 
  options={officeOptions}
  value={selectedOffice}
  onChange={setSelectedOffice}
  placeholder="Select office..."
  searchable
  clearable
/>

<Select 
  options={roleOptions}
  value={selectedRoles}
  onChange={setSelectedRoles}
  multiple
  placeholder="Select roles..."
/>
```

## Composite Components

### **Form Component System**

```typescript
interface FormProps extends BaseComponentProps {
  // Form behavior
  onSubmit?: (data: FormData, event: FormEvent) => void | Promise<void>
  onChange?: (data: Partial<FormData>) => void
  
  // Validation
  validationSchema?: ValidationSchema
  validateOnChange?: boolean
  validateOnBlur?: boolean
  
  // State
  initialValues?: Partial<FormData>
  loading?: boolean
  disabled?: boolean
  
  // Layout
  layout?: 'vertical' | 'horizontal' | 'inline'
  spacing?: 'sm' | 'md' | 'lg'
  
  children: ReactNode
}

interface FormFieldProps extends BaseComponentProps {
  // Field definition
  name: string
  label?: string
  description?: string
  required?: boolean
  
  // Layout
  layout?: 'vertical' | 'horizontal'
  labelWidth?: string
  
  children: ReactNode
}

interface FormSectionProps extends BaseComponentProps {
  title?: string
  description?: string
  collapsible?: boolean
  defaultCollapsed?: boolean
  
  children: ReactNode
}

// Usage Example
<Form onSubmit={handleSubmit} validationSchema={schema}>
  <FormSection title="Basic Information">
    <FormField name="name" label="Scenario Name" required>
      <Input placeholder="Enter scenario name..." />
    </FormField>
    
    <FormField name="description" label="Description">
      <Textarea placeholder="Describe this scenario..." />
    </FormField>
  </FormSection>
  
  <FormSection title="Configuration">
    <FormField name="offices" label="Offices" required>
      <Select options={officeOptions} multiple />
    </FormField>
  </FormSection>
</Form>
```

### **DataTable Component**

```typescript
interface Column<T> {
  id: string
  header: string | ReactNode
  accessorKey?: keyof T
  accessor?: (row: T) => any
  cell?: (info: CellContext<T>) => ReactNode
  
  // Behavior
  sortable?: boolean
  searchable?: boolean
  
  // Appearance
  width?: number | string
  minWidth?: number
  maxWidth?: number
  align?: 'left' | 'center' | 'right'
  
  // Advanced
  sticky?: boolean
  resizable?: boolean
}

interface DataTableProps<T> extends BaseComponentProps {
  // Data
  data: T[]
  columns: Column<T>[]
  
  // Behavior
  onRowClick?: (row: T, index: number) => void
  onSelectionChange?: (selectedRows: T[]) => void
  
  // Features
  sortable?: boolean
  searchable?: boolean
  filterable?: boolean
  selectable?: boolean | 'single' | 'multiple'
  
  // Pagination
  pagination?: boolean
  pageSize?: number
  currentPage?: number
  onPageChange?: (page: number) => void
  
  // Search
  searchValue?: string
  onSearchChange?: (value: string) => void
  searchPlaceholder?: string
  
  // Appearance
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'striped' | 'bordered'
  
  // States
  loading?: boolean
  error?: string
  
  // Empty state
  emptyState?: ReactNode
}

// Usage Example
<DataTable
  data={scenarios}
  columns={scenarioColumns}
  onRowClick={handleScenarioClick}
  selectable="multiple"
  onSelectionChange={setSelectedScenarios}
  searchable
  searchPlaceholder="Search scenarios..."
  pagination
  pageSize={25}
  loading={isLoading}
  emptyState={<EmptyState title="No scenarios" description="Create your first scenario" />}
/>
```

### **Modal Component System**

```typescript
interface ModalProps extends BaseComponentProps {
  // Visibility
  open: boolean
  onClose: () => void
  
  // Behavior
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
  preventClose?: boolean
  
  // Appearance
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  centered?: boolean
  
  // Animation
  animation?: 'fade' | 'scale' | 'slide'
  
  children: ReactNode
}

interface ModalHeaderProps extends BaseComponentProps {
  title?: string
  subtitle?: string
  showCloseButton?: boolean
  onClose?: () => void
  
  children?: ReactNode
}

interface ModalBodyProps extends BaseComponentProps {
  padding?: 'none' | 'sm' | 'md' | 'lg'
  scrollable?: boolean
  
  children: ReactNode
}

interface ModalFooterProps extends BaseComponentProps {
  justify?: 'start' | 'center' | 'end' | 'between'
  
  children: ReactNode
}

// Usage Example
<Modal open={isOpen} onClose={handleClose} size="lg">
  <ModalHeader 
    title="Create New Scenario" 
    subtitle="Define your workforce growth scenario"
    onClose={handleClose}
  />
  <ModalBody>
    <ScenarioForm onSubmit={handleSubmit} />
  </ModalBody>
  <ModalFooter justify="end">
    <Button variant="ghost" onClick={handleClose}>Cancel</Button>
    <Button variant="primary" onClick={handleSubmit}>Create Scenario</Button>
  </ModalFooter>
</Modal>
```

## Layout Components

### **Container System**

```typescript
interface ContainerProps extends BaseComponentProps {
  // Size constraints
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' | string
  
  // Spacing
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  margin?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  
  // Behavior
  centered?: boolean
  fluid?: boolean
  
  children: ReactNode
}

interface StackProps extends BaseComponentProps {
  // Direction
  direction?: 'vertical' | 'horizontal'
  
  // Spacing
  spacing?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  
  // Alignment
  align?: 'start' | 'center' | 'end' | 'stretch'
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly'
  
  // Responsive
  responsive?: boolean
  breakpoint?: 'sm' | 'md' | 'lg'
  
  children: ReactNode
}

interface GridProps extends BaseComponentProps {
  // Grid definition
  columns?: number | 'auto' | string
  rows?: number | 'auto' | string
  
  // Spacing
  gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  columnGap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  rowGap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  
  // Responsive
  responsive?: {
    sm?: Partial<GridProps>
    md?: Partial<GridProps>
    lg?: Partial<GridProps>
  }
  
  children: ReactNode
}

// Usage Examples
<Container maxWidth="2xl" padding="lg">
  <Stack direction="vertical" spacing="xl">
    <PageHeader title="Scenarios" />
    
    <Grid columns={3} gap="md" responsive={{
      sm: { columns: 1 },
      md: { columns: 2 }
    }}>
      <StatsCard title="Total Scenarios" value={scenarios.length} />
      <StatsCard title="Active Simulations" value={activeCount} />
      <StatsCard title="Completed Today" value={completedToday} />
    </Grid>
    
    <DataTable data={scenarios} columns={columns} />
  </Stack>
</Container>
```

## Pattern Components

### **PageHeader Component**

```typescript
interface PageHeaderProps extends BaseComponentProps {
  // Content
  title: string
  subtitle?: string
  description?: string
  
  // Actions
  primaryAction?: {
    label: string
    onClick: () => void
    loading?: boolean
    disabled?: boolean
  }
  secondaryActions?: Array<{
    label: string
    onClick: () => void
    icon?: ReactNode
    disabled?: boolean
  }>
  
  // Navigation
  breadcrumbs?: Array<{
    label: string
    href?: string
    onClick?: () => void
  }>
  
  // Status
  status?: {
    label: string
    variant: 'success' | 'warning' | 'error' | 'info'
  }
  
  // Layout
  size?: 'sm' | 'md' | 'lg'
}

// Usage Example
<PageHeader
  title="Growth Scenarios Q1 2024"
  subtitle="Workforce Planning"
  description="Analyze different growth trajectories for the upcoming quarter"
  primaryAction={{
    label: "Create Scenario",
    onClick: handleCreateScenario
  }}
  secondaryActions={[
    { label: "Import", onClick: handleImport, icon: <Upload /> },
    { label: "Export All", onClick: handleExportAll, icon: <Download /> }
  ]}
  breadcrumbs={[
    { label: "Dashboard", href: "/" },
    { label: "Scenarios", href: "/scenarios" },
    { label: "Q1 2024" }
  ]}
  status={{
    label: "3 simulations running",
    variant: "info"
  }}
/>
```

### **StatsGrid Component**

```typescript
interface Stat {
  id: string
  label: string
  value: string | number
  change?: {
    value: number
    period: string
    trend: 'up' | 'down' | 'flat'
  }
  icon?: ReactNode
  color?: 'primary' | 'success' | 'warning' | 'error'
  onClick?: () => void
}

interface StatsGridProps extends BaseComponentProps {
  stats: Stat[]
  columns?: 2 | 3 | 4 | 5
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'minimal' | 'detailed'
  loading?: boolean
}

// Usage Example
<StatsGrid
  stats={[
    {
      id: 'total-fte',
      label: 'Total FTE',
      value: 1247,
      change: { value: 12, period: 'vs last month', trend: 'up' },
      icon: <Users />,
      color: 'primary'
    },
    {
      id: 'growth-rate',
      label: 'Growth Rate',
      value: '8.5%',
      change: { value: 2.1, period: 'vs target', trend: 'up' },
      icon: <TrendingUp />,
      color: 'success'
    }
  ]}
  columns={3}
  size="lg"
/>
```

## Component Composition Patterns

### **Compound Components Pattern**

```typescript
// Example: Table with compound components
interface TableComponents {
  Table: ComponentType<TableProps>
  Header: ComponentType<TableHeaderProps>
  Body: ComponentType<TableBodyProps>
  Row: ComponentType<TableRowProps>
  Cell: ComponentType<TableCellProps>
}

const Table: TableComponents = {
  Table: TableRoot,
  Header: TableHeader,
  Body: TableBody,
  Row: TableRow,
  Cell: TableCell
}

// Usage
<Table.Table>
  <Table.Header>
    <Table.Row>
      <Table.Cell>Name</Table.Cell>
      <Table.Cell>FTE</Table.Cell>
      <Table.Cell>Actions</Table.Cell>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {offices.map(office => (
      <Table.Row key={office.id}>
        <Table.Cell>{office.name}</Table.Cell>
        <Table.Cell>{office.fte}</Table.Cell>
        <Table.Cell>
          <Button size="sm">Edit</Button>
        </Table.Cell>
      </Table.Row>
    ))}
  </Table.Body>
</Table.Table>
```

### **Render Props Pattern**

```typescript
interface DataFetcherProps<T> {
  url: string
  children: (state: {
    data: T | null
    loading: boolean
    error: string | null
    refetch: () => void
  }) => ReactNode
}

// Usage
<DataFetcher url="/api/scenarios">
  {({ data, loading, error, refetch }) => (
    <div>
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} onRetry={refetch} />}
      {data && <ScenarioList scenarios={data} />}
    </div>
  )}
</DataFetcher>
```

## Component Testing Patterns

### **Component Test Structure**

```typescript
// Component test template
describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })
  
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('shows loading state', () => {
    render(<Button loading>Click me</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
  })
  
  it('supports all variants', () => {
    const variants = ['primary', 'secondary', 'ghost', 'destructive']
    variants.forEach(variant => {
      const { rerender } = render(<Button variant={variant}>Test</Button>)
      expect(screen.getByRole('button')).toHaveClass(`button-${variant}`)
      rerender(<></>)
    })
  })
})
```

This comprehensive component API specification ensures consistent, predictable, and maintainable components throughout the SimpleSim design system.