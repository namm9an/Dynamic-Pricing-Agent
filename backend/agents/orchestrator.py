"""
Pricing Orchestrator for Dynamic Pricing Agent
Coordinates Data Agent and Pricing Agent for optimal pricing strategies

This module implements the core orchestration logic for the AI-powered pricing system,
managing the interaction between data collection agents and pricing recommendation agents.

Features:
- CrewAI agent coordination
- Sequential task processing
- Memory-enabled agents
- Comprehensive error handling
"""

import json
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process
from backend.tools import TwitterScraperTool, CalendarCollectorTool


class PricingOrchestrator:
    """Orchestrator to manage the pricing strategy using data collection and analysis"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.data_agent = None
        self.pricing_agent = None
        self.crew = None
        self.twitter_tool = TwitterScraperTool()
        self.calendar_tool = CalendarCollectorTool()
    
    def _create_data_agent(self) -> None:
        """
        Create and configure data agent
        """
        self.data_agent = Agent(
            role="Market Data Scout",
            goal="Collect real-time market signals from social media and events",
            backstory="""You are an expert market researcher specialized in gathering 
            real-time data from social media platforms and event calendars. Your insights 
            help predict demand patterns and market trends.""",
            tools=[self.twitter_tool, self.calendar_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    def _create_pricing_agent(self) -> None:
        """
        Create and configure pricing agent
        """
        self.pricing_agent = Agent(
            role="Dynamic Pricing Analyst",
            goal="Generate optimal pricing recommendations based on market data",
            backstory="""You are a seasoned pricing strategist with expertise in 
            analyzing market signals and generating optimal pricing recommendations. 
            You consider demand patterns, events, and sentiment to maximize revenue.""",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    def _create_crew(self) -> None:
        """
        Create and configure the crew with tasks
        """
        # Create data collection task
        data_collection_task = Task(
            description="""Collect and analyze market data for the product/service. 
            Use Twitter to gauge market sentiment and trending topics. 
            Use Calendar to identify upcoming high-impact events.
            Provide a comprehensive market analysis report.""",
            agent=self.data_agent,
            expected_output="JSON report with sentiment scores, trending topics, and event impacts"
        )
        
        # Create pricing recommendation task
        pricing_task = Task(
            description="""Based on the market data collected, generate optimal pricing 
            recommendations. Consider sentiment trends, upcoming events, and demand forecasts 
            to suggest price adjustments that maximize revenue while maintaining competitiveness.""",
            agent=self.pricing_agent,
            context=[data_collection_task],
            expected_output="JSON report with pricing recommendations, confidence levels, and justifications"
        )
        
        # Create crew
        self.crew = Crew(
            agents=[self.data_agent, self.pricing_agent],
            tasks=[data_collection_task, pricing_task],
            process=Process.sequential,
            verbose=2,
            memory=True
        )
    
    def orchestrate(self, product_query: str = "product") -> Dict[str, Any]:
        """
        Run the orchestration process for pricing
        
        Args:
            product_query: Product or service to analyze
            
        Returns:
            Dictionary with pricing recommendations and analysis
        """
        try:
            # Initialize agents and crew
            self._create_data_agent()
            self._create_pricing_agent()
            self._create_crew()
            
            # Execute crew tasks
            result = self.crew.kickoff(inputs={"product": product_query})
            
            # Parse and structure the result
            return {
                "status": "success",
                "product": product_query,
                "analysis": result,
                "timestamp": json.loads(self.twitter_tool._run(product_query))["analysis_timestamp"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "product": product_query
            }
