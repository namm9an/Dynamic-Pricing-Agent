import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simulate current pricing data
    const pricingData = {
      products: [
        {
          id: "premium-plan",
          name: "Premium Plan",
          currentPrice: 29.99 + (Math.random() - 0.5) * 4,
          optimalPrice: 32.5 + (Math.random() - 0.5) * 2,
          confidence: 0.87 + (Math.random() - 0.5) * 0.1,
          demand: Math.random() > 0.5 ? "high" : "medium",
          priceChange: (Math.random() - 0.5) * 10,
        },
        {
          id: "enterprise-plan",
          name: "Enterprise Plan",
          currentPrice: 99.99 + (Math.random() - 0.5) * 10,
          optimalPrice: 105.0 + (Math.random() - 0.5) * 5,
          confidence: 0.92 + (Math.random() - 0.5) * 0.08,
          demand: Math.random() > 0.3 ? "medium" : "high",
          priceChange: (Math.random() - 0.5) * 8,
        },
        {
          id: "starter-plan",
          name: "Starter Plan",
          currentPrice: 9.99 + (Math.random() - 0.5) * 2,
          optimalPrice: 11.5 + (Math.random() - 0.5) * 1,
          confidence: 0.78 + (Math.random() - 0.5) * 0.12,
          demand: Math.random() > 0.4 ? "high" : "medium",
          priceChange: (Math.random() - 0.5) * 12,
        },
      ],
      lastUpdated: new Date().toISOString(),
    }

    return NextResponse.json(pricingData)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch pricing data" }, { status: 500 })
  }
}
