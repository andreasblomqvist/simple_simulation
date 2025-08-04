import React from 'react'
import { cn } from '@/lib/utils'
import { Container } from '../layout'

export interface EditorTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Toolbar content - editing tools, actions, and controls
   */
  toolbar?: React.ReactNode
  
  /**
   * Main editor content
   */
  children: React.ReactNode
  
  /**
   * Preview content (for withPreview variant)
   */
  preview?: React.ReactNode
  
  /**
   * Layout variant for the editor
   */
  variant?: 'standard' | 'splitView' | 'withPreview'
  
  /**
   * Container size for the editor
   */
  containerSize?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Whether to apply container padding
   */
  containerPadding?: boolean
  
  /**
   * Optional header content above the editor
   */
  header?: React.ReactNode
  
  /**
   * Optional footer content below the editor
   */
  footer?: React.ReactNode
  
  /**
   * Whether the toolbar should be sticky (default: true)
   */
  stickyToolbar?: boolean
  
  /**
   * Custom toolbar height for sticky positioning calculations
   */
  toolbarHeight?: string
  
  /**
   * Preview panel width (for withPreview variant)
   */
  previewWidth?: string
}

/**
 * Editor Layout Template
 * 
 * Provides the standard editor layout pattern:
 * - Sticky Toolbar: Fixed below header+context bar (120px from top)
 * - Content Area: Full-width scrollable content with appropriate padding
 * - Split View: Two equal columns for side-by-side editing
 * - Preview Mode: Main editor + preview panel
 * 
 * Based on layout-composition-patterns.md Editor Layout specification:
 * - Toolbar positioned sticky at 120px from top (below header + context bar)
 * - Content area with minimum height calc(100vh - 200px)
 * - Split view uses 1fr 1fr grid with 1px gray divider
 * - Preview variant uses 1fr + 400px grid layout
 * 
 * @example
 * ```tsx
 * // Standard editor
 * <EditorTemplate
 *   toolbar={
 *     <div className="flex justify-between items-center">
 *       <div className="flex gap-2">
 *         <Button size="sm" variant="ghost">Bold</Button>
 *         <Button size="sm" variant="ghost">Italic</Button>
 *         <Button size="sm" variant="ghost">Link</Button>
 *       </div>
 *       <div className="flex gap-2">
 *         <Button size="sm" variant="secondary">Save Draft</Button>
 *         <Button size="sm">Publish</Button>
 *       </div>
 *     </div>
 *   }
 * >
 *   <textarea className="w-full h-full resize-none border-none outline-none p-6" />
 * </EditorTemplate>
 * 
 * // Split view editor
 * <EditorTemplate
 *   variant="splitView"
 *   toolbar={<EditorToolbar />}
 * >
 *   <div>
 *     <textarea placeholder="Markdown content..." />
 *   </div>
 *   <div>
 *     <MarkdownPreview />
 *   </div>
 * </EditorTemplate>
 * 
 * // Editor with preview panel
 * <EditorTemplate
 *   variant="withPreview"
 *   preview={<PreviewPanel />}
 * >
 *   <CodeEditor />
 * </EditorTemplate>
 * ```
 */
export const EditorTemplate = React.forwardRef<HTMLDivElement, EditorTemplateProps>(
  ({ 
    toolbar,
    preview,
    variant = 'standard',
    containerSize = 'fluid',
    containerPadding = false,
    header,
    footer,
    stickyToolbar = true,
    toolbarHeight = '56px',
    previewWidth = '400px',
    className,
    children,
    ...props 
  }, ref) => {
    return (
      <div ref={ref} className={cn('editor-template', className)} {...props}>
        {/* Optional header */}
        {header && (
          <Container size={containerSize} padding={containerPadding}>
            {header}
          </Container>
        )}
        
        {/* Sticky Toolbar */}
        {toolbar && (
          <div 
            className={cn(
              'editor-toolbar',
              'bg-white border-b border-gray-200 px-6 py-3',
              'z-10', // Ensure toolbar stays above content
              {
                'sticky top-[120px]': stickyToolbar, // 64px header + 56px context bar
                'relative': !stickyToolbar,
              }
            )}
            style={{
              height: toolbarHeight,
            }}
          >
            <Container size={containerSize} padding={false}>
              {toolbar}
            </Container>
          </div>
        )}
        
        {/* Editor Content */}
        <div className="editor-content-container">
          <Container size={containerSize} padding={containerPadding}>
            <div 
              className={cn(
                'editor-content',
                'min-h-[calc(100vh-200px)]', // Account for header, context bar, toolbar
                {
                  // Standard: Full width content
                  'p-6': variant === 'standard',
                  
                  // Split view: Two equal columns with divider
                  'grid grid-cols-2 gap-px bg-gray-200': variant === 'splitView',
                  
                  // With preview: Main content + preview panel
                  'grid gap-6 p-6': variant === 'withPreview',
                }
              )}
              style={{
                // Custom grid template for withPreview variant
                ...(variant === 'withPreview' && {
                  gridTemplateColumns: `1fr ${previewWidth}`,
                }),
              }}
            >
              {variant === 'splitView' ? (
                // Split view: Two equal panels
                <>
                  <div className="editor-panel bg-white p-6">
                    {React.Children.toArray(children)[0] || children}
                  </div>
                  <div className="editor-panel bg-white p-6">
                    {React.Children.toArray(children)[1] || (
                      <div className="flex items-center justify-center h-full text-gray-500">
                        Preview panel
                      </div>
                    )}
                  </div>
                </>
              ) : variant === 'withPreview' ? (
                // With preview: Main editor + preview panel
                <>
                  <main className="editor-main">
                    {children}
                  </main>
                  <aside className="editor-preview">
                    {preview || (
                      <div className="flex items-center justify-center h-full text-gray-500 border border-gray-200 rounded-lg">
                        Preview
                      </div>
                    )}
                  </aside>
                </>
              ) : (
                // Standard: Full width content
                <main className="editor-main">
                  {children}
                </main>
              )}
            </div>
          </Container>
        </div>
        
        {/* Optional footer */}
        {footer && (
          <Container size={containerSize} padding={containerPadding}>
            {footer}
          </Container>
        )}
      </div>
    )
  }
)

EditorTemplate.displayName = 'EditorTemplate'

export default EditorTemplate