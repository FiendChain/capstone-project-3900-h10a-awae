import uuid

class TempDB:
    def __init__(self):
        self.products = {}

        for i in range(1,4):
            id = self.gen_uuid()
            self.products[id] = {
                "id": id,
                "name": "Lite Latte",
                "unit_price": 10.20,
                "est_delivery_amount": 3,
                "est_delivery_units": "days",
                "in_stock": 10,
                "category": "coffee",
                "image_url": f"/static/images/coffee_{i}.jpg",
                "description": "A deliciously light latte that gives you the runs"
            }
    
    def gen_uuid(self):
        while (uid := str(uuid.uuid4())[:7]) in self.products:
            pass
        return uid 

db = TempDB()