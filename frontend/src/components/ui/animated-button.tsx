/**
 * Enhanced Button with delightful micro-interactions
 * Adds satisfying press feedback, hover effects, and loading states
 */
import React, { forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, ButtonProps } from './button';
import { animations, getAnimationConfig } from '../../lib/animations';
import { cn } from '../../lib/utils';
import { Loader2, Check, AlertCircle } from 'lucide-react';

export interface AnimatedButtonProps extends ButtonProps {
  isLoading?: boolean;
  isSuccess?: boolean;
  isError?: boolean;
  successMessage?: string;
  errorMessage?: string;
  enableHaptics?: boolean;
}

export const AnimatedButton = forwardRef<HTMLButtonElement, AnimatedButtonProps>(
  ({ 
    children, 
    className, 
    isLoading = false,
    isSuccess = false,
    isError = false,
    successMessage,
    errorMessage,
    enableHaptics = true,
    disabled,
    onClick,
    ...props 
  }, ref) => {
    const buttonAnimation = getAnimationConfig(animations.buttonPress);
    
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      // Trigger haptic feedback on mobile devices
      if (enableHaptics && 'vibrate' in navigator) {
        navigator.vibrate(50);
      }
      
      onClick?.(e);
    };

    const getButtonContent = () => {
      if (isLoading) {
        return (
          <motion.div
            className="flex items-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Loading...</span>
          </motion.div>
        );
      }

      if (isSuccess) {
        return (
          <motion.div
            className="flex items-center gap-2"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 20 }}
          >
            <motion.div
              animate={animations.successCelebration.celebrate}
            >
              <Check className="h-4 w-4" />
            </motion.div>
            <span>{successMessage || 'Success!'}</span>
          </motion.div>
        );
      }

      if (isError) {
        return (
          <motion.div
            className="flex items-center gap-2"
            initial={{ x: 0 }}
            animate={animations.validationError.error}
          >
            <AlertCircle className="h-4 w-4" />
            <span>{errorMessage || 'Error'}</span>
          </motion.div>
        );
      }

      return children;
    };

    return (
      <motion.div
        whileHover={!disabled ? buttonAnimation.hover : {}}
        whileTap={!disabled ? buttonAnimation.pressed : {}}
        transition={buttonAnimation.transition}
      >
        <Button
          ref={ref}
          className={cn(
            "relative transition-all duration-200",
            isSuccess && "bg-emerald-500 hover:bg-emerald-600 border-emerald-500",
            isError && "bg-red-500 hover:bg-red-600 border-red-500",
            className
          )}
          disabled={disabled || isLoading}
          onClick={handleClick}
          {...props}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={isLoading ? 'loading' : isSuccess ? 'success' : isError ? 'error' : 'default'}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.15 }}
            >
              {getButtonContent()}
            </motion.div>
          </AnimatePresence>
        </Button>
      </motion.div>
    );
  }
);

AnimatedButton.displayName = "AnimatedButton";