import mysql.connector
from FASToryEM.configurations import DB_NAME,DB_PASSWORD,DB_SERVER,DB_USER

mydb = mysql.connector.connect(
	host=DB_SERVER,
	user=DB_USER,
	passwd = DB_PASSWORD,
    auth_plugin='mysql_native_password'
	)

my_cursor = mydb.cursor()

my_cursor.execute(f"CREATE DATABASE {DB_NAME}")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
	print(db)