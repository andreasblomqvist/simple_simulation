/**
 * Success Celebration Component
 * Delightful feedback for completed actions with confetti and positive messaging
 */
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils';
import { animations } from '../../lib/animations';
import { 
  CheckCircle2, 
  Star, 
  Trophy, 
  Sparkles, 
  Heart,
  Target,
  Award,
  Zap
} from 'lucide-react';

export interface SuccessCelebrationProps {
  show: boolean;
  message?: string;
  type?: 'default' | 'milestone' | 'completion' | 'achievement' | 'save';
  duration?: number;
  onComplete?: () => void;
  confettiCount?: number;
  size?: 'sm' | 'md' | 'lg';
}

const celebrationTypes = {
  default: {
    icon: CheckCircle2,
    emoji: '✅',
    color: 'text-emerald-500',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30',
    border: 'border-emerald-200 dark:border-emerald-800',
    message: 'Great job!'
  },
  milestone: {
    icon: Target,
    emoji: '🎯',
    color: 'text-blue-500',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800',
    message: 'Milestone reached!'
  },
  completion: {
    icon: Trophy,
    emoji: '🏆',
    color: 'text-yellow-500',
    bg: 'bg-yellow-50 dark:bg-yellow-950/30',
    border: 'border-yellow-200 dark:border-yellow-800',
    message: 'Task completed!'
  },
  achievement: {
    icon: Award,
    emoji: '🏅',
    color: 'text-purple-500',
    bg: 'bg-purple-50 dark:bg-purple-950/30',
    border: 'border-purple-200 dark:border-purple-800',
    message: 'Achievement unlocked!'
  },
  save: {
    icon: Zap,
    emoji: '💾',
    color: 'text-green-500',
    bg: 'bg-green-50 dark:bg-green-950/30',
    border: 'border-green-200 dark:border-green-800',
    message: 'Changes saved!'
  }
};

const sizeConfig = {
  sm: {
    container: 'px-3 py-2',
    icon: 'h-4 w-4',
    text: 'text-sm',
    emoji: 'text-base'
  },
  md: {
    container: 'px-4 py-3',
    icon: 'h-5 w-5',
    text: 'text-base',
    emoji: 'text-lg'
  },
  lg: {
    container: 'px-6 py-4',
    icon: 'h-6 w-6',
    text: 'text-lg',
    emoji: 'text-xl'
  }
};

export const SuccessCelebration: React.FC<SuccessCelebrationProps> = ({
  show,
  message,
  type = 'default',
  duration = 3000,
  onComplete,
  confettiCount = 12,
  size = 'md'
}) => {
  const [showConfetti, setShowConfetti] = useState(false);
  
  const config = celebrationTypes[type];
  const sizeConf = sizeConfig[size];
  const Icon = config.icon;

  useEffect(() => {
    if (show) {
      setShowConfetti(true);
      
      const timer = setTimeout(() => {
        setShowConfetti(false);
        onComplete?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [show, duration, onComplete]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Celebration card */}
          <motion.div
            className={cn(
              "relative rounded-xl border shadow-lg pointer-events-auto",
              config.bg,
              config.border,
              sizeConf.container
            )}
            initial={{ scale: 0, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0, y: -20 }}
            transition={{
              type: "spring",
              stiffness: 500,
              damping: 25
            }}
          >
            <div className="flex items-center gap-3">
              {/* Animated icon */}
              <motion.div
                animate={animations.successCelebration.celebrate}
                className={config.color}
              >
                <Icon className={sizeConf.icon} />
              </motion.div>

              {/* Message */}
              <div className="flex items-center gap-2">
                <span className={cn("font-semibold", config.color, sizeConf.text)}>
                  {message || config.message}
                </span>
                <span className={sizeConf.emoji}>{config.emoji}</span>
              </div>
            </div>

            {/* Sparkle effects around the card */}
            <div className="absolute inset-0 pointer-events-none">
              {[...Array(4)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute"
                  style={{
                    left: i % 2 === 0 ? '-10px' : 'calc(100% - 10px)',
                    top: i < 2 ? '-10px' : 'calc(100% - 10px)'
                  }}
                  animate={{
                    scale: [0, 1, 0],
                    rotate: [0, 180, 360],
                    opacity: [0, 1, 0]
                  }}
                  transition={{
                    duration: 1,
                    delay: i * 0.1,
                    ease: "easeInOut"
                  }}
                >
                  <Sparkles className="h-4 w-4 text-yellow-400" />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Confetti burst */}
          {showConfetti && (
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              {[...Array(confettiCount)].map((_, i) => {
                const colors = [
                  'text-red-500',
                  'text-blue-500',
                  'text-green-500',
                  'text-yellow-500',
                  'text-purple-500',
                  'text-pink-500'
                ];
                const icons = [Star, Heart, Sparkles, Trophy];
                const Icon = icons[i % icons.length];
                
                return (
                  <motion.div
                    key={i}
                    className={cn("absolute", colors[i % colors.length])}
                    style={{
                      left: `${45 + (i % 4) * 2.5}%`,
                      top: '50%'
                    }}
                    initial={{
                      scale: 0,
                      rotate: 0,
                      opacity: 1,
                      x: 0,
                      y: 0
                    }}
                    animate={{
                      scale: [0, 1, 0.5],
                      rotate: [0, 360, 720],
                      opacity: [1, 1, 0],
                      x: [(Math.random() - 0.5) * 200],
                      y: [0, -100 - Math.random() * 100, -200 - Math.random() * 100]
                    }}
                    transition={{
                      duration: 2 + Math.random(),
                      delay: i * 0.05,
                      ease: "easeOut"
                    }}
                  >
                    <Icon className="h-4 w-4" />
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SuccessCelebration;