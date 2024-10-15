from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import login
from app import db
import platform
import random

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

if platform.system() != "Windows":
    import adafruit_dht

class DHT11Sensor:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.is_windows = platform.system() == "Windows"  #Check if running on Windows
    
    def get_readings(self):
        if self.is_windows:
            # Simulate data if on Windows
            return {
                'temperature': round(random.uniform(20.0, 30.0), 2),
                'humidity': round(random.uniform(30.0, 70.0), 2)
            }
        else:
            # Read actual sensor data on Raspberry Pi
            humidity, temperature = adafruit_dht.read(self.sensor, self.gpio_pin)
            if humidity is not None and temperature is not None:
                return {'temperature': temperature, 'humidity': humidity}
            else:
                return {'error': 'Failed to retrieve data from the sensor'}