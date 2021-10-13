import uuid
import os

from server import app

from abc import ABC, abstractmethod
# rough outline of how cart data is stored
class Cart(ABC):
    @abstractmethod
    def to_list(self):
        pass

    @abstractmethod
    def purge(self, validator):
        pass

    @abstractmethod
    def add_product(self, id, quantity):
        pass

    @abstractmethod
    def update_product(self, id, quantity):
        pass

class DictCart(Cart):
    def __init__(self):
        super().__init__()
        self.items = {} 
    
    def to_list(self):
        for id, quantity in self.items.items():
            yield (id, quantity)
    
    def purge(self, validator):
        bad_ids = [id for id in self.items if not validator(id)]
        for id in bad_ids:
            del self.items[id]
    
    def add_product(self, id, quantity):
        if id not in self.items:
            self.items[id] = quantity
            return
        self.items[id] += quantity
    
    def update_product(self, id, quantity):
        if id not in self.items and quantity > 0:
            self.items[id] = quantity
            return
        
        if id not in self.items:
            return
        
        if quantity > 0:
            self.items[id] = quantity
        else:
            del self.items[id]

# convert flask session object to store a cart 
class SessionCart(DictCart):
    def __init__(self, session):
        self.session = session
    
    @property
    def items(self):
        return self.session.setdefault('cart', {})
    
    def add_product(self, id, quantity):
        rv = super().add_product(id, quantity)
        self.session.changed = True
        print(f'Added: {self.session}')
        return rv
    
    def update_product(self, id, quantity):
        rv = super().update_product(id, quantity)
        self.session.changed = True
        print(f'Updated: {self.session}')
        return rv

# temporary user login code for flask
class TempUser:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

        self.cart = DictCart() 
        self.roles = set(["user"]) 

    def has_roles(self, *roles):
        for role in roles:
            if role not in self.roles:
                return False
        return True

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id

class InvalidFileExtension(Exception):
    def __init__(self, filename, message=None):
        super().__init__(message)
        self.filename = filename

# temporary db for storing products and users
# basic uuid generation
class TempDB:
    def __init__(self):
        self.all_ids = set()

        self.products = {}
        self.users = {}
        self.images = {}

        for i in range(1,4):
            id = self.gen_uuid()
            self.products[id] = {
                "id": id,
                "name": "Lite Latte",
                "unit_price": 10.20,
                "delivery_days": 3,
                "warranty_days": 5,
                "in_stock": 10,
                "brand": f"Adele {i}",
                "category": "coffee",
                "image_url": f"/static/uploads/images/coffee_{i}.jpg",
                "description": "A deliciously light latte that gives you the runs"
            }

        for i in range(1,4):
            id = self.gen_uuid() 
            self.users[id] = TempUser(id, f"user{i:02d}", f"pass{i:02d}")

        # create admin accounts 
        for i in range(1,2):
            id = self.gen_uuid()
            user = TempUser(id, f"admin{i:02d}", f"pass{i:02d}")
            user.roles.add("admin")
            self.users[id] = user

    def add_image(self, file):
        valid_filename = file.filename != '' and '.' in file.filename
        if not valid_filename:
            raise InvalidFileExtension(valid_filename)

        ext = os.path.splitext(file.filename)[1]

        id = uuid.uuid4()
        rand_filename = f"{id}.{ext}"

        # TODO: Decide on how you want to store images
        file.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], rand_filename))
        image_url = f"/static/uploads/images/{rand_filename}"
        self.images[rand_filename] = image_url

        return image_url


    def gen_uuid(self):
        while True:
            uid = str(uuid.uuid4())[:7]
            if uid not in self.all_ids:
                break
        return uid 

db = TempDB()