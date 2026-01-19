import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "lifeos_guardian.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                personal_goals TEXT  -- JSON string for personal goals
            )
        ''')
        
        # Daily missions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mission_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_duration INTEGER,  -- in minutes
                created_at DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Timers table (active and completed timers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mission_id INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER,
                is_active BOOLEAN DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (mission_id) REFERENCES daily_missions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, telegram_id: int, username: str = None) -> Dict:
        """Get existing user or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''SELECT id, telegram_id, username FROM users WHERE telegram_id = ?''',
                (telegram_id,)
            )
            user = cursor.fetchone()
            
            if user:
                return {"id": user[0], "telegram_id": user[1], "username": user[2]}
            
            # Create new user
            cursor.execute(
                '''INSERT INTO users (telegram_id, username) VALUES (?, ?)''',
                (telegram_id, username)
            )
            conn.commit()
            
            # Return newly created user
            cursor.execute(
                '''SELECT id, telegram_id, username FROM users WHERE telegram_id = ?''',
                (telegram_id,)
            )
            new_user = cursor.fetchone()
            return {"id": new_user[0], "telegram_id": new_user[1], "username": new_user[2]}
        
        finally:
            conn.close()
    
    def create_daily_missions(self, user_id: int, missions: List[Dict]) -> bool:
        """Create daily missions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete existing missions for today
            today = datetime.now().date()
            cursor.execute(
                '''DELETE FROM daily_missions WHERE user_id = ? AND created_at = ?''',
                (user_id, today.isoformat())
            )
            
            # Insert new missions
            for mission in missions:
                cursor.execute('''
                    INSERT INTO daily_missions 
                    (user_id, mission_type, title, description, target_duration, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    mission.get('type'),
                    mission.get('title'),
                    mission.get('description'),
                    mission.get('target_duration'),
                    today.isoformat()
                ))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Ошибка при создании ежедневных миссий: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_todays_missions(self, user_id: int) -> List[Dict]:
        """Get today's missions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT dm.id, dm.mission_type, dm.title, dm.description, dm.target_duration, t.is_active, t.duration_minutes
            FROM daily_missions dm
            LEFT JOIN timers t ON dm.id = t.mission_id AND t.completed = 0
            WHERE dm.user_id = ? AND dm.created_at = ?
            ORDER BY dm.id
        ''', (user_id, today.isoformat()))
        
        missions = []
        for row in cursor.fetchall():
            missions.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'description': row[3],
                'target_duration': row[4],
                'is_active': bool(row[5]),
                'duration_minutes': row[6]
            })
        
        conn.close()
        return missions
    
    def start_timer(self, user_id: int, mission_id: int) -> bool:
        """Start a timer for a specific mission"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if there's already an active timer for this mission
            cursor.execute('''
                SELECT id FROM timers 
                WHERE user_id = ? AND mission_id = ? AND is_active = 1
            ''', (user_id, mission_id))
            
            existing_timer = cursor.fetchone()
            if existing_timer:
                return False  # Timer already active
            
            # Create new timer
            cursor.execute('''
                INSERT INTO timers (user_id, mission_id, start_time, is_active)
                VALUES (?, ?, ?, 1)
            ''', (user_id, mission_id, datetime.now()))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Ошибка при запуске таймера: {e}")
            return False
        
        finally:
            conn.close()
    
    def complete_timer(self, timer_id: int) -> bool:
        """Complete an active timer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get the timer to calculate duration
            cursor.execute('''
                SELECT start_time FROM timers 
                WHERE id = ? AND is_active = 1
            ''', (timer_id,))
            
            timer = cursor.fetchone()
            if not timer:
                return False
            
            start_time = datetime.fromisoformat(timer[0])
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds() / 60)  # Duration in minutes
            
            # Update the timer
            cursor.execute('''
                UPDATE timers 
                SET end_time = ?, duration_minutes = ?, is_active = 0, completed = 1
                WHERE id = ?
            ''', (end_time, duration, timer_id))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Ошибка при завершении таймера: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_active_timer(self, user_id: int) -> Optional[Dict]:
        """Get the currently active timer for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.start_time, t.mission_id, dm.title, dm.mission_type
            FROM timers t
            JOIN daily_missions dm ON t.mission_id = dm.id
            WHERE t.user_id = ? AND t.is_active = 1
        ''', (user_id,))
        
        timer = cursor.fetchone()
        if timer:
            start_time = datetime.fromisoformat(timer[1])
            elapsed = int((datetime.now() - start_time).total_seconds() / 60)
            return {
                'id': timer[0],
                'start_time': start_time,
                'mission_id': timer[2],
                'mission_title': timer[3],
                'mission_type': timer[4],
                'elapsed_minutes': elapsed
            }
        
        conn.close()
        return None
    
    def get_weekly_analytics(self, user_id: int) -> Dict:
        """Get weekly analytics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date range for the week (Monday to Sunday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        
        # Get completed timers for the week
        cursor.execute('''
            SELECT dm.mission_type, SUM(t.duration_minutes), COUNT(*)
            FROM timers t
            JOIN daily_missions dm ON t.mission_id = dm.id
            WHERE t.user_id = ? AND t.completed = 1 
            AND t.end_time >= ? AND t.end_time <= ?
            GROUP BY dm.mission_type
        ''', (user_id, start_of_week.isoformat(), end_of_week.isoformat()))
        
        weekly_data = {}
        for row in cursor.fetchall():
            weekly_data[row[0]] = {
                'total_minutes': row[1] or 0,
                'completed_sessions': row[2]
            }
        
        # Get total sessions planned for the week
        cursor.execute('''
            SELECT dm.mission_type, COUNT(*)
            FROM daily_missions dm
            WHERE dm.user_id = ? AND dm.created_at >= ? AND dm.created_at <= ?
            GROUP BY dm.mission_type
        ''', (user_id, start_of_week.date().isoformat(), end_of_week.date().isoformat()))
        
        planned_data = {}
        for row in cursor.fetchall():
            planned_data[row[0]] = row[1]
        
        conn.close()
        
        # Combine data
        analytics = {}
        all_types = set(weekly_data.keys()) | set(planned_data.keys())
        
        for mission_type in all_types:
            completed_data = weekly_data.get(mission_type, {'total_minutes': 0, 'completed_sessions': 0})
            planned_count = planned_data.get(mission_type, 0)
            
            analytics[mission_type] = {
                'total_minutes': completed_data['total_minutes'],
                'completed_sessions': completed_data['completed_sessions'],
                'planned_sessions': planned_count,
                'completion_rate': round((completed_data['completed_sessions'] / planned_count * 100) if planned_count > 0 else 0, 2)
            }
        
        return analytics


# Global database instance
db = DatabaseManager()