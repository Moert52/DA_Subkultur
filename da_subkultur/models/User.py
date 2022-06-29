class User:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def __str__(self):
        return "ID: {} EMail: {} Password: {}".format(self.id, self.email, self.password)