import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rtruong3990",
    database="361_project"
)


def sql_SELECT(sql, single=None):
    """SELECT MySQL using query"""
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql)
    if single:  # if SELECT only one item
        result = mycursor.fetchone()
    else:  # if SELECT all
        result = mycursor.fetchall()
    mycursor.close()
    return result

def sql_INSERT(sql, values):
    """INSERT into MySQL using query and values"""
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql, values)
    print(mycursor.rowcount, "record inserted.")
    mydb.commit()
    mycursor.close()

def sql_UPDATE(sql):
    """UPDATE MySQL using query"""
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(sql)
    print(mycursor.rowcount, "record updated")
    mydb.commit()
    mycursor.close()

def sql_DELETE(sql):
    """DELETE MySQL row using ID"""
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    print(mycursor.rowcount, "record deleted")
    mydb.commit()
    mycursor.close()