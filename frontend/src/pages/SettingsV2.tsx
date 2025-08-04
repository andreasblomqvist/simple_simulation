import React, { useState, useEffect } from 'react'
import { Settings, Users, TrendingUp, Grid3X3, Save, RotateCcw } from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'
import { Input } from '../components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { DataTableMinimal } from '../components/ui/data-table-minimal'
import type { ColumnDef } from '@tanstack/react-table'

// Import existing types
import type { OfficeConfig } from '../types/office'

interface SettingsV2Props {}

interface CATMatrixRow {
  level: string;
  CAT0: string;
  CAT6: string;
  CAT12: string;
  CAT18: string;
  CAT24: string;
  CAT30: string;
  CAT36: string;
  CAT42: string;
  CAT48: string;
  CAT54: string;
  CAT60: string;
}

// Mock office data - in real implementation this would come from the store
const mockOffice: OfficeConfig = {
  id: 'settings-office',
  name: 'Global Settings',
  journey: 'mature' as any,
  timezone: 'Europe/Stockholm',
  economic_parameters: {
    cost_of_living: 1.0,
    market_multiplier: 1.0,
    tax_rate: 0.25,
  },
  total_fte: 0,
  roles: {},
}

// CAT Matrix data from backend config - EXACT values from progression_config.py CAT_CURVES only
const catMatrixData: CATMatrixRow[] = [
  { level: 'A', CAT0: '0.0%', CAT6: '91.9%', CAT12: '85.0%', CAT18: '0.0%', CAT24: '0.0%', CAT30: '0.0%', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'AC', CAT0: '0.0%', CAT6: '5.4%', CAT12: '75.9%', CAT18: '40.0%', CAT24: '0.0%', CAT30: '0.0%', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'C', CAT0: '0.0%', CAT6: '5.0%', CAT12: '44.2%', CAT18: '59.7%', CAT24: '27.8%', CAT30: '64.3%', CAT36: '20.0%', CAT42: '0.0%', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'SrC', CAT0: '0.0%', CAT6: '20.6%', CAT12: '43.8%', CAT18: '31.7%', CAT24: '21.1%', CAT30: '20.6%', CAT36: '16.7%', CAT42: '0.0%', CAT48: '0.0%', CAT54: '0.0%', CAT60: '0.0%' },
  { level: 'AM', CAT0: '0.0%', CAT6: '0.0%', CAT12: '0.0%', CAT18: '18.9%', CAT24: '19.7%', CAT30: '23.4%', CAT36: '4.8%', CAT42: '0.0%', CAT48: '0.0%', CAT54: '0.0%', CAT60: '0.0%' },
  { level: 'M', CAT0: '0.0%', CAT6: '0.0%', CAT12: '1.0%', CAT18: '2.0%', CAT24: '3.0%', CAT30: '4.0%', CAT36: '5.0%', CAT42: '6.0%', CAT48: '7.0%', CAT54: '8.0%', CAT60: '10.0%' },
  { level: 'SrM', CAT0: '0.0%', CAT6: '0.0%', CAT12: '0.5%', CAT18: '1.0%', CAT24: '1.5%', CAT30: '2.0%', CAT36: '2.5%', CAT42: '3.0%', CAT48: '4.0%', CAT54: '5.0%', CAT60: '6.0%' },
  { level: 'Pi', CAT0: '0.0%', CAT6: '', CAT12: '', CAT18: '', CAT24: '', CAT30: '', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'P', CAT0: '0.0%', CAT6: '', CAT12: '', CAT18: '', CAT24: '', CAT30: '', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'X', CAT0: '0.0%', CAT6: '', CAT12: '', CAT18: '', CAT24: '', CAT30: '', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
  { level: 'OPE', CAT0: '0.0%', CAT6: '', CAT12: '', CAT18: '', CAT24: '', CAT30: '', CAT36: '', CAT42: '', CAT48: '', CAT54: '', CAT60: '' },
];

// Helper function to get color based on percentage value (conditional formatting)
const getConditionalColor = (value: string): string => {
  if (!value || value === '') return '';
  
  // Extract numeric value from percentage string
  const numValue = parseFloat(value.replace('%', ''));
  
  if (numValue === 0) return 'bg-red-500 text-white';
  if (numValue > 0 && numValue <= 10) return 'bg-red-400 text-white';
  if (numValue > 10 && numValue <= 25) return 'bg-orange-400 text-white';
  if (numValue > 25 && numValue <= 50) return 'bg-yellow-400 text-black';
  if (numValue > 50 && numValue <= 75) return 'bg-lime-400 text-black';
  if (numValue > 75) return 'bg-green-500 text-white';
  
  return '';
};

const catMatrixColumns: ColumnDef<CATMatrixRow>[] = [
  { accessorKey: 'level', header: 'Level' },
  { 
    accessorKey: 'CAT0', 
    header: 'CAT0',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT6', 
    header: 'CAT6',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT12', 
    header: 'CAT12',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT18', 
    header: 'CAT18',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT24', 
    header: 'CAT24',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT30', 
    header: 'CAT30',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT36', 
    header: 'CAT36',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT42', 
    header: 'CAT42',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT48', 
    header: 'CAT48',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT54', 
    header: 'CAT54',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
  { 
    accessorKey: 'CAT60', 
    header: 'CAT60',
    cell: ({ getValue }) => {
      const value = getValue() as string;
      return (
        <div className={`px-2 py-1 rounded text-center font-medium ${getConditionalColor(value)}`}>
          {value}
        </div>
      );
    }
  },
];

export const SettingsV2: React.FC<SettingsV2Props> = () => {
  const [activeTab, setActiveTab] = useState<'progression' | 'cat-matrix' | 'general'>('progression')
  const [isDirty, setIsDirty] = useState(false)

  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']

  const getDefaultTenureValues = (level: string) => {
    const tenureDefaults: Record<string, { startTenure: number, timeOnLevel: number, journey: string }> = {
      'A': { startTenure: 0, timeOnLevel: 18, journey: 'J-1' },
      'AC': { startTenure: 18, timeOnLevel: 24, journey: 'J-2' },
      'C': { startTenure: 42, timeOnLevel: 36, journey: 'J-3' },
      'SrC': { startTenure: 78, timeOnLevel: 48, journey: 'J-4' },
      'AM': { startTenure: 126, timeOnLevel: 60, journey: 'Management' },
      'M': { startTenure: 186, timeOnLevel: 72, journey: 'Senior Management' },
      'SrM': { startTenure: 258, timeOnLevel: 84, journey: 'Executive' },
      'PiP': { startTenure: 342, timeOnLevel: 120, journey: 'Partner' }
    }
    return tenureDefaults[level] || { startTenure: 0, timeOnLevel: 12, journey: 'Default' }
  }

  const handleSave = async () => {
    try {
      // Save logic would go here
      console.log('Saving settings...')
      setIsDirty(false)
      // Show success message
    } catch (error) {
      console.error('Failed to save settings:', error)
    }
  }

  const handleReset = () => {
    // Reset to defaults logic
    setIsDirty(false)
  }

  const renderProgressionSettings = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="mr-2 h-5 w-5" />
          Level Tenure Configuration
        </CardTitle>
        <CardDescription>
          Configure tenure thresholds and time requirements for each career level
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="text-sm text-muted-foreground">
            Set the starting tenure and minimum time on level for career progression.
          </div>
          
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Level</TableHead>
                  <TableHead className="w-32">Journey</TableHead>
                  <TableHead className="w-32">Start Tenure (months)</TableHead>
                  <TableHead className="w-32">Time on Level (months)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {levels.map(level => {
                  const defaults = getDefaultTenureValues(level)
                  return (
                    <TableRow key={level}>
                      <TableCell className="font-medium">{level}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{defaults.journey}</TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="0"
                          step="1"
                          defaultValue={defaults.startTenure}
                          className="w-full text-center"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="1"
                          step="1"
                          defaultValue={defaults.timeOnLevel}
                          className="w-full text-center"
                        />
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>

          <div className="text-xs text-muted-foreground space-y-1">
            <p><strong>Start Tenure:</strong> Minimum tenure (in months) required to reach this level</p>
            <p><strong>Time on Level:</strong> Minimum time (in months) required to spend on this level before progression</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderCatMatrix = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Grid3X3 className="mr-2 h-5 w-5" />
          CAT Matrix Configuration
        </CardTitle>
        <CardDescription>
          Configure the Career Advancement Timeline (CAT) values for each level and category
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            CAT values represent progression probability coefficients (0.0 - 1.0) for each level and category.
          </div>
          
          <DataTableMinimal 
            columns={catMatrixColumns} 
            data={catMatrixData}
            enablePagination={false}
          />

          <div className="flex items-center space-x-2 pt-4">
            <div className="text-sm text-muted-foreground">
              Values must be between 0.0 and 1.0. Higher values indicate higher progression probability.
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderGeneralSettings = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Settings className="mr-2 h-5 w-5" />
          General Settings
        </CardTitle>
        <CardDescription>
          Global application and simulation settings
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Default Currency</label>
              <select className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm">
                <option value="SEK">Swedish Krona (SEK)</option>
                <option value="EUR">Euro (EUR)</option>
                <option value="USD">US Dollar (USD)</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Default Timezone</label>
              <select className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm">
                <option value="Europe/Stockholm">Stockholm</option>
                <option value="Europe/Oslo">Oslo</option>
                <option value="Europe/Helsinki">Helsinki</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-medium">Simulation Defaults</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Default Working Hours/Month</label>
                <Input
                  type="number"
                  defaultValue="160"
                  className="w-full"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Employment Cost Rate</label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  defaultValue="0.30"
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight flex items-center">
            <Settings className="mr-2 h-6 w-6" />
            Settings
          </h2>
          <p className="text-muted-foreground">
            Configure progression settings, CAT matrix, and global application preferences
          </p>
        </div>
        <div className="flex space-x-2">
          {isDirty && (
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Reset
            </Button>
          )}
          <Button onClick={handleSave} disabled={!isDirty}>
            <Save className="mr-2 h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('progression')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'progression'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <TrendingUp className="mr-2 h-4 w-4 inline" />
          Level Tenure
        </button>
        <button
          onClick={() => setActiveTab('cat-matrix')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'cat-matrix'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Grid3X3 className="mr-2 h-4 w-4 inline" />
          CAT Matrix
        </button>
        <button
          onClick={() => setActiveTab('general')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'general'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Settings className="mr-2 h-4 w-4 inline" />
          General
        </button>
      </div>

      {/* Content */}
      {activeTab === 'progression' && renderProgressionSettings()}
      {activeTab === 'cat-matrix' && renderCatMatrix()}
      {activeTab === 'general' && renderGeneralSettings()}
    </div>
  )
}