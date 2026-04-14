from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger, Numeric, DateTime, Text, JSON, func
from sqlalchemy.orm import declarative_base, relationship, Mapped

Base = declarative_base()

class Shops(Base):
    __tablename__ = 'shops'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    domain = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)

    product_links = relationship("ProductLinks", back_populates="shop")

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(300))
    brand = Column(String(100))
    properties = Column(JSON)
    image_url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    product_links = relationship("ProductLinks", back_populates="product")
    subscriptions = relationship("Subscriptions", back_populates="product")

class ProductLinks(Base):
    __tablename__ = 'product_links'
    
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey('shops.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    url = Column(Text)
    is_available = Column(Boolean, default=True)

    shop = relationship("Shops", back_populates="product_links")
    product = relationship("Products", back_populates="product_links")
    history = relationship("PriceHistory", back_populates="product_link")

class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(BigInteger, primary_key=True)
    link_id = Column(Integer, ForeignKey('product_links.id'))
    price = Column(Numeric(12, 2))
    parsed_at = Column(DateTime, server_default=func.now())

    product_link = relationship("ProductLinks", back_populates="history")

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    login = Column(String(50), nullable=False, unique=True)
    password_hash = Column(Text)
    chat_id = Column(String)
    is_active = Column(Boolean, default=True)
    parse_interval = Column(Integer, default=1)
    last_parse_at = Column(DateTime, nullable=True)
    
    subscriptions = relationship("Subscriptions", back_populates="user")
    contacts = relationship("Contacts", uselist=False, back_populates="user", lazy="joined")

class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    created_at = Column(DateTime, server_default=func.now())
    target_price = Column(Numeric(12, 2))

    user = relationship("Users", back_populates="subscriptions")
    product = relationship("Products", back_populates="subscriptions")

class Contacts(Base):
    __tablename__ = "contacts"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    email = Column(String(255))
    phone_number = Column(String(20))
    tg = Column(String(34))

    user = relationship("Users", back_populates="contacts", lazy="joined")
