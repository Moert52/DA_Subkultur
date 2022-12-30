class User:
    def __init__(self, firstname, lastname, birthdate, email, password, role=None):
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate
        self.email = email
        self.password = password
        self.role = role

    def __str__(self):
        return "First Name: {} Last Name: {} Birthdate: {} " \
               "EMail: {} Password: {} Role: {}".format(self.firstname, self.lastname, self.birthdate,
                                                        self.email, self.password, self.role)

    