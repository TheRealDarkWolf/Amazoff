import sqlite3

def gen_custID():
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET custnum = custnum + 1")
    conn.commit()
    custnum = str([i for i in cur.execute("SELECT custnum FROM metadata")][0][0])
    conn.close()
    id = "CID"+"0"*(7-len(custnum))+custnum
    return id

def gen_prodID():
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET prodnum = prodnum + 1")
    conn.commit()
    prodnum = str([i for i in cur.execute("SELECT prodnum FROM metadata")][0][0])
    conn.close()
    id = "PID"+"0"*(7-len(prodnum))+prodnum
    return id

def gen_orderID():
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET ordernum = ordernum + 1")
    conn.commit()
    ordernum = str([i for i in cur.execute("SELECT ordernum FROM metadata")][0][0])
    conn.close()
    id = "OID"+"0"*(7-len(ordernum))+ ordernum
    return id

def home_recommender():
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    items={}
    categories=['Electronics','Fashion','Sports']
    for category in categories:
        cur.execute("SELECT prodID, name, description, sell_price FROM product where category=? ORDER BY prod_buy DESC", (category,))
        output = cur.fetchmany(4)
        items[category]=[list(item) for item in output]
        while len(items[category])<4:
            items[category].append(['dummy','dummy','dummy',0])
    if len(items) == 0:
        return False
    return items


def add_user(data):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    print("FUNC CALLED")
    cur = conn.cursor()
    email = data["email"]
    a = cur.execute("SELECT * FROM customer WHERE email=?", (email,))
    if len(list(a))!=0:
        return False
    tup = ( data["name"],
            data["email"],
            data["phone"],
            data["address"],
            data["city"],
            data["state"],
            data["password"])
    cur.execute("INSERT INTO customer VALUES (?,?,?,?,?,?,?,?)",(gen_custID(), *tup))
    conn.commit()
    conn.close()
    return True

def auth_user(data):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    email = data["email"]
    password = data["password"]
    a = cur.execute("SELECT custID, name FROM customer WHERE email=? AND password=?", (email, password))
    a = list(a)
    conn.close()
    if len(a)==0:
        return False
    return a[0]

def fetch_details(userid):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM customer WHERE custID=?", (userid,))
    a = list(a)
    b = []
    conn.close()
    return a, b

def update_details(data, userid):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    print("userID", userid, "data",data)
    cur.execute("UPDATE customer SET Name=?, Phone=?, Address = ?, City=?, State=? WHERE custID=?", (data["name"], 
                data["phone"],
                data["address"],
                data["city"],
                data["state"],
                userid))
    conn.commit()
    conn.close()

def check_psswd(psswd, userid):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    a = cur.execute("SELECT password FROM customer WHERE custID=?", (userid,))
    real_psswd = list(a)[0][0]
    conn.close()
    return psswd==real_psswd

def set_psswd(psswd, userid):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    a = cur.execute("UPDATE customer SET password=? WHERE custID=?", (psswd, userid))
    conn.commit()
    conn.close()

def get_product_info(id):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT p.name, p.quantity, p.category, p.cost_price, p.sell_price,
                    p.sellID, p.description, s.name FROM product p JOIN seller s
                    WHERE p.sellID=s.sellID AND p.prodID=? """, (id,))
    res = [i for i in a]
    conn.close()
    if len(res)==0:
        return False, res
    return True, res[0]

def search_products(srchBy, category, keyword):
    conn = sqlite3.connect("Amazoff/Online_Shopping.db")
    cur = conn.cursor()
    keyword = ['%'+i+'%' for i in keyword.split()]
    if len(keyword)==0: keyword.append('%%')
    if srchBy=="by category":
        print("Inside by category", category)
        a = cur.execute("""SELECT prodID, name, category, sell_price
                        FROM product WHERE category=? AND quantity!=0 """,(category,))
        res = [i for i in a]
        print(res)
    elif srchBy=="by keyword":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, category, sell_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ? OR category LIKE ?) AND quantity!=0 """,
                            (word, word, word))
            res += list(a)
        res = list(set(res))
    elif srchBy=="both":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, category, sell_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ?) AND quantity!=0 AND category=? """,
                            (word, word, category))
            res += list(a)
        res = list(set(res))
    conn.close()
    return res


def place_order(prodID, custID, qty):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    orderID = gen_orderID()
    cur.execute("""INSERT INTO orders
                    SELECT ?,?,?,?,datetime('now'), cost_price*?, sell_price*?, 'PLACED'
                    FROM product WHERE prodID=? """, (orderID, custID, prodID, qty, qty, qty, prodID))
    conn.commit()
    conn.close()

def cust_orders(custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT o.orderID, o.prodID, p.name, o.quantity, o.sell_price, o.date_, o.status
                       FROM orders o JOIN product p
                       WHERE o.prodID=p.prodID AND o.custID=? AND o.status!='RECIEVED'
                       ORDER BY o.date_ DESC """, (custID,))
    res = [i for i in a]
    conn.close()
    return res

