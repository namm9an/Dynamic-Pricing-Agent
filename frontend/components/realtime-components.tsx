"use client"

import type React from "react"

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronUp, ChevronDown, AlertCircle, CheckCircle, Clock } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { AnimatedCounter } from "./apple-animations"

// Animated Number Ticker Component
export const AnimatedNumber = ({
  value,
  prefix = "",
  suffix = "",
  className = "",
  duration = 800,
}: {
  value: number
  prefix?: string
  suffix?: string
  className?: string
  duration?: number
}) => (
  <span className={className}>
    {prefix}
    <AnimatedCounter value={value} duration={duration / 1000} />
    {suffix}
  </span>
)

// Confidence Bar Component
export const ConfidenceBar = ({ score, className = "" }: { score: number; className?: string }) => (
  <div className={`flex items-center space-x-2 ${className}`}>
    <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-gradient-to-r from-[#FF6B35] to-[#00D4AA]"
        initial={{ width: 0 }}
        animate={{ width: `${score * 100}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />
    </div>
    <span className="text-xs text-gray-400">{(score * 100).toFixed(0)}%</span>
  </div>
)

// Demand Indicator Component
export const DemandIndicator = ({ level }: { level: "low" | "medium" | "high" }) => {
  const colors = {
    low: "bg-gray-500",
    medium: "bg-[#FF6B35]",
    high: "bg-[#00D4AA]",
  }

  const textColors = {
    low: "text-gray-400",
    medium: "text-[#FF6B35]",
    high: "text-[#00D4AA]",
  }

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${colors[level]} animate-pulse`} />
      <span className={`text-sm font-medium ${textColors[level]}`}>{level} demand</span>
    </div>
  )
}

// Real-time Price Card Component
export const RealtimePriceCard = ({
  currentPrice,
  predictedDemand,
  confidenceScore,
  productName,
  priceChange,
}: {
  currentPrice: number
  predictedDemand: "low" | "medium" | "high"
  confidenceScore: number
  productName: string
  priceChange?: number
}) => (
  <motion.div className="enhanced-glass p-6 rounded-xl" whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-semibold text-[#EAE0D5]">{productName}</h3>
      {priceChange && (
        <div className={`flex items-center space-x-1 ${priceChange > 0 ? "text-[#00D4AA]" : "text-red-400"}`}>
          {priceChange > 0 ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="text-sm font-medium">{Math.abs(priceChange).toFixed(2)}%</span>
        </div>
      )}
    </div>

    <div className="flex items-center justify-between mb-4">
      <AnimatedNumber value={currentPrice} prefix="$" className="text-3xl font-bold text-[#FF6B35]" duration={800} />
      <ConfidenceBar score={confidenceScore} />
    </div>

    <DemandIndicator level={predictedDemand} />
  </motion.div>
)

// Decision Row Component
const DecisionRow = ({
  timestamp,
  product_id,
  old_price,
  new_price,
  reason,
  confidence_score,
}: {
  timestamp: string
  product_id: string
  old_price: number
  new_price: number
  reason: string
  confidence_score: number
}) => {
  const priceChange = ((new_price - old_price) / old_price) * 100

  return (
    <motion.tr
      className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <td className="px-4 py-3 text-sm text-gray-300">{new Date(timestamp).toLocaleTimeString()}</td>
      <td className="px-4 py-3 text-sm text-[#EAE0D5] font-medium">{product_id}</td>
      <td className="px-4 py-3 text-sm text-gray-400">${old_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-sm text-[#FF6B35] font-medium">${new_price.toFixed(2)}</td>
      <td className="px-4 py-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">{reason}</span>
          <div className={`flex items-center space-x-1 ${priceChange > 0 ? "text-[#00D4AA]" : "text-red-400"}`}>
            {priceChange > 0 ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            <span className="text-xs">{Math.abs(priceChange).toFixed(1)}%</span>
          </div>
        </div>
      </td>
    </motion.tr>
  )
}

// Decision Log Table Component
export const DecisionLogTable = ({ decisions }: { decisions: any[] }) => {
  const [sortBy, setSortBy] = useState<"timestamp" | "product_id" | "confidence_score">("timestamp")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")

  const sortedDecisions = useMemo(() => {
    return [...decisions].sort((a, b) => {
      const aVal = a[sortBy]
      const bVal = b[sortBy]
      const multiplier = sortOrder === "asc" ? 1 : -1

      if (sortBy === "timestamp") {
        return (new Date(aVal).getTime() - new Date(bVal).getTime()) * multiplier
      }
      return (aVal > bVal ? 1 : -1) * multiplier
    })
  }, [decisions, sortBy, sortOrder])

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortBy(column)
      setSortOrder("desc")
    }
  }

  if (decisions.length === 0) {
    return (
      <div className="enhanced-glass rounded-xl p-8 text-center">
        <h3 className="text-xl font-bold text-[#EAE0D5] mb-4">Recent Pricing Decisions</h3>
        <p className="text-gray-400">No pricing decisions found. Use the data simulator to generate sample data.</p>
      </div>
    )
  }

  return (
    <div className="enhanced-glass rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-800">
        <h3 className="text-xl font-bold text-[#EAE0D5]">Recent Pricing Decisions</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800/50">
            <tr>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-300 cursor-pointer hover:text-[#FF6B35] transition-colors"
                onClick={() => handleSort("timestamp")}
              >
                <div className="flex items-center space-x-1">
                  <span>Time</span>
                  {sortBy === "timestamp" && (
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                      {sortOrder === "asc" ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </motion.div>
                  )}
                </div>
              </th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-300 cursor-pointer hover:text-[#FF6B35] transition-colors"
                onClick={() => handleSort("product_id")}
              >
                Product
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Old Price</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">New Price</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Reason</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {sortedDecisions.slice(0, 10).map((decision) => (
                <DecisionRow key={decision.id} {...decision} />
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Fixed Demand Prediction Chart Component
export const DemandChart = ({ data }: { data: any[] }) => {
  // Transform the data for the chart
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      // Return sample data if no real data is available
      return [
        { date: "2024-01-01", predicted_demand: 150, actual_demand: 142, product: "premium-plan" },
        { date: "2024-01-02", predicted_demand: 165, actual_demand: 158, product: "premium-plan" },
        { date: "2024-01-03", predicted_demand: 140, actual_demand: 135, product: "premium-plan" },
        { date: "2024-01-04", predicted_demand: 175, actual_demand: 168, product: "premium-plan" },
        { date: "2024-01-05", predicted_demand: 160, actual_demand: 155, product: "premium-plan" },
      ]
    }

    // Group data by date and aggregate
    const groupedData = data.reduce((acc, item) => {
      const date = item.prediction_date
      if (!acc[date]) {
        acc[date] = {
          date,
          predicted_demand: 0,
          actual_demand: 0,
          count: 0,
        }
      }
      acc[date].predicted_demand += item.predicted_demand || 0
      acc[date].actual_demand += item.actual_demand || 0
      acc[date].count += 1
      return acc
    }, {})

    // Convert to array and calculate averages
    return Object.values(groupedData)
      .map((item: any) => ({
        date: item.date,
        predicted_demand: Math.round(item.predicted_demand / item.count),
        actual_demand: Math.round(item.actual_demand / item.count),
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-7) // Show last 7 days
  }, [data])

  // Calculate accuracy metrics
  const accuracy = useMemo(() => {
    if (chartData.length === 0) return { mape: 0, accuracy: 0 }

    const mapeSum = chartData.reduce((sum, item) => {
      if (item.actual_demand === 0) return sum
      return sum + Math.abs((item.predicted_demand - item.actual_demand) / item.actual_demand)
    }, 0)

    const mape = (mapeSum / chartData.length) * 100
    const accuracy = Math.max(0, 100 - mape)

    return { mape: mape.toFixed(1), accuracy: accuracy.toFixed(1) }
  }, [chartData])

  return (
    <div className="enhanced-glass p-6 rounded-xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-[#EAE0D5]">Demand Prediction Accuracy</h3>
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[#00D4AA]">{accuracy.accuracy}%</div>
            <div className="text-xs text-gray-400">Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#FF6B35]">{accuracy.mape}%</div>
            <div className="text-xs text-gray-400">MAPE</div>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9CA3AF"
            tickFormatter={(value) => new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
          />
          <YAxis stroke="#9CA3AF" />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(0,0,0,0.8)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(255,107,53,0.3)",
              borderRadius: "8px",
              color: "#EAE0D5",
            }}
            labelFormatter={(value) => `Date: ${new Date(value).toLocaleDateString()}`}
          />
          <Line
            type="monotone"
            dataKey="predicted_demand"
            stroke="#FF6B35"
            strokeWidth={3}
            name="Predicted"
            dot={{ fill: "#FF6B35", strokeWidth: 2, r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="actual_demand"
            stroke="#EAE0D5"
            strokeWidth={3}
            strokeDasharray="5 5"
            name="Actual"
            dot={{ fill: "#EAE0D5", strokeWidth: 2, r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 flex items-center justify-between text-sm text-gray-400">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-[#FF6B35]" />
            <span>Predicted Demand</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-[#EAE0D5] border-dashed border-t" />
            <span>Actual Demand</span>
          </div>
        </div>
        <div>{data.length > 0 ? `${data.length} predictions` : "Sample data"}</div>
      </div>
    </div>
  )
}

// System Status Component
export const SystemStatus = ({ status }: { status: any }) => {
  const getStatusColor = (apiStatus: string) => {
    switch (apiStatus) {
      case "healthy":
        return "text-[#00D4AA]"
      case "degraded":
        return "text-[#FF6B35]"
      case "down":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const getStatusIcon = (apiStatus: string) => {
    switch (apiStatus) {
      case "healthy":
        return <CheckCircle className="w-4 h-4" />
      case "degraded":
        return <AlertCircle className="w-4 h-4" />
      case "down":
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className="flex items-center space-x-4">
      <div className={`flex items-center space-x-2 ${getStatusColor(status.api)}`}>
        {getStatusIcon(status.api)}
        <span className="text-sm font-medium capitalize">{status.api}</span>
      </div>
      <div className="text-sm text-gray-300">
        Model {status.model} • {status.latency} • {status.uptime}% uptime
      </div>
    </div>
  )
}

// Loading Skeleton Components
export const PriceCardSkeleton = () => (
  <div className="enhanced-glass p-6 rounded-xl animate-pulse">
    <div className="flex justify-between items-start mb-4">
      <div className="h-5 bg-gray-700 rounded w-24" />
      <div className="h-4 bg-gray-700 rounded-full w-16" />
    </div>
    <div className="h-8 bg-gray-700 rounded mb-4 w-20" />
    <div className="h-4 bg-gray-700 rounded w-32" />
  </div>
)

export const ChartSkeleton = () => (
  <div className="enhanced-glass p-6 rounded-xl animate-pulse">
    <div className="h-6 bg-gray-700 rounded mb-4 w-48" />
    <div className="h-64 bg-gray-700 rounded" />
  </div>
)

// Error Boundary Component
export const DashboardErrorBoundary = ({ children, error }: { children: React.ReactNode; error?: string }) => {
  if (error) {
    return (
      <motion.div
        className="bg-red-900/20 border border-red-500/50 p-6 rounded-xl"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center space-x-3 mb-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <h3 className="text-red-400 font-semibold">Dashboard Error</h3>
        </div>
        <p className="text-red-300 text-sm">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg text-sm transition-colors"
        >
          Retry
        </button>
      </motion.div>
    )
  }

  return <>{children}</>
}
