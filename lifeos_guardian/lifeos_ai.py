"""Enhanced LifeOS AI - System of Personal Development with AI Analytics"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from config import (
    SCIENCE_DATA, 
    PERSONAL_GOALS, 
    MISSION_EMOJIS, 
    MISSION_TITLES, 
    MISSION_DESCRIPTIONS
)
from ai_analyzer import ai_analyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Пожалуйста, установите BOT_TOKEN в переменных окружения")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def create_main_menu_keyboard():
    """Create main menu keyboard with emoji buttons for LifeOS AI"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="📊 МОЙ LIFEOS DASHBOARD", callback_data="dashboard")
    keyboard.button(text="📝 Чек-ин", callback_data="checkin")
    keyboard.button(text="🔍 Аналитика", callback_data="analytics")
    keyboard.button(text="🎮 Челленджи", callback_data="challenges")
    keyboard.button(text="👥 Группы", callback_data="groups")
    keyboard.button(text="🏆 Достижения", callback_data="achievements")
    keyboard.button(text="⚙️ Настройки", callback_data="settings")
    keyboard.adjust(1)
    
    return keyboard.as_markup()


def create_checkin_keyboard():
    """Create keyboard for daily check-in"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="⭐ Сон", callback_data="checkin_sleep")
    keyboard.button(text="🏃‍♂️ Спорт", callback_data="checkin_exercise")
    keyboard.button(text="🎯 Цели", callback_data="checkin_goals")
    keyboard.button(text="❤️ Семья", callback_data="checkin_family")
    keyboard.button(text="📚 Развитие", callback_data="checkin_learning")
    keyboard.button(text="📝 Полный чек-ин", callback_data="full_checkin")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    return keyboard.as_markup()


def create_challenges_keyboard():
    """Create keyboard for challenges"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="➕ Новый челлендж", callback_data="new_challenge")
    keyboard.button(text="📊 Мои челленджи", callback_data="my_challenges")
    keyboard.button(text="🏆 Таблица лидеров", callback_data="leaderboard")
    keyboard.button(text="🎁 Награды", callback_data="rewards")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    return keyboard.as_markup()


def create_groups_keyboard():
    """Create keyboard for groups"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="👥 Создать группу", callback_data="create_group")
    keyboard.button(text="🔍 Найти группу", callback_data="find_group")
    keyboard.button(text="📊 Мои группы", callback_data="my_groups")
    keyboard.button(text="👥 Участники", callback_data="group_members")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    return keyboard.as_markup()


def create_settings_keyboard():
    """Create keyboard for settings"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="🎯 Управление ценностями", callback_data="manage_values")
    keyboard.button(text="📊 Управление целями", callback_data="manage_goals")
    keyboard.button(text="🔔 Уведомления", callback_data="notifications")
    keyboard.button(text="🔄 Сброс данных", callback_data="reset_data")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    return keyboard.as_markup()


def create_dashboard_keyboard():
    """Create keyboard for dashboard"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="🔄 Обновить", callback_data="refresh_dashboard")
    keyboard.button(text="📊 Подробная аналитика", callback_data="detailed_analytics")
    keyboard.button(text="🔍 Зеркало ценностей", callback_data="values_mirror")
    keyboard.button(text="🗺️ Карта баланса", callback_data="balance_map")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    return keyboard.as_markup()


async def generate_dashboard(user_id: int) -> str:
    """Generate comprehensive dashboard with user metrics"""
    # Get user's goals and check-ins
    goals = db.get_user_goals(user_id)
    checkins = db.get_user_checkins(user_id, days=7)
    
    # Calculate basic metrics
    sleep_avg = 0
    sleep_count = 0
    for checkin in checkins:
        if checkin['metric_type'] == 'sleep_quality':
            sleep_avg += checkin['value']
            sleep_count += 1
    sleep_avg = sleep_avg / sleep_count if sleep_count > 0 else 0
    
    # Get recent journal entries
    journal_entries = db.get_journal_entries(user_id, days=7)
    high_value_count = len([e for e in journal_entries if e['category'] == 'high_value'])
    medium_value_count = len([e for e in journal_entries if e['category'] == 'medium_value'])
    low_value_count = len([e for e in journal_entries if e['category'] == 'low_value'])
    
    # Calculate overall score
    total_entries = len(journal_entries)
    if total_entries > 0:
        avg_score = sum([entry['value_score'] for entry in journal_entries]) / total_entries
    else:
        avg_score = 0
    
    # Get user values
    user_values = db.get_user_values(user_id)
    
    # Format dashboard
    dashboard_text = f"""
