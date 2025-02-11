from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Tweet:
    """Represents a tweet from X (Twitter) with minimal required information"""
    id: str
    text: str
    created_at: datetime
    author_username: str