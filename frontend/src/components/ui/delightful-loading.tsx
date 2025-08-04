/**
 * Delightful Loading States with Business-Themed Messages
 * Makes waiting feel purposeful and engaging with personality touches
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils';
import { 
  Loader2, 
  Brain, 
  Calculator, 
  TrendingUp, 
  Users, 
  Building2,
  Sparkles,
  Coffee,
  Lightbulb,
  Target
} from 'lucide-react';

export interface DelightfulLoadingProps {
  isLoading: boolean;
  context?: 'planning' | 'calculating' | 'saving' | 'analyzing' | 'generating' | 'optimizing';
  size?: 'sm' | 'md' | 'lg';
  showMessages?: boolean;
  customMessage?: string;
  className?: string;
}

const loadingContexts = {
  planning: {
    icon: Building2,
    emoji: '📋',
    messages: [
      "Crafting your perfect plan...",
      "Organizing workforce strategies...",
      "Aligning business objectives...",
      "Optimizing resource allocation...",
      "Building your roadmap to success..."
    ],
    color: 'text-blue-500',
    bg: 'bg-blue-50 dark:bg-blue-950/30'
  },
  calculating: {
    icon: Calculator,
    emoji: '🧮',
    messages: [
      "Crunching the numbers...",
      "Analyzing financial projections...",
      "Computing growth scenarios...",
      "Balancing the books...",
      "Running the calculations..."
    ],
    color: 'text-emerald-500',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30'
  },
  saving: {
    icon: Sparkles,
    emoji: '💾',
    messages: [
      "Saving your brilliant work...",
      "Securing your data...",
      "Storing your progress...",
      "Backing up your plan...",
      "Preserving your insights..."
    ],
    color: 'text-purple-500',
    bg: 'bg-purple-50 dark:bg-purple-950/30'
  },
  analyzing: {
    icon: Brain,
    emoji: '🔍',
    messages: [
      "Analyzing patterns...",
      "Discovering insights...",
      "Processing data trends...",
      "Examining correlations...",
      "Uncovering opportunities..."
    ],
    color: 'text-amber-500',
    bg: 'bg-amber-50 dark:bg-amber-950/30'
  },
  generating: {
    icon: Lightbulb,
    emoji: '✨',
    messages: [
      "Generating recommendations...",
      "Creating smart suggestions...",
      "Cooking up new ideas...",
      "Brewing insights...",
      "Crafting possibilities..."
    ],
    color: 'text-orange-500',
    bg: 'bg-orange-50 dark:bg-orange-950/30'
  },
  optimizing: {
    icon: Target,
    emoji: '🎯',
    messages: [
      "Optimizing performance...",
      "Fine-tuning parameters...",
      "Improving efficiency...",
      "Polishing the details...",
      "Maximizing results..."
    ],
    color: 'text-red-500',
    bg: 'bg-red-50 dark:bg-red-950/30'
  }
};

const sizeConfig = {
  sm: {
    container: 'p-3',
    icon: 'h-4 w-4',
    text: 'text-sm',
    emoji: 'text-base'
  },
  md: {
    container: 'p-4',
    icon: 'h-6 w-6',
    text: 'text-base',
    emoji: 'text-lg'
  },
  lg: {
    container: 'p-6',
    icon: 'h-8 w-8',
    text: 'text-lg',
    emoji: 'text-xl'
  }
};

const funnyMessages = [
  "Teaching AI to count... 🤖",
  "Caffeinating the algorithms... ☕",
  "Asking the data nicely... 🙏",
  "Convincing numbers to cooperate... 🔢",
  "Summoning the spreadsheet spirits... 👻",
  "Tickling the databases... 😄",
  "Negotiating with Excel... 📊",
  "Herding cats... but for data... 🐱",
  "Consulting the business oracle... 🔮",
  "Loading awesomeness... 🚀"
];

export const DelightfulLoading: React.FC<DelightfulLoadingProps> = ({
  isLoading,
  context = 'calculating',
  size = 'md',
  showMessages = true,
  customMessage,
  className
}) => {
  const [messageIndex, setMessageIndex] = useState(0);
  const [showFunnyMessage, setShowFunnyMessage] = useState(false);
  
  const config = loadingContexts[context];
  const sizeConf = sizeConfig[size];
  const Icon = config.icon;

  useEffect(() => {
    if (!isLoading) return;

    // Cycle through messages
    const messageTimer = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % config.messages.length);
    }, 2000);

    // Show funny message occasionally
    const funnyTimer = setInterval(() => {
      setShowFunnyMessage(true);
      setTimeout(() => setShowFunnyMessage(false), 1500);
    }, 8000);

    return () => {
      clearInterval(messageTimer);
      clearInterval(funnyTimer);
    };
  }, [isLoading, config.messages.length]);

  if (!isLoading) return null;

  const currentMessage = customMessage || 
    (showFunnyMessage ? funnyMessages[Math.floor(Math.random() * funnyMessages.length)] : config.messages[messageIndex]);

  return (
    <motion.div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border",
        config.bg,
        "border-gray-200 dark:border-gray-700",
        sizeConf.container,
        className
      )}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      {/* Animated loading icon */}
      <div className="relative mb-3">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className={cn("absolute inset-0", config.color)}
        >
          <Loader2 className={cn(sizeConf.icon, "opacity-30")} />
        </motion.div>
        
        <motion.div
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 5, -5, 0] 
          }}
          transition={{ 
            duration: 1.5, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
          className={config.color}
        >
          <Icon className={sizeConf.icon} />
        </motion.div>
      </div>

      {/* Loading message with emoji */}
      {showMessages && (
        <div className="text-center space-y-1">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentMessage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="flex items-center gap-2"
            >
              <span className={cn("font-medium text-gray-700 dark:text-gray-300", sizeConf.text)}>
                {currentMessage}
              </span>
              <span className={sizeConf.emoji}>{config.emoji}</span>
            </motion.div>
          </AnimatePresence>

          {/* Animated dots */}
          <div className="flex justify-center gap-1">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className={cn("w-1.5 h-1.5 rounded-full", config.color.replace('text-', 'bg-'))}
                animate={{
                  opacity: [0.3, 1, 0.3],
                  scale: [0.8, 1.2, 0.8]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  delay: i * 0.2,
                  ease: "easeInOut"
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Subtle sparkle effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute opacity-20"
            style={{
              left: `${20 + i * 25}%`,
              top: `${20 + i * 15}%`
            }}
            animate={{
              scale: [0, 1, 0],
              rotate: [0, 180, 360],
              opacity: [0, 0.3, 0]
            }}
            transition={{
              duration: 3,
              delay: i * 1,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Sparkles className="h-3 w-3 text-yellow-400" />
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default DelightfulLoading;