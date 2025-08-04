/**
 * Business-Specific Modal Components for SimpleSim
 * 
 * Specialized modal components for common business operations
 * Built on top of the unified modal system
 */
"use client"

import * as React from "react"
import { Download, Upload, Trash2, Edit, Eye, AlertTriangle } from "lucide-react"
import { 
  Modal, 
  ConfirmationDialog, 
  FormDialog, 
  DisplayDialog,
  type ConfirmationDialogProps 
} from "./modal"
import { 
  Sheet, 
  SheetContent, 
  SheetDescription, 
  SheetHeader, 
  SheetTitle 
} from "./sheet"
import { Button } from "./button"
import { Badge } from "./badge"
import { Alert, AlertDescription } from "./alert"

// Scenario Delete Dialog
interface ScenarioDeleteDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  scenarioName?: string
  loading?: boolean
}

export const ScenarioDeleteDialog: React.FC<ScenarioDeleteDialogProps> = ({
  open,
  onClose,
  onConfirm,
  scenarioName = "this scenario",
  loading = false
}) => {
  return (
    <ConfirmationDialog
      open={open}
      onClose={onClose}
      onConfirm={onConfirm}
      title="Delete Scenario"
      description={`Are you sure you want to delete "${scenarioName}"? This action cannot be undone and will remove all associated results.`}
      confirmLabel="Delete Scenario"
      destructive={true}
      loading={loading}
    />
  )
}

// Office Delete Dialog  
interface OfficeDeleteDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  officeName?: string
  hasScenarios?: boolean
  loading?: boolean
}

export const OfficeDeleteDialog: React.FC<OfficeDeleteDialogProps> = ({
  open,
  onClose,
  onConfirm,
  officeName = "this office",
  hasScenarios = false,
  loading = false
}) => {
  return (
    <ConfirmationDialog
      open={open}
      onClose={onClose}
      onConfirm={onConfirm}
      title="Delete Office"
      description={
        hasScenarios 
          ? `Deleting "${officeName}" will also remove all associated scenarios and results. This action cannot be undone.`
          : `Are you sure you want to delete "${officeName}"? This action cannot be undone.`
      }
      confirmLabel="Delete Office"
      destructive={true}
      loading={loading}
    />
  )
}

// Import Dialog Props
interface ImportDialogProps {
  open: boolean
  onClose: () => void
  onImport: (file: File) => void
  title: string
  description?: string
  acceptedTypes?: string
  loading?: boolean
  maxSize?: number // in MB
}

