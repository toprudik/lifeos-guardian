"""Configuration module for LifeOS Guardian with scientific data"""

# Scientific research-based recommendations from Mayo Clinic, Harvard, Stanford
SCIENCE_DATA = {
    "sleep": {
        "optimal_hours": 7.5,
        "deep_sleep_percentage": 13,  # 13-23% of total sleep
        "rem_sleep_percentage": 20,   # 20-25% of total sleep
        "benefits": [
            "Улучшенная консолидация памяти",
            "Повышенная функция иммунитета",
            "Лучшая эмоциональная регуляция",
            "Снижение риска хронических заболеваний"
        ],
        "motivational_quote": "Sleep is the best meditation. - Dalai Lama"
    },
    "exercise": {
        "daily_minutes": 30,
        "cardio_frequency": 5,  # days per week
        "strength_training_frequency": 2,  # days per week
        "benefits": [
            "Снижение риска сердечных заболеваний на 35%",
            "Улучшение настроения и снижение тревожности",
            "Повышение когнитивной функции",
            "Помощь в поддержании здорового веса"
        ],
        "motivational_quote": "Take care of your body. It's the only place you have to live. - Jim Rohn"
    },
    "family": {
        "quality_time_hours": 2,  # per day minimum
        "connection_importance": "Strong family relationships improve longevity and mental health",
        "benefits": [
            "Повышенное чувство принадлежности",
            "Лучшее управление стрессом",
            "Улучшенное эмоциональное благополучие",
            "Более продолжительная жизнь"
        ],
        "motivational_quote": "Family isn't always blood. It's the people in your life who want you in theirs. - Maya Angelou"
    },
    "deep_work": {
        "focus_blocks": 90,  # minutes per block
        "optimal_sessions_per_day": 2,  # max effective sessions
        "break_duration": 15,  # minutes between focus blocks
        "benefits": [
            "Повышенная продуктивность и концентрация",
            "Лучшее качество производимой работы",
            "Сниженная умственная усталость со временем",
            "Улучшенное развитие навыков"
        ],
        "motivational_quote": "Deep work is an ability to focus intensely on cognitively demanding activities. - Cal Newport"
    },
    "hydration": {
        "daily_liters": 2.7,  # for women, 3.7 for men
        "water_percentage_body": 60,
        "signs_dehydration": ["усталость", "головная боль", "плохая концентрация"],
        "benefits": [
            "Поддержание уровня энергии",
            "Поддержка функции почек",
            "Помощь в регулировании температуры",
            "Способствует ясности мышления"
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
    "sleep": "Хорошо выспаться сегодня ночью",
    "exercise": "Двигать телом",
    "family": "Общение с семьей",
    "deep_work": "Сессия глубокой работы",
    "hydration": "Поддерживать гидратацию"
}

MISSION_DESCRIPTIONS = {
    "sleep": "Приоритет качества сна для оптимального здоровья и производительности",
    "exercise": "Заниматься физической активностью для укрепления здоровья",
    "family": "Проводить значимое время с близкими",
    "deep_work": "Интенсивно сосредоточиться на важных задачах без отвлечений",
    "hydration": "Пить достаточное количество воды в течение дня"
}

# Weekly analytics thresholds
ANALYTICS_THRESHOLDS = {
    "sleep": {"min_hours": 7, "max_hours": 9},
    "exercise": {"min_minutes": 30, "recommended_minutes": 45},
    "family": {"min_hours": 1, "recommended_hours": 2},
    "deep_work": {"min_minutes": 60, "recommended_minutes": 120},
    "hydration": {"min_liters": 2.0, "recommended_liters": 3.0}
}