"""Base model class for all database models"""

from typing import Dict, Any, Optional
from datetime import datetime
try:
    from ..database import DatabaseManager
except ImportError:
    from src.database import DatabaseManager

class BaseModel:
    """Base class for all database models"""
    
    _table_name: str = ""
    _db: Optional[DatabaseManager] = None
    
    def __init__(self, **kwargs):
        """Initialize model with data"""
        self.id: Optional[int] = kwargs.get('id')
        self.created_at: Optional[datetime] = kwargs.get('created_at')
        self.updated_at: Optional[datetime] = kwargs.get('updated_at')
        
        # Set all provided attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_db(cls) -> DatabaseManager:
        """Get database manager instance"""
        if cls._db is None:
            cls._db = DatabaseManager()
        return cls._db
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        return cls(**data)
    
    def save(self) -> int:
        """Save model to database (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement save()")
    
    @classmethod
    def find_by_id(cls, id: int):
        """Find model by ID (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement find_by_id()")
    
    @classmethod
    def find_by_slug(cls, slug: str):
        """Find model by slug (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement find_by_slug()")
    
    def delete(self) -> bool:
        """Delete this model instance from database"""
        if not self.id:
            return False
        
        db = self.get_db()
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(f"DELETE FROM {self._table_name} WHERE id = ?", (self.id,))
                return cursor.rowcount > 0
        except Exception as e:
            if "FOREIGN KEY constraint failed" in str(e):
                refs = self._find_foreign_key_references()
                if refs:
                    ref_info = ", ".join([f"{ref['count']} {ref['table']}" for ref in refs])
                    print(f"Cannot delete {self.__class__.__name__} '{getattr(self, 'name', getattr(self, 'title', self.id))}' - referenced by: {ref_info}")
                else:
                    print(f"Error deleting {self.__class__.__name__}: {e}")
            else:
                print(f"Error deleting {self.__class__.__name__}: {e}")
            return False
    
    def _find_foreign_key_references(self):
        """Find what database records reference this item"""
        references = []
        table_name = self._table_name
        record_id = self.id
        
        try:
            db = self.get_db()
            with db.get_connection() as conn:
                # Get all tables
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row['name'] for row in cursor.fetchall()]
                
                # For each table, check its foreign key constraints
                for target_table in tables:
                    if target_table == table_name:
                        continue
                        
                    try:
                        # Get foreign key info for this table
                        cursor = conn.execute(f'PRAGMA foreign_key_list({target_table})')
                        fks = cursor.fetchall()
                        
                        for fk in fks:
                            fk_dict = dict(fk)
                            if fk_dict['table'] == table_name:
                                fk_column = fk_dict['from']
                                
                                # Validate column and table names to prevent SQL injection/errors
                                if not fk_column or not fk_column.replace('_', '').isalnum():
                                    continue
                                if not target_table or not target_table.replace('_', '').isalnum():
                                    continue
                                
                                # Check if any records reference our ID
                                query = f'SELECT COUNT(*) as count FROM {target_table} WHERE {fk_column} = ?'
                                cursor = conn.execute(query, (record_id,))
                                count = cursor.fetchone()['count']
                                
                                if count > 0:
                                    references.append({
                                        'table': target_table,
                                        'count': count
                                    })
                    except Exception:
                        continue
                        
        except Exception:
            pass
            
        return references
    
    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        """Delete model by ID"""
        db = cls.get_db()
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(f"DELETE FROM {cls._table_name} WHERE id = ?", (id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting {cls.__name__}: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation"""
        return f"<{self.__class__.__name__} id={self.id}>"