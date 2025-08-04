/**
 * Enhanced Table Row with delightful hover animations
 * Includes smooth elevation, highlighting, and contextual interactions
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils';
import { animations, getAnimationConfig } from '../../lib/animations';
import { ChevronRight, Star, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

export interface AnimatedTableRowProps {
  children: React.ReactNode;
  className?: string;
  isHeader?: boolean;
  isHighlighted?: boolean;
  hasWarning?: boolean;
  trend?: 'up' | 'down' | 'neutral';
  importance?: 'high' | 'medium' | 'low';
  onClick?: () => void;
  expandable?: boolean;
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const importanceConfig = {
  high: {
    indicator: 'bg-red-500',
    hover: 'hover:bg-red-50 dark:hover:bg-red-950/20',
    border: 'border-l-red-200 dark:border-l-red-800'
  },
  medium: {
    indicator: 'bg-amber-500',
    hover: 'hover:bg-amber-50 dark:hover:bg-amber-950/20',
    border: 'border-l-amber-200 dark:border-l-amber-800'
  },
  low: {
    indicator: 'bg-emerald-500',
    hover: 'hover:bg-emerald-50 dark:hover:bg-emerald-950/20',
    border: 'border-l-emerald-200 dark:border-l-emerald-800'
  }
};

export const AnimatedTableRow: React.FC<AnimatedTableRowProps> = ({
  children,
  className,
  isHeader = false,
  isHighlighted = false,
  hasWarning = false,
  trend = 'neutral',
  importance,
  onClick,
  expandable = false,
  expanded = false,
  onToggleExpand
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const hoverAnimation = getAnimationConfig(animations.tableRowHover);
  const config = importance ? importanceConfig[importance] : null;

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-3 w-3 text-emerald-500" />;
      case 'down':
        return <TrendingDown className="h-3 w-3 text-red-500" />;
      default:
        return null;
    }
  };

  const handleRowClick = () => {
    if (expandable && onToggleExpand) {
      onToggleExpand();
    } else if (onClick) {
      onClick();
    }
  };

  return (
    <motion.tr
      className={cn(
        "group relative transition-all duration-200",
        isHeader && "bg-gray-50 dark:bg-gray-800 font-semibold",
        !isHeader && "border-b border-gray-200 dark:border-gray-700",
        isHighlighted && "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800",
        hasWarning && "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800",
        config && config.hover,
        config && `border-l-4 ${config.border}`,
        (onClick || expandable) && "cursor-pointer",
        className
      )}
      initial={hoverAnimation.initial}
      whileHover={!isHeader ? hoverAnimation.hover : {}}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleRowClick}
    >
      {/* Importance indicator */}
      {config && (
        <td className="w-1 p-0">
          <motion.div
            className={cn("w-1 h-full", config.indicator)}
            initial={{ scaleY: 0 }}
            animate={{ scaleY: isHovered ? 1.2 : 1 }}
            transition={{ duration: 0.2 }}
          />
        </td>
      )}

      {/* Row content */}
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child) && child.type === 'td') {
          return React.cloneElement(child as React.ReactElement<any>, {
            className: cn(
              child.props.className,
              "transition-all duration-200",
              index === 0 && "relative"
            ),
            children: (
              <div className="flex items-center gap-2">
                {/* First cell content with indicators */}
                {index === 0 && (
                  <>
                    {/* Trend indicator */}
                    <AnimatePresence>
                      {isHovered && getTrendIcon() && (
                        <motion.div
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          exit={{ scale: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          {getTrendIcon()}
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Warning indicator */}
                    {hasWarning && (
                      <motion.div
                        animate={animations.statusPulse.pulse}
                      >
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                      </motion.div>
                    )}

                    {/* Star for highlighted rows */}
                    {isHighlighted && (
                      <Star className="h-4 w-4 text-blue-500 fill-current" />
                    )}
                  </>
                )}

                {/* Original cell content */}
                {child.props.children}

                {/* Expandable indicator */}
                {index === 0 && expandable && (
                  <motion.div
                    className="ml-auto"
                    animate={{ rotate: expanded ? 90 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
                  </motion.div>
                )}
              </div>
            )
          });
        }
        return child;
      })}

      {/* Hover glow effect */}
      <AnimatePresence>
        {isHovered && !isHeader && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </AnimatePresence>
    </motion.tr>
  );
};

export default AnimatedTableRow;