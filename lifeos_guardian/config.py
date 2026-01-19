"""Configuration module for LifeOS Guardian with scientific data"""

# Scientific research-based recommendations from Mayo Clinic, Harvard, Stanford
SCIENCE_DATA = {
    "sleep": {
        "optimal_hours": 7.5,
        "deep_sleep_percentage": 13,  # 13-23% of total sleep
        "rem_sleep_percentage": 20,   # 20-25% of total sleep
        "benefits": [
            "Improved memory consolidation",
            "Enhanced immune function",
            "Better emotional regulation",
            "Reduced risk of chronic diseases"
        ],
        "motivational_quote": "Sleep is the best meditation. - Dalai Lama"
    },
    "exercise": {
        "daily_minutes": 30,
        "cardio_frequency": 5,  # days per week
        "strength_training_frequency": 2,  # days per week
        "benefits": [
            "Reduces risk of heart disease by 35%",
            "Improves mood and reduces anxiety",
            "Boosts cognitive function",
            "Helps maintain healthy weight"
        ],
        "motivational_quote": "Take care of your body. It's the only place you have to live. - Jim Rohn"
    },
    "family": {
        "quality_time_hours": 2,  # per day minimum
        "connection_importance": "Strong family relationships improve longevity and mental health",
        "benefits": [
            "Increased sense of belonging",
            "Better stress management",
            "Improved emotional well-being",
            "Longer life expectancy"
        ],
        "motivational_quote": "Family isn't always blood. It's the people in your life who want you in theirs. - Maya Angelou"
    },
    "deep_work": {
        "focus_blocks": 90,  # minutes per block
        "optimal_sessions_per_day": 2,  # max effective sessions
        "break_duration": 15,  # minutes between focus blocks
        "benefits": [
            "Enhanced productivity and concentration",
            "Better quality of work produced",
            "Reduced mental fatigue over time",
            "Improved skill development"
        ],
        "motivational_quote": "Deep work is an ability to focus intensely on cognitively demanding activities. - Cal Newport"
    },
    "hydration": {
        "daily_liters": 2.7,  # for women, 3.7 for men
        "water_percentage_body": 60,
        "signs_dehydration": ["fatigue", "headache", "poor concentration"],
        "benefits": [
            "Maintains energy levels",
            "Supports kidney function",
            "Aids in temperature regulation",
            "Promotes clear thinking"
        ],
        "motivational_quote": "Water is the driving force of all nature. - Leonardo da Vinci"
    }
}

# Personal goals for toprudik
PERSONAL_GOALS = {
    "toprudik": {
        "sleep_target": 8,  # hours per night
        "exercise_target": 45,  # minutes per day
        "family_time_target": 3,  # hours per day
        "deep_work_target": 120,  # minutes per day (2 sessions of 60 min)
        "hydration_target": 3.0,  # liters per day
        "weekly_exercise_days": 5,
        "weekly_family_days": 7,
        "weekly_deep_work_days": 5
    }
}

# Mission types and their corresponding emoji
MISSION_EMOJIS = {
    "sleep": "😴",
    "exercise": "💪",
    "family": "👨‍👩‍👧‍👦",
    "deep_work": "🎯",
    "hydration": "💧"
}

# Default mission titles and descriptions
MISSION_TITLES = {
    "sleep": "Sleep Well Tonight",
    "exercise": "Move Your Body",
    "family": "Connect with Family",
    "deep_work": "Deep Work Session",
    "hydration": "Stay Hydrated"
}

MISSION_DESCRIPTIONS = {
    "sleep": "Prioritize quality sleep for optimal health and performance",
    "exercise": "Engage in physical activity to boost your health",
    "family": "Spend meaningful time with loved ones",
    "deep_work": "Focus intensely on important tasks without distractions",
    "hydration": "Drink enough water throughout the day"
}

# Weekly analytics thresholds
ANALYTICS_THRESHOLDS = {
    "sleep": {"min_hours": 7, "max_hours": 9},
    "exercise": {"min_minutes": 30, "recommended_minutes": 45},
    "family": {"min_hours": 1, "recommended_hours": 2},
    "deep_work": {"min_minutes": 60, "recommended_minutes": 120},
    "hydration": {"min_liters": 2.0, "recommended_liters": 3.0}
}