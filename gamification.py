from datetime import datetime, date

def get_avatar(level: int) -> str:
    """Returns an evolving avatar based on the user's level."""
    if level < 4:
        return "🌱" # Sprout (Levels 1-3)
    elif level < 10:
        return "🪴" # Small Plant (Levels 4-9)
    elif level < 20:
        return "🌸" # Blossoming Flower (Levels 10-19)
    else:
        return "🌳✨" # Magical Tree (Levels 20+)

def get_level_threshold(level: int) -> int:
    """Calculates how much total XP is required to reach the NEXT level."""
    # Exponential scaling: Lvl 1->2 needs 100. Lvl 2->3 needs 150 (Total 250). 
    # Base formula: 100 * (level^1.5) approx
    return int(100 * (level ** 1.5))

def get_xp_for_priority(priority: int) -> int:
    """XP awarded based on task priority (1 is highest, 5 is lowest)."""
    xp_map = {
        1: 50,
        2: 40,
        3: 30,
        4: 20,
        5: 10
    }
    return xp_map.get(priority, 10)

def calculate_streak(current_streak: int, last_active: str) -> int:
    """
    Given the current streak and the date of last activity (YYYY-MM-DD),
    calculates the new streak. Return 0 if the streak is broken,
    return current_streak + 1 if continued, or current_streak if already active today.
    """
    if not last_active:
        return 1

    try:
        last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
    except ValueError:
        return 1
        
    today = date.today()
    delta = (today - last_date).days

    if delta == 0:
        return current_streak # Already active today
    elif delta == 1:
        return current_streak + 1 # Streak continues!
    else:
        return 1 # Streak broken, starts over at 1
