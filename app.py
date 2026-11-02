import tkinter as tk
from tkinter import ttk,messagebox
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd

#MYSQL CONNECTION
db=mysql.connector.connect(host="localhost",user="root",password="",database="expense_tracker") 
cursor=db.cursor()

#ADD EXPENSE
def add_expense():
    date=date_entry.get()
    category=category_entry.get()
    description=description_entry.get()
    paymentmethod=payment_entry.get()
    amount=amount_entry.get()
    if date==""or category==""or amount=="":
        messagebox.showwarning("Warning","Please Enter Date, Category and Amount")
        return
    query="""INSERT INTO expenses(date,category,description,paymentmethod,amount)VALUES(%s,%s,%s,%s,%s)"""
    values=(date,category,description,paymentmethod,amount)

    cursor.execute(query,values)
    db.commit()
    messagebox.showinfo("Success","Expense added successfully")
    clear_fields()
    view_expenses()

#VIEW EXPENSES
def view_expenses():
    cursor.execute("SELECT*FROM expenses")
    records=cursor.fetchall()

    # Clear old rows
    for item in expense_table.get_children():
        expense_table.delete(item)

    # Insert database records into Tikinter
    for record in records:
        expense_table.insert("",tk.END,values=record)

#CLEAR INPUT FIELDS
def clear_fields():
    date_entry.delete(0,tk.END)
    category_entry.delete(0,tk.END)
    description_entry.delete(0,tk.END)
    payment_entry.delete(0,tk.END)
    amount_entry.delete(0,tk.END)

#DELETE EXPENSE
def delete_expense():
    selected=expense_table.selection()
    if not selected:
        messagebox.showwarning("Warning","Please select an expense")
        return
    record=expense_table.item(selected[0])
    expense_id=record["values"][0]
    query="DELETE FROM expenses WHERE id=%s"
    cursor.execute(query,(expense_id,))
    db.commit()
    messagebox.showinfo("Success","Expense deleted successfully")
    view_expenses()

#EDIT EXPENSE
def edit_expense():
    selected=expense_table.selection()
    if not selected:
        messagebox.showwarning("Warning","Please select an expense")
        return
    record=expense_table.item(selected[0])
    expense_id=record["values"][0]
    date=date_entry.get()
    category=category_entry.get()
    description=description_entry.get()
    paymentmethod=payment_entry.get()
    amount=amount_entry.get()

    query="""UPDATE expenses SET date=%s,category=%s,description=%s,paymentmethod=%s,amount=%s WHERE id=%s"""
    values=(date,category,description,paymentmethod,amount,expense_id)
    cursor.execute(query,values)
    db.commit()
    messagebox.showinfo("Success","Expense updated successfully")
    clear_fields()
    view_expenses()

#SEARCH EXPENSE
def search_expense():
    search=search_entry.get()
    query="""SELECT*FROM expenses WHERE category LIKE %s OR date LIKE %s"""
    value="%"+search+"%"
    cursor.execute(query,(value,value))
    rows=cursor.fetchall()

    #Clear table
    for item in expense_table.get_children():
        expense_table.delete(item)

    #Display search results
    for row in rows:
        expense_table.insert("",tk.END,values=row)

#TOTAL EXPENSES
def total_expenses():
    query="SELECT SUM(amount) FROM expenses"
    cursor.execute(query)
    result=cursor.fetchone()
    total=result[0]
    if total is None:
        total=0
    total_label.config(text=f"Total Expenses:{total:.2f}")

#CATEGORY-WISE EXPENSES
def category_expenses():
    cursor.execute("SELECT category, amount FROM expenses")
    rows=cursor.fetchall()
    df=pd.DataFrame(rows,columns=["category", "amount"])
    category_total=df.groupby("category")["amount"].sum()

    #Clear table
    for item in expense_table.get_children():
        expense_table.delete(item)

    #Display category totals
    for category,amount in category_total.items():
        expense_table.insert("",tk.END,values=("","",category,"","",amount))

#MONTHLY EXPENSES
def monthly_expenses():
    query="""SELECT DATE_FORMAT(date,'%Y-%m') AS month,SUM(amount) AS total FROM expenses GROUP BY DATE_FORMAT(date,'%Y-%m') ORDER BY month"""
    cursor.execute(query)
    rows=cursor.fetchall()
    monthly_window=tk.Toplevel(window)
    monthly_window.title("Monthly Expenses")
    monthly_window.geometry("500x400")
    title=tk.Label(monthly_window,text="Monthly Expenses")
    title.pack(pady=10)

    monthly_table = ttk.Treeview(monthly_window,columns=("Month","Total"),show="headings")
    monthly_table.heading("Month",text="Month")
    monthly_table.heading("Total",text="Total Expense")
    monthly_table.column("Month",width=150)
    monthly_table.column("Total",width=200)
    monthly_table.pack(fill="both",expand=True,padx=20,pady=20)
    for row in rows:
        monthly_table.insert("",tk.END,values=(row[0],f"{row[1]}"))
#CATEGORY EXPENSE CHART
def category_chart():
    cursor.execute("SELECT category, amount FROM expenses")
    rows = cursor.fetchall()

    if len(rows) == 0:
        messagebox.showinfo("Information", "No data available for chart")
        return

    # Convert data into Pandas DataFrame
    df = pd.DataFrame(rows, columns=["category", "amount"])

    # Calculate total expense for each category
    category_total = df.groupby("category")["amount"].sum()

    # Create chart
    plt.figure(figsize=(8, 5))
    plt.bar(category_total.index, category_total.values)
    plt.title("Category Wise Expenses")
    plt.xlabel("Category")
    plt.ylabel("Total Expense")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

