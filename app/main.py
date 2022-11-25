#--------#
# Import #
#--------#

from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import uuid
import json
import datetime
import hashlib

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
default_usermode = cfg["default_usermode"] # If you change this, you should see README.md

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

@app.get("/getpost/{isbn}")
async def getpost(isbn: str, page: int = None, type = None, uuid: str = None):
    global connection
    value = execute_query(connection, f"SELECT * FROM `{isbn}`")
    if len(value)==0:
        return {"state": False, "message": "Requested ISBN does not exist in the database"}
    result = []
    for v in value:
        tmp = {}
        tmp["postid"] = v[0]
        tmp["page"] = v[1]
        tmp["x"] = v[2]
        tmp["y"] = v[3]
        tmp["type"] = v[4]
        tmp["postdate"] = v[5]
        tmp["updatedate"] = v[6]
        tmp["account_uuid"] = v[7]
        tmp["content"] = v[8]
        result.append(tmp)
    return {"state": True, "data": result}

@app.get("/users/{id}")
async def showusers(id: str):
    global connection
    value = execute_query(connection, f"SELECT * FROM {db_table_users} WHERE id='{id}';")
    if len(value)==0:
        return {"state": False, "message": "Requested ID does not exist in the database"}
    v = value[0]
    return {"state": True, "id": v[1], "username": v[2], "usermode": v[3], "posts": v[5], "goods": v[6], "registerdate": v[8], "verify": v[9]}

class Register(BaseModel):
    id: str
    username: str
    password: str

@app.post("/register")
async def register(account: Register):
    global connection
    # check if the requested user already exists or not
    value = execute_query(connection, f"SELECT count(id) FROM {db_table_users} WHERE id='{account.id}'")
    if value[0][0]==0:
        uniqueid = str(uuid.uuid4())
        passhash = hashlib.sha256(account.password.encode('utf-8')).hexdigest()
        dt = datetime.datetime.now()
        rdate = int(str(dt.year) + str(dt.month).zfill(2) + str(dt.day).zfill(2) + str(dt.hour).zfill(2) + str(dt.minute).zfill(2) + str(dt.second).zfill(2))
        execute_query(connection, f"""INSERT INTO {db_table_users} (uuid, id, username, usermode, password, posts, goods, coins, registerdate, verify)
                                        VALUES ('{uniqueid}', '{account.id}', '{account.username}', {default_usermode}, '{passhash}', 0, 0, 0, {rdate}, 0);""")
        execute_query(connection, f"""CREATE TABLE IF NOT EXISTS `user-posts-{uniqueid}`(
                                        isbn VARCHAR(13),
                                        postid VARCHAR(36) PRIMARY KEY);""")
        execute_query(connection, f"""CREATE TABLE IF NOT EXISTS `user-favorite-{uniqueid}`(
                                        type INT,
                                        id VARCHAR(36) PRIMARY KEY);""")
        return {"state": True, "message": "User created successfully", "uuid": uniqueid, "id": account.id, "username": account.username, "usermode": default_usermode}
    return {"state": False, "message": "User did not created"}

class Post(BaseModel):
    isbn: str
    page: int
    x: float
    y: float
    type: int
    account_uuid: str
    content: str

@app.post("/post")
async def post(post: Post):
    global connection
    # check if the requested isbn already exists or not
    value = execute_query(connection, f"SELECT count(isbn) FROM {db_table_books} WHERE isbn='{post.isbn}'")
    if value[0][0]==0:
        execute_query(connection, f"INSERT INTO {db_table_books} (isbn, posts) VALUES ('{post.isbn}', 0)")
        execute_query(connection, f"""CREATE TABLE IF NOT EXISTS `book-posts-{post.isbn}`(
                                        postid VARCHAR(36) PRIMARY KEY,
                                        page INT,
                                        x FLOAT,
                                        y FLOAT,
                                        type INT,
                                        postdate BIGINT,
                                        updatedate BIGINT,
                                        account_uuid VARCHAR(36),
                                        content VARCHAR(10000),
                                        FOREIGN KEY (account_uuid) REFERENCES {db_table_users} (uuid) ON DELETE RESTRICT);""")
    # check if the given uuid is exists or not
    value = execute_query(connection, f"SELECT count(uuid) FROM {db_table_users} WHERE uuid='{post.account_uuid}'")
    if value[0][0]!=0:
        uniqueid = str(uuid.uuid4())
        dt = datetime.datetime.now()
        postdate = int(str(dt.year) + str(dt.month).zfill(2) + str(dt.day).zfill(2) + str(dt.hour).zfill(2) + str(dt.minute).zfill(2) + str(dt.second).zfill(2))
        execute_query(connection, f"""INSERT INTO `{post.isbn}` (postid, page, x, y, type, postdate, updatedate, account_uuid, content)
                                        VALUES ('{uniqueid}', '{post.page}', {post.x}, {post.y}, {post.type}, {postdate}, NULL, '{post.account_uuid}', '{post.content}');""")
        execute_query(connection, f"UPDATE {db_table_books} SET posts=posts+1 WHERE isbn='{post.isbn}'")
        execute_query(connection, f"UPDATE {db_table_users} SET posts=posts+1 WHERE uuid='{post.account_uuid}'")
        return {"state": True, "message": "Your post has been accepted", "postid": {uniqueid}}
    return {"state": False, "message": "Your post has been refused"}

#---------------#
# Connect to DB #
#---------------#

connection = create_server_connection(db_hostname, db_username, db_password)
create_database(connection, "CREATE DATABASE IF NOT EXISTS "+db_name)
connection = create_db_connection(db_hostname, db_username, db_password, db_name)
execute_query(connection, f"""CREATE TABLE IF NOT EXISTS {db_table_users}(
                uuid VARCHAR(36) PRIMARY KEY,
                id VARCHAR(15),
                username VARCHAR(50),
                usermode INT,
                password VARCHAR(64),
                posts INT,
                goods INT,
                coins INT,
                registerdate BIGINT,
                verify INT);""")
execute_query(connection, f"""CREATE TABLE IF NOT EXISTS {db_table_books}(
                isbn VARCHAR(13) PRIMARY KEY,
                posts INT);""")

