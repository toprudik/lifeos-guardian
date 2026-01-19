import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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
    """Create main menu keyboard with emoji buttons"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="📊 Дашборд", callback_data="dashboard")
    keyboard.button(text="🎯 Миссии дня", callback_data="missions")
    keyboard.button(text="📈 Недельная аналитика", callback_data="analytics")
    keyboard.button(text="📖 Научные факты", callback_data="science_facts")
    
    keyboard.adjust(2)  # 2 buttons per row
    return keyboard.as_markup()


def create_missions_keyboard(missions: List[Dict]):
    """Create keyboard for today's missions"""
    keyboard = InlineKeyboardBuilder()
    
    for mission in missions:
        status = "⏱️ Активен" if mission.get('is_active') else "▶️ Старт"
        button_text = f"{MISSION_EMOJIS.get(mission['type'], '📝')} {mission['title']} - {status}"
        
        if mission.get('is_active'):
            # Show stop button for active mission
            keyboard.button(
                text=f"⏹️ Стоп {MISSION_EMOJIS.get(mission['type'], '📝')}", 
                callback_data=f"stop_timer_{mission['id']}"
            )
        else:
            # Show start button for inactive mission
            keyboard.button(
                text=f"▶️ Старт {MISSION_EMOJIS.get(mission['type'], '📝')}", 
                callback_data=f"start_timer_{mission['id']}"
            )
    
    keyboard.button(text="🔙 Назад в меню", callback_data="main_menu")
    keyboard.adjust(1)  # 1 button per row
    return keyboard.as_markup()


def create_science_facts_keyboard():
    """Create keyboard for science facts"""
    keyboard = InlineKeyboardBuilder()
    
    for category, data in SCIENCE_DATA.items():
        emoji = MISSION_EMOJIS.get(category, '❓')
        keyboard.button(
            text=f"{emoji} {category.replace('_', ' ').title()} Facts", 
            callback_data=f"science_{category}"
        )
    
    keyboard.button(text="🔙 Назад в меню", callback_data="main_menu")
    keyboard.adjust(1)
    return keyboard.as_markup()


async def generate_dashboard(user_id: int) -> str:
    """Generate dashboard with user progress"""
    # Get today's missions
    missions = db.get_todays_missions(user_id)
    
    # Get active timer if any
    active_timer = db.get_active_timer(user_id)
    
    # Get weekly analytics
    weekly_analytics = db.get_weekly_analytics(user_id)
    
    dashboard = "🏠 <b>ЛИФЕОС СТРАЖ ДАШБОРД</b>\n\n"
    
    # Today's missions
    dashboard += "<b>Миссии сегодня:</b>\n"
    if missions:
        for mission in missions:
            status = "✅ Активна" if mission.get('is_active') else "⏳ В ожидании"
            emoji = MISSION_EMOJIS.get(mission['type'], '📝')
            dashboard += f"• {emoji} {mission['title']} - {status}\n"
    else:
        dashboard += "Сегодня нет миссий. Добавьте некоторые!\n"
    
    # Active timer info
    if active_timer:
        dashboard += f"\n<b>Активный таймер:</b>\n"
        dashboard += f"⏱️ {active_timer['mission_title']} - {active_timer['elapsed_minutes']} мин прошло\n"
    
    # Weekly analytics summary
    dashboard += f"\n<b>Еженедельный прогресс:</b>\n"
    if weekly_analytics:
        for mission_type, data in weekly_analytics.items():
            emoji = MISSION_EMOJIS.get(mission_type, '❓')
            completion_rate = data.get('completion_rate', 0)
            total_minutes = data.get('total_minutes', 0)
            dashboard += f"• {emoji} {mission_type.title()}: {completion_rate}% ({total_minutes} min)\n"
    else:
        dashboard += "Данные пока не доступны.\n"
    
    dashboard += f"\n💡 <i>{SCIENCE_DATA['sleep']['motivational_quote']}</i>"
    
    return dashboard


