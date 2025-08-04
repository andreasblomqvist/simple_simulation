/**
 * Typography Test Component
 * 
 * Tests all typography variants with different themes and features.
 * Demonstrates the typography system functionality.
 */

import * as React from 'react'
import { Text, Heading, H1, H2, H3, H4, H5, H6 } from '../design-system/typography'
import { Card } from './ui/card'

export const TypographyTest: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      <div className="space-y-4">
        <H1>Typography System Test</H1>
        <Text variant="body-lg" color="secondary">
          Complete test of all typography variants with design tokens integration
        </Text>
      </div>

      {/* Display Variants */}
      <Card className="p-6">
        <H3 className="mb-4">Display Variants</H3>
        <div className="space-y-4">
          <Text variant="display-xl">Display XL - Hero Headlines</Text>
          <Text variant="display-lg">Display LG - Page Titles</Text>
          <Text variant="display-md">Display MD - Section Headers</Text>
          <Text variant="display-sm">Display SM - Subsection Headers</Text>
        </div>
      </Card>

      {/* Heading Variants */}
      <Card className="p-6">
        <H3 className="mb-4">Heading Variants</H3>
        <div className="space-y-3">
          <Text variant="heading-xl">Heading XL - Major Sections</Text>
          <Text variant="heading-lg">Heading LG - Content Headers</Text>
          <Text variant="heading-md">Heading MD - Card Titles</Text>
          <Text variant="heading-sm">Heading SM - Minor Headings</Text>
        </div>
      </Card>

      {/* Body Text Variants */}
      <Card className="p-6">
        <H3 className="mb-4">Body Text Variants</H3>
        <div className="space-y-3">
          <Text variant="body-lg">
            Body LG - Large body text for important content and emphasized paragraphs.
          </Text>
          <Text variant="body-md">
            Body MD - Standard body text for regular content, descriptions, and most paragraph text.
          </Text>
          <Text variant="body-sm">
            Body SM - Small body text for secondary information and compact layouts.
          </Text>
        </div>
      </Card>

      {/* Label and Caption Variants */}
      <Card className="p-6">
        <H3 className="mb-4">Label & Caption Variants</H3>
        <div className="space-y-3">
          <div>
            <Text variant="label-lg">Label LG - Form Labels</Text>
            <Text variant="body-md" color="secondary">Associated with form inputs</Text>
          </div>
          <div>
            <Text variant="label-md">Label MD - Table Headers</Text>
            <Text variant="body-sm" color="secondary">Column headings and data labels</Text>
          </div>
          <div>
            <Text variant="label-sm">Label SM - Compact Labels</Text>
            <Text variant="caption-lg" color="muted">Caption LG - Help text and metadata</Text>
          </div>
          <div>
            <Text variant="caption-md" color="muted">Caption MD - Secondary information</Text>
          </div>
          <div>
            <Text variant="caption-sm" color="muted">Caption SM - Minimal text</Text>
          </div>
        </div>
      </Card>

      {/* Semantic Heading Components */}
      <Card className="p-6">
        <H3 className="mb-4">Semantic Heading Components</H3>
        <div className="space-y-2">
          <H1>H1 - Page Title</H1>
          <H2>H2 - Major Section</H2>
          <H3>H3 - Subsection</H3>
          <H4>H4 - Content Group</H4>
          <H5>H5 - Minor Heading</H5>
          <H6>H6 - Smallest Heading</H6>
        </div>
      </Card>

      {/* Color Variants */}
      <Card className="p-6">
        <H3 className="mb-4">Color Variants</H3>
        <div className="space-y-2">
          <Text color="primary">Primary - Main text color</Text>
          <Text color="secondary">Secondary - Supporting text</Text>
          <Text color="muted">Muted - Subdued text</Text>
          <Text color="accent">Accent - Brand colored text</Text>
          <Text color="success">Success - Positive states</Text>
          <Text color="warning">Warning - Attention needed</Text>
          <Text color="error">Error - Destructive states</Text>
        </div>
      </Card>

      {/* Font Weights */}
      <Card className="p-6">
        <H3 className="mb-4">Font Weight Variants</H3>
        <div className="space-y-2">
          <Text weight="light">Light Weight Text</Text>
          <Text weight="normal">Normal Weight Text</Text>
          <Text weight="medium">Medium Weight Text</Text>
          <Text weight="semibold">Semibold Weight Text</Text>
          <Text weight="bold">Bold Weight Text</Text>
        </div>
      </Card>

      {/* Text Transformations */}
      <Card className="p-6">
        <H3 className="mb-4">Text Transformations</H3>
        <div className="space-y-2">
          <Text transform="uppercase">Uppercase Text</Text>
          <Text transform="lowercase">LOWERCASE TEXT</Text>  
          <Text transform="capitalize">capitalize each word</Text>
          <Text transform="none">Normal Case Text</Text>
        </div>
      </Card>

      {/* Alignment Options */}
      <Card className="p-6">
        <H3 className="mb-4">Text Alignment</H3>
        <div className="space-y-3">
          <Text align="left">Left aligned text (default)</Text>
          <Text align="center">Center aligned text</Text>
          <Text align="right">Right aligned text</Text>
          <Text align="justify">
            Justified text that spreads across the full width of the container, 
            adjusting spacing between words to create clean edges on both sides.
          </Text>
        </div>
      </Card>

      {/* Truncation */}
      <Card className="p-6">
        <H3 className="mb-4">Text Truncation</H3>
        <div className="space-y-2">
          <div className="w-48">
            <Text truncate>
              This is a very long text that will be truncated when it exceeds the container width
            </Text>
          </div>
          <Text>
            This is normal text without truncation that will wrap naturally across multiple lines
          </Text>
        </div>
      </Card>

      {/* Custom HTML Elements */}
      <Card className="p-6">
        <H3 className="mb-4">Custom HTML Elements</H3>
        <div className="space-y-2">
          <Text as="span" variant="heading-md">Span element with heading styling</Text>
          <Text as="div" variant="body-lg">Div element with body styling</Text>
          <Text as="label" variant="label-lg">Label element for forms</Text>
        </div>
      </Card>

      {/* Inter Font Test */}
      <Card className="p-6">
        <H3 className="mb-4">Inter Font Family Test</H3>
        <div className="space-y-2">
          <Text variant="body-md">
            This text uses the Inter font family as specified in the design tokens. 
            Inter provides excellent readability and modern appearance.
          </Text>
          <Text variant="caption-md" color="muted" className="font-mono">
            This text explicitly uses monospace for comparison: JetBrains Mono
          </Text>
        </div>
      </Card>
    </div>
  )
}

export default TypographyTest