#SELECT ROW
def select_expense(event):
    selected=expense_table.selection()
    if not selected:
        return
    record=expense_table.item(selected[0])
    values=record["values"]
    if len(values)<6:
        return
    #selected data into input fields
    date_entry.delete(0,tk.END)
    date_entry.insert(0,values[1])

    category_entry.delete(0,tk.END)
    category_entry.insert(0,values[2])

    description_entry.delete(0,tk.END)
    description_entry.insert(0,values[3])

    payment_entry.delete(0,tk.END)
    payment_entry.insert(0,values[4])

    amount_entry.delete(0,tk.END)
    amount_entry.insert(0,values[5])

#MAIN WINDOW
window=tk.Tk()
window.title("PERSONAL EXPENSES TRACKER")
window.geometry("1100x700")

#TITLE
title=tk.Label(window,text="PERSONAL EXPENSES TRACKER")
title.pack(pady=15)

#INPUT FRAME
input_frame=tk.Frame(window)
input_frame.pack(pady=5)

#Date
tk.Label(input_frame,text="Date").grid(row=0,column=0,padx=5,pady=5)
date_entry=tk.Entry(input_frame,width=20)
date_entry.grid(row=0,column=1,padx=5,pady=5)

#Category
tk.Label(input_frame,text="Category").grid(row=0,column=2,padx=5,pady=5)
category_entry=tk.Entry(input_frame,width=20)
category_entry.grid(row=0,column=3,padx=5,pady=5)

#Description
tk.Label(input_frame,text="Description").grid(row=1,column=0,padx=5,pady=5)
description_entry=tk.Entry(input_frame,width=20)
description_entry.grid(row=1,column=1,padx=5,pady=5)

#Payment
tk.Label(input_frame,text="Payment Method").grid(row=1,column=2,padx=5,pady=5)
payment_entry=tk.Entry(input_frame,width=20)
payment_entry.grid(row=1,column=3,padx=5,pady=5)

#Amount
tk.Label(input_frame,text="Amount").grid(row=2,column=0,padx=5,pady=5)
amount_entry=tk.Entry(input_frame,width=20)
amount_entry.grid(row=2,column=1,padx=5,pady=5)

#BUTTON FRAME
button_frame=tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(button_frame,text="Add Expense",width=18,command=add_expense).grid(row=0,column=0,padx=5,pady=5)
tk.Button(button_frame,text="View Expenses",width=18,command=view_expenses).grid(row=0,column=1,padx=5,pady=5)
tk.Button(button_frame,text="Delete Expense",width=18,command=delete_expense).grid(row=0,column=2,padx=5,pady=5)
tk.Button(button_frame,text="Edit Expense",width=18,command=edit_expense).grid(row=0,column=3,padx=5,pady=5)
tk.Button(button_frame,text="Total Expenses",width=18,command=total_expenses).grid(row=1,column=0,padx=5,pady=5)
tk.Button(button_frame,text="Category-wise Expenses",width=18,command=category_expenses).grid(row=1,column=1,padx=5,pady=5)
tk.Button(button_frame,text="Monthly Expenses",width=18,command=monthly_expenses).grid(row=1,column=2,padx=5,pady=5)
tk.Button(button_frame,text="Category Expense Chart",width=18,command=category_chart).grid(row=1,column=3,padx=5,pady=5)

#TOTAL LABEL
total_label=tk.Label(window,text="Total Expenses:0.00")
total_label.pack(pady=5)

#SEARCH FRAME
search_frame=tk.Frame(window)
search_frame.pack(pady=5)
tk.Label(search_frame,text="Search Category/Date:").pack(side=tk.LEFT,padx=5)
search_entry=tk.Entry(search_frame,width=25)
search_entry.pack(side=tk.LEFT,padx=5)
tk.Button(search_frame,text="Search",command=search_expense).pack(side=tk.LEFT,padx=5)
tk.Button(search_frame,text="Show All",command=view_expenses).pack(side=tk.LEFT,padx=5)

#TABLE FRAME
table_frame = tk.Frame(window)
table_frame.pack(fill="both",expand=True,padx=20,pady=10)

#EXPENSE TABLE
columns = ("ID","Date","Category","Description","Payment","Amount")
expense_table=ttk.Treeview(table_frame,columns=columns,show="headings")

#Headings
expense_table.heading("ID",text="ID")
expense_table.heading("Date",text="Date")
expense_table.heading("Category",text="Category")
expense_table.heading("Description",text="Description")
expense_table.heading("Payment",text="Payment")
expense_table.heading("Amount",text="Amount")


#Column widths
expense_table.column("ID",width=60)
expense_table.column("Date",width=120)
expense_table.column("Category",width=120)
expense_table.column("Description",width=250)
expense_table.column("Payment",width=130)
expense_table.column("Amount",width=120)

#SCROLLBAR
scrollbar=ttk.Scrollbar(table_frame,orient="vertical",command=expense_table.yview)
expense_table.configure(yscrollcommand=scrollbar.set)
expense_table.pack(side="left",fill="both",expand=True)
scrollbar.pack(side="right",fill="y")

#SELECT TABLE ROW
expense_table.bind("<ButtonRelease-1>",select_expense)

#LOAD DATA WHEN PROGRAM STARTS
view_expenses()

#START APPLICATION
window.mainloop()