async def generate_missions_list(user_id: int) -> str:
    """Generate list of today's missions"""
    missions = db.get_todays_missions(user_id)
    
    if not missions:
        return "🎯 <b>Сегодня нет миссий!</b>\n\nВаш AI-страж может создать миссии, чтобы помочь вам оптимизировать вашу жизнь."
    
    missions_text = "🎯 <b>Миссии дня:</b>\n\n"
    for i, mission in enumerate(missions, 1):
        status = "⏱️ Активна" if mission.get('is_active') else "⏳ В ожидании"
        emoji = MISSION_EMOJIS.get(mission['type'], '📝')
        duration = mission.get('target_duration', 0)
        
        missions_text += f"<b>{i}. {emoji} {mission['title']}</b>\n"
        missions_text += f"   • Тип: {mission['type'].replace('_', ' ').title()}\n"
        missions_text += f"   • Цель: {duration} мин\n"
        missions_text += f"   • Статус: {status}\n"
        if mission.get('duration_minutes'):
            missions_text += f"   • Текущее: {mission['duration_minutes']} мин\n"
        missions_text += "\n"
    
    return missions_text


async def generate_weekly_analytics(user_id: int) -> str:
    """Generate weekly analytics report"""
    analytics = db.get_weekly_analytics(user_id)
    
    if not analytics:
        return "📈 <b>Недельная аналитика</b>\n\nДанные пока не доступны. Выполните несколько миссий, чтобы увидеть свой прогресс!"
    
    analytics_text = "📈 <b>Отчет по недельной аналитике</b>\n\n"
    
    for mission_type, data in analytics.items():
        emoji = MISSION_EMOJIS.get(mission_type, '❓')
        total_minutes = data.get('total_minutes', 0)
        completed_sessions = data.get('completed_sessions', 0)
        planned_sessions = data.get('planned_sessions', 0)
        completion_rate = data.get('completion_rate', 0)
        
        analytics_text += f"<b>{emoji} {mission_type.replace('_', ' ').title()}</b>\n"
        analytics_text += f"   • Общее время: {total_minutes} мин\n"
        analytics_text += f"   • Выполнено: {completed_sessions}/{planned_sessions} сессий\n"
        analytics_text += f"   • Процент выполнения: {completion_rate}%\n\n"
    
    return analytics_text


async def generate_science_fact(category: str) -> str:
    """Generate science fact for a specific category"""
    if category not in SCIENCE_DATA:
        return f"❌ No science data found for {category}"
    
    data = SCIENCE_DATA[category]
    emoji = MISSION_EMOJIS.get(category, '❓')
    
    fact_text = f"{emoji} <b>Научные данные: {category.replace('_', ' ').title()}</b>\n\n"
    
    if 'optimal_hours' in data:
        fact_text += f"🔬 <b>Оптимальное количество:</b> {data['optimal_hours']} hours\n"
    elif 'daily_minutes' in data:
        fact_text += f"🔬 <b>Рекомендация в день:</b> {data['daily_minutes']} minutes\n"
    elif 'daily_liters' in data:
        fact_text += f"🔬 <b>Рекомендация в день:</b> {data['daily_liters']} liters\n"
    
    if 'benefits' in data:
        fact_text += f"\n🌟 <b>Основные преимущества:</b>\n"
        for benefit in data['benefits']:
            fact_text += f"   • {benefit}\n"
    
    if 'motivational_quote' in data:
        fact_text += f"\n💡 <i>{data['motivational_quote']}</i>"
    
    return fact_text


