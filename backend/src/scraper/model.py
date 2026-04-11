from dataclasses import dataclass, field

@dataclass(frozen=True)
class ParsedProduct:
    title: str
    price: int
    source: str
    brand: str
    url: str
    sku: str
    image_url: str | None = None
    properties: dict = field(default_factory=dict)