import os
import sqlite3
import uuid
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
SQLITE_DB = os.getenv('SQLITE_DB', 'panchayat_seva.db')

# Track if we're using PostgreSQL
USE_POSTGRES = bool(DATABASE_URL)

# PostgreSQL connection pool (lazy initialization)
_pg_conn = None

def get_db_connection():
    """Get database connection - PostgreSQL or SQLite based on DATABASE_URL"""
    if USE_POSTGRES:
        return get_pg_connection()
    else:
        return get_sqlite_connection()

def get_sqlite_connection():
    """Get SQLite connection (for local development)"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_pg_connection():
    """Get PostgreSQL connection (for production) with RealDictCursor"""
    global _pg_conn
    if _pg_conn is None:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        _pg_conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return _pg_conn

def get_pg_cursor():
    """Get PostgreSQL cursor with RealDictCursor"""
    conn = get_pg_connection()
    return conn.cursor()

@contextmanager
def get_cursor():
    """Context manager for database cursor"""
    if USE_POSTGRES:
        conn = get_pg_connection()
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
    else:
        conn = get_sqlite_connection()
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

def init_db():
    """Initialize database tables"""
    if USE_POSTGRES:
        init_postgres_db()
    else:
        init_sqlite_db()

def init_sqlite_db():
    """Initialize SQLite database"""
    conn = get_sqlite_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            category TEXT NOT NULL,
            income INTEGER NOT NULL,
            age INTEGER NOT NULL,
            family_size INTEGER NOT NULL,
            language TEXT DEFAULT 'malayalam',
            notify INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            message_en TEXT,
            message_ml TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS scheme_log (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            deadline TEXT,
            criteria TEXT,
            found_at TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS scheme_log_auto (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            deadline TEXT,
            criteria TEXT,
            found_at TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_extra_profile (
            user_id TEXT PRIMARY KEY,
            has_pucca_house INTEGER,
            owns_4_wheeler INTEGER,
            government_employee INTEGER,
            receives_other_pension INTEGER,
            remarried INTEGER,
            has_disability_cert INTEGER,
            disability_percentage INTEGER,
            is_artisan INTEGER,
            is_student INTEGER,
            has_private_insurance INTEGER,
            is_food_business INTEGER,
            has_other_govt_scheme INTEGER,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Run migration for extra fields
    migration_add_extra_fields_sqlite()

def init_postgres_db():
    """Initialize PostgreSQL database"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            category TEXT NOT NULL,
            income INTEGER NOT NULL,
            age INTEGER NOT NULL,
            family_size INTEGER NOT NULL,
            language TEXT DEFAULT 'malayalam',
            notify INTEGER DEFAULT 1,
            created_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP
        )
    ''')
    
    # Notifications table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            message_en TEXT,
            message_ml TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Scheme log tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scheme_log (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            deadline TEXT,
            criteria TEXT,
            found_at TIMESTAMP NOT NULL
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scheme_log_auto (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            deadline TEXT,
            criteria TEXT,
            found_at TIMESTAMP NOT NULL
        )
    ''')
    
    # User extra profile table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_extra_profile (
            user_id TEXT PRIMARY KEY,
            gender TEXT,
            employment_status TEXT,
            marital_status TEXT,
            education_level TEXT,
            occupation TEXT,
            house_ownership TEXT,
            vehicle_type TEXT,
            has_pucca_house INTEGER,
            owns_4_wheeler INTEGER,
            government_employee INTEGER,
            receives_other_pension INTEGER,
            remarried INTEGER,
            has_disability_cert INTEGER,
            disability_percentage INTEGER,
            is_artisan INTEGER,
            is_student INTEGER,
            has_private_insurance INTEGER,
            is_food_business INTEGER,
            has_other_govt_scheme INTEGER,
            has_health_insurance INTEGER,
            has_life_insurance INTEGER,
            is_urban INTEGER,
            annual_turnover INTEGER,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    cur.close()

