from app import db
from models import Device,User
from datetime import date

#Create database Schema
db.create_all()

#Create Self-representation
create_at = update_at = date.today()
device = Device(name="This Gateway", description="This is self-representation of gateway.",categories = [], is_gateway=True, create_at = create_at, update_at=update_at)

#Create Default User
user = User(username="admin", password="admin")

#Save Changes
db.session.add(device)
db.session.add(user)
db.session.commit()    