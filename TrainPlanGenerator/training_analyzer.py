import sqlite3
from datetime import datetime, timedelta
import pandas as pd

class TrainingAnalyzer:
    def __init__(self, db_path='training.db'):
        self.db_path = db_path

    def _execute_query(self, query, params=None):
     
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def get_recent_training(self, user_id, limit=10):
       
      
        query = """
        SELECT tr.*, u.username
        FROM training_records tr
        JOIN users u ON tr.user_id = u.id
        WHERE tr.user_id = ?
        ORDER BY tr.training_date DESC
        LIMIT ?
        """
        results = self._execute_query(query, (user_id, limit))
        return [dict(row) for row in results]


