from hashids import Hashids
import os

SALT = os.getenv("HASHIDS_SALT", "my_secret_salt")
MIN_LENGTH = int(os.getenv("HASHIDS_MIN_LENGTH", 8))

hashids = Hashids(salt=SALT, min_length=MIN_LENGTH)

def encode_id(real_id: int) -> str:
    return hashids.encode(real_id)

def decode_id(hashed_id: str) -> int:
    decoded = hashids.decode(hashed_id)
    if not decoded:
        return None
    return decoded[0]