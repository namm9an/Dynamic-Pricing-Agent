import { createClient } from "@supabase/supabase-js"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Missing Supabase environment variables")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
})

// Database types
export interface PricingDecision {
  id: string
  timestamp: string
  product_id: string
  old_price: number
  new_price: number
  reason: string
  confidence_score: number
  created_at: string
}

export interface DemandPrediction {
  id: string
  product_id: string
  predicted_demand: number
  actual_demand: number | null
  prediction_date: string
  created_at: string
}

// Helper functions for database operations
export const fetchPricingDecisions = async (limit = 100) => {
  try {
    const { data, error } = await supabase
      .from("pricing_decisions")
      .select("*")
      .order("timestamp", { ascending: false })
      .limit(limit)

    if (error) {
      console.error("Error fetching pricing decisions:", error)
      throw error
    }

    return data as PricingDecision[]
  } catch (error) {
    console.error("Failed to fetch pricing decisions:", error)
    throw error
  }
}

export const fetchDemandPredictions = async (limit = 50) => {
  try {
    const { data, error } = await supabase
      .from("demand_predictions")
      .select("*")
      .order("prediction_date", { ascending: false })
      .limit(limit)

    if (error) {
      console.error("Error fetching demand predictions:", error)
      throw error
    }

    return data as DemandPrediction[]
  } catch (error) {
    console.error("Failed to fetch demand predictions:", error)
    throw error
  }
}

export const insertPricingDecision = async (decision: Omit<PricingDecision, "id" | "created_at">) => {
  try {
    const { data, error } = await supabase.from("pricing_decisions").insert([decision]).select()

    if (error) {
      console.error("Error inserting pricing decision:", error)
      throw error
    }

    return data[0] as PricingDecision
  } catch (error) {
    console.error("Failed to insert pricing decision:", error)
    throw error
  }
}

export const insertDemandPrediction = async (prediction: Omit<DemandPrediction, "id" | "created_at">) => {
  try {
    const { data, error } = await supabase.from("demand_predictions").insert([prediction]).select()

    if (error) {
      console.error("Error inserting demand prediction:", error)
      throw error
    }

    return data[0] as DemandPrediction
  } catch (error) {
    console.error("Failed to insert demand prediction:", error)
    throw error
  }
}

// Test connection function
export const testSupabaseConnection = async () => {
  try {
    const { data, error } = await supabase.from("pricing_decisions").select("count", { count: "exact", head: true })

    if (error) throw error

    return { success: true, message: "Connection successful" }
  } catch (error) {
    console.error("Supabase connection test failed:", error)
    return {
      success: false,
      message: error instanceof Error ? error.message : "Connection failed",
    }
  }
}
