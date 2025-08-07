# Population Snapshot Components

This directory contains React components for managing population snapshots in the SimpleSim application. These components provide a complete frontend interface for capturing, viewing, comparing, and managing historical workforce data.

## Components Overview

### Core Components

#### `SnapshotSelector`
- **Purpose**: Dropdown selector for choosing between current workforce data or historical snapshots
- **Key Features**:
  - Shows current workforce option
  - Lists available snapshots with metadata
  - Displays selected snapshot details
  - Auto-refresh functionality
- **Usage**: Embedded in workforce views to switch data sources

#### `SnapshotManager`
- **Purpose**: Full management interface for population snapshots
- **Key Features**:
  - List all snapshots with filtering and sorting
  - Create, edit, delete snapshots
  - Export snapshots to CSV
  - Compare snapshots side-by-side
  - Tag-based filtering
- **Usage**: Main snapshots management page

#### `CreateSnapshotModal`
- **Purpose**: Modal form for creating new population snapshots
- **Key Features**:
  - Captures current office workforce state
  - Adds metadata (name, description, tags)
  - Form validation and error handling
- **Usage**: Triggered from "Save Snapshot" buttons

#### `SnapshotComparison`
- **Purpose**: Side-by-side comparison of two snapshots
- **Key Features**:
  - Shows baseline vs comparison snapshots
  - Calculates and displays workforce changes
  - Summary metrics (FTE changes, role changes)
  - Detailed change table with filtering
- **Usage**: Standalone comparison view

#### `SnapshotWorkforceTable`
- **Purpose**: Table displaying snapshot workforce data
- **Key Features**:
  - Role and level breakdown
  - Salary information (optional)
  - Summary totals and role distribution
  - Responsive design
- **Usage**: Detail views for snapshot data

## Data Flow

```
Current Office Data → Snapshot Creation → Historical Storage
                                      ↓
Snapshot Selector ← API ← Snapshot Store ← Backend API
                                      ↓
Comparison Engine ← Selected Snapshots ← User Selection
```

## State Management

### Zustand Store (`snapshotStore.ts`)
- Manages snapshot data and UI state
- Handles API interactions with optimistic updates
- Provides computed selectors for common access patterns
- Caches snapshot data by office

### Key Store Methods
- `loadSnapshotsByOffice(officeId)` - Load snapshots for specific office
- `createSnapshot(data)` - Create new snapshot from current workforce
- `compareSnapshots(baseline, comparison)` - Generate comparison data
- `deleteSnapshot(id)` - Remove snapshot with cleanup

## API Integration

### Service Layer (`snapshotApi.ts`)
- Typed HTTP client for snapshot operations
- Error handling and response transformation
- Utility functions for data formatting
- Export functionality for CSV downloads

### Key API Endpoints
- `GET /api/snapshots/office/{office_id}` - Get office snapshots
- `POST /api/snapshots` - Create new snapshot
- `POST /api/snapshots/compare` - Compare two snapshots
- `DELETE /api/snapshots/{id}` - Delete snapshot
- `GET /api/snapshots/{id}/export` - Export snapshot data

## Integration Points

### Office Management
- **OfficeViewWithTabs**: Integrated snapshot selector in workforce tab
- **Workforce Display**: Switch between current and historical data
- **Save Snapshot**: One-click snapshot creation from current state

### Scenario Planning
- **ScenariosV2**: Shows snapshot baseline indicators
- **Future Enhancement**: Snapshot selection in scenario creation

## Styling and Theming

- Consistent with existing dark theme (`backgroundColor: '#1f2937'`)
- Uses shadcn/ui components for consistency
- Mobile-responsive design patterns
- Follows SimpleSim design system guidelines

## Data Types

### Core Types (`types/snapshots.ts`)
- `PopulationSnapshot` - Complete snapshot with metadata
- `SnapshotWorkforce` - Individual workforce entries
- `SnapshotComparison` - Comparison results with changes
- `CreateSnapshotRequest` - API request payloads

## Performance Considerations

- **Caching**: Store caches snapshots by office for quick access
- **Pagination**: Large snapshot lists are paginated
- **Optimistic Updates**: UI updates immediately with server sync
- **Debounced Search**: Search filtering with debouncing

## Error Handling

- Network error recovery with retry mechanisms
- Form validation with user-friendly messages
- Graceful degradation when snapshots unavailable
- Loading states for all async operations

## Testing Strategy

- Unit tests for utility functions and data transformations
- Component tests with react-testing-library
- Integration tests for store operations
- E2E tests for complete user workflows

## Future Enhancements

1. **Snapshot Scheduling**: Automated snapshot creation
2. **Advanced Comparisons**: Multi-snapshot comparisons
3. **Snapshot Templates**: Predefined snapshot configurations
4. **Bulk Operations**: Batch create/delete snapshots
5. **Data Visualization**: Charts for snapshot trends
6. **Export Formats**: PDF, Excel export options
7. **Snapshot Sharing**: Share snapshots between users
8. **Snapshot Versioning**: Track snapshot modifications

## Usage Examples

### Basic Snapshot Selection
```tsx
import { SnapshotSelector } from '../components/snapshot';

<SnapshotSelector
  officeId={office.id}
  selectedSnapshot={selectedSnapshot}
  onSnapshotSelect={setSelectedSnapshot}
  showCurrentOption={true}
/>
```

### Full Management Interface
```tsx
import { SnapshotManager } from '../components/snapshot';

<SnapshotManager
  officeId={office.id}
  onSnapshotCreated={(snapshot) => console.log('Created:', snapshot.name)}
  onSnapshotDeleted={(id) => console.log('Deleted:', id)}
/>
```

### Creating Snapshots
```tsx
import { CreateSnapshotModal } from '../components/snapshot';

<CreateSnapshotModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onSnapshotCreated={handleSnapshotCreated}
  officeId={office.id}
  officeName={office.name}
/>
```