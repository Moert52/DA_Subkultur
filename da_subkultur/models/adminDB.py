import sqlite3

databasePath = 'models/admins.db'


def insertAdmin(email):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        c.execute("INSERT INTO admins (email) VALUES (?)", [email])
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while inserting an email", error)
    finally:
        conn.close()


def deleteAdmin(email):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        c.execute("DELETE FROM admins WHERE email=?", [email])
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while deleting an email", error)
    finally:
        conn.close()
    return 204


def getAllAdmins():
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        c.execute("SELECT * FROM admins")
        users = c.fetchall()
        return users
    except sqlite3.Error as error:
        raise Exception("An error occurred while getting an email", error)
    finally:
        conn.close()


def assignRole(email):
    list = getAllAdmins()
    if list.count(email) > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    insertAdmin("meesen@tsn.at")