def migration_add_extra_fields_sqlite():
    """Add new columns to SQLite user_extra_profile table"""
    conn = get_sqlite_connection()
    c = conn.cursor()
    
    new_columns = [
        ('gender', 'TEXT'),
        ('employment_status', 'TEXT'),
        ('marital_status', 'TEXT'),
        ('education_level', 'TEXT'),
        ('occupation', 'TEXT'),
        ('house_ownership', 'TEXT'),
        ('vehicle_type', 'TEXT'),
        ('has_health_insurance', 'INTEGER'),
        ('has_life_insurance', 'INTEGER'),
        ('is_urban', 'INTEGER'),
        ('annual_turnover', 'INTEGER'),
    ]
    
    for col_name, col_type in new_columns:
        try:
            c.execute(f'ALTER TABLE user_extra_profile ADD COLUMN {col_name} {col_type}')
            print(f"[DB] Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if 'duplicate column' not in str(e).lower():
                pass  # Column already exists
    
    conn.commit()
    conn.close()

def create_user(profile: dict) -> dict:
    user_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    with get_cursor() as c:
        try:
            if USE_POSTGRES:
                c.execute('''
                    INSERT INTO users (
                        user_id, phone, password_hash, name, district, 
                        category, income, age, family_size, language, 
                        notify, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    user_id,
                    profile['phone'],
                    profile['password_hash'],
                    profile['name'],
                    profile['district'],
                    profile['category'],
                    profile['income'],
                    profile['age'],
                    profile['family_size'],
                    profile.get('language', 'malayalam'),
                    profile.get('notify', 1),
                    created_at
                ))
            else:
                c.execute('''
                    INSERT INTO users (
                        user_id, phone, password_hash, name, district, 
                        category, income, age, family_size, language, 
                        notify, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    profile['phone'],
                    profile['password_hash'],
                    profile['name'],
                    profile['district'],
                    profile['category'],
                    profile['income'],
                    profile['age'],
                    profile['family_size'],
                    profile.get('language', 'malayalam'),
                    profile.get('notify', 1),
                    created_at
                ))
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
            
        except Exception as e:
            error_str = str(e).lower()
            if 'phone' in error_str or 'unique' in error_str:
                return {
                    'success': False,
                    'error': 'Phone number already registered'
                }
            return {
                'success': False,
                'error': str(e)
            }

def verify_user(phone: str, password_hash: str) -> dict:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                SELECT user_id, phone, password_hash, name, district,
                       category, income, age, family_size, language,
                       notify, created_at, last_login
                FROM users WHERE phone = %s
            ''', (phone,))
        else:
            c.execute('''
                SELECT user_id, phone, password_hash, name, district,
                       category, income, age, family_size, language,
                       notify, created_at, last_login
                FROM users WHERE phone = ?
            ''', (phone,))
        
        row = c.fetchone()
        
        if not row:
            return {'success': False, 'error': 'User not found'}
        
        if row['password_hash'] != password_hash:
            return {'success': False, 'error': 'Invalid password'}
        
        # Update last login
        if USE_POSTGRES:
            c.execute('''
                UPDATE users SET last_login = %s WHERE user_id = %s
            ''', (datetime.now().isoformat(), row['user_id']))
        else:
            c.execute('''
                UPDATE users SET last_login = ? WHERE user_id = ?
            ''', (datetime.now().isoformat(), row['user_id']))
        
        return {
            'success': True,
            'user_id': row['user_id'],
            'phone': row['phone'],
            'name': row['name'],
            'district': row['district'],
            'category': row['category'],
            'income': row['income'],
            'age': row['age'],
            'family_size': row['family_size'],
            'language': row['language'],
            'notify': row['notify'],
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'last_login': str(row['last_login']) if row['last_login'] else None
        }

def get_user_profile(user_id: str) -> Optional[dict]:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                SELECT user_id, phone, name, district, category,
                       income, age, family_size, language, notify,
                       created_at, last_login
                FROM users WHERE user_id = %s
            ''', (user_id,))
        else:
            c.execute('''
                SELECT user_id, phone, name, district, category,
                       income, age, family_size, language, notify,
                       created_at, last_login
                FROM users WHERE user_id = ?
            ''', (user_id,))
        
        row = c.fetchone()
        
        if not row:
            return None
        
        result = dict(row)
        if result.get('created_at'):
            result['created_at'] = str(result['created_at'])
        if result.get('last_login'):
            result['last_login'] = str(result['last_login'])
        return result

def update_user_profile(user_id: str, updates: dict) -> dict:
    allowed_fields = ['name', 'district', 'category', 'income', 
                      'age', 'family_size', 'language', 'notify']
    
    with get_cursor() as c:
        for key, value in updates.items():
            if key in allowed_fields:
                if USE_POSTGRES:
                    c.execute(f'UPDATE users SET {key} = %s WHERE user_id = %s', 
                             (value, user_id))
                else:
                    c.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', 
                             (value, user_id))
    
    return {'success': True, 'message': 'Profile updated'}

def user_exists(phone: str) -> bool:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('SELECT 1 FROM users WHERE phone = %s', (phone,))
        else:
            c.execute('SELECT 1 FROM users WHERE phone = ?', (phone,))
        return c.fetchone() is not None

def get_unread_notifications(user_id: str) -> list:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                SELECT id, scheme_name, message_en, message_ml, created_at
                FROM notifications
                WHERE user_id = %s AND is_read = 0
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            c.execute('''
                SELECT id, scheme_name, message_en, message_ml, created_at
                FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
            ''', (user_id,))
        
        rows = c.fetchall()
        return [dict(row) for row in rows]

