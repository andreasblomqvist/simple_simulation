import React from 'react';
import { Row, Col } from 'antd';
import type { RowProps, ColProps } from 'antd';

interface ResponsiveGridProps extends RowProps {
  children: React.ReactNode;
  spacing?: 'small' | 'medium' | 'large';
  className?: string;
}

interface ResponsiveColProps extends ColProps {
  children: React.ReactNode;
  desktop?: number;
  tablet?: number;
  mobile?: number;
  className?: string;
}

const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  spacing = 'medium',
  className = '',
  ...rowProps
}) => {
  const spacingMap = {
    small: [8, 8] as [number, number],
    medium: [16, 16] as [number, number],
    large: [24, 24] as [number, number]
  };

  return (
    <Row
      {...rowProps}
      gutter={spacingMap[spacing]}
      className={`responsive-grid ${className}`}
    >
      {children}
    </Row>
  );
};

const ResponsiveCol: React.FC<ResponsiveColProps> = ({
  children,
  desktop = 24,
  tablet = 24,
  mobile = 24,
  className = '',
  ...colProps
}) => {
  // Responsive breakpoints following Ant Design standards
  const responsiveProps = {
    xs: mobile,      // < 576px
    sm: mobile,      // ≥ 576px
    md: tablet,      // ≥ 768px
    lg: desktop,     // ≥ 992px
    xl: desktop,     // ≥ 1200px
    xxl: desktop,    // ≥ 1600px
  };

  return (
    <Col
      {...colProps}
      {...responsiveProps}
      className={`responsive-col ${className}`}
    >
      {children}
    </Col>
  );
};

// Predefined grid layouts following design specifications
const GridLayout = {
  // Desktop: 3-column, Tablet: 2-column, Mobile: 1-column
  ThreeColumn: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="medium">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={8} tablet={12} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),

  // Desktop: 4-column, Tablet: 2-column, Mobile: 1-column  
  FourColumn: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="medium">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={6} tablet={12} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),

  // Desktop: 2-column, Tablet: 2-column, Mobile: 1-column
  TwoColumn: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="medium">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={12} tablet={12} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),

  // Single column on all devices
  SingleColumn: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="medium">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={24} tablet={24} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),

  // KPI Layout: Desktop 3-col, Tablet 2-col, Mobile 1-col
  KPILayout: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="large">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={8} tablet={12} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),

  // Form Layout: Consistent 2-column on desktop/tablet, 1-column on mobile
  FormLayout: ({ children }: { children: React.ReactNode }) => (
    <ResponsiveGrid spacing="medium">
      {React.Children.map(children, (child, index) => (
        <ResponsiveCol key={index} desktop={12} tablet={12} mobile={24}>
          {child}
        </ResponsiveCol>
      ))}
    </ResponsiveGrid>
  ),
};

export { ResponsiveGrid, ResponsiveCol, GridLayout };
export default ResponsiveGrid; 