🌟 <b>МОЙ LIFEOS DASHBOARD</b>

┌─────────────────────────────────────┐
│ 🌟 ОБЩИЙ SCORE: {int(avg_score * 10)}/100        │
│ 📈 Тренд: {"+" if avg_score > 5 else "-"}{abs(int(avg_score - 5)) * 2}% за неделю        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎯 ЦЕЛИ: {len([g for g in goals if g['current_value'] >= g['target_value']])}/{len(goals)} выполнено        │
│ ❤️ ЗДОРОВЬЕ: {int(sleep_avg * 10) if sleep_avg > 0 else 50}/100            │
│ 📚 РАЗВИТИЕ: {int(high_value_count/total_entries*100) if total_entries > 0 else 0}/100         │
│ 👥 ОТНОШЕНИЯ: {int(len(user_values) * 10) if user_values else 50}/100        │
└─────────────────────────────────────┘

📊 <b>Активности за неделю:</b>
• Высокая ценность: {high_value_count}
• Средняя ценность: {medium_value_count}  
• Низкая ценность: {low_value_count}

🎯 <b>Ваши ценности:</b>
{chr(10).join([f"• {v['value_name']} ({v['importance_level']}/10)" for v in user_values[:3]]) if user_values else "Пока не указаны"}
    """
    
    return dashboard_text


async def generate_checkin_form(user_id: int) -> str:
    """Generate form for daily check-in"""
    checkins = db.get_user_checkins(user_id, days=1)
    
    # Prepare the check-in form
    sleep_rating = next((c['value'] for c in checkins if c['metric_type'] == 'sleep_quality'), 0)
    exercise_time = next((c['value'] for c in checkins if c['metric_type'] == 'exercise_minutes'), 0)
    family_time = next((c['value'] for c in checkins if c['metric_type'] == 'family_time'), 0)
    
    checkin_text = f"""
📝 <b>ЕЖЕДНЕВНЫЙ ЧЕК-ИН (2 минуты)</b>

┌─────────────────────────────────────┐
│ 💤 СОН: {"⭐" * int(sleep_rating)}{"☆" * (5-int(sleep_rating))} ({sleep_rating}/5)      │
│ 🏃 СПОРТ: {exercise_time} минут           │
│ 🎯 ЦЕЛИ: 0/0 выполнено         │
│ 👨‍👩‍👧 СЕМЬЯ: {family_time} часа качество │
└─────────────────────────────────────┘

<b>Введите значение для:</b>
1. Качество сна (1-5): /sleep_rating
2. Время на спорт (мин): /exercise_time
3. Время с семьей (часы): /family_time
    """
    
    return checkin_text


async def generate_challenges_list(user_id: int) -> str:
    """Generate list of user's challenges"""
    challenges = db.get_user_challenges(user_id)
    
    if not challenges:
        challenges_text = "🎮 <b>МОИ ЛИЧНЫЕ ЧЕЛЛЕНДЖИ</b>\n\nПока нет активных челленджей. Начните новый!"
    else:
        challenges_text = "🎮 <b>МОИ ЛИЧНЫЕ ЧЕЛЛЕНДЖИ</b>\n"
        for challenge in challenges:
            progress_bar = "█" * int(challenge['current_streak'] * 10 / challenge['target_duration'])
            progress_bar += "░" * (10 - len(progress_bar))
            
            challenges_text += f"\n┌─────────────────────────────────────┐\n"
            challenges_text += f"│ 🏆 {challenge['challenge_name']}      │\n"
            challenges_text += f"│    Прогресс: {progress_bar} {int(challenge['current_streak']/challenge['target_duration']*100)}% │\n"
            challenges_text += f"│    Серия: 🔥{challenge['current_streak']} дней подряд      │\n"
            challenges_text += f"└─────────────────────────────────────┘\n"
    
    return challenges_text


