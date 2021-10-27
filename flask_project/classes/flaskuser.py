# User class specifically for Flask login and authentication
# Other attributes for user are extracted from database

class FlaskUser(object):
    def __init__(self, username, authenticated, active, anonymous, id, admin):
        self.username = username
        self.authenticated = authenticated
        self.active = active
        self.anonymous = anonymous
        self.id = chr(id)    # Must be unicode
        self.admin = admin

    def get_username(self):
        return self.username
    
    @property
    def is_authenticated(self):
        return self.authenticated
    
    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return self.anonymous
    
    def get_id(self):
        return ord(self.id) # convert unicode back to int