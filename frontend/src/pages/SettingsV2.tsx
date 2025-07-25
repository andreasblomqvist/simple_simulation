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

// Import existing types
import type { OfficeConfig } from '../types/office'

interface SettingsV2Props {}

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

export const SettingsV2: React.FC<SettingsV2Props> = () => {
  const [activeTab, setActiveTab] = useState<'progression' | 'cat-matrix' | 'general'>('progression')
  const [isDirty, setIsDirty] = useState(false)

  // CAT Matrix data - this would be loaded from the backend
  const [catMatrix, setCatMatrix] = useState<Record<string, Record<string, number>>>({
    'A': { 'CAT0': 0.0, 'CAT1': 0.1, 'CAT2': 0.2, 'CAT3': 0.3, 'CAT4': 0.5, 'CAT5': 0.7, 'CAT6': 0.9 },
    'AC': { 'CAT0': 0.0, 'CAT1': 0.15, 'CAT2': 0.25, 'CAT3': 0.4, 'CAT4': 0.6, 'CAT5': 0.8, 'CAT6': 0.95 },
    'C': { 'CAT0': 0.0, 'CAT1': 0.2, 'CAT2': 0.3, 'CAT3': 0.5, 'CAT4': 0.7, 'CAT5': 0.85, 'CAT6': 1.0 },
    'SrC': { 'CAT0': 0.0, 'CAT1': 0.25, 'CAT2': 0.4, 'CAT3': 0.6, 'CAT4': 0.8, 'CAT5': 0.9, 'CAT6': 1.0 },
    'AM': { 'CAT0': 0.0, 'CAT1': 0.3, 'CAT2': 0.5, 'CAT3': 0.7, 'CAT4': 0.85, 'CAT5': 0.95, 'CAT6': 1.0 },
    'M': { 'CAT0': 0.0, 'CAT1': 0.35, 'CAT2': 0.55, 'CAT3': 0.75, 'CAT4': 0.9, 'CAT5': 0.98, 'CAT6': 1.0 },
    'SrM': { 'CAT0': 0.0, 'CAT1': 0.4, 'CAT2': 0.6, 'CAT3': 0.8, 'CAT4': 0.95, 'CAT5': 1.0, 'CAT6': 1.0 },
    'PiP': { 'CAT0': 0.0, 'CAT1': 0.5, 'CAT2': 0.7, 'CAT3': 0.85, 'CAT4': 1.0, 'CAT5': 1.0, 'CAT6': 1.0 },
  })

  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
  const catLevels = ['CAT0', 'CAT1', 'CAT2', 'CAT3', 'CAT4', 'CAT5', 'CAT6']

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

  const handleCatValueChange = (level: string, cat: string, value: string) => {
    const numValue = parseFloat(value)
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 1) {
      setCatMatrix(prev => ({
        ...prev,
        [level]: {
          ...prev[level],
          [cat]: numValue
        }
      }))
      setIsDirty(true)
    }
  }

  const handleSave = async () => {
    try {
      // Save logic would go here
      console.log('Saving settings...', { catMatrix })
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
          
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Level</TableHead>
                  {catLevels.map(cat => (
                    <TableHead key={cat} className="w-24 text-center">
                      {cat}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {levels.map(level => (
                  <TableRow key={level}>
                    <TableCell className="font-medium">{level}</TableCell>
                    {catLevels.map(cat => (
                      <TableCell key={cat} className="p-2">
                        <Input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={catMatrix[level]?.[cat] || 0}
                          onChange={(e) => handleCatValueChange(level, cat, e.target.value)}
                          className="w-full text-center text-sm"
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

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