async def generate_analytics_report(user_id: int) -> str:
    """Generate detailed analytics report"""
    # Get all data for analysis
    journal_entries = db.get_journal_entries(user_id, days=7)
    checkins = db.get_user_checkins(user_id, days=7)
    goals = db.get_user_goals(user_id)
    
    # Prepare metrics for balance analysis
    user_metrics = {
        'sleep': {'average_hours': 0},
        'work': {'daily_average': 0},
        'family': {'weekly_total': 0},
        'exercise': {'weekly_times': 0},
        'learning': {'daily_minutes': 0},
        'rest': {'daily_hours': 0}
    }
    
    # Calculate sleep average
    sleep_checkins = [c for c in checkins if c['metric_type'] == 'sleep_hours']
    if sleep_checkins:
        user_metrics['sleep']['average_hours'] = sum(c['value'] for c in sleep_checkins) / len(sleep_checkins)
    
    # Calculate exercise frequency
    exercise_checkins = [c for c in checkins if c['metric_type'] == 'exercise_minutes']
    user_metrics['exercise']['weekly_times'] = len(exercise_checkins)
    
    # Calculate family time
    family_checkins = [c for c in checkins if c['metric_type'] == 'family_time']
    if family_checkins:
        user_metrics['family']['weekly_total'] = sum(c['value'] for c in family_checkins)
    
    # Perform balance analysis
    balance_analysis = ai_analyzer.analyze_balance(user_metrics)
    
    # Format analytics report
    analytics_text = f"""
🔍 <b>ГЛУБОКАЯ АНАЛИТИКА</b>

📊 <b>Общий анализ:</b>
• Всего записей: {len(journal_entries)}
• Средняя ценность: {sum(e['value_score'] for e in journal_entries) / len(journal_entries) if journal_entries else 0:.1f}/10
• Высокоценных активностей: {len([e for e in journal_entries if e['category'] == 'high_value'])}

🚨 <b>КРИТИЧНЫЙ ДИСБАЛАНС:</b>
{chr(10).join(['• '+issue for issue in balance_analysis['critical_imbalances']]) if balance_analysis['critical_imbalances'] else 'Нет критических дисбалансов'}

📈 <b>КОРРЕЛЯЦИИ:</b>
{chr(10).join(['• '+corr for corr in balance_analysis['correlations']]) if balance_analysis['correlations'] else 'Корреляции не выявлены'}

💡 <b>СОВЕТЫ:</b>
{chr(10).join([f'{i+1}. {rec}' for i, rec in enumerate(balance_analysis['recommendations'][:3])])}

❓ <b>ВЕЧЕРНИЙ ВОПРОС:</b>
{balance_analysis['evening_reflection']}
    """
    
    return analytics_text


async def generate_values_mirror(user_id: int) -> str:
    """Generate values alignment mirror"""
    user_values = db.get_user_values(user_id)
    journal_entries = db.get_journal_entries(user_id, days=7)
    
    if not user_values:
        return "🔍 <b>ЗЕРКАЛО ЦЕННОСТЕЙ</b>\n\nВы пока не указали свои ценности. Добавьте их в настройках."
    
    # Perform values alignment analysis
    values_analysis = ai_analyzer.analyze_values_alignment(journal_entries, user_values)
    
    mirror_text = "🔍 <b>ЗЕРКАЛО ЦЕННОСТЕЙ</b>\n\n"
    
    for item in values_analysis['alignment_report']:
        alignment_status = "✅" if item['alignment_score'] >= item['importance'] * 0.7 else "⚠️" if item['alignment_score'] >= item['importance'] * 0.4 else "❌"
        mirror_text += f"{alignment_status} {item['value']}: важность {item['importance']}/10, соответствие {item['alignment_score']}/10\n"
    
    if values_analysis['misalignments']:
        mirror_text += f"\n❓ <b>ВОПРОС ДЛЯ РЕФЛЕКСИИ:</b>\n{values_analysis['reflection_questions'][0]}"
    
    return mirror_text


