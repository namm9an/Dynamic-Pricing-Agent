import { NextResponse } from "next/server"
import { supabase } from "../../../lib/supabase"

export async function POST() {
  try {
    // Call the simulation functions
    const { error: pricingError } = await supabase.rpc("simulate_pricing_decision")
    if (pricingError) throw pricingError

    const { error: demandError } = await supabase.rpc("simulate_demand_prediction")
    if (demandError) throw demandError

    return NextResponse.json({
      success: true,
      message: "Simulated data generated successfully",
    })
  } catch (error) {
    console.error("Simulation error:", error)
    return NextResponse.json({ error: "Failed to simulate data" }, { status: 500 })
  }
}
