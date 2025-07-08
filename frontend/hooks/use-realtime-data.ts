"use client"

import { useState, useEffect, useCallback } from "react"
import { supabase, fetchPricingDecisions, fetchDemandPredictions } from "../lib/supabase"
import type { PricingDecision, DemandPrediction } from "../lib/supabase"

interface PricingData {
  products: Array<{
    id: string
    name: string
    currentPrice: number
    optimalPrice: number
    confidence: number
    demand: "low" | "medium" | "high"
    priceChange?: number
  }>
  lastUpdated: string
}

export const useRealtimeData = () => {
  const [pricingData, setPricingData] = useState<PricingData | null>(null)
  const [decisions, setDecisions] = useState<PricingDecision[]>([])
  const [demandPredictions, setDemandPredictions] = useState<DemandPrediction[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCurrentPrices = useCallback(async () => {
    try {
      // Simulate API call - replace with actual endpoint
      const response = await fetch("/api/pricing/current")
      if (!response.ok) throw new Error("Failed to fetch pricing data")
      const data = await response.json()
      setPricingData(data)
    } catch (err) {
      console.error("Error fetching current prices:", err)
      setError(err instanceof Error ? err.message : "Unknown error")
    }
  }, [])

  const loadDecisions = useCallback(async () => {
    try {
      const data = await fetchPricingDecisions(100)
      console.log("Loaded pricing decisions:", data.length)
      setDecisions(data)
    } catch (err) {
      console.error("Failed to fetch decisions:", err)
      setError(err instanceof Error ? err.message : "Failed to fetch decisions")
    }
  }, [])

  const loadDemandPredictions = useCallback(async () => {
    try {
      const data = await fetchDemandPredictions(50)
      console.log("Loaded demand predictions:", data.length)
      setDemandPredictions(data)
    } catch (err) {
      console.error("Failed to fetch demand predictions:", err)
      setError(err instanceof Error ? err.message : "Failed to fetch demand predictions")
    }
  }, [])

  // Auto-refresh system with 30-second intervals
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)

      try {
        await Promise.all([fetchCurrentPrices(), loadDecisions(), loadDemandPredictions()])
      } catch (err) {
        console.error("Error fetching data:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

    const interval = setInterval(() => {
      fetchCurrentPrices()
      loadDemandPredictions()
    }, 30000) // 30s refresh

    return () => clearInterval(interval)
  }, [fetchCurrentPrices, loadDecisions, loadDemandPredictions])

  // Real-time subscription to pricing_decisions table
  useEffect(() => {
    const channel = supabase
      .channel("pricing_changes")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "pricing_decisions",
        },
        (payload) => {
          console.log("New pricing decision:", payload.new)
          setDecisions((prev) => [payload.new as PricingDecision, ...prev.slice(0, 99)])
        },
      )
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "demand_predictions",
        },
        (payload) => {
          console.log("New demand prediction:", payload.new)
          setDemandPredictions((prev) => [payload.new as DemandPrediction, ...prev.slice(0, 49)])
        },
      )
      .subscribe((status) => {
        console.log("Subscription status:", status)
      })

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      await Promise.all([fetchCurrentPrices(), loadDecisions(), loadDemandPredictions()])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh data")
    } finally {
      setIsLoading(false)
    }
  }, [fetchCurrentPrices, loadDecisions, loadDemandPredictions])

  return {
    pricingData,
    decisions,
    demandPredictions,
    isLoading,
    error,
    refresh,
  }
}

export const useSystemStatus = () => {
  const [status, setStatus] = useState({
    api: "healthy" as "healthy" | "degraded" | "down",
    model: "v2.1.0",
    latency: "120ms",
    uptime: 99.9,
  })

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const start = performance.now()
        const response = await fetch("/api/health")
        const end = performance.now()

        if (response.ok) {
          const data = await response.json()
          setStatus({
            api: "healthy",
            model: data.model_version || "v2.1.0",
            latency: `${Math.round(end - start)}ms`,
            uptime: data.uptime || 99.9,
          })
        } else {
          setStatus((prev) => ({ ...prev, api: "degraded" }))
        }
      } catch (error) {
        setStatus((prev) => ({ ...prev, api: "down" }))
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 60000) // Check every minute

    return () => clearInterval(interval)
  }, [])

  return status
}