async def generate_balance_map(user_id: int) -> str:
    """Generate life balance radar map"""
    # Prepare metrics for balance map
    checkins = db.get_user_checkins(user_id, days=7)
    
    user_metrics = {
        'sleep': {'average_hours': 0},
        'work': {'daily_average': 0},
        'family': {'weekly_total': 0},
        'exercise': {'weekly_times': 0},
        'learning': {'daily_minutes': 0},
        'rest': {'daily_hours': 0}
    }
    
    # Calculate sleep average
    sleep_checkins = [c for c in checkins if c['metric_type'] == 'sleep_hours']
    if sleep_checkins:
        user_metrics['sleep']['average_hours'] = sum(c['value'] for c in sleep_checkins) / len(sleep_checkins)
    
    # Calculate exercise frequency
    exercise_checkins = [c for c in checkins if c['metric_type'] == 'exercise_minutes']
    user_metrics['exercise']['weekly_times'] = len(exercise_checkins)
    
    # Calculate family time
    family_checkins = [c for c in checkins if c['metric_type'] == 'family_time']
    if family_checkins:
        user_metrics['family']['weekly_total'] = sum(c['value'] for c in family_checkins)
    
    balance_radar = ai_analyzer.generate_balance_radar(user_metrics)
    
    return f"<pre>{balance_radar}</pre>"


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command with enhanced LifeOS AI features"""
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    
    # Initialize daily missions for new users
    # (existing functionality)
    
    welcome_message = f"""
🤖 <b>Добро пожаловать в LIFEOS AI!</b>

Ваша цифровая система управления жизнью с AI-аналитикой — как цифровой тренер, который помогает вам становиться лучше во всех важных аспектах жизни.

🎯 <b>ВОЗМОЖНОСТИ:</b>
• Отслеживание ключевых метрик по 5 категориям
• Ежедневный чек-ин с оценкой баланса
• AI-анализ дисбалансов и рекомендаций
• Система челленджей и геймификация
• Групповая аналитика и поддержка
• Зеркало ценностей и карта баланса

Выберите опцию для начала:
    """
    
    await message.answer(welcome_message, reply_markup=create_main_menu_keyboard())


@dp.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu"""
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\nВыберите опцию:",
        reply_markup=create_main_menu_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "dashboard")
async def show_dashboard(callback: CallbackQuery):
    """Show dashboard with user progress"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    dashboard_text = await generate_dashboard(user['id'])
    
    await callback.message.edit_text(
        dashboard_text,
        reply_markup=create_dashboard_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "checkin")
async def show_checkin(callback: CallbackQuery):
    """Show daily check-in form"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    checkin_text = await generate_checkin_form(user['id'])
    
    await callback.message.edit_text(
        checkin_text,
        reply_markup=create_checkin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("checkin_"))
async def handle_checkin_selection(callback: CallbackQuery):
    """Handle check-in selection"""
    checkin_type = callback.data.split("_")[1]
    
    prompts = {
        "sleep": "Введите оценку качества сна (1-10):",
        "exercise": "Введите время на спорт в минутах:",
        "goals": "Введите количество выполненных целей сегодня:",
        "family": "Введите время с семьей в часах:",
        "learning": "Введите время на обучение в минутах:"
    }
    
    await callback.message.edit_text(
        f"✏️ {prompts.get(checkin_type, 'Введите значение:')}",
        reply_markup=InlineKeyboardBuilder().button(
            text="🔙 Назад", callback_data="checkin"
        ).as_markup()
    )
    await callback.answer()


