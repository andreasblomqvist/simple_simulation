/**
 * CreateSnapshotModal Component
 * Modal form for creating new population snapshots
 */

import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Calendar, Save, X, Plus, AlertCircle } from 'lucide-react';
import { useSnapshotActions, useSnapshotLoading, useSnapshotError } from '../../stores/snapshotStore';
import type { CreateSnapshotModalProps, SnapshotFormData } from '../../types/snapshots';

export const CreateSnapshotModal: React.FC<CreateSnapshotModalProps> = ({
  isOpen,
  onClose,
  onSnapshotCreated,
  officeId,
  officeName = 'Selected Office'
}) => {
  const { createSnapshot, clearError } = useSnapshotActions();
  const loading = useSnapshotLoading();
  const error = useSnapshotError();

  const [formData, setFormData] = useState<SnapshotFormData>({
    name: '',
    description: '',
    office_id: officeId,
    snapshot_date: new Date(),
    tags: []
  });

  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        description: '',
        office_id: officeId,
        snapshot_date: new Date(),
        tags: []
      });
      setTagInput('');
      setErrors({});
      clearError();
    }
  }, [isOpen, officeId, clearError]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Snapshot name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Name must be less than 100 characters';
    }

    if (formData.description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    if (formData.tags.length > 10) {
      newErrors.tags = 'Maximum 10 tags allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      const snapshot = await createSnapshot({
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        office_id: formData.office_id,
        snapshot_date: formData.snapshot_date.toISOString(),
        tags: formData.tags.length > 0 ? formData.tags : undefined
      });

      onSnapshotCreated(snapshot);
      onClose();
    } catch (error) {
      // Error is handled by the store and will be displayed
      console.error('Failed to create snapshot:', error);
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag) && formData.tags.length < 10) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent 
        className="sm:max-w-[500px] bg-gray-800 border-gray-600 text-gray-100"
        onPointerDownOutside={(e) => e.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Calendar className="h-5 w-5" style={{ color: '#3b82f6' }} />
            Create Population Snapshot
          </DialogTitle>
          <DialogDescription style={{ color: '#d1d5db' }}>
            Capture the current workforce composition for <strong>{officeName}</strong> as a snapshot for future reference and comparison.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name Field */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
              Snapshot Name *
            </Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Q4 2024 Headcount, Post-Restructure"
              className="bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
              disabled={loading}
            />
            {errors.name && (
              <p className="text-sm flex items-center gap-1" style={{ color: '#ef4444' }}>
                <AlertCircle className="h-3 w-3" />
                {errors.name}
              </p>
            )}
          </div>

          {/* Description Field */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
              Description
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Optional description of what this snapshot represents..."
              rows={3}
              className="bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400 resize-none"
              disabled={loading}
            />
            {errors.description && (
              <p className="text-sm flex items-center gap-1" style={{ color: '#ef4444' }}>
                <AlertCircle className="h-3 w-3" />
                {errors.description}
              </p>
            )}
          </div>

          {/* Snapshot Date */}
          <div className="space-y-2">
            <Label htmlFor="snapshot_date" className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
              Snapshot Date
            </Label>
            <Input
              id="snapshot_date"
              type="datetime-local"
              value={formData.snapshot_date.toISOString().slice(0, 16)}
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                snapshot_date: new Date(e.target.value) 
              }))}
              className="bg-gray-700 border-gray-600 text-gray-100"
              disabled={loading}
            />
          </div>

          {/* Tags Field */}
          <div className="space-y-2">
            <Label className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
              Tags
            </Label>
            <div className="flex gap-2">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={handleTagInputKeyPress}
                placeholder="Add a tag..."
                className="bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
                disabled={loading || formData.tags.length >= 10}
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddTag}
                disabled={!tagInput.trim() || loading || formData.tags.length >= 10}
                className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Tag List */}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag) => (
                  <Badge 
                    key={tag} 
                    variant="secondary"
                    className="bg-blue-900 text-blue-100 hover:bg-blue-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-2 hover:text-blue-300"
                      disabled={loading}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
            
            {errors.tags && (
              <p className="text-sm flex items-center gap-1" style={{ color: '#ef4444' }}>
                <AlertCircle className="h-3 w-3" />
                {errors.tags}
              </p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-3 rounded-lg flex items-start gap-2" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
              <AlertCircle className="h-4 w-4 mt-0.5" style={{ color: '#ef4444' }} />
              <div>
                <p className="text-sm font-medium" style={{ color: '#dc2626' }}>Error creating snapshot</p>
                <p className="text-xs mt-1" style={{ color: '#991b1b' }}>{error}</p>
              </div>
            </div>
          )}

          <DialogFooter className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !formData.name.trim()}
              className="bg-blue-600 text-white hover:bg-blue-700"
            >
              {loading && <Save className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? 'Creating...' : 'Create Snapshot'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateSnapshotModal;