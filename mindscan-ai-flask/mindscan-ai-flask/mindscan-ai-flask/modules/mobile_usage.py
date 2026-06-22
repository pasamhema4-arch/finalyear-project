import random

def simulate_mobile_usage():
    """
    Returns random screen time hours and app usage patterns
    """
    screen_time = round(random.uniform(1, 6), 2)  # hours per day
    usage_pattern = {
        "social_apps": round(screen_time*0.5,2),
        "productivity_apps": round(screen_time*0.3,2),
        "games": round(screen_time*0.2,2)
    }
    return screen_time, usage_pattern