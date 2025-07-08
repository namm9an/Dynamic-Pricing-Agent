"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useSpring } from "framer-motion"

// Smooth momentum scrolling hook
export const useSmoothScroll = () => {
  const [isScrolling, setIsScrolling] = useState(false)

  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    const handleScroll = () => {
      setIsScrolling(true)
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => setIsScrolling(false), 150)
    }

    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => {
      window.removeEventListener("scroll", handleScroll)
      clearTimeout(timeoutId)
    }
  }, [])

  return isScrolling
}

// Apple-style spring physics
export const useAppleSpring = (value: number, config = {}) => {
  const defaultConfig = {
    stiffness: 300,
    damping: 30,
    mass: 0.8,
    ...config,
  }

  return useSpring(value, defaultConfig)
}

// Magnetic hover effect hook
export const useMagneticHover = (strength = 0.3) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const elementRef = useRef<HTMLElement>(null)

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!elementRef.current) return

      const rect = elementRef.current.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2

      const deltaX = (e.clientX - centerX) * strength
      const deltaY = (e.clientY - centerY) * strength

      setMousePosition({ x: deltaX, y: deltaY })
    },
    [strength],
  )

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true)
    document.addEventListener("mousemove", handleMouseMove)
  }, [handleMouseMove])

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false)
    setMousePosition({ x: 0, y: 0 })
    document.removeEventListener("mousemove", handleMouseMove)
  }, [handleMouseMove])

  return {
    elementRef,
    mousePosition,
    isHovered,
    handleMouseEnter,
    handleMouseLeave,
  }
}

// Gesture recognition hook
export const useGestures = () => {
  const [gesture, setGesture] = useState<string | null>(null)
  const startPos = useRef({ x: 0, y: 0 })
  const threshold = 50

  const handleTouchStart = useCallback((e: TouchEvent) => {
    const touch = e.touches[0]
    startPos.current = { x: touch.clientX, y: touch.clientY }
  }, [])

  const handleTouchEnd = useCallback((e: TouchEvent) => {
    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - startPos.current.x
    const deltaY = touch.clientY - startPos.current.y

    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      if (Math.abs(deltaX) > threshold) {
        setGesture(deltaX > 0 ? "swipe-right" : "swipe-left")
      }
    } else {
      if (Math.abs(deltaY) > threshold) {
        setGesture(deltaY > 0 ? "swipe-down" : "swipe-up")
      }
    }

    setTimeout(() => setGesture(null), 100)
  }, [])

  useEffect(() => {
    document.addEventListener("touchstart", handleTouchStart, { passive: true })
    document.addEventListener("touchend", handleTouchEnd, { passive: true })

    return () => {
      document.removeEventListener("touchstart", handleTouchStart)
      document.removeEventListener("touchend", handleTouchEnd)
    }
  }, [handleTouchStart, handleTouchEnd])

  return gesture
}

// Performance monitoring hook
export const usePerformanceMonitor = () => {
  const [fps, setFps] = useState(60)
  const frameCount = useRef(0)
  const lastTime = useRef(performance.now())

  useEffect(() => {
    const measureFPS = () => {
      frameCount.current++
      const currentTime = performance.now()

      if (currentTime - lastTime.current >= 1000) {
        setFps(Math.round((frameCount.current * 1000) / (currentTime - lastTime.current)))
        frameCount.current = 0
        lastTime.current = currentTime
      }

      requestAnimationFrame(measureFPS)
    }

    requestAnimationFrame(measureFPS)
  }, [])

  return fps
}

// Predictive animation hook
export const usePredictiveAnimation = (element: HTMLElement | null) => {
  const [isPredicting, setIsPredicting] = useState(false)

  useEffect(() => {
    if (!element) return

    let timeoutId: NodeJS.Timeout

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect()
      const distance = Math.sqrt(
        Math.pow(e.clientX - (rect.left + rect.width / 2), 2) + Math.pow(e.clientY - (rect.top + rect.height / 2), 2),
      )

      if (distance < 100 && !isPredicting) {
        setIsPredicting(true)
        // Pre-load hover state
        element.style.transform = "scale(1.01)"

        timeoutId = setTimeout(() => {
          if (!element.matches(":hover")) {
            element.style.transform = "scale(1)"
            setIsPredicting(false)
          }
        }, 200)
      }
    }

    document.addEventListener("mousemove", handleMouseMove, { passive: true })

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      clearTimeout(timeoutId)
    }
  }, [element, isPredicting])

  return isPredicting
}
