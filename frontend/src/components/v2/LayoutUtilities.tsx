import React from 'react';
import { Space, Divider, Flex } from 'antd';
import type { SpaceProps, FlexProps } from 'antd';

interface SpacingProps extends Omit<SpaceProps, 'size'> {
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large' | number;
  className?: string;
}

interface FlexContainerProps extends FlexProps {
  children: React.ReactNode;
  className?: string;
}

interface SectionDividerProps {
  title?: string;
  className?: string;
  orientation?: 'left' | 'right' | 'center';
  dashed?: boolean;
}

interface StackProps {
  children: React.ReactNode;
  spacing?: 'small' | 'medium' | 'large';
  direction?: 'vertical' | 'horizontal';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
  className?: string;
  style?: React.CSSProperties;
}

// Enhanced spacing component with consistent sizing
const Spacing: React.FC<SpacingProps> = ({
  children,
  size = 'medium',
  className = '',
  ...spaceProps
}) => {
  const sizeMap = {
    small: 8,
    medium: 16,
    large: 24
  };

  const actualSize = typeof size === 'string' ? sizeMap[size] : size;

  return (
    <Space
      {...spaceProps}
      size={actualSize}
      className={`layout-spacing ${className}`}
    >
      {children}
    </Space>
  );
};

// Flexible container with common patterns
const FlexContainer: React.FC<FlexContainerProps> = ({
  children,
  className = '',
  ...flexProps
}) => {
  return (
    <Flex
      {...flexProps}
      className={`flex-container ${className}`}
      style={{
        width: '100%',
        ...flexProps.style
      }}
    >
      {children}
    </Flex>
  );
};

// Section divider with optional title
const SectionDivider: React.FC<SectionDividerProps> = ({
  title,
  className = '',
  orientation = 'left',
  dashed = false
}) => {
  return (
    <Divider
      orientation={orientation}
      dashed={dashed}
      className={`section-divider ${className}`}
      style={{
        margin: '24px 0',
        color: '#8c8c8c',
        fontWeight: 500
      }}
    >
      {title}
    </Divider>
  );
};

// Stack layout component for consistent vertical/horizontal stacking
const Stack: React.FC<StackProps> = ({
  children,
  spacing = 'medium',
  direction = 'vertical',
  align = 'stretch',
  justify = 'start',
  className = '',
  style = {}
}) => {
  const spacingMap = {
    small: 8,
    medium: 16,
    large: 24
  };

  const flexDirection = direction === 'vertical' ? 'column' : 'row';
  const alignItems = align === 'stretch' ? 'stretch' : 
                     align === 'start' ? 'flex-start' :
                     align === 'end' ? 'flex-end' : 'center';
  const justifyContent = justify === 'start' ? 'flex-start' :
                        justify === 'end' ? 'flex-end' :
                        justify === 'space-between' ? 'space-between' :
                        justify === 'space-around' ? 'space-around' : 'center';

  return (
    <div
      className={`stack stack-${direction} ${className}`}
      style={{
        display: 'flex',
        flexDirection,
        alignItems,
        justifyContent,
        gap: spacingMap[spacing],
        width: '100%',
        ...style
      }}
    >
      {children}
    </div>
  );
};

// Common layout patterns
const LayoutPatterns = {
  // Header with title and actions
  SectionHeader: ({ 
    title, 
    actions, 
    subtitle 
  }: { 
    title: React.ReactNode;
    actions?: React.ReactNode;
    subtitle?: React.ReactNode;
  }) => (
    <div className="section-header" style={{ marginBottom: '16px' }}>
      <FlexContainer justify="space-between" align="flex-start">
        <div>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
            {title}
          </h3>
          {subtitle && (
            <div style={{ color: '#8c8c8c', fontSize: '14px', marginTop: '4px' }}>
              {subtitle}
            </div>
          )}
        </div>
        {actions && <div>{actions}</div>}
      </FlexContainer>
    </div>
  ),

  // Content with sidebar pattern
  ContentWithSidebar: ({
    content,
    sidebar,
    sidebarWidth = '280px',
    sidebarPosition = 'right'
  }: {
    content: React.ReactNode;
    sidebar: React.ReactNode;
    sidebarWidth?: string;
    sidebarPosition?: 'left' | 'right';
  }) => (
    <FlexContainer gap="large" align="flex-start">
      {sidebarPosition === 'left' && (
        <div style={{ flexShrink: 0, width: sidebarWidth }}>
          {sidebar}
        </div>
      )}
      <div style={{ flex: 1, minWidth: 0 }}>
        {content}
      </div>
      {sidebarPosition === 'right' && (
        <div style={{ flexShrink: 0, width: sidebarWidth }}>
          {sidebar}
        </div>
      )}
    </FlexContainer>
  ),

  // Centered content with max width
  CenteredContainer: ({
    children,
    maxWidth = '1200px'
  }: {
    children: React.ReactNode;
    maxWidth?: string;
  }) => (
    <div
      className="centered-container"
      style={{
        width: '100%',
        maxWidth,
        margin: '0 auto',
        padding: '0 24px'
      }}
    >
      {children}
    </div>
  ),

  // Form section with consistent spacing
  FormSection: ({
    title,
    children,
    collapsible = false
  }: {
    title?: string;
    children: React.ReactNode;
    collapsible?: boolean;
  }) => (
    <div className="form-section" style={{ marginBottom: '24px' }}>
      {title && (
        <h4 style={{ 
          margin: '0 0 16px 0', 
          fontSize: '14px', 
          fontWeight: 500,
          color: '#262626'
        }}>
          {title}
        </h4>
      )}
      <div style={{ padding: collapsible ? '16px' : '0' }}>
        {children}
      </div>
    </div>
  )
};

export { 
  Spacing, 
  FlexContainer, 
  SectionDivider, 
  Stack, 
  LayoutPatterns 
};

export default {
  Spacing,
  FlexContainer,
  SectionDivider,
  Stack,
  LayoutPatterns
}; 