def get_order_details(orderID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    a = cur.execute(""" SELECT o.custID, p.sellID, o.status FROM orders o JOIN product p
                        WHERE o.orderID=? AND o.prodID=p.prodID """, (orderID,))
    res = [i for i in a]
    conn.close()
    return res

def change_order_status(orderID, new_status):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE orderID=? ", (new_status, orderID))
    conn.commit()
    conn.close()

def cust_purchases(custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT o.prodID, p.name, o.quantity, o.sell_price, o.date_
                       FROM orders o JOIN product p
                       WHERE o.prodID=p.prodID AND o.custID=? AND o.status='RECIEVED'
                       ORDER BY o.date_ DESC """, (custID,))
    res = [i for i in a]
    conn.close()
    return res

def add_product_to_cart(prodID, custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO cart VALUES (?,?,1) """, (custID, prodID))
    conn.commit()
    conn.close()

def get_cart(custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT p.prodID, p.name, p.sell_price, c.sum_qty, p.quantity
                       FROM (SELECT custID, prodID, SUM(quantity) AS sum_qty FROM cart
                       GROUP BY custID, prodID) c JOIN product p
                       WHERE p.prodID=c.prodID AND c.custID=?""", (custID,))
    res = [i for i in a]
    conn.close()
    return res

def update_cart(custID, qty):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    for prodID in qty:
        cur.execute("DELETE FROM cart WHERE prodID=? AND custID=?", (prodID, custID))
        cur.execute("INSERT INTO cart VALUES (?,?,?)", (custID, prodID, qty[prodID]))
    conn.commit()
    conn.close()

def cart_purchase(custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cart = get_cart(custID)
    for item in cart:
        orderID = gen_orderID()
        prodID = item[0]
        qty = item[3]
        cur.execute("UPDATE product SET prod_buy=prod_buy+1 WHERE prodID = ?", (prodID,))
        cur.execute("""INSERT INTO orders
                        SELECT ?,?,?,?,datetime('now'), cost_price*?, sell_price*?, 'PLACED'
                        FROM product WHERE prodID=? """, (orderID, custID, prodID, qty, qty, qty, prodID))
        cur.execute("DELETE FROM cart WHERE custID=? AND prodID=?", (custID, prodID))
        conn.commit()
    conn.close()

def empty_cart(custID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE custID=?", (custID,))
    conn.commit()

def remove_from_cart(custID, prodID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE custID=? AND prodID=?", (custID, prodID))
    conn.commit()
    
def recommended_items(prodID):
    conn = sqlite3.connect('Amazoff/Online_Shopping.db')
    cur = conn.cursor()
    cur.execute("SELECT category, sellID FROM product where prodID = ? ", (prodID,))
    output = cur.fetchall()
    if len(output) == 0:
        return False

    category, sellID = output[0]
    cur.execute("SELECT prodID FROM product WHERE sellID = ?", (sellID,))
    recID = cur.fetchall()
    cur.execute("SELECT prodID FROM product WHERE category = ?", (category,))    
    recID.extend(cur.fetchall())
    result = []
    for id in recID:
        cur.execute("SELECT prodID, name, category, sell_price FROM product WHERE prodID = ?", (id[0],))
        result.extend(cur.fetchall())
        if result[-1][0] == prodID:
            del result[-1]
    return list(set(result))