def mark_notification_read(notification_id: int):
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('UPDATE notifications SET is_read = 1 WHERE id = %s', (notification_id,))
        else:
            c.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))

def add_notification(user_id: str, scheme_name: str, 
                    message_en: str = None, message_ml: str = None) -> dict:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                INSERT INTO notifications (user_id, scheme_name, message_en, 
                                          message_ml, created_at)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, scheme_name, message_en, message_ml,
                  datetime.now().isoformat()))
            notification_id = c.lastrowid
        else:
            c.execute('''
                INSERT INTO notifications (user_id, scheme_name, message_en, 
                                          message_ml, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, scheme_name, message_en, message_ml,
                  datetime.now().isoformat()))
            notification_id = c.lastrowid
    
    return {'success': True, 'notification_id': notification_id}

def get_all_users_for_notifications() -> list:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                SELECT user_id, name, phone, district, income, 
                       family_size, category, age, notify
                FROM users WHERE notify = 1
            ''')
        else:
            c.execute('''
                SELECT user_id, name, phone, district, income, 
                       family_size, category, age, notify
                FROM users WHERE notify = 1
            ''')
        
        rows = c.fetchall()
        return [dict(row) for row in rows]

def get_user_extra_profile(user_id: str) -> Optional[dict]:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('SELECT * FROM user_extra_profile WHERE user_id = %s', (user_id,))
        else:
            c.execute('SELECT * FROM user_extra_profile WHERE user_id = ?', (user_id,))
        
        row = c.fetchone()
        
        if not row:
            return None
        
        result = dict(row)
        # Convert integer booleans back to Python booleans
        bool_fields = ['has_pucca_house', 'owns_4_wheeler', 'government_employee', 
            'receives_other_pension', 'remarried', 'has_disability_cert', 'is_artisan', 
            'is_student', 'has_private_insurance', 'is_food_business', 'has_other_govt_scheme',
            'has_health_insurance', 'has_life_insurance', 'is_urban']
        
        for key in bool_fields:
            if key in result and result[key] is not None:
                result[key] = bool(result[key])
        
        return result

def update_user_extra_profile(user_id: str, field: str, value) -> dict:
    if isinstance(value, bool):
        value = 1 if value else 0
    
    now = datetime.now().isoformat()
    
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                INSERT INTO user_extra_profile (user_id, {}, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(user_id) DO UPDATE SET {} = %s, updated_at = %s
            '''.format(field, field), (user_id, value, now, now, value, now))
        else:
            c.execute('''
                INSERT OR REPLACE INTO user_extra_profile (user_id, {}, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            '''.format(field), (user_id, value, now, now))
    
    return {'success': True}

def get_all_extra_profile_fields(user_id: str) -> dict:
    extra = get_user_extra_profile(user_id)
    if not extra:
        return {}
    
    result = {}
    for key in ['has_pucca_house', 'owns_4_wheeler', 'government_employee', 
                'receives_other_pension', 'remarried', 'has_disability_cert',
                'disability_percentage', 'is_artisan', 'is_student', 
                'has_private_insurance', 'is_food_business', 'has_other_govt_scheme',
                'gender', 'employment_status', 'marital_status', 'education_level',
                'occupation', 'house_ownership', 'vehicle_type', 'has_health_insurance',
                'has_life_insurance', 'is_urban', 'annual_turnover']:
        if key in extra and extra[key] is not None:
            result[key] = extra[key]
    
    return result

def get_user_full_profile(user_id: str) -> Optional[dict]:
    user = get_user_profile(user_id)
    if not user:
        return None
    
    extra = get_all_extra_profile_fields(user_id)
    if extra:
        user.update(extra)
    
    return user

def get_all_users_full_profile() -> list:
    users = get_all_users_for_notifications()
    result = []
    
    for user in users:
        extra = get_all_extra_profile_fields(user['user_id'])
        if extra:
            user.update(extra)
        result.append(user)
    
    return result

def was_notified_recently(user_id: str, scheme_name: str, days: int = 30) -> bool:
    with get_cursor() as c:
        if USE_POSTGRES:
            c.execute('''
                SELECT 1 FROM notifications 
                WHERE user_id = %s AND scheme_name = %s
                AND created_at > NOW() - INTERVAL '%s days'
            ''', (user_id, scheme_name, str(days)))
        else:
            c.execute('''
                SELECT 1 FROM notifications 
                WHERE user_id = ? AND scheme_name = ?
                AND created_at > datetime('now', '-' || ? || ' days')
            ''', (user_id, scheme_name, days))
        
        return c.fetchone() is not None

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print(f"Using: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
