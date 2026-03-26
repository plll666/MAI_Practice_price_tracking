from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedProduct:
    title: str
    price: int
    source: str
    url: str
