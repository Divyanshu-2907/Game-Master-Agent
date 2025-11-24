"""
Demo Scenario: The Cursed Tavern
A complete example campaign showcasing all game features.
"""

from src.agent import GameMasterAgent
from src.character import create_character, get_character_summary
from src.content_generator import generate_location, generate_combat_encounter
from src.combat_system import create_enemy, CombatManager
from src.state_manager import GameStateManager
import os


def run_demo_scenario():
    """Run the complete demo scenario."""
    
    print("=" * 60)
    print("THE CURSED TAVERN - Demo Campaign")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_GENAI_API_KEY environment variable not set!")
        print("Please set it before running the demo.")
        return
    
    # Create character
    print("Step 1: Character Creation")
    print("-" * 60)
    character = create_character(
        name="Aria",
        race="elf",
        character_class="ranger"
    )
    print(get_character_summary(character))
    print()
    
    # Initialize agent
    print("Step 2: Initializing Game Master Agent")
    print("-" * 60)
    agent = GameMasterAgent(api_key=api_key)
    
    # Start session
    initial_prompt = """You are the Game Master for a D&D campaign. The player's character, Aria, 
    an elven ranger, has just arrived at a small town. As they walk through the streets, they notice 
    something unusual - the local tavern, "The Rusty Tankard", appears to be closed and boarded up, 
    despite it being evening when taverns are usually busy. Strange sounds can be heard from inside.
    
    Begin the adventure by describing the scene and inviting the player to investigate."""
    
    agent.start_session(character, initial_prompt)
    print("Agent initialized successfully!")
    print()
    
    # Demo gameplay loop
    print("Step 3: Gameplay Demo")
    print("-" * 60)
    print("(This would normally be interactive)")
    print()
    
    # Example interactions
    demo_messages = [
        "I approach the tavern and try to peer through the boarded windows.",
        "I want to check for any signs of what happened here using my perception skill.",
        "I'll try to find another way in, maybe through the back door.",
        "I enter the tavern carefully, keeping my bow ready."
    ]
    
    print("Example player actions:")
    for i, msg in enumerate(demo_messages, 1):
        print(f"\n{i}. Player: {msg}")
        print("   (Agent would process this and respond)")
    
    print("\n" + "=" * 60)
    print("Demo scenario setup complete!")
    print("=" * 60)
    print("\nTo run the full interactive demo, use the notebook.ipynb file.")


if __name__ == "__main__":
    run_demo_scenario()

