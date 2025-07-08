import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simulate health check
    const healthData = {
      status: "healthy",
      model_version: "v2.1.0",
      uptime: 99.9,
      timestamp: new Date().toISOString(),
    }

    return NextResponse.json(healthData)
  } catch (error) {
    return NextResponse.json({ status: "error", message: "Health check failed" }, { status: 500 })
  }
}