async def initialize_daily_missions(user_id: int):
    """Initialize daily missions based on personal goals"""
    user_goals = PERSONAL_GOALS.get('toprudik', {})
    
    missions = []
    
    # Sleep mission
    if 'sleep_target' in user_goals:
        missions.append({
            'type': 'sleep',
            'title': MISSION_TITLES['sleep'],
            'description': MISSION_DESCRIPTIONS['sleep'],
            'target_duration': user_goals['sleep_target'] * 60  # Convert hours to minutes
        })
    
    # Exercise mission
    if 'exercise_target' in user_goals:
        missions.append({
            'type': 'exercise',
            'title': MISSION_TITLES['exercise'],
            'description': MISSION_DESCRIPTIONS['exercise'],
            'target_duration': user_goals['exercise_target']
        })
    
    # Family time mission
    if 'family_time_target' in user_goals:
        missions.append({
            'type': 'family',
            'title': MISSION_TITLES['family'],
            'description': MISSION_DESCRIPTIONS['family'],
            'target_duration': user_goals['family_time_target'] * 60  # Convert hours to minutes
        })
    
    # Deep work mission
    if 'deep_work_target' in user_goals:
        missions.append({
            'type': 'deep_work',
            'title': MISSION_TITLES['deep_work'],
            'description': MISSION_DESCRIPTIONS['deep_work'],
            'target_duration': user_goals['deep_work_target']
        })
    
    # Hydration mission
    if 'hydration_target' in user_goals:
        missions.append({
            'type': 'hydration',
            'title': MISSION_TITLES['hydration'],
            'description': MISSION_DESCRIPTIONS['hydration'],
            'target_duration': int(user_goals['hydration_target'] * 1000 / 250)  # Convert liters to glasses (assuming 250ml per glass)
        })
    
    db.create_daily_missions(user_id, missions)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    
    # Initialize daily missions for new users
    initialize_daily_missions(user['id'])
    
    welcome_message = (
        f"🤖 <b>Добро пожаловать в ЛИФЕОС СТРАЖ!</b>\n\n"
        f"Ваш персональный AI-ассистент для оптимизации жизни на основе научных "
        f"исследований из Mayo Clinic, Гарвардского университета и Стэнфорда.\n\n"
        f"🎯 Отслеживайте свои ежедневные миссии\n"
        f"📊 Мониторьте свой недельный прогресс\n"
        f"🔬 Изучайте научно обоснованные инсайты\n\n"
        f"Выберите один из вариантов ниже, чтобы начать:"
    )
    
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
        reply_markup=create_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "missions")
async def show_missions(callback: CallbackQuery):
    """Show today's missions"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    missions_text = await generate_missions_list(user['id'])
    
    # Get missions to create appropriate keyboard
    missions = db.get_todays_missions(user['id'])
    
    await callback.message.edit_text(
        missions_text,
        reply_markup=create_missions_keyboard(missions),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("start_timer_"))
async def start_timer(callback: CallbackQuery):
    """Start a timer for a mission"""
    mission_id = int(callback.data.split("_")[2])
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    
    success = db.start_timer(user['id'], mission_id)
    
    if success:
        await callback.answer("✅ Таймер успешно запущен!", show_alert=True)
    else:
        await callback.answer("⚠️ Таймер уже активен для этой миссии!", show_alert=True)
    
    # Refresh missions display
    missions_text = await generate_missions_list(user['id'])
    missions = db.get_todays_missions(user['id'])
    
    await callback.message.edit_text(
        missions_text,
        reply_markup=create_missions_keyboard(missions),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("stop_timer_"))
async def stop_timer(callback: CallbackQuery):
    """Stop an active timer"""
    timer_id = int(callback.data.split("_")[2])
    
    success = db.complete_timer(timer_id)
    
    if success:
        await callback.answer("✅ Таймер остановлен и записан!", show_alert=True)
    else:
        await callback.answer("⚠️ Не удалось остановить таймер. Уже завершен или недействителен.", show_alert=True)
    
    # Refresh missions display
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    missions_text = await generate_missions_list(user['id'])
    missions = db.get_todays_missions(user['id'])
    
    await callback.message.edit_text(
        missions_text,
        reply_markup=create_missions_keyboard(missions),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "analytics")
async def show_analytics(callback: CallbackQuery):
    """Show weekly analytics"""
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    analytics_text = await generate_weekly_analytics(user['id'])
    
    await callback.message.edit_text(
        analytics_text,
        reply_markup=create_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "science_facts")
async def show_science_facts(callback: CallbackQuery):
    """Show science facts menu"""
    await callback.message.edit_text(
        "🔬 <b>Научно обоснованные выводы</b>\n\n"
        "Выберите категорию, чтобы узнать рекомендации, основанные на доказательствах:",
        reply_markup=create_science_facts_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("science_"))
async def show_specific_science_fact(callback: CallbackQuery):
    """Show specific science fact"""
    category = callback.data.split("_", 1)[1]
    fact_text = await generate_science_fact(category)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Назад к научным фактам", callback_data="science_facts")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        fact_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


async def main():
    """Main function to run the bot"""
    logger.info("Запуск бота LifeOS Guardian...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())