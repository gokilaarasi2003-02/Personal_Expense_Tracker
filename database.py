import mysql.connector
db=mysql.connector.connect(host="localhost",user="root",password="",database="expense_tracker")
print("Connected to mysql Successfully")
cursor=db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (id INT AUTO_INCREMENT PRIMARY KEY,date DATE,category VARCHAR(50),description VARCHAR(255),
payment_method VARCHAR(50),amount DECIMAL(10,2))""")
print("Expenses table created successfully")
