import mysql.connector


def sql_SELECT(sql, single=None, is_tuple=None):
    """SELECT MySQL using query"""
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
    if single:  # if SELECT only one item
        result = mycursor.fetchone()
    else:  # if SELECT all
        result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return result


def sql_INSERT(sql, values):
    """INSERT into MySQL using query and values"""
    mydb = connect_mysql()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql, values)
    print(mycursor.rowcount, "record inserted.")
    mydb.commit()
    mycursor.close()
    mydb.close()


def sql_UPDATE(sql):
    """UPDATE MySQL using query"""
    mydb = connect_mysql()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql)
    print(mycursor.rowcount, "record updated")
    mydb.commit()
    mycursor.close()
    mydb.close()


def sql_DELETE(sql):
    """DELETE MySQL row using ID"""
    mydb = connect_mysql()
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    print(mycursor.rowcount, "record deleted")
    mydb.commit()
    mycursor.close()
    mydb.close()


def connect_mysql():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rtruong3990",
        database="361_project")
    return mydb