@dp.message(F.text.startswith("/sleep_rating"))
async def handle_sleep_rating(message: Message):
    """Handle sleep rating input"""
    try:
        rating = int(message.text.split()[1])
        if 1 <= rating <= 10:
            user = db.get_or_create_user(message.from_user.id, message.from_user.username)
            success = db.create_daily_checkin(user['id'], 'sleep_quality', rating)
            if success:
                await message.answer("✅ Оценка сна сохранена!")
            else:
                await message.answer("❌ Ошибка при сохранении оценки сна.")
        else:
            await message.answer("❌ Оценка должна быть от 1 до 10.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /sleep_rating 7")


@dp.message(F.text.startswith("/exercise_time"))
async def handle_exercise_time(message: Message):
    """Handle exercise time input"""
    try:
        minutes = int(message.text.split()[1])
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.create_daily_checkin(user['id'], 'exercise_minutes', minutes)
        if success:
            await message.answer("✅ Время на спорт сохранено!")
        else:
            await message.answer("❌ Ошибка при сохранении времени на спорт.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /exercise_time 45")


@dp.message(F.text.startswith("/family_time"))
async def handle_family_time(message: Message):
    """Handle family time input"""
    try:
        hours = float(message.text.split()[1])
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.create_daily_checkin(user['id'], 'family_time', hours)
        if success:
            await message.answer("✅ Время с семьей сохранено!")
        else:
            await message.answer("❌ Ошибка при сохранении времени с семьей.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /family_time 2.5")


@dp.callback_query(F.data == "full_checkin")
async def show_full_checkin(callback: CallbackQuery):
    """Show full check-in form with all metrics"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    
    full_checkin_text = """
📝 <b>ПОЛНЫЙ ЕЖЕДНЕВНЫЙ ЧЕК-ИН</b>

Введите значения для каждой метрики:

1. <b>Сон</b> - качество сна (1-10): <code>/sleep_rating X</code>
2. <b>Спорт</b> - время на физическую активность (мин): <code>/exercise_time X</code>
3. <b>Семья</b> - время с близкими (часы): <code>/family_time X</code>
4. <b>Работа</b> - время в состоянии потока (часы): <code>/focus_time X</code>
5. <b>Обучение</b> - время на развитие (мин): <code>/learning_time X</code>
6. <b>Питание</b> - качество питания (1-10): <code>/nutrition_rating X</code>
7. <b>Стресс</b> - уровень стресса (1-10): <code>/stress_level X</code>
8. <b>Энергия</b> - уровень энергии (1-10): <code>/energy_level X</code>
    """
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.button(text="🔄 Обновить", callback_data="full_checkin")
    
    await callback.message.edit_text(
        full_checkin_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.message(F.text.startswith("/focus_time"))
async def handle_focus_time(message: Message):
    """Handle focus time input"""
    try:
        hours = float(message.text.split()[1])
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.create_daily_checkin(user['id'], 'focus_hours', hours)
        if success:
            await message.answer("✅ Время в состоянии потока сохранено!")
        else:
            await message.answer("❌ Ошибка при сохранении времени потока.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /focus_time 2.5")


@dp.message(F.text.startswith("/learning_time"))
async def handle_learning_time(message: Message):
    """Handle learning time input"""
    try:
        minutes = int(message.text.split()[1])
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.create_daily_checkin(user['id'], 'learning_minutes', minutes)
        if success:
            await message.answer("✅ Время на обучение сохранено!")
        else:
            await message.answer("❌ Ошибка при сохранении времени на обучение.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /learning_time 30")


@dp.message(F.text.startswith("/nutrition_rating"))
async def handle_nutrition_rating(message: Message):
    """Handle nutrition rating input"""
    try:
        rating = int(message.text.split()[1])
        if 1 <= rating <= 10:
            user = db.get_or_create_user(message.from_user.id, message.from_user.username)
            success = db.create_daily_checkin(user['id'], 'nutrition_quality', rating)
            if success:
                await message.answer("✅ Оценка питания сохранена!")
            else:
                await message.answer("❌ Ошибка при сохранении оценки питания.")
        else:
            await message.answer("❌ Оценка должна быть от 1 до 10.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /nutrition_rating 7")


@dp.message(F.text.startswith("/stress_level"))
async def handle_stress_level(message: Message):
    """Handle stress level input"""
    try:
        level = int(message.text.split()[1])
        if 1 <= level <= 10:
            user = db.get_or_create_user(message.from_user.id, message.from_user.username)
            success = db.create_daily_checkin(user['id'], 'stress_level', level)
            if success:
                await message.answer("✅ Уровень стресса сохранен!")
            else:
                await message.answer("❌ Ошибка при сохранении уровня стресса.")
        else:
            await message.answer("❌ Уровень должен быть от 1 до 10.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /stress_level 4")


@dp.message(F.text.startswith("/energy_level"))
async def handle_energy_level(message: Message):
    """Handle energy level input"""
    try:
        level = int(message.text.split()[1])
        if 1 <= level <= 10:
            user = db.get_or_create_user(message.from_user.id, message.from_user.username)
            success = db.create_daily_checkin(user['id'], 'energy_level', level)
            if success:
                await message.answer("✅ Уровень энергии сохранен!")
            else:
                await message.answer("❌ Ошибка при сохранении уровня энергии.")
        else:
            await message.answer("❌ Уровень должен быть от 1 до 10.")
    except (ValueError, IndexError):
        await message.answer("❌ Пожалуйста, введите команду в формате: /energy_level 8")


@dp.callback_query(F.data == "analytics")
async def show_analytics(callback: CallbackQuery):
    """Show detailed analytics"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    analytics_text = await generate_analytics_report(user['id'])
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔄 Обновить", callback_data="analytics")
    keyboard.button(text="🔍 Зеркало ценностей", callback_data="values_mirror")
    keyboard.button(text="🗺️ Карта баланса", callback_data="balance_map")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await callback.message.edit_text(
        analytics_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "values_mirror")
