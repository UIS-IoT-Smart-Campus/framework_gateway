from app import db
from models import Device,User,Property
from datetime import date
import selfconfig as sc

#Create database Schema
db.create_all()

#Create Self-representation
create_at = update_at = date.today()
device = Device(name="Gateway-01", description="Gateway",global_id=1, is_gateway=True, create_at = create_at, update_at=update_at)

#Create Default User
user = User(username="admin", password="admin")

#Save Changes
db.session.add(device)
db.session.add(user)
db.session.commit()

#Create Device Properties
settings = sc.get_config_values()

standalone_settings_properties = [
    'devicebrokerurl',
    'devicebrokerport',
    'devicebrokertopic',
    'mqttclient',
    'mqttkeepalive'
]

nostandalone_settings_properties = [
    'backendurl',
    'backendport',
    'brokerbackendurl',
    'brokerbackendport',
    'brokerbackendtopic',
    'global_id',
    'gateway_ipv4'
]

prop_count = 0

for key in standalone_settings_properties:
    prop_count+=1
    property_d = Property(name=key,value=settings[key],prop_type="DEVICE",parent_id=device.id,global_id=prop_count)
    db.session.add(property_d)
    db.session.commit()

for key in nostandalone_settings_properties:
    if key != "global_id":
        prop_count+=1
        property_d = Property(name=key,value=settings[key],prop_type="DEVICE",parent_id=device.id,global_id=prop_count)
        db.session.add(property_d)
        db.session.commit()