"""Database module for SQLite connection and operations"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Tuple, Dict, Any

from app.config import DATABASE_PATH, DATA_DIR, DEVICE_LEFT, DEVICE_RIGHT


def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create sensor_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            packet_id INTEGER,
            real_time TEXT NOT NULL,
            ch0 INTEGER NOT NULL,
            ch1 INTEGER NOT NULL,
            ch2 INTEGER NOT NULL,
            ch3 INTEGER NOT NULL,
            ch4 INTEGER NOT NULL,
            ch5 INTEGER NOT NULL,
            ch6 INTEGER NOT NULL,
            ch7 INTEGER NOT NULL
        )
    """)
    
    # Create index on device_id for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_device_id ON sensor_data(device_id)
    """)
    
    conn.commit()
    conn.close()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection as context manager."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_session_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch all session data separated by device (left/right foot).
    
    Returns:
        Tuple of (left_foot_data, right_foot_data)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Fetch left foot data (device_id = 1)
        cursor.execute("""
            SELECT id, device_id, packet_id, real_time, 
                   ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7
            FROM sensor_data
            WHERE device_id = ?
            ORDER BY real_time
        """, (DEVICE_LEFT,))
        left_foot = [dict(row) for row in cursor.fetchall()]
        
        # Fetch right foot data (device_id = 2)
        cursor.execute("""
            SELECT id, device_id, packet_id, real_time,
                   ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7
            FROM sensor_data
            WHERE device_id = ?
            ORDER BY real_time
        """, (DEVICE_RIGHT,))
        right_foot = [dict(row) for row in cursor.fetchall()]
        
        return left_foot, right_foot


def clear_session_data() -> int:
    """
    Clear all session data from the database.
    
    Returns:
        Number of rows deleted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sensor_data")
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count


def insert_sensor_data(data: List[Dict[str, Any]]) -> int:
    """
    Insert sensor data into the database.
    
    Args:
        data: List of dictionaries with sensor readings
        
    Returns:
        Number of rows inserted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.executemany("""
            INSERT INTO sensor_data 
            (device_id, packet_id, real_time, ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7)
            VALUES (:device_id, :packet_id, :real_time, :ch0, :ch1, :ch2, :ch3, :ch4, :ch5, :ch6, :ch7)
        """, data)
        
        inserted_count = cursor.rowcount
        conn.commit()
        return inserted_count


def get_data_count() -> Dict[str, int]:
    """
    Get count of records per device.
    
    Returns:
        Dictionary with counts for left and right foot
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT device_id, COUNT(*) as count
            FROM sensor_data
            GROUP BY device_id
        """)
        
        counts = {"left": 0, "right": 0, "total": 0}
        for row in cursor.fetchall():
            if row["device_id"] == DEVICE_LEFT:
                counts["left"] = row["count"]
            elif row["device_id"] == DEVICE_RIGHT:
                counts["right"] = row["count"]
        
        counts["total"] = counts["left"] + counts["right"]
        return counts


def check_database_exists() -> bool:
    """Check if the database file exists."""
    return DATABASE_PATH.exists()
