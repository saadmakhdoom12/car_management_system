"""Basic implementation of a database manager for SQLite operations"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Database manager class for SQLite operations"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        self.db_path = (
            db_path if db_path else os.path.join("data", "car_management.db")
        )
        self.conn: Optional[sqlite3.Connection] = None
        self.connect()  # Establish connection when initialized

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            directory = os.path.dirname(self.db_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def ensure_connection(self):
        """Ensure database connection exists"""
        if not self.conn:
            return self.connect()
        return True

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            yield cursor
            self.conn.commit()
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()

    def initialize_tables(self):
        """Create tables if they don't exist"""
        with self.get_connection() as cursor:
            try:
                # Create estimates table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS estimates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER,
                        vehicle_id INTEGER,
                        date TEXT,
                        total_amount REAL,
                        status TEXT,
                        FOREIGN KEY (customer_id) REFERENCES customers(id),
                        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
                    )
                """)

                # Create services table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        estimate_id INTEGER,
                        description TEXT NOT NULL,
                        parts_cost REAL,
                        labor_cost REAL,
                        total_cost REAL,
                        FOREIGN KEY (estimate_id) 
                        REFERENCES estimates (estimate_id)
                    )
                """)

                # Create inventory table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory (
                        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_code TEXT UNIQUE NOT NULL,
                        description TEXT NOT NULL,
                        quantity INTEGER DEFAULT 0,
                        unit_price REAL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Add JobCard table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        estimate_id INTEGER,
                        description TEXT,
                        start_date TEXT,
                        end_date TEXT,
                        status TEXT,
                        FOREIGN KEY (estimate_id) REFERENCES estimates(id)
                    )
                """)
            except sqlite3.Error as e:
                raise sqlite3.DatabaseError(
                    f"Table creation error: {str(e)}"
                ) from e

    def add_estimate(self, data: Dict) -> Optional[int]:
        """Add new estimate with proper validation"""
        required_fields = [
            "customer_id",
            "vehicle_id",
            "date",
            "total_amount",
            "status",
        ]

        # Validate required fields
        if not all(field in data for field in required_fields):
            missing_fields = [
                field for field in required_fields if field not in data
            ]
            print(f"Missing required fields: {missing_fields}")
            return None

        try:
            with self.get_connection() as cursor:
                query = """
                    INSERT INTO estimates 
                    (customer_id, vehicle_id, date, total_amount, status)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        int(data["customer_id"]),
                        int(data["vehicle_id"]),
                        data["date"],
                        float(data["total_amount"]),
                        data["status"],
                    ),
                )
                self.conn.commit()
                return cursor.lastrowid
        except (sqlite3.Error, ValueError) as e:
            print(f"Error adding estimate: {e}")
            return None

    def add_service(self, service_data: Dict) -> int:
        """Add new service and return its ID"""
        with self.get_connection() as cursor:
            query = """
                INSERT INTO services (
                    estimate_id, description, parts_cost,
                    labor_cost, total_cost
                ) VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    service_data["estimate_id"],
                    service_data["description"],
                    service_data["parts_cost"],
                    service_data["labor_cost"],
                    service_data["total_cost"],
                ),
            )
            if cursor:
                if cursor.lastrowid is not None:
                    return cursor.lastrowid
                else:
                    raise sqlite3.DatabaseError("Failed to retrieve lastrowid")
            else:
                raise sqlite3.DatabaseError(
                    "Cursor is None, cannot fetch lastrowid"
                )

    def get_estimate(self, estimate_id: int) -> Optional[Dict]:
        """Retrieve estimate by ID"""
        with self.get_connection() as cursor:
            query = "SELECT * FROM estimates WHERE estimate_id = ?"
            cursor.execute(query, (estimate_id,))
            if cursor:
                result = cursor.fetchone()
                if result:
                    return dict(
                        zip([col[0] for col in cursor.description], result)
                    )
            return None

    def get_services_for_estimate(self, estimate_id: int) -> List[Dict]:
        """Retrieve all services for an estimate"""
        with self.get_connection() as cursor:
            query = "SELECT * FROM services WHERE estimate_id = ?"
            cursor.execute(query, (estimate_id,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_inventory(self, item_data: Dict) -> bool:
        """Update or insert inventory item"""
        with self.get_connection() as cursor:
            try:
                query = """
                    INSERT OR REPLACE INTO inventory (
                        item_code, description, quantity, unit_price
                    ) VALUES (?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        item_data["item_code"],
                        item_data["description"],
                        item_data["quantity"],
                        item_data["unit_price"],
                    ),
                )
                return True
            except sqlite3.Error:
                return False

    def get_all_estimates(self) -> List[Dict]:
        """Retrieve all estimates"""
        with self.get_connection() as cursor:
            query = "SELECT * FROM estimates ORDER BY created_date DESC"
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_inventory_items(self) -> List[Dict]:
        """
        Retrieve all inventory items

        Returns:
            List[Dict]: List of inventory items with their details
        """
        with self.get_connection() as cursor:
            cursor.execute("SELECT * FROM inventory ORDER BY item_code")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_job_card(self, data):
        try:
            query = """INSERT INTO job_cards 
                       (estimate_id, description, start_date, end_date, status)
                       VALUES (?, ?, ?, ?, ?)"""
            cursor: sqlite3.Cursor = self.conn.cursor()
            cursor.execute(
                query,
                (
                    data["estimate_id"],
                    data["description"],
                    data["start_date"],
                    data["end_date"],
                    data["status"],
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def add_jobcard(self, jobcard_data: Dict) -> int:
        """Add new jobcard and return its ID"""
        with self.get_connection() as cursor:
            query = """
                INSERT INTO jobcards (
                    estimate_id, status, technician,
                    start_date, completion_date,
                    labor_hours, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    jobcard_data["estimate_id"],
                    jobcard_data["status"],
                    jobcard_data["technician"],
                    jobcard_data["start_date"],
                    jobcard_data["completion_date"],
                    jobcard_data["labor_hours"],
                    jobcard_data["notes"],
                ),
            )
            if cursor:
                if cursor.lastrowid is not None:
                    return cursor.lastrowid
                else:
                    raise sqlite3.DatabaseError("Failed to retrieve lastrowid")
            else:
                raise sqlite3.DatabaseError(
                    "Cursor is None, cannot fetch lastrowid"
                )

    def get_jobcards(self) -> List[Dict]:
        """Retrieve all jobcards"""
        with self.get_connection() as cursor:
            query = """
                SELECT j.*, e.customer_name, e.vehicle_make, e.vehicle_model
                FROM jobcards j
                LEFT JOIN estimates e ON j.estimate_id = e.estimate_id
                ORDER BY j.start_date DESC
            """
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_job_cards(self) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as cursor:
                query = """
                    SELECT j.*, e.customer_name,
                           v.make as vehicle_make,
                           v.model as vehicle_model
                    FROM job_cards j
                    LEFT JOIN estimates e ON j.estimate_id = e.id
                    LEFT JOIN vehicles v ON e.vehicle_id = v.id
                    ORDER BY j.start_date DESC
                """
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching job cards: {e}")
            return []

    def close(self) -> None:
        """Close database connection safely"""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                print(f"Error closing connection: {e}")
            finally:
                self.conn = None
                self.cursor = None

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()
