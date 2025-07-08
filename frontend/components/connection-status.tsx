"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { CheckCircle, AlertCircle, Loader2, Database } from "lucide-react"
import { AppleButton } from "./apple-animations"

interface ConnectionStatus {
  status: "testing" | "connected" | "error" | "idle"
  message: string
  details?: any
}

export const ConnectionStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    status: "idle",
    message: "Not tested",
  })

  const testConnection = async () => {
    setConnectionStatus({ status: "testing", message: "Testing connection..." })

    try {
      const response = await fetch("/api/test-connection")
      const data = await response.json()

      if (response.ok) {
        setConnectionStatus({
          status: "connected",
          message: "Successfully connected to Supabase",
          details: data,
        })
      } else {
        setConnectionStatus({
          status: "error",
          message: data.message || "Connection failed",
          details: data,
        })
      }
    } catch (error) {
      setConnectionStatus({
        status: "error",
        message: "Failed to test connection",
        details: { error: error instanceof Error ? error.message : "Unknown error" },
      })
    }
  }

  useEffect(() => {
    // Auto-test connection on component mount
    testConnection()
  }, [])

  const getStatusIcon = () => {
    switch (connectionStatus.status) {
      case "testing":
        return <Loader2 className="w-5 h-5 animate-spin text-[#FF6B35]" />
      case "connected":
        return <CheckCircle className="w-5 h-5 text-[#00D4AA]" />
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-400" />
      default:
        return <Database className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (connectionStatus.status) {
      case "testing":
        return "border-[#FF6B35]/50 bg-[#FF6B35]/10"
      case "connected":
        return "border-[#00D4AA]/50 bg-[#00D4AA]/10"
      case "error":
        return "border-red-400/50 bg-red-400/10"
      default:
        return "border-gray-400/50 bg-gray-400/10"
    }
  }

  return (
    <motion.div
      className={`enhanced-glass rounded-lg p-4 border ${getStatusColor()}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-[#EAE0D5]">Supabase Connection</h3>
            <p className="text-sm text-gray-400">{connectionStatus.message}</p>
            {connectionStatus.details && connectionStatus.status === "connected" && (
              <p className="text-xs text-[#00D4AA] mt-1">Database tables accessible • Real-time ready</p>
            )}
            {connectionStatus.details && connectionStatus.status === "error" && (
              <p className="text-xs text-red-400 mt-1">
                {connectionStatus.details.error || "Check your environment variables"}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <AppleButton
            onClick={testConnection}
            disabled={connectionStatus.status === "testing"}
            variant="secondary"
            className="px-4 py-2 text-sm"
          >
            {connectionStatus.status === "testing" ? "Testing..." : "Test Connection"}
          </AppleButton>
        </div>
      </div>

      {connectionStatus.details && connectionStatus.status === "connected" && (
        <motion.div
          className="mt-4 p-3 bg-gray-800/50 rounded-lg"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          transition={{ duration: 0.3 }}
        >
          <h4 className="text-sm font-medium text-[#EAE0D5] mb-2">Connection Details</h4>
          <div className="text-xs text-gray-400 space-y-1">
            <div>✅ Pricing decisions table: Accessible</div>
            <div>✅ Demand predictions table: Accessible</div>
            <div>✅ Real-time subscriptions: Ready</div>
            <div>✅ Last tested: {new Date(connectionStatus.details.timestamp).toLocaleTimeString()}</div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
