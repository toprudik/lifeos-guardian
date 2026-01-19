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
        
        # Journal entries table for AI analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity TEXT NOT NULL,
                duration INTEGER,  -- in minutes
                ai_analysis TEXT,
                value_score INTEGER,  -- 1-10 scale
                category TEXT,  -- high_value, medium_value, low_value, negative_value
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Goals table for tracking user goals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal_name TEXT NOT NULL,
                category TEXT NOT NULL,  -- effectiveness, health, development, relationships, values
                target_value REAL,
                current_value REAL DEFAULT 0,
                unit TEXT,  -- percentage, hours, minutes, etc.
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Daily check-ins for various metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                metric_type TEXT NOT NULL,  -- sleep_quality, stress_level, productivity, etc.
                value REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date, metric_type)
            )
        ''')
        
        # Challenges table for gamification
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                target_duration INTEGER,  -- in days
                current_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Achievements table for gamification
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points INTEGER DEFAULT 10,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User values and preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                value_name TEXT NOT NULL,
                importance_level INTEGER,  -- 1-10 scale
                alignment_score INTEGER,  -- how well actions align with values (1-10)
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Group/family connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                group_type TEXT,  -- family, team, friends
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Group members
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(group_id, user_id)
            )
        ''')
        
        # Group activities/challenges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                description TEXT,
                assigned_to INTEGER,  -- user_id
                completed_by INTEGER,  -- user_id who completed
                is_completed BOOLEAN DEFAULT 0,
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id)
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
            print(f"Ошибка создания ежедневных миссий: {e}")
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
            print(f"Ошибка запуска таймера: {e}")
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
            print(f"Ошибка завершения таймера: {e}")
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

    def add_journal_entry(self, user_id: int, activity: str, duration: int = 0, ai_analysis: str = "", value_score: int = 5, category: str = "unknown") -> bool:
        """Add a journal entry with AI analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO journal_entries 
                (user_id, activity, duration, ai_analysis, value_score, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, activity, duration, ai_analysis, value_score, category))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Ошибка добавления записи в журнал: {e}")
            return False
        
        finally:
            conn.close()

    def get_journal_entries(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get journal entries for a user for the specified number of days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT activity, duration, ai_analysis, value_score, category, timestamp
            FROM journal_entries
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (user_id, from_date.isoformat()))
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'activity': row[0],
                'duration': row[1],
                'ai_analysis': row[2],
                'value_score': row[3],
                'category': row[4],
                'timestamp': row[5]
            })
        
        conn.close()
        return entries

    def get_environment_analysis(self, user_id: int) -> Dict:
        """Analyze user's environment based on journal entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get entries for the last 7 days
        from_date = datetime.now() - timedelta(days=7)
        
        cursor.execute('''
            SELECT activity, category, value_score
            FROM journal_entries
            WHERE user_id = ? AND timestamp >= ?
        ''', (user_id, from_date.isoformat()))
        
        entries = cursor.fetchall()
        conn.close()
        
        # Analyze environment
        positive_influences = []
        neutral_influences = []
        toxic_influences = []
        
        activity_scores = {}
        
        for activity, category, score in entries:
            if activity not in activity_scores:
                activity_scores[activity] = {'count': 0, 'total_score': 0, 'category': category}
            
            activity_scores[activity]['count'] += 1
            activity_scores[activity]['total_score'] += score
        
        # Categorize influences based on average scores
        for activity, data in activity_scores.items():
            avg_score = data['total_score'] / data['count']
            
            if avg_score >= 7:
                positive_influences.append({'activity': activity, 'score': round(avg_score, 2), 'count': data['count']})
            elif avg_score >= 4:
                neutral_influences.append({'activity': activity, 'score': round(avg_score, 2), 'count': data['count']})
            else:
                toxic_influences.append({'activity': activity, 'score': round(avg_score, 2), 'count': data['count']})
        
        return {
            'positive_influences': sorted(positive_influences, key=lambda x: x['score'], reverse=True)[:5],
            'neutral_influences': sorted(neutral_influences, key=lambda x: x['score'], reverse=True)[:5],
            'toxic_influences': sorted(toxic_influences, key=lambda x: x['score'])[:5]
        }

    def set_user_value(self, user_id: int, value_name: str, importance_level: int, notes: str = "") -> bool:
        """Set or update a user value with importance level"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_values 
                (user_id, value_name, importance_level, notes, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, value_name, importance_level, notes))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении ценности пользователя: {e}")
            return False
        finally:
            conn.close()

    def get_user_values(self, user_id: int) -> List[Dict]:
        """Get user's values and their importance levels"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT value_name, importance_level, alignment_score, notes, updated_at
            FROM user_values
            WHERE user_id = ?
            ORDER BY importance_level DESC
        ''', (user_id,))

        values = []
        for row in cursor.fetchall():
            values.append({
                'value_name': row[0],
                'importance_level': row[1],
                'alignment_score': row[2],
                'notes': row[3],
                'updated_at': row[4]
            })

        conn.close()
        return values

    def create_goal(self, user_id: int, goal_name: str, category: str, target_value: float, unit: str,
                    end_date: str = None) -> bool:
        """Create a new goal for the user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO goals 
                (user_id, goal_name, category, target_value, unit, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, CURRENT_DATE, ?)
            ''', (user_id, goal_name, category, target_value, unit, end_date))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании цели: {e}")
            return False
        finally:
            conn.close()

    def get_user_goals(self, user_id: int) -> List[Dict]:
        """Get all active goals for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, goal_name, category, target_value, current_value, unit, start_date, end_date
            FROM goals
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        ''', (user_id,))

        goals = []
        for row in cursor.fetchall():
            goals.append({
                'id': row[0],
                'goal_name': row[1],
                'category': row[2],
                'target_value': row[3],
                'current_value': row[4],
                'unit': row[5],
                'start_date': row[6],
                'end_date': row[7]
            })

        conn.close()
        return goals

    def update_goal_progress(self, goal_id: int, new_value: float) -> bool:
        """Update progress for a specific goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE goals
                SET current_value = ?
                WHERE id = ?
            ''', (new_value, goal_id))

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении прогресса цели: {e}")
            return False
        finally:
            conn.close()

    def create_daily_checkin(self, user_id: int, metric_type: str, value: float, notes: str = "") -> bool:
        """Create a daily check-in for a specific metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_checkins
                (user_id, date, metric_type, value, notes)
                VALUES (?, CURRENT_DATE, ?, ?, ?)
            ''', (user_id, metric_type, value, notes))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании ежедневной проверки: {e}")
            return False
        finally:
            conn.close()

    def get_user_checkins(self, user_id: int, metric_type: str = None, days: int = 7) -> List[Dict]:
        """Get user's check-ins for a specific metric type or all metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        from_date = datetime.now() - timedelta(days=days)

        if metric_type:
            cursor.execute('''
                SELECT date, metric_type, value, notes, created_at
                FROM daily_checkins
                WHERE user_id = ? AND metric_type = ? AND date >= ?
                ORDER BY date DESC
            ''', (user_id, metric_type, from_date.date().isoformat()))
        else:
            cursor.execute('''
                SELECT date, metric_type, value, notes, created_at
                FROM daily_checkins
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC, metric_type
            ''', (user_id, from_date.date().isoformat()))

        checkins = []
        for row in cursor.fetchall():
            checkins.append({
                'date': row[0],
                'metric_type': row[1],
                'value': row[2],
                'notes': row[3],
                'created_at': row[4]
            })

        conn.close()
        return checkins

    def create_challenge(self, user_id: int, challenge_name: str, category: str, description: str,
                        target_duration: int) -> bool:
        """Create a new challenge for the user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO challenges
                (user_id, challenge_name, category, description, target_duration, start_date)
                VALUES (?, ?, ?, ?, ?, CURRENT_DATE)
            ''', (user_id, challenge_name, category, description, target_duration))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании челленджа: {e}")
            return False
        finally:
            conn.close()

    def get_user_challenges(self, user_id: int) -> List[Dict]:
        """Get all active challenges for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, challenge_name, category, description, target_duration, current_streak, best_streak, start_date
            FROM challenges
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        ''', (user_id,))

        challenges = []
        for row in cursor.fetchall():
            challenges.append({
                'id': row[0],
                'challenge_name': row[1],
                'category': row[2],
                'description': row[3],
                'target_duration': row[4],
                'current_streak': row[5],
                'best_streak': row[6],
                'start_date': row[7]
            })

        conn.close()
        return challenges

    def update_challenge_streak(self, challenge_id: int, increment: bool = True) -> bool:
        """Update streak for a challenge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if increment:
                cursor.execute('''
                    UPDATE challenges
                    SET current_streak = current_streak + 1,
                        best_streak = MAX(best_streak, current_streak + 1)
                    WHERE id = ?
                ''', (challenge_id,))
            else:
                cursor.execute('''
                    UPDATE challenges
                    SET current_streak = 0
                    WHERE id = ?
                ''', (challenge_id,))

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении серии челленджа: {e}")
            return False
        finally:
            conn.close()

    def create_group(self, group_name: str, group_type: str, creator_user_id: int) -> Optional[int]:
        """Create a new group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO groups
                (group_name, group_type, created_by)
                VALUES (?, ?, ?)
            ''', (group_name, group_type, creator_user_id))

            group_id = cursor.lastrowid
            conn.commit()
            
            # Add creator as admin member
            cursor.execute('''
                INSERT INTO group_members
                (group_id, user_id, role)
                VALUES (?, ?, 'admin')
            ''', (group_id, creator_user_id))
            
            conn.commit()
            return group_id
        except Exception as e:
            print(f"Ошибка при создании группы: {e}")
            return None
        finally:
            conn.close()

    def add_user_to_group(self, group_id: int, user_id: int, role: str = 'member') -> bool:
        """Add a user to a group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO group_members
                (group_id, user_id, role)
                VALUES (?, ?, ?)
            ''', (group_id, user_id, role))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя в группу: {e}")
            return False
        finally:
            conn.close()

    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Get all groups a user belongs to"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT g.id, g.group_name, g.group_type, gm.role
            FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = ?
            ORDER BY g.created_at DESC
        ''', (user_id,))

        groups = []
        for row in cursor.fetchall():
            groups.append({
                'id': row[0],
                'group_name': row[1],
                'group_type': row[2],
                'role': row[3]
            })

        conn.close()
        return groups

    def create_group_activity(self, group_id: int, activity_name: str, description: str = "",
                              assigned_to: int = None, deadline: str = None) -> bool:
        """Create a group activity/task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO group_activities
                (group_id, activity_name, description, assigned_to, deadline)
                VALUES (?, ?, ?, ?, ?)
            ''', (group_id, activity_name, description, assigned_to, deadline))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании групповой активности: {e}")
            return False
        finally:
            conn.close()

    def get_group_activities(self, group_id: int) -> List[Dict]:
        """Get all activities for a group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, activity_name, description, assigned_to, is_completed, deadline, created_at
            FROM group_activities
            WHERE group_id = ?
            ORDER BY created_at DESC
        ''', (group_id,))

        activities = []
        for row in cursor.fetchall():
            activities.append({
                'id': row[0],
                'activity_name': row[1],
                'description': row[2],
                'assigned_to': row[3],
                'is_completed': bool(row[4]),
                'deadline': row[5],
                'created_at': row[6]
            })

        conn.close()
        return activities


# Global database instance
db = DatabaseManager()