async def show_values_mirror(callback: CallbackQuery):
    """Show values alignment mirror"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    mirror_text = await generate_values_mirror(user['id'])
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔄 Обновить", callback_data="values_mirror")
    keyboard.button(text="🎯 Управление ценностями", callback_data="manage_values")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await callback.message.edit_text(
        mirror_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "balance_map")
async def show_balance_map(callback: CallbackQuery):
    """Show life balance map"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    map_text = await generate_balance_map(user['id'])
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔄 Обновить", callback_data="balance_map")
    keyboard.button(text="🔍 Подробная аналитика", callback_data="analytics")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await callback.message.edit_text(
        f"🗺️ <b>КАРТА ЖИЗНЕННОГО БАЛАНСА</b>\n\n{map_text}",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "challenges")
async def show_challenges(callback: CallbackQuery):
    """Show challenges section"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    challenges_text = await generate_challenges_list(user['id'])
    
    await callback.message.edit_text(
        challenges_text,
        reply_markup=create_challenges_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "groups")
async def show_groups(callback: CallbackQuery):
    """Show groups section"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    
    # Get user's groups
    user_groups = db.get_user_groups(user['id'])
    
    groups_text = "👥 <b>МОИ ГРУППЫ</b>\n\n"
    if user_groups:
        for group in user_groups:
            groups_text += f"• {group['group_name']} ({group['group_type']}) - {group['role']}\n"
    else:
        groups_text += "Вы пока не состоите ни в одной группе."
    
    await callback.message.edit_text(
        groups_text,
        reply_markup=create_groups_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    """Show settings section"""
    await callback.message.edit_text(
        "⚙️ <b>НАСТРОЙКИ</b>\n\nВыберите параметр для настройки:",
        reply_markup=create_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "manage_values")
async def manage_values(callback: CallbackQuery):
    """Manage user values"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    user_values = db.get_user_values(user['id'])
    
    values_text = "🎯 <b>УПРАВЛЕНИЕ ЦЕННОСТЯМИ</b>\n\n"
    if user_values:
        for value in user_values:
            values_text += f"• {value['value_name']} - важность: {value['importance_level']}/10\n"
    else:
        values_text += "Пока не указаны ваши ценности.\n\n"
        values_text += "Чтобы добавить ценность, введите: /add_value НАЗВАНИЕ_ЦЕННОСТИ УРОВЕНЬ_ВАЖНОСТИ (1-10)"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔄 Обновить", callback_data="manage_values")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    
    await callback.message.edit_text(
        values_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.message(F.text.startswith("/add_value"))
async def add_user_value(message: Message):
    """Add a user value"""
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ Пожалуйста, используйте формат: /add_value НАЗВАНИЕ_ЦЕННОСТИ УРОВЕНЬ_ВАЖНОСТИ (1-10)")
            return
        
        value_name = " ".join(parts[1:-1])
        importance_level = int(parts[-1])
        
        if not 1 <= importance_level <= 10:
            await message.answer("❌ Уровень важности должен быть от 1 до 10.")
            return
        
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.set_user_value(user['id'], value_name, importance_level)
        
        if success:
            await message.answer(f"✅ Ценность '{value_name}' добавлена с уровнем важности {importance_level}!")
        else:
            await message.answer("❌ Ошибка при добавлении ценности.")
            
    except ValueError:
        await message.answer("❌ Пожалуйста, укажите числовой уровень важности (1-10).")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.callback_query(F.data == "manage_goals")
async def manage_goals(callback: CallbackQuery):
    """Manage user goals"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    user_goals = db.get_user_goals(user['id'])
    
    goals_text = "📊 <b>УПРАВЛЕНИЕ ЦЕЛЯМИ</b>\n\n"
    if user_goals:
        for goal in user_goals:
            progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
            goals_text += f"• {goal['goal_name']} - {goal['current_value']}/{goal['target_value']} {goal['unit']} ({progress:.1f}%)\n"
    else:
        goals_text += "Пока не установлены цели.\n\n"
        goals_text += "Чтобы добавить цель, введите: /add_goal НАЗВАНИЕ_ЦЕЛИ КАТЕГОРИЯ ТАРГЕТ ЕДИНИЦА_ИЗМЕРЕНИЯ"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔄 Обновить", callback_data="manage_goals")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    
    await callback.message.edit_text(
        goals_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.message(F.text.startswith("/add_goal"))
async def add_user_goal(message: Message):
    """Add a user goal"""
    try:
        parts = message.text.split()
        if len(parts) < 5:
            await message.answer("❌ Пожалуйста, используйте формат: /add_goal НАЗВАНИЕ_ЦЕЛИ КАТЕГОРИЯ ТАРГЕТ ЕДИНИЦА_ИЗМЕРЕНИЯ")
            return
        
        goal_name = " ".join(parts[1:2])  # Just take the first word as name for now
        category = parts[2]
        target_value = float(parts[3])
        unit = parts[4]
        
        user = db.get_or_create_user(message.from_user.id, message.from_user.username)
        success = db.create_goal(user['id'], goal_name, category, target_value, unit)
        
        if success:
            await message.answer(f"✅ Цель '{goal_name}' добавлена! Категория: {category}, цель: {target_value} {unit}")
        else:
            await message.answer("❌ Ошибка при добавлении цели.")
            
    except ValueError:
        await message.answer("❌ Пожалуйста, укажите числовой целевой показатель.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.callback_query(F.data == "refresh_dashboard")
async def refresh_dashboard(callback: CallbackQuery):
    """Refresh dashboard data"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    dashboard_text = await generate_dashboard(user['id'])
    
    await callback.message.edit_text(
        dashboard_text,
        reply_markup=create_dashboard_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("📊 Дашборд обновлен!")


async def main():
    """Main function to run the LifeOS AI bot"""
    logger.info("Запуск бота LifeOS AI...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())