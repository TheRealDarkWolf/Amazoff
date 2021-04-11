import sqlite3
conn = sqlite3.connect("Online_Shopping.db")
cur = conn.cursor()
'''
prodID = "PID0000003"

cur.execute("SELECT category FROM product where prodID = ? ", (prodID,))
print(cur.fetchall()[0][0])
#    cur.execute("SELECT prodID FROM product WHERE sellID = {}".format(sellID))
'''
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
for i in tables:
    print(i[0])
    cur.execute("PRAGMA table_info({})".format(i[0]))
    for j in cur.fetchall():
        print(j[1], end = "\t")
    print()
    cur.execute("SELECT * FROM {}".format(i[0]))
    for k in cur.fetchall():
        for l in k:
            print(l, end = "\t")
        print()
    print()
    print()


'''

cur.execute("SELECT * FROM product WHERE category='Electronics and Tech'")
print(cur.fetchall())
'''