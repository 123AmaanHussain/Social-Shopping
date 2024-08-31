from app import mongo

class Product:
    @staticmethod
    def fetch_all():
        return mongo.db.products.find()

    @staticmethod
    def fetch_by_mood(mood):
        return mongo.db.products.find({"mood": mood})

    @staticmethod
    def add_product(data):
        return mongo.db.products.insert_one(data)
