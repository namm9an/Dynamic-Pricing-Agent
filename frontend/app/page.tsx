"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  TrendingUp,
  Activity,
  BarChart3,
  User,
  Bell,
  ChevronDown,
  RefreshCw,
  Target,
  Zap,
  Shield,
  Clock,
} from "lucide-react"
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import {
  StaggerContainer,
  StaggerItem,
  AppleButton,
  AnimatedCounter,
  AppleToggle,
  ParallaxElement,
} from "../components/apple-animations"
import { PerformanceIndicator } from "../components/performance-monitor"
import { useRealtimeData, useSystemStatus } from "../hooks/use-realtime-data"
import {
  RealtimePriceCard,
  DecisionLogTable,
  DemandChart,
  SystemStatus,
  PriceCardSkeleton,
  ChartSkeleton,
  DashboardErrorBoundary,
} from "../components/realtime-components"
import { RevenueLiftCalculator } from "../components/revenue-calculator"
import { DataSimulator } from "../components/data-simulator"
import { ConnectionStatus } from "../components/connection-status"

// Sample data
const pricingData = [
  { time: "00:00", price: 29.99, demand: 65, revenue: 1950 },
  { time: "04:00", price: 31.5, demand: 72, revenue: 2268 },
  { time: "08:00", price: 33.25, demand: 85, revenue: 2826 },
  { time: "12:00", price: 35.0, demand: 92, revenue: 3220 },
  { time: "16:00", price: 32.75, demand: 78, revenue: 2555 },
  { time: "20:00", price: 30.25, demand: 68, revenue: 2057 },
]

const rewardHistory = [
  { timestamp: "09:00", reward: 1250.75 },
  { timestamp: "10:00", reward: 1340.2 },
  { timestamp: "11:00", reward: 1425.8 },
  { timestamp: "12:00", reward: 1580.45 },
  { timestamp: "13:00", reward: 1520.3 },
  { timestamp: "14:00", reward: 1650.9 },
]

const products = [
  { id: 1, name: "Premium Plan", currentPrice: 29.99, optimalPrice: 32.5, confidence: 0.87, demand: "high" },
  { id: 2, name: "Enterprise Plan", currentPrice: 99.99, optimalPrice: 105.0, confidence: 0.92, demand: "medium" },
  { id: 3, name: "Starter Plan", currentPrice: 9.99, optimalPrice: 11.5, confidence: 0.78, demand: "high" },
]

const WavyUnderline = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <span className={`relative inline-block ${className}`}>
    {children}
    <motion.div
      className="absolute -bottom-1 left-0 h-0.5 bg-gradient-to-r from-[#FF6B35] to-[#EAE0D5]"
      initial={{ width: 0 }}
      animate={{ width: "100%" }}
      transition={{ duration: 1.5, ease: "easeInOut" }}
    />
  </span>
)

