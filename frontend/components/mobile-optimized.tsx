"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, ChevronLeft, ChevronRight } from "lucide-react"

export const MobileNavigation = ({ isOpen, setIsOpen }: { isOpen: boolean; setIsOpen: (open: boolean) => void }) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        initial={{ x: "-100%" }}
        animate={{ x: 0 }}
        exit={{ x: "-100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed inset-y-0 left-0 z-50 w-64 backdrop-blur-xl bg-black/90 border-r border-orange-500/20"
      >
        <div className="flex items-center justify-between p-4 border-b border-orange-500/20">
          <span className="text-xl font-bold text-[#EAE0D5]">PriceAI</span>
          <button onClick={() => setIsOpen(false)} className="p-2 rounded-lg hover:bg-orange-500/10 transition-colors">
            <X className="w-5 h-5 text-[#EAE0D5]" />
          </button>
        </div>
        <nav className="p-4 space-y-2">
          {["Pricing", "Analytics", "Documentation", "API"].map((item) => (
            <a
              key={item}
              href="#"
              className="block px-4 py-3 rounded-lg text-[#EAE0D5] hover:bg-orange-500/10 hover:text-[#FF6B35] transition-all touch-target"
            >
              {item}
            </a>
          ))}
        </nav>
      </motion.div>
    )}
  </AnimatePresence>
)

export const SwipeableCards = ({ cards }: { cards: any[] }) => {
  const [currentIndex, setCurrentIndex] = useState(0)

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % cards.length)
  }

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length)
  }

  return (
    <div className="relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-header">Pricing Overview</h3>
        <div className="flex space-x-2">
          <button
            onClick={prevCard}
            className="p-2 rounded-lg bg-orange-500/10 hover:bg-orange-500/20 transition-colors touch-target"
          >
            <ChevronLeft className="w-5 h-5 text-[#FF6B35]" />
          </button>
          <button
            onClick={nextCard}
            className="p-2 rounded-lg bg-orange-500/10 hover:bg-orange-500/20 transition-colors touch-target"
          >
            <ChevronRight className="w-5 h-5 text-[#FF6B35]" />
          </button>
        </div>
      </div>

      <motion.div
        key={currentIndex}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        transition={{ duration: 0.3 }}
        className="mobile-card glass-card"
      >
        {/* Card content */}
        <div className="space-y-4">
          <div className="flex justify-between items-start">
            <h4 className="text-lg font-semibold text-[#EAE0D5]">{cards[currentIndex]?.name}</h4>
            <div className="px-2 py-1 rounded-full bg-orange-500/20 text-xs text-[#FF6B35]">
              {currentIndex + 1} of {cards.length}
            </div>
          </div>
          <div className="metric-text">${cards[currentIndex]?.currentPrice}</div>
        </div>
      </motion.div>
    </div>
  )
}
