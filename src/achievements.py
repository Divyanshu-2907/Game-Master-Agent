"""
Game Master Agent - Achievements System
Tracks player achievements and milestones.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class AchievementsSystem:
    """Manages player achievements and milestones."""
    
    def __init__(self):
        """Initialize the achievements system."""
        self.achievements: List[Dict[str, Any]] = []
        self.milestones: Dict[str, Any] = {
            "enemies_defeated": 0,
            "quests_completed": 0,
            "npcs_met": 0,
            "locations_discovered": 0,
            "gold_earned": 0,
            "levels_gained": 0,
            "critical_hits": 0,
            "skill_checks_passed": 0
        }
    
    def unlock_achievement(self, achievement_id: str, name: str, 
                         description: str, category: str = "general") -> Dict[str, Any]:
        """
        Unlock an achievement.
        
        Args:
            achievement_id: Unique achievement ID
            name: Achievement name
            description: Achievement description
            category: Achievement category
        
        Returns:
            Achievement dictionary
        """
        # Check if already unlocked
        if any(a["id"] == achievement_id for a in self.achievements):
            return {"success": False, "error": "Achievement already unlocked"}
        
        achievement = {
            "id": achievement_id,
            "name": name,
            "description": description,
            "category": category,
            "unlocked_at": datetime.now().isoformat()
        }
        
        self.achievements.append(achievement)
        
        return {
            "success": True,
            "achievement": achievement,
            "message": f"🏆 Achievement Unlocked: {name}!"
        }
    
    def update_milestone(self, milestone: str, amount: int = 1) -> Dict[str, Any]:
        """
        Update a milestone counter.
        
        Args:
            milestone: Milestone name
            amount: Amount to add
        
        Returns:
            Update result
        """
        if milestone in self.milestones:
            self.milestones[milestone] += amount
            
            # Check for milestone-based achievements
            self._check_milestone_achievements(milestone)
            
            return {
                "success": True,
                "milestone": milestone,
                "value": self.milestones[milestone]
            }
        
        return {"success": False, "error": f"Unknown milestone: {milestone}"}
    
    def _check_milestone_achievements(self, milestone: str):
        """Check if milestones trigger achievements."""
        value = self.milestones[milestone]
        
        # Define achievement thresholds
        thresholds = {
            "enemies_defeated": [
                (1, "first_blood", "First Blood", "Defeat your first enemy"),
                (10, "warrior", "Warrior", "Defeat 10 enemies"),
                (50, "slayer", "Slayer", "Defeat 50 enemies"),
                (100, "legend", "Legend", "Defeat 100 enemies")
            ],
            "quests_completed": [
                (1, "adventurer", "Adventurer", "Complete your first quest"),
                (5, "hero", "Hero", "Complete 5 quests"),
                (10, "champion", "Champion", "Complete 10 quests"),
                (25, "master", "Master", "Complete 25 quests")
            ],
            "npcs_met": [
                (5, "social", "Social Butterfly", "Meet 5 NPCs"),
                (15, "networker", "Networker", "Meet 15 NPCs"),
                (30, "diplomat", "Diplomat", "Meet 30 NPCs")
            ],
            "gold_earned": [
                (100, "wealthy", "Wealthy", "Earn 100 gold"),
                (500, "rich", "Rich", "Earn 500 gold"),
                (1000, "tycoon", "Tycoon", "Earn 1000 gold")
            ],
            "levels_gained": [
                (2, "rising", "Rising Star", "Reach level 2"),
                (5, "experienced", "Experienced", "Reach level 5"),
                (10, "veteran", "Veteran", "Reach level 10")
            ]
        }
        
        if milestone in thresholds:
            for threshold, achievement_id, name, description in thresholds[milestone]:
                if value >= threshold:
                    # Check if already unlocked
                    if not any(a["id"] == achievement_id for a in self.achievements):
                        self.unlock_achievement(achievement_id, name, description, "milestone")
    
    def get_achievements_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get achievements, optionally filtered by category."""
        if category:
            return [a for a in self.achievements if a["category"] == category]
        return self.achievements.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get achievement statistics."""
        total = len(self.achievements)
        by_category = {}
        for achievement in self.achievements:
            cat = achievement["category"]
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_achievements": total,
            "by_category": by_category,
            "milestones": self.milestones.copy()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievements system to dictionary."""
        return {
            "achievements": self.achievements.copy(),
            "milestones": self.milestones.copy()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load achievements system from dictionary."""
        self.achievements = data.get("achievements", [])
        self.milestones = data.get("milestones", {
            "enemies_defeated": 0,
            "quests_completed": 0,
            "npcs_met": 0,
            "locations_discovered": 0,
            "gold_earned": 0,
            "levels_gained": 0,
            "critical_hits": 0,
            "skill_checks_passed": 0
        })