export default function DynamicPricingDashboard() {
  const [activeTab, setActiveTab] = useState("1H")
  const { pricingData, decisions, demandPredictions, isLoading, error, refresh } = useRealtimeData()
  const systemStatus = useSystemStatus()

  // Use real-time data or fallback to static data
  const currentProducts = pricingData?.products || products

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="bg-black border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-8">
            <motion.div
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              <div className="w-8 h-8 bg-[#FF6B35] rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-[#EAE0D5]">PriceAI</span>
            </motion.div>
            <nav className="hidden md:flex space-x-6">
              <a href="#" className="text-[#EAE0D5] hover:text-[#FF6B35] apple-ease">
                Pricing
              </a>
              <a href="#" className="text-gray-400 hover:text-[#FF6B35] apple-ease">
                Analytics
              </a>
              <a href="#" className="text-gray-400 hover:text-[#FF6B35] apple-ease">
                Documentation
              </a>
              <a href="#" className="text-gray-400 hover:text-[#FF6B35] apple-ease">
                API
              </a>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <Bell className="w-5 h-5 text-gray-400 hover:text-[#FF6B35] cursor-pointer apple-ease" />
            <div className="flex items-center space-x-2 cursor-pointer">
              <User className="w-5 h-5 text-gray-400" />
              <ChevronDown className="w-4 h-4 text-gray-400" />
            </div>
            <AppleButton className="px-4 py-2">Start Free Trial</AppleButton>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <ParallaxElement offset={0.3}>
        <section className="relative px-6 py-16 bg-gradient-to-b from-black to-[#1A1A1A]">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="text-5xl md:text-6xl font-bold mb-6"
            >
              Stop the{" "}
              <span className="text-[#FF6B35]">
                <WavyUnderline>PRICING IDLE</WavyUnderline>
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="text-xl text-[#EAE0D5] mb-8 leading-relaxed"
            >
              Transform your revenue with AI-driven dynamic pricing that learns, adapts, and optimizes in real-time.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
            >
              <AppleButton className="px-8 py-4 text-lg">Start Optimizing Now</AppleButton>
            </motion.div>
          </div>
        </section>
      </ParallaxElement>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Data Simulator */}
        <DataSimulator />

        {/* Connection Status */}
        <ConnectionStatus />

        {/* Live Status Bar */}
        <motion.div
          className="flex items-center justify-between enhanced-glass rounded-lg p-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <SystemStatus status={systemStatus} />
          <div className="flex items-center space-x-2">
            <AppleToggle checked={!isLoading} onChange={() => refresh()} />
            <AppleButton variant="secondary" className="p-2" onClick={refresh}>
              <RefreshCw className="w-4 h-4" />
            </AppleButton>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <DashboardErrorBoundary error={error}>
          <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {isLoading
              ? Array.from({ length: 3 }).map((_, index) => (
                  <StaggerItem key={index}>
                    <PriceCardSkeleton />
                  </StaggerItem>
                ))
              : currentProducts.map((product, index) => (
                  <StaggerItem key={product.id}>
                    <RealtimePriceCard
                      currentPrice={product.currentPrice}
                      predictedDemand={product.demand as "low" | "medium" | "high"}
                      confidenceScore={product.confidence}
                      productName={product.name}
                      priceChange={product.priceChange}
                    />
                  </StaggerItem>
                ))}
          </StaggerContainer>
        </DashboardErrorBoundary>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Price & Demand Chart */}
          <motion.div
            className="enhanced-glass rounded-xl p-6"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-[#EAE0D5]">
                <WavyUnderline>Price & Demand Trends</WavyUnderline>
              </h3>
              <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
                {["1H", "24H", "7D", "30D"].map((period) => (
                  <AppleButton
                    key={period}
                    onClick={() => setActiveTab(period)}
                    variant={activeTab === period ? "primary" : "secondary"}
                    className="px-3 py-1 text-sm"
                  >
                    {period}
                  </AppleButton>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={pricingData}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF6B35" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#FF6B35" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.8)",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255,107,53,0.3)",
                    borderRadius: "8px",
                    color: "#EAE0D5",
                  }}
                />
                <Area type="monotone" dataKey="price" stroke="#FF6B35" fillOpacity={1} fill="url(#priceGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          {/* RL Reward History */}
          <motion.div
            className="enhanced-glass rounded-xl p-6"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            <h3 className="text-xl font-bold text-[#EAE0D5] mb-6">
              <WavyUnderline>RL Reward History</WavyUnderline>
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={rewardHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.8)",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255,107,53,0.3)",
                    borderRadius: "8px",
                    color: "#EAE0D5",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="reward"
                  stroke="#00D4AA"
                  strokeWidth={3}
                  dot={{ fill: "#00D4AA", strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 text-sm text-gray-400">
              <WavyUnderline className="text-[#FF6B35]">Reward = Revenue - Penalty</WavyUnderline>
            </div>
          </motion.div>
        </div>

        {/* Decision Log Table */}
        <DashboardErrorBoundary error={error}>
          {isLoading ? <ChartSkeleton /> : <DecisionLogTable decisions={decisions} />}
        </DashboardErrorBoundary>

        {/* Demand Prediction Chart */}
        <DashboardErrorBoundary error={error}>
          {isLoading ? <ChartSkeleton /> : <DemandChart data={demandPredictions} />}
        </DashboardErrorBoundary>

        {/* Revenue Simulator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <RevenueLiftCalculator />
        </motion.div>

        {/* Agent Insights & API Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Agent Insights */}
          <motion.div
            className="enhanced-glass rounded-xl p-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h3 className="text-xl font-bold text-[#EAE0D5] mb-6">
              <WavyUnderline>Agent Insights</WavyUnderline>
            </h3>
            <div className="space-y-4">
              <motion.div
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover-lift"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-3">
                  <Target className="w-5 h-5 text-[#FF6B35]" />
                  <span className="text-[#EAE0D5]">Price increased by $2.50</span>
                </div>
                <div className="text-sm text-gray-400">2 min ago</div>
              </motion.div>
              <motion.div
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover-lift"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-3">
                  <Zap className="w-5 h-5 text-[#00D4AA]" />
                  <span className="text-[#EAE0D5]">High demand detected</span>
                </div>
                <div className="text-sm text-gray-400">5 min ago</div>
              </motion.div>
              <motion.div
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover-lift"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-[#FF6B35]" />
                  <span className="text-[#EAE0D5]">Revenue optimization complete</span>
                </div>
                <div className="text-sm text-gray-400">12 min ago</div>
              </motion.div>
            </div>
          </motion.div>

          {/* API Status */}
          <motion.div
            className="enhanced-glass rounded-xl p-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <h3 className="text-xl font-bold text-[#EAE0D5] mb-6">
              <WavyUnderline>API Status</WavyUnderline>
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-[#00D4AA]" />
                  <span className="text-[#EAE0D5]">System Health</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-[#00D4AA] rounded-full pulse-orange" />
                  <span className="text-[#00D4AA] font-medium">Healthy</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Clock className="w-5 h-5 text-[#FF6B35]" />
                  <span className="text-[#EAE0D5]">Response Time</span>
                </div>
                <span className="text-[#EAE0D5] font-medium">
                  <AnimatedCounter value={45} />
                  ms
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Activity className="w-5 h-5 text-[#FF6B35]" />
                  <span className="text-[#EAE0D5]">Uptime</span>
                </div>
                <span className="text-[#00D4AA] font-medium">
                  <AnimatedCounter value={99.9} />%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="w-5 h-5 text-[#FF6B35]" />
                  <span className="text-[#EAE0D5]">Requests/sec</span>
                </div>
                <span className="text-[#EAE0D5] font-medium">
                  <AnimatedCounter value={1247} />
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Performance Monitor */}
      <PerformanceIndicator />
    </div>
  )
}
