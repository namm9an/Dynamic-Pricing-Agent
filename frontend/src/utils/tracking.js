/**
 * Tracking and Analytics Utility
 * ================================
 * 
 * Handles A/B testing tracking, user behavior analytics,
 * and performance metrics for the Dynamic Pricing Agent.
 */

import { api } from './api.js';

class AnalyticsTracker {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    this.events = [];
    this.startTime = Date.now();
    
    // Initialize tracking
    this.initializeTracking();
  }

  /**
   * Generate unique session ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get or create user ID
   */
  getUserId() {
    let userId = localStorage.getItem('analytics_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('analytics_user_id', userId);
    }
    return userId;
  }

  /**
   * Initialize tracking on page load
   */
  initializeTracking() {
    // Track page load
    this.track('page_load', {
      url: window.location.href,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      timestamp: new Date().toISOString()
    });

    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.track('page_hidden', { timestamp: new Date().toISOString() });
      } else {
        this.track('page_visible', { timestamp: new Date().toISOString() });
      }
    });

    // Track page unload
    window.addEventListener('beforeunload', () => {
      this.track('page_unload', { 
        session_duration: Date.now() - this.startTime,
        timestamp: new Date().toISOString()
      });
      this.flush(); // Send any pending events
    });

    // Flush events periodically
    setInterval(() => this.flush(), 30000); // Every 30 seconds
  }

  /**
   * Track an event
   */
  track(eventName, properties = {}) {
    const event = {
      event_name: eventName,
      session_id: this.sessionId,
      user_id: this.userId,
      timestamp: new Date().toISOString(),
      properties: {
        ...properties,
        page_url: window.location.href,
        page_title: document.title
      }
    };

    this.events.push(event);
    console.log('Analytics Event:', event);

    // Flush immediately for critical events
    if (this.isCriticalEvent(eventName)) {
      this.flush();
    }
  }

  /**
   * Track pricing interaction
   */
  trackPricingInteraction(action, data = {}) {
    this.track('pricing_interaction', {
      action,
      ...data,
      component: 'pricing_dashboard'
    });
  }

  /**
   * Track A/B test events
   */
  trackABTest(action, data = {}) {
    this.track('ab_test_event', {
      action,
      ...data,
      component: 'ab_testing'
    });
  }

  /**
   * Track conversion events
   */
  trackConversion(type, data = {}) {
    this.track('conversion', {
      conversion_type: type,
      ...data,
      value: data.revenue || data.value || 0
    });
  }

  /**
   * Track user engagement
   */
  trackEngagement(action, data = {}) {
    this.track('user_engagement', {
      action,
      ...data,
      engagement_time: Date.now() - this.startTime
    });
  }

  /**
   * Track performance metrics
   */
  trackPerformance(metrics) {
    this.track('performance_metrics', {
      ...metrics,
      page_load_time: performance.now(),
      memory_usage: this.getMemoryUsage()
    });
  }

  /**
   * Track errors
   */
  trackError(error, context = {}) {
    this.track('error', {
      error_message: error.message || error,
      error_stack: error.stack,
      error_type: error.name || 'Unknown',
      context,
      user_agent: navigator.userAgent
    });
  }

  /**
   * Check if event is critical and needs immediate flushing
   */
  isCriticalEvent(eventName) {
    const criticalEvents = [
      'conversion',
      'error',
      'pricing_interaction',
      'ab_test_event',
      'page_unload'
    ];
    return criticalEvents.includes(eventName);
  }

  /**
   * Get memory usage if available
   */
  getMemoryUsage() {
    if (performance.memory) {
      return {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      };
    }
    return null;
  }

  /**
   * Flush events to backend
   */
  async flush() {
    if (this.events.length === 0) return;

    const eventsToSend = [...this.events];
    this.events = []; // Clear events array

    try {
      // In a real implementation, send to analytics service
      // For demo purposes, we'll simulate analytics tracking
      console.log('Flushing analytics events:', eventsToSend);
      
      // You could send to services like:
      // - Google Analytics
      // - Mixpanel
      // - Custom analytics endpoint
      // await api.post('/analytics/events', { events: eventsToSend });
      
    } catch (error) {
      console.error('Failed to flush analytics events:', error);
      // Re-add events to queue for retry
      this.events.unshift(...eventsToSend);
    }
  }

  /**
   * Get session summary
   */
  getSessionSummary() {
    const sessionDuration = Date.now() - this.startTime;
    const eventCounts = this.events.reduce((counts, event) => {
      counts[event.event_name] = (counts[event.event_name] || 0) + 1;
      return counts;
    }, {});

    return {
      session_id: this.sessionId,
      user_id: this.userId,
      session_duration: sessionDuration,
      total_events: this.events.length,
      event_counts: eventCounts,
      start_time: new Date(this.startTime).toISOString()
    };
  }
}

