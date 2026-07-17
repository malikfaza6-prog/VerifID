"""
FaceEncoding model - represents the face_encodings table.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import numpy as np


@dataclass
class FaceEncoding:
    """Face encoding domain model."""
    id: Optional[int] = None
    pegawai_id: Optional[int] = None
    encoding: Optional[bytes] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FaceEncoding":
        return cls(
            id=data.get("id"),
            pegawai_id=data.get("pegawai_id"),
            encoding=data.get("encoding"),
            created_at=data.get("created_at"),
        )

    def get_numpy_encoding(self) -> Optional[np.ndarray]:
        """Deserialize binary encoding to numpy array."""
        if self.encoding is None:
            return None
        return np.frombuffer(self.encoding, dtype=np.float64)

    @staticmethod
    def encode_numpy(array: np.ndarray) -> bytes:
        """Serialize numpy array to binary."""
        return array.astype(np.float64).tobytes()
