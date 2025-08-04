/**
 * Enhanced Input with delightful focus animations and smart validation
 * Includes glow effects, validation feedback, and contextual suggestions
 */
import React, { forwardRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Input } from './input';
import { Badge } from './badge';
import { animations, getAnimationConfig } from '../../lib/animations';
import { cn } from '../../lib/utils';
import { Check, AlertCircle, Lightbulb, TrendingUp, TrendingDown } from 'lucide-react';

export interface AnimatedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  isValid?: boolean;
  isError?: boolean;
  errorMessage?: string;
  successMessage?: string;
  suggestion?: string;
  showTrend?: 'up' | 'down' | null;
  contextualHint?: string;
  enableSmartSuggestions?: boolean;
}

export const AnimatedInput = forwardRef<HTMLInputElement, AnimatedInputProps>(
  ({ 
    className,
    isValid = false,
    isError = false,
    errorMessage,
    successMessage,
    suggestion,
    showTrend = null,
    contextualHint,
    enableSmartSuggestions = true,
    onFocus,
    onBlur,
    onChange,
    value,
    ...props 
  }, ref) => {
    const [isFocused, setIsFocused] = useState(false);
    const [showSuggestion, setShowSuggestion] = useState(false);
    const [showContextHint, setShowContextHint] = useState(false);
    
    const focusAnimation = getAnimationConfig(animations.inputFocus);

    useEffect(() => {
      // Show suggestion when user pauses typing
      if (enableSmartSuggestions && value && !isError) {
        const timer = setTimeout(() => {
          setShowSuggestion(true);
        }, 1000);
        
        return () => clearTimeout(timer);
      } else {
        setShowSuggestion(false);
      }
    }, [value, enableSmartSuggestions, isError]);

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      setShowContextHint(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      setShowContextHint(false);
      setShowSuggestion(false);
      onBlur?.(e);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setShowSuggestion(false); // Hide suggestion when typing
      onChange?.(e);
    };

    const getTrendIcon = () => {
      if (showTrend === 'up') return <TrendingUp className="h-3 w-3 text-emerald-500" />;
      if (showTrend === 'down') return <TrendingDown className="h-3 w-3 text-red-500" />;
      return null;
    };

    const getValidationIcon = () => {
      if (isValid) return <Check className="h-4 w-4 text-emerald-500" />;
      if (isError) return <AlertCircle className="h-4 w-4 text-red-500" />;
      return null;
    };

    return (
      <div className="relative space-y-2">
        <motion.div
          className="relative"
          animate={isFocused ? focusAnimation.focused : focusAnimation.initial}
        >
          <Input
            ref={ref}
            className={cn(
              "transition-all duration-200 pr-8",
              isValid && "border-emerald-500 bg-emerald-50/30 dark:bg-emerald-950/30",
              isError && "border-red-500 bg-red-50/30 dark:bg-red-950/30",
              isFocused && "ring-2 ring-blue-500/20",
              className
            )}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onChange={handleChange}
            value={value}
            {...props}
          />
          
          {/* Validation and trend icons */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {getTrendIcon()}
            <AnimatePresence>
              {(isValid || isError) && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 20 }}
                >
                  {getValidationIcon()}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Contextual hint */}
        <AnimatePresence>
          {showContextHint && contextualHint && (
            <motion.div
              className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400"
              {...animations.slideIn}
            >
              <Lightbulb className="h-3 w-3 mt-0.5 text-amber-500" />
              <span>{contextualHint}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Smart suggestion */}
        <AnimatePresence>
          {showSuggestion && suggestion && !isError && (
            <motion.div
              className="flex items-center gap-2"
              {...animations.slideIn}
            >
              <Badge 
                variant="outline" 
                className="text-xs bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800"
              >
                <Lightbulb className="h-3 w-3 mr-1" />
                Suggestion: {suggestion}
              </Badge>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Validation messages */}
        <AnimatePresence>
          {(successMessage || errorMessage) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className={cn(
                "text-xs flex items-center gap-1.5",
                isValid && "text-emerald-600 dark:text-emerald-400",
                isError && "text-red-600 dark:text-red-400"
              )}
            >
              {getValidationIcon()}
              <span>{successMessage || errorMessage}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

AnimatedInput.displayName = "AnimatedInput";