// A/B Testing utilities
export class ABTestManager {
  constructor() {
    this.currentTests = {};
    this.loadActiveTests();
  }

  /**
   * Load active A/B tests from backend
   */
  async loadActiveTests() {
    try {
      // In production, fetch from backend
      // const response = await api.get('/ab-tests/active');
      // this.currentTests = response.data;
      
      // For demo, simulate active tests
      this.currentTests = {
        'pricing_strategy': {
          id: 'pricing_strategy_v1',
          name: 'Dynamic vs Static Pricing',
          variants: ['control', 'test'],
          traffic_split: 0.5,
          status: 'active'
        }
      };
    } catch (error) {
      console.error('Failed to load A/B tests:', error);
    }
  }

  /**
   * Get user's variant for a test
   */
  getUserVariant(testId, userId) {
    const test = this.currentTests[testId];
    if (!test || test.status !== 'active') {
      return 'control'; // Default to control
    }

    // Consistent assignment based on user ID hash
    const hash = this.hashString(userId + testId);
    const normalized = (hash % 10000) / 10000; // 0-1 range
    
    return normalized < test.traffic_split ? 'test' : 'control';
  }

  /**
   * Hash string to number for consistent assignment
   */
  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Record test exposure
   */
  recordExposure(testId, variant, userId) {
    tracker.trackABTest('exposure', {
      test_id: testId,
      variant,
      user_id: userId
    });
  }

  /**
   * Record test conversion
   */
  recordConversion(testId, variant, userId, value = 0) {
    tracker.trackConversion('ab_test', {
      test_id: testId,
      variant,
      user_id: userId,
      value
    });
  }
}

// Create global instances
export const tracker = new AnalyticsTracker();
export const abTestManager = new ABTestManager();

// Convenience functions
export const trackPricing = (action, data) => tracker.trackPricingInteraction(action, data);
export const trackABTest = (action, data) => tracker.trackABTest(action, data);
export const trackConversion = (type, data) => tracker.trackConversion(type, data);
export const trackError = (error, context) => tracker.trackError(error, context);
export const trackEngagement = (action, data) => tracker.trackEngagement(action, data);

// Price sensitivity tracking
export class PriceSensitivityTracker {
  constructor() {
    this.priceInteractions = [];
  }

  /**
   * Track price change interaction
   */
  trackPriceChange(oldPrice, newPrice, context = {}) {
    const interaction = {
      timestamp: new Date().toISOString(),
      old_price: oldPrice,
      new_price: newPrice,
      change_percent: ((newPrice - oldPrice) / oldPrice) * 100,
      context,
      session_id: tracker.sessionId
    };

    this.priceInteractions.push(interaction);
    
    tracker.track('price_sensitivity', {
      ...interaction,
      total_interactions: this.priceInteractions.length
    });
  }

  /**
   * Calculate price sensitivity metrics
   */
  calculateSensitivity() {
    if (this.priceInteractions.length < 2) {
      return null;
    }

    const changes = this.priceInteractions.map(i => Math.abs(i.change_percent));
    const avgChange = changes.reduce((a, b) => a + b, 0) / changes.length;
    const maxChange = Math.max(...changes);
    
    return {
      average_change_percent: avgChange,
      max_change_percent: maxChange,
      total_interactions: this.priceInteractions.length,
      sensitivity_score: Math.min(avgChange / 10, 1) // 0-1 scale
    };
  }
}

export const priceSensitivity = new PriceSensitivityTracker();

// Export default tracker
export default tracker;
