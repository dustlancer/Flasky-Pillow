class UserLogin():

    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self
 
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def is_anonymous(self):
        return False
    
    def get_id(self):
        if not self.__user: return False
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])