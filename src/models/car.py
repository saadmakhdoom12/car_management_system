from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Car:
    """Class representing a car in the management system"""
    make: str
    model: str
    year: int
    vin: Optional[str] = None
    mileage: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    last_service_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate data after initialization"""
        self.validate_year()
        self.validate_vin()
        self.validate_mileage()

    def validate_year(self):
        """Validate the car year"""
        current_year = datetime.now().year
        if not isinstance(self.year, int):
            raise ValueError("Year must be an integer")
        if self.year < 1900 or self.year > current_year + 1:
            raise ValueError(
                f"Year must be between 1900 and {current_year + 1}"
            )

    def validate_vin(self):
        """Validate VIN if provided"""
        if self.vin:
            # Remove spaces and convert to uppercase
            self.vin = self.vin.replace(" ", "").upper()
            if not len(self.vin) == 17:
                raise ValueError("VIN must be 17 characters long")
            if not self.vin.isalnum():
                raise ValueError("VIN must contain only letters and numbers")

    def validate_mileage(self):
        """Validate mileage if provided"""
        if self.mileage is not None:
            if not isinstance(self.mileage, int):
                raise ValueError("Mileage must be an integer")
            if self.mileage < 0:
                raise ValueError("Mileage cannot be negative")

    def to_dict(self) -> dict:
        """Convert car object to dictionary"""
        return {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'vin': self.vin,
            'mileage': self.mileage,
            'color': self.color,
            'license_plate': self.license_plate,
            'last_service_date': (
                self.last_service_date.isoformat()
                if self.last_service_date
                else None
            )
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Car':
        """Create car object from dictionary"""
        if 'last_service_date' in data and data['last_service_date']:
            data['last_service_date'] = datetime.fromisoformat(
                data['last_service_date']
            )
        return cls(**data)

    def get_full_name(self) -> str:
        """Get full car name (year make model)"""
        return f"{self.year} {self.make} {self.model}"

    def needs_service(self, mileage_interval: int = 5000) -> bool:
        """Check if car needs service based on mileage"""
        if not self.mileage or not self.last_service_date:
            return False
        
        days_since_service = (datetime.now() - self.last_service_date).days
        return days_since_service > 180 or self.mileage > mileage_interval

    def __str__(self) -> str:
        """String representation of the car"""
        return f"{self.get_full_name()} (VIN: {self.vin or 'N/A'})"

    def __repr__(self) -> str:
        """Detailed string representation of the car"""
        return (f"Car(make='{self.make}', model='{self.model}', year={self.year}, "
                f"vin='{self.vin}', mileage={self.mileage}, "
                f"color='{self.color}', license_plate='{self.license_plate}', "
                f"last_service_date='{self.last_service_date}')")
