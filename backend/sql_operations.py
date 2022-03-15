import mysql.connector


def sql_SELECT(sql, single=None, is_tuple=None):
    """SELECT MySQL using sql"""
    mydb = connect_mysql()
    if is_tuple:
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        city, state, url = mycursor.fetchone()
        mycursor.close()
        mydb.close()
        return city, state, url
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql)
    result = mycursor.fetchone() if single else mycursor.fetchall()  # grab one value or all values
    mycursor.close()
    mydb.close()
    return result


def sql_INSERT(sql, values):
    """INSERT into MySQL using sql and values"""
    mydb = connect_mysql()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql, values)
    print(mycursor.rowcount, "record INSERTED.")
    mydb.commit()
    mycursor.close()
    mydb.close()


def sql_UPDATE(sql):
    """UPDATE MySQL using sql"""
    mydb = connect_mysql()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql)
    print(mycursor.rowcount, "record UPDATED")
    mydb.commit()
    mycursor.close()
    mydb.close()


def sql_DELETE(sql):
    """DELETE MySQL row using ID"""
    mydb = connect_mysql()
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    print(mycursor.rowcount, "record DELETED")
    mydb.commit()
    mycursor.close()
    mydb.close()


def connect_mysql():
    """Connect to mysql DB no peeking"""
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rtruong3990",
        database="361_project")
    return mydb
