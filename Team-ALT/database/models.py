# database/models.py
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib
import json

class DatabaseManager:
    def __init__(self, db_path: str = "database/users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    height REAL,
                    current_weight REAL,
                    goal_weight REAL,
                    age INTEGER,
                    fitness_level TEXT,
                    goals TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Workouts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    exercise_type TEXT NOT NULL,
                    duration INTEGER,
                    reps INTEGER,
                    sets INTEGER,
                    calories_burned REAL,
                    form_score REAL,
                    notes TEXT,
                    workout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User metrics table (for tracking progress over time)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    body_fat_percentage REAL,
                    muscle_mass REAL,
                    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Chat history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()

class User:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, username: str, email: str, password: str, name: str,
                   height: Optional[float] = None, current_weight: Optional[float] = None,
                   goal_weight: Optional[float] = None, age: Optional[int] = None,
                   fitness_level: Optional[str] = None, goals: Optional[str] = None) -> bool:
        """Create a new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, name, height, 
                                     current_weight, goal_weight, age, fitness_level, goals)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, name, height, current_weight,
                      goal_weight, age, fitness_level, goals))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, name, height, current_weight, 
                       goal_weight, age, fitness_level, goals
                FROM users WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'name': result[3],
                    'height': result[4],
                    'current_weight': result[5],
                    'goal_weight': result[6],
                    'age': result[7],
                    'fitness_level': result[8],
                    'goals': result[9]
                }
            return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile information"""
        if not kwargs:
            return False
        
        # Build dynamic query
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user data by ID"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, name, height, current_weight, 
                       goal_weight, age, fitness_level, goals
                FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'name': result[3],
                    'height': result[4],
                    'current_weight': result[5],
                    'goal_weight': result[6],
                    'age': result[7],
                    'fitness_level': result[8],
                    'goals': result[9]
                }
            return None

class WorkoutTracker:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def log_workout(self, user_id: int, exercise_type: str, duration: Optional[int] = None,
                   reps: Optional[int] = None, sets: Optional[int] = None,
                   calories_burned: Optional[float] = None, form_score: Optional[float] = None,
                   notes: Optional[str] = None) -> bool:
        """Log a workout session"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workouts (user_id, exercise_type, duration, reps, sets,
                                    calories_burned, form_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, exercise_type, duration, reps, sets, calories_burned, form_score, notes))
            conn.commit()
            return True
    
    def get_user_workouts(self, user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get user's workout history"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT exercise_type, duration, reps, sets, calories_burned, 
                       form_score, notes, workout_date
                FROM workouts WHERE user_id = ?
                ORDER BY workout_date DESC
            '''
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            return [
                {
                    'exercise_type': result[0],
                    'duration': result[1],
                    'reps': result[2],
                    'sets': result[3],
                    'calories_burned': result[4],
                    'form_score': result[5],
                    'notes': result[6],
                    'workout_date': result[7]
                }
                for result in results
            ]
    
    def get_workout_stats(self, user_id: int) -> Dict:
        """Get workout statistics for dashboard"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Total workouts
            cursor.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,))
            total_workouts = cursor.fetchone()[0]
            
            # Total calories burned
            cursor.execute('SELECT SUM(calories_burned) FROM workouts WHERE user_id = ?', (user_id,))
            total_calories = cursor.fetchone()[0] or 0
            
            # Average form score
            cursor.execute('SELECT AVG(form_score) FROM workouts WHERE user_id = ? AND form_score IS NOT NULL', (user_id,))
            avg_form_score = cursor.fetchone()[0] or 0
            
            # Workouts this week
            cursor.execute('''
                SELECT COUNT(*) FROM workouts 
                WHERE user_id = ? AND workout_date >= date('now', '-7 days')
            ''', (user_id,))
            workouts_this_week = cursor.fetchone()[0]
            
            return {
                'total_workouts': total_workouts,
                'total_calories': total_calories,
                'avg_form_score': round(avg_form_score, 2),
                'workouts_this_week': workouts_this_week
            }

class ChatHistory:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_chat(self, user_id: int, message: str, response: str) -> bool:
        """Save chat interaction"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (user_id, message, response)
                VALUES (?, ?, ?)
            ''', (user_id, message, response))
            conn.commit()
            return True
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's chat history"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT message, response, timestamp
                FROM chat_history WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            return [
                {
                    'message': result[0],
                    'response': result[1],
                    'timestamp': result[2]
                }
                for result in reversed(results)  # Show oldest first
            ]