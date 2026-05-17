"""
Learning layer for self-optimization.

This module provides the core components for the super thinking
self-optimization system, including:
- ProfileManager: Manages user profiles
- FeedbackCollector: Collects multi-dimensional feedback
- RoutingOptimizer: Optimizes expert routing based on feedback
- ExpertCombinationTracker: Tracks expert combination effectiveness

Usage:
    from src.learning import ProfileManager, FeedbackCollector, RoutingOptimizer
    
    # Initialize
    pm = ProfileManager("profiles/")
    
    # Get recommendations
    recs = pm.get_recommendations("user123", "Should I change my career?")
    
    # Collect feedback
    fc = FeedbackCollector()
    feedback = fc.collect(analysis_result)
    
    # Update profile
    pm.update_profile("user123", feedback)
"""

__version__ = "1.0.0"

from .profile_manager import ProfileManager
from .feedback_collector import FeedbackCollector
from .routing_optimizer import RoutingOptimizer
from .expert_combination_tracker import ExpertCombinationTracker

__all__ = [
    "ProfileManager",
    "FeedbackCollector", 
    "RoutingOptimizer",
    "ExpertCombinationTracker",
]
