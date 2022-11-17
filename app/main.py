#--------#
# Import #
#--------#

from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import uuid
import json

app = FastAPI()

#------------------------#
# Settings for variables #
#------------------------#

with open("config") as f:
    cfg = json.load(f)

db_hostname = cfg["db_hostname"]
db_username = cfg["db_username"]
db_password = cfg["db_password"]
db_name = cfg["db_name"]
db_table_users = cfg["db_table_users"]
db_table_books = cfg["db_table_books"]

#-------------------#---------------------------------------------------------------------#
# Functions for SQL # https://www.freecodecamp.org/japanese/news/connect-python-with-sql/ #
#-------------------#---------------------------------------------------------------------#

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL:\tDatabase connection successful")
    except Error as err:
        print(f"SQLError:\t'{err}'")

    return connection

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL:\tDatabase connection successful")
    except Error as err:
        print(f"SQLError:\t'{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("MySQL:\tDatabase created successfully")
    except Error as err:
        print(f"SQLError:\t'{err}'")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        value = cursor.fetchall()
        connection.commit()
        return value
    except Error as err:
        print(f"SQLError:\t'{err}'")

#----------------------#
# Functions for WebAPI #
#----------------------#

@app.get("/")
async def root():
    return {"message": "Hello World"}

class Register(BaseModel):
    id: str
    username: str

@app.post("/register")
async def register(account: Register):
    global connection
    value = execute_query(connection, f"SELECT count(id) FROM {db_table_users} WHERE id='{account.id}'")
    if value[0][0]==0:
        uniqueid = str(uuid.uuid4())
        execute_query(connection, f"INSERT INTO {db_table_users} (uuid, id, username) VALUES ('{uniqueid}', '{account.id}', '{account.username}');")
        return {"state": True, "message": "User created successfully", "uuid": uniqueid, "id": account.id, "username": account.username}
    return {"state": False, "message": "User did not created"}

#---------------#
# Connect to DB #
#---------------#

connection = create_server_connection(db_hostname, db_username, db_password)
create_database(connection, "CREATE DATABASE IF NOT EXISTS "+db_name)
connection = create_db_connection(db_hostname, db_username, db_password, db_name)
execute_query(connection, f"""CREATE TABLE IF NOT EXISTS {db_table_users}(
                uuid VARCHAR(36) PRIMARY KEY,
                id VARCHAR(15),
                username VARCHAR(50));""")
execute_query(connection, f"""CREATE TABLE IF NOT EXISTS {db_table_books}(
                isbn VARCHAR(13) PRIMARY KEY);""")

