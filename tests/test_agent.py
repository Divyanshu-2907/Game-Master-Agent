"""
Basic tests for the Game Master Agent.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import roll_dice, skill_check
from src.character import create_character, get_character_summary
from src.content_generator import generate_npc, create_quest
from src.state_manager import GameStateManager


def test_dice_rolling():
    """Test dice rolling functionality."""
    print("Testing dice rolling...")
    result = roll_dice("1d20")
    assert result.get("success"), "Dice roll should succeed"
    assert "total" in result, "Result should have total"
    assert 1 <= result["total"] <= 20, "d20 should be between 1 and 20"
    print("✅ Dice rolling works!")


def test_character_creation():
    """Test character creation."""
    print("Testing character creation...")
    character = create_character(
        name="Test Hero",
        race="human",
        character_class="fighter"
    )
    assert character["name"] == "Test Hero", "Character name should match"
    assert character["level"] == 1, "Character should start at level 1"
    assert "hp" in character, "Character should have HP"
    print("✅ Character creation works!")
    print(get_character_summary(character))


def test_skill_check():
    """Test skill check system."""
    print("Testing skill checks...")
    modifiers = {
        "stats": {"wisdom": 14},
        "level": 1,
        "skills": {"proficient": ["perception"]}
    }
    result = skill_check("perception", difficulty=12, modifiers=modifiers)
    assert result.get("success") is not None, "Skill check should return success status"
    print("✅ Skill checks work!")


def test_npc_generation():
    """Test NPC generation."""
    print("Testing NPC generation...")
    result = generate_npc(
        context="A test scenario",
        role="tavern_owner"
    )
    assert result.get("success"), "NPC generation should succeed"
    assert "npc" in result, "Result should contain NPC"
    print("✅ NPC generation works!")


def test_quest_creation():
    """Test quest creation."""
    print("Testing quest creation...")
    result = create_quest(
        difficulty="medium",
        theme="the_cursed_tavern"
    )
    assert result.get("success"), "Quest creation should succeed"
    assert "quest" in result, "Result should contain quest"
    print("✅ Quest creation works!")


def test_state_management():
    """Test state management."""
    print("Testing state management...")
    state_manager = GameStateManager()
    character = create_character("Test", "elf", "ranger")
    state = state_manager.create_initial_state(character)
    assert state is not None, "State should be created"
    assert state["character"]["name"] == "Test", "State should contain character"
    print("✅ State management works!")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Game Master Agent Tests")
    print("=" * 60)
    print()
    
    try:
        test_dice_rolling()
        print()
        test_character_creation()
        print()
        test_skill_check()
        print()
        test_npc_generation()
        print()
        test_quest_creation()
        print()
        test_state_management()
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

