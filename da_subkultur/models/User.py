from sqlalchemy import Column, Integer, Text, Float, DateTime, create_engine, or_, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from dataclasses import dataclass

Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'  # Abbildung auf diese Tabelle
    id: int
    firstname: str
    lastname: str
    birthdate: str
    email: str
    password: str
    role: str

    id = Column(Integer, primary_key=True)
    firstname = Column(Text)
    lastname = Column(Text)
    birthdate = Column(DateTime)
    email = Column(Text)
    password = Column(Text)
    role = Column(Text)

    def __init__(self, firstname, lastname, birthdate, email, password, role):
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