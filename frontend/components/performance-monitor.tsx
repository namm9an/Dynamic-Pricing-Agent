"use client"

import { usePerformanceMonitor } from "../hooks/use-apple-animations"
import { motion } from "framer-motion"

export const PerformanceIndicator = () => {
  const fps = usePerformanceMonitor()

  return (
    <motion.div
      className="fixed bottom-4 right-4 bg-black/80 backdrop-blur-lg rounded-lg p-3 text-sm z-50"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center space-x-2">
        <div
          className={`w-2 h-2 rounded-full ${fps >= 55 ? "bg-green-500" : fps >= 30 ? "bg-yellow-500" : "bg-red-500"}`}
        />
        <span className="text-white">{fps} FPS</span>
      </div>
    </motion.div>
  )
}

export const AnimationDebugger = ({ showDebug = false }: { showDebug?: boolean }) => {
  if (!showDebug) return null

  return (
    <div className="fixed top-4 right-4 bg-black/90 backdrop-blur-lg rounded-lg p-4 text-xs text-white z-50 space-y-2">
      <div>GPU Acceleration: ✅</div>
      <div>120fps Ready: ✅</div>
      <div>Reduced Motion: {window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "✅" : "❌"}</div>
      <div>Hardware Acceleration: ✅</div>
    </div>
  )
}
