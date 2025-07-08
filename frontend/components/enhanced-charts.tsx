"use client"

import { motion } from "framer-motion"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const chartVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut",
    },
  },
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="backdrop-blur-lg bg-black/80 border border-orange-500/30 rounded-lg p-3 shadow-xl">
        <p className="text-[#EAE0D5] font-medium">{`Time: ${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-[#FF6B35]">
            {`${entry.name}: ${entry.value}`}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export const EnhancedAreaChart = ({ data, dataKey, title }: { data: any[]; dataKey: string; title: string }) => (
  <motion.div
    className="backdrop-blur-lg bg-black/30 border border-orange-500/20 rounded-xl p-6"
    variants={chartVariants}
    initial="hidden"
    animate="visible"
  >
    <h3 className="section-header mb-6">{title}</h3>
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="enhancedGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#FF6B35" stopOpacity={0.9} />
            <stop offset="50%" stopColor="#FF6B35" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#EAE0D5" stopOpacity={0.1} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,107,53,0.1)" />
        <XAxis dataKey="time" stroke="#9CA3AF" />
        <YAxis stroke="#9CA3AF" />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke="#FF6B35"
          strokeWidth={3}
          fill="url(#enhancedGradient)"
          filter="url(#glow)"
        />
      </AreaChart>
    </ResponsiveContainer>
  </motion.div>
)

export const CircularProgress = ({
  value,
  size = 120,
  strokeWidth = 8,
}: { value: number; size?: number; strokeWidth?: number }) => {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="relative inline-flex items-center justify-center">
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
          stroke="url(#circularGradient)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
        <defs>
          <linearGradient id="circularGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF6B35" />
            <stop offset="100%" stopColor="#EAE0D5" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="metric-text">{value}%</span>
      </div>
    </div>
  )
}
