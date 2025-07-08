"use client"

import { useState, useMemo } from "react"
import { motion } from "framer-motion"
import { AnimatedCounter } from "./apple-animations"

// Price Slider Component
const PriceSlider = ({
  value,
  onChange,
  min,
  max,
  label,
}: {
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  label: string
}) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center">
      <label className="text-sm font-medium text-gray-400">{label}</label>
      <span className="text-sm text-[#FF6B35] font-medium">
        $<AnimatedCounter value={value} />
      </span>
    </div>
    <div className="relative">
      <input
        type="range"
        min={min}
        max={max}
        step={0.01}
        value={value}
        onChange={(e) => onChange(Number.parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
      />
      <div
        className="absolute top-0 h-2 bg-gradient-to-r from-[#FF6B35] to-[#EAE0D5] rounded-lg pointer-events-none"
        style={{ width: `${((value - min) / (max - min)) * 100}%` }}
      />
    </div>
  </div>
)

// Elasticity Slider Component
const ElasticitySlider = ({
  value,
  onChange,
  min,
  max,
  label,
}: {
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  label: string
}) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center">
      <label className="text-sm font-medium text-gray-400">{label}</label>
      <span className="text-sm text-[#FF6B35] font-medium">
        <AnimatedCounter value={value} />
      </span>
    </div>
    <div className="relative">
      <input
        type="range"
        min={min}
        max={max}
        step={0.1}
        value={value}
        onChange={(e) => onChange(Number.parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
      />
      <div
        className="absolute top-0 h-2 bg-gradient-to-r from-[#00D4AA] to-[#FF6B35] rounded-lg pointer-events-none"
        style={{ width: `${((value - min) / (max - min)) * 100}%` }}
      />
    </div>
  </div>
)

// Revenue Comparison Component
const RevenueComparison = ({
  staticRevenue,
  dynamicRevenue,
  improvement,
}: {
  staticRevenue: number
  dynamicRevenue: number
  improvement: number
}) => (
  <div className="bg-[#EAE0D5] rounded-lg p-4 space-y-3">
    <h4 className="text-lg font-semibold text-black">Revenue Impact</h4>
    <div className="grid grid-cols-2 gap-4">
      <div className="text-center">
        <div className="text-2xl font-bold text-gray-700">
          $<AnimatedCounter value={staticRevenue} />
        </div>
        <div className="text-sm text-gray-600">Static Pricing</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-[#FF6B35]">
          $<AnimatedCounter value={dynamicRevenue} />
        </div>
        <div className="text-sm text-gray-600">Dynamic Pricing</div>
      </div>
    </div>
    <div className="text-center pt-3 border-t border-gray-400">
      <motion.div
        key={improvement}
        initial={{ scale: 1.1, color: "#FF6B35" }}
        animate={{ scale: 1, color: "#00D4AA" }}
        className="text-3xl font-bold"
      >
        +<AnimatedCounter value={improvement} />%
      </motion.div>
      <div className="text-sm text-gray-600">Revenue Improvement</div>
    </div>
  </div>
)

// Revenue Lift Calculator Component
export const RevenueLiftCalculator = () => {
  const [basePrice, setBasePrice] = useState(29.99)
  const [elasticity, setElasticity] = useState(0.5)
  const [marketMultiplier, setMarketMultiplier] = useState(1.0)

  const comparison = useMemo(() => {
    const staticRevenue = basePrice * 1000 // Assume 1000 units
    const demandAdjustment = 1 - elasticity * 0.1 // Simplified elasticity model
    const dynamicRevenue = basePrice * 1000 * demandAdjustment * marketMultiplier
    const improvement = ((dynamicRevenue - staticRevenue) / staticRevenue) * 100

    return {
      static: staticRevenue,
      dynamic: dynamicRevenue,
      improvement: improvement,
    }
  }, [basePrice, elasticity, marketMultiplier])

  return (
    <div className="enhanced-glass p-6 rounded-xl">
      <h3 className="text-xl font-semibold text-[#EAE0D5] mb-6">Revenue Impact Calculator</h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <PriceSlider value={basePrice} onChange={setBasePrice} min={10} max={100} label="Base Price" />

          <ElasticitySlider value={elasticity} onChange={setElasticity} min={0.1} max={2.0} label="Price Elasticity" />

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Market Conditions</label>
            <div className="flex space-x-2">
              {[
                { label: "Low", value: 0.7 },
                { label: "Normal", value: 1.0 },
                { label: "High", value: 1.3 },
              ].map((condition) => (
                <button
                  key={condition.label}
                  onClick={() => setMarketMultiplier(condition.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    marketMultiplier === condition.value
                      ? "bg-[#FF6B35] text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {condition.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <RevenueComparison
            staticRevenue={comparison.static}
            dynamicRevenue={comparison.dynamic}
            improvement={comparison.improvement}
          />
        </div>
      </div>
    </div>
  )
}
