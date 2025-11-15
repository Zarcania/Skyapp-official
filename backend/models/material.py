from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Material Management Models
class MaterialStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    DAMAGED = "DAMAGED"
    LOST = "LOST"

class MaterialCategory(str, Enum):
    TOOL = "TOOL"                    # Outils (perceuse, visseuse, etc.)
    SAFETY = "SAFETY"                # Équipement de sécurité
    MEASUREMENT = "MEASUREMENT"      # Instruments de mesure
    VEHICLE = "VEHICLE"             # Véhicules
    EQUIPMENT = "EQUIPMENT"         # Équipement lourd
    CONSUMABLE = "CONSUMABLE"       # Consommables

class Material(BaseModel):
    id: Optional[str] = None
    company_id: int
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: MaterialCategory
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    qr_code: str  # Code unique généré
    status: MaterialStatus = MaterialStatus.AVAILABLE
    current_user_id: Optional[int] = None  # Qui l'utilise actuellement
    location: Optional[str] = None
    last_maintenance: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MaterialCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: MaterialCategory
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    location: Optional[str] = None

class MaterialAssignment(BaseModel):
    id: Optional[str] = None
    material_id: str
    user_id: int
    company_id: int
    assigned_at: datetime
    returned_at: Optional[datetime] = None
    notes: Optional[str] = None