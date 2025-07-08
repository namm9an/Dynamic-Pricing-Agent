import { NextResponse } from "next/server"
import { supabase } from "../../../lib/supabase"

export async function GET() {
  try {
    // Test the connection by checking if we can access the database
    const { data, error } = await supabase.from("pricing_decisions").select("count", { count: "exact", head: true })

    if (error) {
      console.error("Supabase connection error:", error)
      return NextResponse.json(
        {
          status: "error",
          message: "Failed to connect to Supabase",
          error: error.message,
        },
        { status: 500 },
      )
    }

    // Test real-time capabilities
    const { data: realtimeData, error: realtimeError } = await supabase
      .from("demand_predictions")
      .select("count", { count: "exact", head: true })

    return NextResponse.json({
      status: "success",
      message: "Successfully connected to Supabase",
      pricing_decisions_count: data,
      demand_predictions_available: !realtimeError,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Connection test failed:", error)
    return NextResponse.json(
      {
        status: "error",
        message: "Connection test failed",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
