import re
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Customer:
    """Class representing a customer in the management system"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    last_visit: Optional[datetime] = None
    visit_history: List[datetime] = field(default_factory=list)

    def __post_init__(self):
        """Validate data after initialization"""
        self.validate_name()
        if self.phone:
            self.validate_phone()
        if self.email:
            self.validate_email()

    def validate_name(self):
        """Validate customer name"""
        if not self.name or not self.name.strip():
            raise ValueError("Customer name cannot be empty")
        if len(self.name) > 100:
            raise ValueError("Customer name is too long")
        self.name = self.name.strip()

    def validate_phone(self):
        """Validate phone number format"""
        # Remove any non-numeric characters
        phone = re.sub(r'\D', '', self.phone)
        if len(phone) < 10 or len(phone) > 15:
            raise ValueError("Invalid phone number length")
        # Format phone number as (XXX) XXX-XXXX
        if len(phone) == 10:
            self.phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        else:
            self.phone = phone

    def validate_email(self):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("Invalid email format")
        self.email = self.email.lower()

    def add_visit(self, visit_date: datetime = None):
        """Record a customer visit"""
        if visit_date is None:
            visit_date = datetime.now()
        self.visit_history.append(visit_date)
        self.last_visit = visit_date

    def get_visit_count(self) -> int:
        """Get total number of visits"""
        return len(self.visit_history)

    def to_dict(self) -> dict:
        """Convert customer object to dictionary"""
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'last_visit': self.last_visit.isoformat() if self.last_visit else None,
            'visit_history': [dt.isoformat() for dt in self.visit_history]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Create customer object from dictionary"""
        if 'created_date' in data:
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        if 'last_visit' in data and data['last_visit']:
            data['last_visit'] = datetime.fromisoformat(data['last_visit'])
        if 'visit_history' in data:
            data['visit_history'] = [datetime.fromisoformat(dt) for dt in data['visit_history']]
        return cls(**data)

    def __str__(self) -> str:
        """String representation of the customer"""
        contact = self.phone or self.email or "No contact info"
        return f"{self.name} ({contact})"

    def get_full_details(self) -> str:
        """Get detailed customer information"""
        details = [f"Name: {self.name}"]
        if self.phone:
            details.append(f"Phone: {self.phone}")
        if self.email:
            details.append(f"Email: {self.email}")
        if self.address:
            details.append(f"Address: {self.address}")
        if self.last_visit:
            details.append(f"Last Visit: {self.last_visit.strftime('%Y-%m-%d')}")
        details.append(f"Total Visits: {self.get_visit_count()}")
        return "\n".join(details)