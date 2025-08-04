import React, { useState } from 'react'
import { Plus, Settings, Trash2, ExternalLink, Download, Heart } from 'lucide-react'
import { Button } from '../ui/button'

export const ButtonDemo: React.FC = () => {
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})

  const handleLoadingDemo = (key: string) => {
    setLoadingStates(prev => ({ ...prev, [key]: true }))
    setTimeout(() => {
      setLoadingStates(prev => ({ ...prev, [key]: false }))
    }, 2000)
  }

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold mb-2">SimpleSim Button Component</h1>
        <p className="text-muted-foreground">
          Comprehensive design system button with all variants, sizes, and interaction states
        </p>
      </div>

      {/* Variants Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Button Variants</h2>
        <div className="flex flex-wrap gap-4">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="link">Link Button</Button>
        </div>
        
        {/* Backward Compatibility */}
        <div className="pt-2">
          <p className="text-sm text-muted-foreground mb-2">Backward compatibility (default variant):</p>
          <Button variant="default">Default (Legacy)</Button>
        </div>
      </section>

      {/* Sizes Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Button Sizes</h2>
        <div className="flex flex-wrap items-center gap-4">
          <Button size="xs">Extra Small</Button>
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="default">Default (Legacy)</Button>
          <Button size="lg">Large</Button>
          <Button size="xl">Extra Large</Button>
        </div>
      </section>

      {/* Icon Support Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Icon Support</h2>
        <div className="space-y-3">
          <div className="flex flex-wrap gap-4">
            <Button icon={<Plus />} iconPosition="left">Add Item</Button>
            <Button icon={<Settings />} iconPosition="left" variant="outline">Configure</Button>
            <Button icon={<ExternalLink />} iconPosition="right" variant="ghost">
              Open External
            </Button>
            <Button icon={<Download />} iconPosition="right" variant="secondary">
              Download
            </Button>
          </div>
          
          <div className="flex gap-4">
            <Button size="icon" variant="outline">
              <Heart className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="ghost">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Loading States Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Loading States</h2>
        <div className="flex flex-wrap gap-4">
          <Button 
            loading={loadingStates.primary} 
            onClick={() => handleLoadingDemo('primary')}
          >
            Save Changes
          </Button>
          <Button 
            variant="outline"
            loading={loadingStates.outline} 
            onClick={() => handleLoadingDemo('outline')}
          >
            Upload File
          </Button>
          <Button 
            variant="destructive"
            loading={loadingStates.destructive} 
            onClick={() => handleLoadingDemo('destructive')}
            icon={<Trash2 />}
          >
            Delete Item
          </Button>
        </div>
      </section>

      {/* Disabled States Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Disabled States</h2>
        <div className="flex flex-wrap gap-4">
          <Button disabled>Primary Disabled</Button>
          <Button variant="secondary" disabled>Secondary Disabled</Button>
          <Button variant="outline" disabled>Outline Disabled</Button>
          <Button variant="ghost" disabled>Ghost Disabled</Button>
          <Button variant="destructive" disabled>Destructive Disabled</Button>
          <Button variant="link" disabled>Link Disabled</Button>
        </div>
      </section>

      {/* Full Width Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Full Width Buttons</h2>
        <div className="space-y-2 max-w-md">
          <Button fullWidth>Full Width Primary</Button>
          <Button fullWidth variant="outline">Full Width Outline</Button>
        </div>
      </section>

      {/* Rounded Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Rounded Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <Button rounded>Rounded Primary</Button>
          <Button rounded variant="outline">Rounded Outline</Button>
          <Button rounded size="sm" icon={<Heart />}>Like</Button>
        </div>
      </section>

      {/* Interactive States Demo */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Interactive States</h2>
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Hover over buttons to see elevation and color changes. Focus with Tab to see focus rings.
            Active states show when pressed.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button>Hover & Focus Me</Button>
            <Button variant="secondary">Try Tab Navigation</Button>
            <Button variant="outline">Press and Hold</Button>
            <Button variant="ghost">Subtle Interactions</Button>
          </div>
        </div>
      </section>

      {/* Theme Compatibility */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Theme Compatibility</h2>
        <p className="text-sm text-muted-foreground">
          All buttons automatically adapt to light and dark themes using design tokens.
          Toggle your theme to see the adaptation in action.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Button>Primary Theme</Button>
          <Button variant="secondary">Secondary Theme</Button>
          <Button variant="outline">Outline Theme</Button>
          <Button variant="ghost">Ghost Theme</Button>
          <Button variant="destructive">Destructive Theme</Button>
          <Button variant="link">Link Theme</Button>
        </div>
      </section>

      {/* Usage Examples */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Common Usage Patterns</h2>
        <div className="space-y-6">
          
          {/* Form Actions */}
          <div className="space-y-2">
            <h3 className="text-lg font-medium">Form Actions</h3>
            <div className="flex gap-2 justify-end p-4 bg-muted/30 rounded-lg">
              <Button variant="ghost">Cancel</Button>
              <Button variant="outline">Save Draft</Button>
              <Button>Publish</Button>
            </div>
          </div>

          {/* Toolbar Actions */}
          <div className="space-y-2">
            <h3 className="text-lg font-medium">Toolbar Actions</h3>
            <div className="flex gap-1 p-2 bg-muted/30 rounded-lg">
              <Button size="sm" variant="ghost" icon={<Plus />} />
              <Button size="sm" variant="ghost" icon={<Settings />} />
              <Button size="sm" variant="ghost" icon={<Trash2 />} />
            </div>
          </div>

          {/* CTA Section */}
          <div className="space-y-2">
            <h3 className="text-lg font-medium">Call-to-Action</h3>
            <div className="text-center p-6 bg-muted/30 rounded-lg space-y-4">
              <h4 className="text-xl font-semibold">Ready to get started?</h4>
              <p className="text-muted-foreground">Create your first scenario in minutes</p>
              <div className="flex gap-2 justify-center">
                <Button size="lg" icon={<Plus />}>Create Scenario</Button>
                <Button size="lg" variant="outline">Learn More</Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default ButtonDemo