// Import Dialog Component
export const ImportDialog: React.FC<ImportDialogProps> = ({
  open,
  onClose,
  onImport,
  title,
  description = "Select a file to import",
  acceptedTypes = ".xlsx,.csv",
  loading = false,
  maxSize = 10
}) => {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [dragActive, setDragActive] = React.useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === "dragenter" || e.type === "dragover")
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      setSelectedFile(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      setSelectedFile(files[0])
    }
  }

  const handleImport = () => {
    if (selectedFile) {
      onImport(selectedFile)
      setSelectedFile(null)
    }
  }

  const handleCancel = () => {
    setSelectedFile(null)
    onClose()
  }

  const fileSizeValid = selectedFile ? selectedFile.size <= maxSize * 1024 * 1024 : true
  const fileTypeValid = selectedFile ? acceptedTypes.includes(selectedFile.name.split('.').pop() || '') : true

  return (
    <FormDialog
      open={open}
      onClose={onClose}
      onSubmit={handleImport}
      onCancel={handleCancel}
      title={title}
      description={description}
      submitLabel="Import"
      submitDisabled={!selectedFile || !fileSizeValid || !fileTypeValid}
      loading={loading}
      size="md"
    >
      <div className="space-y-4">
        {/* File Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            dragActive ? 'border-primary bg-primary/5' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-sm text-gray-600 mb-2">
            Drag and drop your file here, or{" "}
            <button
              type="button"
              className="text-primary hover:text-primary/80 font-medium"
              onClick={() => inputRef.current?.click()}
            >
              browse files
            </button>
          </p>
          <p className="text-xs text-gray-500">
            Supported formats: {acceptedTypes} (max {maxSize}MB)
          </p>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept={acceptedTypes}
            onChange={handleFileSelect}
          />
        </div>

        {/* Selected File */}
        {selectedFile && (
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedFile(null)}
              >
                Remove
              </Button>
            </div>
            
            {/* Validation Errors */}
            {!fileSizeValid && (
              <Alert className="mt-2">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  File size exceeds {maxSize}MB limit
                </AlertDescription>
              </Alert>
            )}
            {!fileTypeValid && (
              <Alert className="mt-2">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Unsupported file type. Please use: {acceptedTypes}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </div>
    </FormDialog>
  )
}

// Export Results Dialog
interface ExportDialogProps {
  open: boolean
  onClose: () => void
  onExport: (format: string, options: any) => void
  title: string
  formats?: Array<{ value: string; label: string; description?: string }>
  loading?: boolean
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  open,
  onClose,
  onExport,
  title,
  formats = [
    { value: 'xlsx', label: 'Excel (.xlsx)', description: 'Spreadsheet format' },
    { value: 'csv', label: 'CSV (.csv)', description: 'Comma-separated values' }
  ],
  loading = false
}) => {
  const [selectedFormat, setSelectedFormat] = React.useState(formats[0]?.value || 'xlsx')
  const [includeCharts, setIncludeCharts] = React.useState(true)
  const [includeRawData, setIncludeRawData] = React.useState(false)

  const handleExport = () => {
    onExport(selectedFormat, {
      includeCharts,
      includeRawData
    })
  }

  return (
    <FormDialog
      open={open}
      onClose={onClose}
      onSubmit={handleExport}
      title={title}
      submitLabel="Export"
      loading={loading}
      size="md"
    >
      <div className="space-y-4">
        {/* Format Selection */}
        <div>
          <label className="text-sm font-medium mb-2 block">Export Format</label>
          <div className="space-y-2">
            {formats.map((format) => (
              <label key={format.value} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  value={format.value}
                  checked={selectedFormat === format.value}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  className="h-4 w-4"
                />
                <div>
                  <p className="text-sm font-medium">{format.label}</p>
                  {format.description && (
                    <p className="text-xs text-gray-500">{format.description}</p>
                  )}
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Export Options */}
        <div>
          <label className="text-sm font-medium mb-2 block">Options</label>
          <div className="space-y-2">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={includeCharts}
                onChange={(e) => setIncludeCharts(e.target.checked)}
                className="h-4 w-4"
              />
              <span className="text-sm">Include charts and visualizations</span>
            </label>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={includeRawData}
                onChange={(e) => setIncludeRawData(e.target.checked)}
                className="h-4 w-4"
              />
              <span className="text-sm">Include raw data sheets</span>
            </label>
          </div>
        </div>
      </div>
    </FormDialog>
  )
}

// Quick Actions Sheet
interface QuickActionsSheetProps {
  open: boolean
  onClose: () => void
  actions: Array<{
    label: string
    icon: React.ReactNode
    onClick: () => void
    disabled?: boolean
    destructive?: boolean
  }>
  title?: string
  description?: string
}

export const QuickActionsSheet: React.FC<QuickActionsSheetProps> = ({
  open,
  onClose,
  actions,
  title = "Quick Actions",
  description
}) => {
  return (
    <Sheet open={open} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-80">
        <SheetHeader>
          <SheetTitle>{title}</SheetTitle>
          {description && <SheetDescription>{description}</SheetDescription>}
        </SheetHeader>
        
        <div className="mt-6 space-y-2">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.destructive ? "destructive" : "ghost"}
              size="sm"
              className="w-full justify-start"
              onClick={() => {
                action.onClick()
                onClose()
              }}
              disabled={action.disabled}
            >
              {action.icon}
              <span className="ml-2">{action.label}</span>
            </Button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  )
}

// Export all business modal components
export {
  type ScenarioDeleteDialogProps,
  type OfficeDeleteDialogProps,
  type ImportDialogProps,
  type ExportDialogProps,
  type QuickActionsSheetProps
}