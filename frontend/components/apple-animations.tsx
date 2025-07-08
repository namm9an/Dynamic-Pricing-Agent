"use client"

import type React from "react"

import { motion, useTransform, useScroll } from "framer-motion"
import { useState, useEffect } from "react"

// Apple-style animation presets
export const appleAnimations = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] },
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] },
  },
  magnetic: {
    whileHover: {
      scale: 1.05,
      y: -2,
      transition: { duration: 0.3, ease: "easeOut" },
    },
  },
  spring: {
    type: "spring",
    stiffness: 300,
    damping: 30,
    mass: 0.8,
  },
}

// Staggered container animation
export const StaggerContainer = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <motion.div
    className={className}
    initial="hidden"
    animate="visible"
    variants={{
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: 0.1,
          delayChildren: 0.1,
        },
      },
    }}
  >
    {children}
  </motion.div>
)

// Staggered item component
export const StaggerItem = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <motion.div
    className={className}
    variants={{
      hidden: { opacity: 0, y: 20 },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.6,
          ease: [0.25, 0.46, 0.45, 0.94],
        },
      },
    }}
  >
    {children}
  </motion.div>
)

// Magnetic card with 3D hover effect
export const MagneticCard = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      className={`magnetic-card ${className}`}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{
        scale: 1.02,
        rotateX: 5,
        rotateY: 5,
        z: 20,
        transition: { duration: 0.3, ease: "easeOut" },
      }}
      style={{
        transformStyle: "preserve-3d",
        transformOrigin: "center",
      }}
    >
      {children}
    </motion.div>
  )
}

// Apple-style button with press feedback
export const AppleButton = ({
  children,
  onClick,
  className = "",
  variant = "primary",
}: {
  children: React.ReactNode
  onClick?: () => void
  className?: string
  variant?: "primary" | "secondary"
}) => (
  <motion.button
    className={`apple-button ${variant === "primary" ? "bg-[#FF6B35]" : "bg-gray-700"} text-white px-6 py-3 rounded-lg font-semibold ${className}`}
    onClick={onClick}
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.96 }}
    transition={{ duration: 0.15, ease: "easeOut" }}
  >
    {children}
  </motion.button>
)

// Smooth number counter with Apple-style easing
export const AnimatedCounter = ({
  value,
  duration = 0.8,
  className = "",
}: {
  value: number
  duration?: number
  className?: string
}) => {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const startTime = performance.now()
    const startValue = displayValue
    const difference = value - startValue

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / (duration * 1000), 1)

      // Apple's easeOutCubic
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      const currentValue = startValue + difference * easeProgress

      setDisplayValue(currentValue)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [value, duration, displayValue])

  return <span className={className}>{Math.round(displayValue * 100) / 100}</span>
}

// Circular progress with Apple-style animation
export const AppleProgress = ({
  value,
  size = 120,
  strokeWidth = 8,
  className = "",
}: {
  value: number
  size?: number
  strokeWidth?: number
  className?: string
}) => {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,107,53,0.1)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{
            duration: 0.8,
            ease: [0.25, 0.46, 0.45, 0.94],
          }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF6B35" />
            <stop offset="100%" stopColor="#EAE0D5" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <AnimatedCounter value={value} className="text-2xl font-bold text-[#FF6B35]" />
        <span className="text-sm text-gray-400 ml-1">%</span>
      </div>
    </div>
  )
}

// Apple-style toggle switch
export const AppleToggle = ({
  checked,
  onChange,
  className = "",
}: {
  checked: boolean
  onChange: (checked: boolean) => void
  className?: string
}) => (
  <motion.div
    className={`toggle-switch ${checked ? "active" : ""} ${className}`}
    onClick={() => onChange(!checked)}
    animate={{
      backgroundColor: checked ? "#FF6B35" : "#ccc",
    }}
    transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
  >
    <motion.div
      className="toggle-knob"
      animate={{
        x: checked ? 26 : 0,
      }}
      transition={{
        duration: 0.3,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
    />
  </motion.div>
)

// Parallax scroll component
export const ParallaxElement = ({
  children,
  offset = 0.5,
  className = "",
}: {
  children: React.ReactNode
  offset?: number
  className?: string
}) => {
  const { scrollY } = useScroll()
  const y = useTransform(scrollY, [0, 1000], [0, -1000 * offset])

  return (
    <motion.div className={`parallax ${className}`} style={{ y }}>
      {children}
    </motion.div>
  )
}

// Liquid morphing container
export const LiquidMorph = ({
  children,
  isActive,
  className = "",
}: {
  children: React.ReactNode
  isActive: boolean
  className?: string
}) => (
  <motion.div
    className={`liquid-morph ${className}`}
    animate={{
      scale: isActive ? 1.05 : 1,
      borderRadius: isActive ? "24px" : "12px",
    }}
    transition={{
      type: "spring",
      stiffness: 300,
      damping: 30,
      mass: 0.8,
    }}
  >
    {children}
  </motion.div>
)

// Gesture-enabled swipe container
export const SwipeContainer = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  className = "",
}: {
  children: React.ReactNode
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  className?: string
}) => (
  <motion.div
    className={className}
    drag="x"
    dragConstraints={{ left: 0, right: 0 }}
    dragElastic={0.2}
    onDragEnd={(_, info) => {
      if (info.offset.x > 100 && onSwipeRight) {
        onSwipeRight()
      } else if (info.offset.x < -100 && onSwipeLeft) {
        onSwipeLeft()
      }
    }}
  >
    {children}
  </motion.div>
)
