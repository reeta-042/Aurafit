"""
SQLite Database Management for AuraFit
Handles incident storage, retrieval, and filtering
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AuraFitDatabase:
    """SQLite database handler for disaster incidents"""

    def __init__(self, db_path: str = "data/aurafit.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                incident_priority TEXT NOT NULL,
                casualty_count_estimate INTEGER,
                hazards_detected TEXT,
                recommended_actions TEXT,
                evacuation_required BOOLEAN,
                emergency_services_required TEXT,
                confidence_score REAL,
                location_description TEXT,
                medical_summary TEXT,
                victim_calm_response TEXT,
                communication_language TEXT,
                latitude REAL,
                longitude REAL,
                gps_coordinates TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'OPEN'
            )
        """)

        # Migration check for existing databases
        cursor.execute("PRAGMA table_info(incidents)")
        columns = [row[1] for row in cursor.fetchall()]
        if "victim_calm_response" not in columns:
            cursor.execute("ALTER TABLE incidents ADD COLUMN victim_calm_response TEXT")
        if "communication_language" not in columns:
            cursor.execute("ALTER TABLE incidents ADD COLUMN communication_language TEXT")
        if "latitude" not in columns:
            cursor.execute("ALTER TABLE incidents ADD COLUMN latitude REAL")
        if "longitude" not in columns:
            cursor.execute("ALTER TABLE incidents ADD COLUMN longitude REAL")
        if "gps_coordinates" not in columns:
            cursor.execute("ALTER TABLE incidents ADD COLUMN gps_coordinates TEXT")
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_priority 
            ON incidents(incident_priority)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON incidents(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def insert_incident(self, incident_data: Dict[str, Any]) -> int:
        """
        Insert a disaster incident record
        
        Args:
            incident_data: Dictionary with incident details from LLM
            
        Returns:
            ID of inserted incident
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO incidents (
                    incident_type,
                    incident_priority,
                    casualty_count_estimate,
                    hazards_detected,
                    recommended_actions,
                    evacuation_required,
                    emergency_services_required,
                    confidence_score,
                    location_description,
                    medical_summary,
                    victim_calm_response,
                    communication_language,
                    latitude,
                    longitude,
                    gps_coordinates
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_data.get("incident_type", "OTHER"),
                incident_data.get("incident_priority", "YELLOW_DELAYED"),
                incident_data.get("casualty_count_estimate", 0),
                json.dumps(incident_data.get("hazards_detected", [])),
                json.dumps(incident_data.get("recommended_actions", [])),
                incident_data.get("evacuation_required", False),
                json.dumps(incident_data.get("emergency_services_required", [])),
                incident_data.get("confidence_score", 0.0),
                incident_data.get("location_description", "Unknown"),
                incident_data.get("medical_summary", ""),
                incident_data.get("victim_calm_response", ""),
                incident_data.get("communication_language", "English"),
                incident_data.get("latitude"),
                incident_data.get("longitude"),
                incident_data.get("gps_coordinates", "")
            ))
            
            conn.commit()
            incident_id = cursor.lastrowid
            logger.info(f"Inserted incident {incident_id}")
            return incident_id
            
        except Exception as e:
            logger.error(f"Error inserting incident: {e}")
            raise
        finally:
            conn.close()

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        """Get all incidents ordered by recency and priority"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Priority order
            priority_order = {
                "RED_IMMEDIATE": 1,
                "YELLOW_DELAYED": 2,
                "GREEN_MINOR": 3,
                "BLACK_EXPECTANT": 4
            }
            
            cursor.execute("""
                SELECT * FROM incidents 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            incidents = []
            
            for row in rows:
                incident = dict(row)
                # Parse JSON fields
                incident["hazards_detected"] = json.loads(incident["hazards_detected"] or "[]")
                incident["recommended_actions"] = json.loads(incident["recommended_actions"] or "[]")
                incident["emergency_services_required"] = json.loads(incident["emergency_services_required"] or "[]")
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            return []
        finally:
            conn.close()

    def get_incidents_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get incidents filtered by priority level"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM incidents 
                WHERE incident_priority = ? AND status = 'OPEN'
                ORDER BY created_at DESC
            """, (priority,))
            
            rows = cursor.fetchall()
            incidents = []
            
            for row in rows:
                incident = dict(row)
                incident["hazards_detected"] = json.loads(incident["hazards_detected"] or "[]")
                incident["recommended_actions"] = json.loads(incident["recommended_actions"] or "[]")
                incident["emergency_services_required"] = json.loads(incident["emergency_services_required"] or "[]")
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error filtering by priority: {e}")
            return []
        finally:
            conn.close()

    def get_incidents_by_type(self, incident_type: str) -> List[Dict[str, Any]]:
        """Get incidents filtered by type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM incidents 
                WHERE incident_type = ? AND status = 'OPEN'
                ORDER BY created_at DESC
            """, (incident_type,))
            
            rows = cursor.fetchall()
            incidents = []
            
            for row in rows:
                incident = dict(row)
                incident["hazards_detected"] = json.loads(incident["hazards_detected"] or "[]")
                incident["recommended_actions"] = json.loads(incident["recommended_actions"] or "[]")
                incident["emergency_services_required"] = json.loads(incident["emergency_services_required"] or "[]")
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error filtering by type: {e}")
            return []
        finally:
            conn.close()

    def search_incidents(self, query: str) -> List[Dict[str, Any]]:
        """Search incidents by location or medical summary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM incidents 
                WHERE (location_description LIKE ? OR medical_summary LIKE ?) 
                AND status = 'OPEN'
                ORDER BY created_at DESC
            """, (search_query, search_query))
            
            rows = cursor.fetchall()
            incidents = []
            
            for row in rows:
                incident = dict(row)
                incident["hazards_detected"] = json.loads(incident["hazards_detected"] or "[]")
                incident["recommended_actions"] = json.loads(incident["recommended_actions"] or "[]")
                incident["emergency_services_required"] = json.loads(incident["emergency_services_required"] or "[]")
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error searching incidents: {e}")
            return []
        finally:
            conn.close()

    def update_incident_status(self, incident_id: int, status: str) -> bool:
        """Update the status of an incident"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE incidents 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, incident_id))
            
            conn.commit()
            logger.info(f"Updated incident {incident_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating incident: {e}")
            return False
        finally:
            conn.close()

    def get_incident_analytics(self) -> Dict[str, Any]:
        """Get analytics summary for dashboard across all recorded incidents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total records in DB
            cursor.execute("SELECT COUNT(*) FROM incidents")
            total_records = cursor.fetchone()[0] or 0

            # Count by status
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'OPEN'")
            open_count = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'IN_PROGRESS'")
            in_progress_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'RESOLVED'")
            resolved_count = cursor.fetchone()[0] or 0

            # Count by priority across all logged cases
            cursor.execute("""
                SELECT incident_priority, COUNT(*) as count
                FROM incidents
                GROUP BY incident_priority
            """)
            
            priority_counts = {}
            for row in cursor.fetchall():
                priority_counts[row[0]] = row[1]
            
            # Count by type
            cursor.execute("""
                SELECT incident_type, COUNT(*) as count
                FROM incidents
                GROUP BY incident_type
            """)
            
            type_counts = {}
            for row in cursor.fetchall():
                type_counts[row[0]] = row[1]
            
            # Total casualty estimate
            cursor.execute("""
                SELECT SUM(casualty_count_estimate) as total_casualties
                FROM incidents
            """)
            
            total_casualties = cursor.fetchone()[0] or 0
            
            # Evacuation count
            cursor.execute("""
                SELECT COUNT(*) as evacuation_count
                FROM incidents
                WHERE evacuation_required = 1
            """)
            
            evacuation_count = cursor.fetchone()[0] or 0
            
            return {
                "total_records": total_records,
                "open_incidents": open_count,
                "active_incidents": open_count + in_progress_count,
                "resolved_incidents": resolved_count,
                "total_incidents": total_records,
                "priority_distribution": priority_counts,
                "type_distribution": type_counts,
                "total_casualties": total_casualties,
                "evacuation_required": evacuation_count
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}
        finally:
            conn.close()
