/**
 * Enhanced Progress Bar with delightful animations
 * Includes smooth filling, celebration effects, and personality touches
 */
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Progress } from './progress';
import { cn } from '../../lib/utils';
import { animations } from '../../lib/animations';
import { Sparkles, Star, Trophy, Zap, Target } from 'lucide-react';

export interface AnimatedProgressProps {
  value: number;
  className?: string;
  showLabel?: boolean;
  showCelebration?: boolean;
  theme?: 'default' | 'success' | 'warning' | 'info' | 'purple';
  size?: 'sm' | 'md' | 'lg';
  emoji?: string;
  milestones?: number[];
  label?: string;
}

const themeConfig = {
  default: {
    bg: 'bg-gray-200 dark:bg-gray-700',
    fill: 'bg-blue-500',
    glow: 'shadow-blue-500/20',
    text: 'text-blue-700 dark:text-blue-300'
  },
  success: {
    bg: 'bg-emerald-100 dark:bg-emerald-900/30',
    fill: 'bg-emerald-500',
    glow: 'shadow-emerald-500/20',
    text: 'text-emerald-700 dark:text-emerald-300'
  },
  warning: {
    bg: 'bg-amber-100 dark:bg-amber-900/30',
    fill: 'bg-amber-500',
    glow: 'shadow-amber-500/20',
    text: 'text-amber-700 dark:text-amber-300'
  },
  info: {
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    fill: 'bg-blue-500',
    glow: 'shadow-blue-500/20',
    text: 'text-blue-700 dark:text-blue-300'
  },
  purple: {
    bg: 'bg-purple-100 dark:bg-purple-900/30',
    fill: 'bg-purple-500',
    glow: 'shadow-purple-500/20',
    text: 'text-purple-700 dark:text-purple-300'
  }
};

const sizeConfig = {
  sm: { height: 'h-2', text: 'text-xs', icon: 'h-3 w-3' },
  md: { height: 'h-3', text: 'text-sm', icon: 'h-4 w-4' },
  lg: { height: 'h-4', text: 'text-base', icon: 'h-5 w-5' }
};

export const AnimatedProgress: React.FC<AnimatedProgressProps> = ({
  value,
  className,
  showLabel = true,
  showCelebration = true,
  theme = 'default',
  size = 'md',
  emoji,
  milestones = [25, 50, 75, 100],
  label
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const [completedMilestones, setCompletedMilestones] = useState<number[]>([]);
  const [showConfetti, setShowConfetti] = useState(false);
  
  const config = themeConfig[theme];
  const sizeConf = sizeConfig[size];

  useEffect(() => {
    // Animate progress value
    const timer = setTimeout(() => {
      setAnimatedValue(value);
    }, 100);

    // Check for milestone completions
    const newMilestones = milestones.filter(
      milestone => value >= milestone && !completedMilestones.includes(milestone)
    );

    if (newMilestones.length > 0) {
      setCompletedMilestones(prev => [...prev, ...newMilestones]);
      
      // Show confetti for 100% completion
      if (newMilestones.includes(100) && showCelebration) {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 2000);
      }
    }

    return () => clearTimeout(timer);
  }, [value, milestones, completedMilestones, showCelebration]);

  const getPersonalityIcon = () => {
    if (value === 100) return <Trophy className={cn(sizeConf.icon, config.text)} />;
    if (value >= 75) return <Star className={cn(sizeConf.icon, config.text)} />;
    if (value >= 50) return <Zap className={cn(sizeConf.icon, config.text)} />;
    if (value >= 25) return <Target className={cn(sizeConf.icon, config.text)} />;
    return null;
  };

  const getMotivationalMessage = () => {
    if (value === 100) return "🎉 Perfect! All done!";
    if (value >= 90) return "🔥 Almost there!";
    if (value >= 75) return "💪 Great progress!";
    if (value >= 50) return "⚡ Halfway there!";
    if (value >= 25) return "🚀 Getting started!";
    return "📋 Just beginning...";
  };

  return (
    <div className={cn("relative space-y-2", className)}>
      {/* Label and value */}
      {showLabel && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getPersonalityIcon()}
            <span className={cn("font-medium", sizeConf.text, config.text)}>
              {label || getMotivationalMessage()}
            </span>
            {emoji && <span className={sizeConf.text}>{emoji}</span>}
          </div>
          <span className={cn("font-bold", sizeConf.text, config.text)}>
            {Math.round(value)}%
          </span>
        </div>
      )}

      {/* Progress bar with glow effect */}
      <motion.div
        className={cn(
          "relative rounded-full overflow-hidden",
          sizeConf.height,
          config.bg
        )}
        whileHover={{
          boxShadow: `0 0 20px ${config.glow}`,
          transition: { duration: 0.3 }
        }}
      >
        <motion.div
          className={cn(
            "h-full rounded-full relative overflow-hidden",
            config.fill
          )}
          initial={{ width: "0%" }}
          animate={{ width: `${animatedValue}%` }}
          transition={{ 
            duration: 1.2, 
            ease: "easeOut",
            delay: 0.1
          }}
        >
          {/* Shimmer effect for active progress */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{
              x: ["-100%", "200%"],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        </motion.div>

        {/* Milestone markers */}
        {milestones.map((milestone) => (
          <motion.div
            key={milestone}
            className="absolute top-0 w-0.5 h-full bg-white/50"
            style={{ left: `${milestone}%` }}
            initial={{ opacity: 0 }}
            animate={{ opacity: animatedValue >= milestone ? 1 : 0.3 }}
            transition={{ duration: 0.3 }}
          />
        ))}
      </motion.div>

      {/* Confetti celebration */}
      <AnimatePresence>
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute"
                style={{
                  left: `${20 + i * 10}%`,
                  top: "50%"
                }}
                {...animations.confetti}
                transition={{
                  ...animations.confetti.burst.transition,
                  delay: i * 0.1
                }}
              >
                <Sparkles className="h-4 w-4 text-yellow-500" />
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Milestone celebrations */}
      <AnimatePresence>
        {completedMilestones.map((milestone) => (
          <motion.div
            key={`celebration-${milestone}`}
            className={cn(
              "absolute right-0 top-0 px-2 py-1 rounded-full text-xs font-bold",
              "bg-gradient-to-r from-yellow-400 to-orange-500 text-white"
            )}
            initial={{ scale: 0, y: 0 }}
            animate={{ 
              scale: [0, 1.2, 1],
              y: [0, -20, -40]
            }}
            exit={{ 
              scale: 0,
              opacity: 0
            }}
            transition={{ 
              duration: 1.5,
              ease: "easeOut"
            }}
          >
            🎯 {milestone}%
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default AnimatedProgress;