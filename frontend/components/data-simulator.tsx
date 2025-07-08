"use client"

import { useState } from "react"
import { AppleButton } from "./apple-animations"
import { motion } from "framer-motion"
import { Play, RotateCcw } from "lucide-react"

export const DataSimulator = () => {
  const [isSimulating, setIsSimulating] = useState(false)
  const [lastSimulation, setLastSimulation] = useState<Date | null>(null)

  const simulateData = async () => {
    try {
      setIsSimulating(true)
      const response = await fetch("/api/simulate-data", {
        method: "POST",
      })

      if (response.ok) {
        setLastSimulation(new Date())
        console.log("Data simulation successful")
      } else {
        console.error("Simulation failed")
      }
    } catch (error) {
      console.error("Simulation error:", error)
    } finally {
      setIsSimulating(false)
    }
  }

  return (
    <motion.div
      className="enhanced-glass rounded-lg p-4 mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-[#EAE0D5] mb-1">Data Simulator</h3>
          <p className="text-sm text-gray-400">Generate sample pricing decisions and demand predictions</p>
          {lastSimulation && (
            <p className="text-xs text-[#00D4AA] mt-1">Last simulated: {lastSimulation.toLocaleTimeString()}</p>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <AppleButton onClick={simulateData} disabled={isSimulating} className="px-4 py-2 flex items-center space-x-2">
            {isSimulating ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Simulate Data</span>
              </>
            )}
          </AppleButton>
        </div>
      </div>
    </motion.div>
  )
}
