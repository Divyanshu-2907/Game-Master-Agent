"""
Game Master Agent - Starting Scenarios
Provides multiple starting scenarios for players to choose from.
"""

from typing import Dict, Any


SCENARIOS = {
    "the_cursed_tavern": {
        "id": "the_cursed_tavern",
        "name": "The Cursed Tavern",
        "description": "A mysterious curse has befallen the local tavern, causing furniture to come alive and attack patrons.",
        "difficulty": "medium",
        "starting_location": "town_square",
        "initial_prompt": """You are the Game Master for a D&D campaign. The player's character has just arrived at a small town called Millbrook. As they walk through the streets in the evening, they notice something unusual - the local tavern, "The Rusty Tankard", appears to be closed and boarded up, despite it being evening when taverns are usually busy. Strange sounds can be heard from inside - creaking, scraping, and what sounds like furniture moving on its own.

Begin the adventure by describing the scene vividly and inviting the player to investigate. Use rich sensory details and create an atmosphere of mystery and tension.""",
        "themes": ["mystery", "horror", "urban"],
        "recommended_level": 1
    },
    "the_lost_treasure": {
        "id": "the_lost_treasure",
        "name": "The Lost Treasure",
        "description": "An ancient map leads to a hidden treasure, but the path is dangerous and filled with traps.",
        "difficulty": "hard",
        "starting_location": "adventurers_guild",
        "initial_prompt": """You are the Game Master for a D&D campaign. The player's character has just received a mysterious map from a dying adventurer in the local tavern. The map shows the location of a legendary treasure hidden deep in an ancient dungeon. However, the path is marked with warnings of deadly traps, guardians, and ancient magic.

The map is old and partially faded, but clearly shows a route through a forest, across a ravine, and into a mountain cave. Begin by describing how the character receives the map and the sense of adventure and danger that awaits.""",
        "themes": ["adventure", "exploration", "treasure"],
        "recommended_level": 2
    },
    "the_bandit_menace": {
        "id": "the_bandit_menace",
        "name": "The Bandit Menace",
        "description": "Bandits have been terrorizing the trade routes. The local lord offers a reward for clearing them out.",
        "difficulty": "easy",
        "starting_location": "lord_manor",
        "initial_prompt": """You are the Game Master for a D&D campaign. The player's character has been summoned to the local lord's manor. The lord, a stern but fair ruler, explains that bandits have been attacking merchant caravans on the trade routes, causing economic damage and fear among the populace. He offers a substantial reward for anyone who can eliminate the bandit threat.

The bandits are said to be holed up in an old fort about a day's travel from town. Begin by describing the meeting with the lord and the mission briefing. Create a sense of urgency and the opportunity for heroism.""",
        "themes": ["combat", "justice", "reward"],
        "recommended_level": 1
    }
}


def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """
    Get a starting scenario by ID.
    
    Args:
        scenario_id: Scenario identifier
    
    Returns:
        Scenario dictionary
    """
    return SCENARIOS.get(scenario_id, SCENARIOS["the_cursed_tavern"])


def list_scenarios() -> Dict[str, Any]:
    """
    List all available starting scenarios.
    
    Returns:
        Dictionary with scenario list
    """
    scenarios_list = []
    for scenario_id, scenario in SCENARIOS.items():
        scenarios_list.append({
            "id": scenario_id,
            "name": scenario["name"],
            "description": scenario["description"],
            "difficulty": scenario["difficulty"],
            "themes": scenario["themes"],
            "recommended_level": scenario["recommended_level"]
        })
    
    return {
        "scenarios": scenarios_list,
        "count": len(scenarios_list),
        "success": True
    }


def get_scenario_by_difficulty(difficulty: str) -> Dict[str, Any]:
    """
    Get scenarios filtered by difficulty.
    
    Args:
        difficulty: Difficulty level ("easy", "medium", "hard")
    
    Returns:
        Dictionary with filtered scenarios
    """
    filtered = [
        {
            "id": scenario_id,
            "name": scenario["name"],
            "description": scenario["description"],
            "difficulty": scenario["difficulty"]
        }
        for scenario_id, scenario in SCENARIOS.items()
        if scenario["difficulty"] == difficulty
    ]
    
    return {
        "scenarios": filtered,
        "count": len(filtered),
        "success": True
    }

