"use client"

import { useState, useEffect, useCallback } from "react"

interface PricingData {
  currentPrice: number
  optimalPrice: number
  confidence: number
  demand: string
  timestamp: string
}

export const useRealTimeData = (initialData: PricingData[], isLive: boolean) => {
  const [data, setData] = useState(initialData)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  const simulateDataUpdate = useCallback(() => {
    setData((prevData) =>
      prevData.map((item) => ({
        ...item,
        currentPrice: Math.max(5, item.currentPrice + (Math.random() - 0.5) * 2),
        confidence: Math.max(0.5, Math.min(0.99, item.confidence + (Math.random() - 0.5) * 0.1)),
        timestamp: new Date().toISOString(),
      })),
    )
    setLastUpdate(new Date())
  }, [])

  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(simulateDataUpdate, 3000)
    return () => clearInterval(interval)
  }, [isLive, simulateDataUpdate])

  const toggleLive = useCallback(() => {
    // This would be handled by parent component
  }, [])

  return {
    data,
    lastUpdate,
    simulateDataUpdate,
    toggleLive,
  }
}

export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const [connectionStatus, setConnectionStatus] = useState<"Connecting" | "Open" | "Closing" | "Closed">("Closed")

  useEffect(() => {
    if (!url) return

    const ws = new WebSocket(url)
    setSocket(ws)
    setConnectionStatus("Connecting")

    ws.onopen = () => setConnectionStatus("Open")
    ws.onclose = () => setConnectionStatus("Closed")
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastMessage(data)
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error)
      }
    }

    return () => {
      ws.close()
    }
  }, [url])

  const sendMessage = useCallback(
    (message: any) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(message))
      }
    },
    [socket],
  )

  return {
    socket,
    lastMessage,
    connectionStatus,
    sendMessage,
  }
}
