#!/usr/bin/python
import MySQLdb
class Mysql:
    db = None
    cursor = None

def setDb():
    Mysql.db = MySQLdb.connect("localhost","root","orangepi","product" )
    Mysql.cursor = Mysql.db.cursor()
def selectList(sql):
    try:
        Mysql.cursor.execute(sql)
        #dataList = Mysql.cursor.fetchmany(dataNum)
        dataList = Mysql.cursor.fetchall()
        #Mysql.db.commit()
        return dataList
    except MySQLdb.Error, e: 
        return False

def select(sql):
    try:
        Mysql.cursor.execute(sql)
        data = Mysql.cursor.fetchone()
        return data
    except MySQLdb.Error, e: 
        return False
	
def insert(sql):
    try:
        Mysql.cursor.execute(sql)
        Mysql.db.commit()
        return True
    except MySQLdb.Error, e: 
        return False

def update(sql):
    insert(sql)

def delete(sql):
    insert(sql)

def closeDb():
    Mysql.db.close()

