from flask import Flask, render_template, request, url_for, redirect, abort, session
from flask_session import Session
from Amazoff.dbaccess import *
import os

app = Flask(__name__)
sess = Session()

@app.route("/", methods=["POST", "GET"])
def home():
    if "userid" in session:
        #print('hey im in')
        items=home_recommender()
        if request.method=="POST":
            data = request.form
            if 'keyword' not in request.form:
                #print(data)
                category = list(data.keys())[0]
                #print(category)
                keyword=""
                srchBy="by category"
                results = search_products(srchBy, category, keyword)
                return render_template('search_products.html', after_srch=True,signedin=True, results=results)
            #print('inside the form')
            #print(data)
            srchBy = 'by keyword'
            category = None
            keyword = data["keyword"]
            results = search_products(srchBy, category, keyword)
            return render_template('search_products.html', after_srch=True,signedin=True, results=results)
        return render_template("home.html", signedin=True, id=session['userid'], name=session['name'],items=items)
    else:
        return redirect(url_for('signup'))

@app.route("/test/<cat>/", methods=["POST", "GET"])
def searchcategory(cat):
    #print("hey im here",cat)
    return render_template("home.html", signedin=True, id=session['userid'], name=session['name'])

@app.route("/signup/", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        data = request.form
        #print("here")
        #print(data)
        ok = add_user(data)
        if ok:
            return render_template("success_signup.html")
        return render_template("signup.html", ok=ok)
    return render_template("signup.html", ok=True)

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.form
        userdat = auth_user(data)
        if userdat:
            session["userid"] = userdat[0]
            session["name"] = userdat[1]
            return redirect(url_for('home'))
        return render_template("login.html", err=True)
    return render_template("login.html", err=False)

@app.route("/logout/")
def logout():
    session.pop('userid')
    session.pop('name')
    return redirect(url_for('home'))

@app.route("/viewprofile/<id>/")
def view_profile(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    userid = session["userid"]
    my = True if userid==id else False
    #print("inside the app route")
    det, _ = fetch_details(id)   #details
    if len(det)==0:
        abort(404)
    #print(det)
    det = det[0]
    return render_template("view_profile.html", 
                            signedin=True, 
                            id=session['userid'],
                            name=det[1],
                            email=det[2],
                            phone=det[3],
                            address=det[4],
                            city=det[5],
                            state=det[6],
                            my=my)

@app.route("/editprofile/", methods=["POST", "GET"])
def edit_profile():
    if 'userid' not in session:
        return redirect(url_for('signup'))

    if request.method=="POST":
        data = request.form
        #print(data)
        update_details(data, session['userid'])
        return redirect(url_for('view_profile', id=session['userid']))

    if request.method=="GET":
        userid = session["userid"]
        det, _ = fetch_details(userid)
        det = det[0]
        #print("det",det)
        return render_template("edit_profile.html", signedin=True, id=session['userid'],
                            name=det[1],
                            email=det[2],
                            phone=det[3],
                            address=det[4],
                            city=det[5],
                            state=det[6])

@app.route("/changepassword/", methods=["POST", "GET"])
def change_password():
    if 'userid' not in session:
        return redirect(url_for('signup'))
    check = True
    equal = True
    if request.method=="POST":
        userid = session["userid"]
        old_psswd = request.form["old_psswd"]
        new_psswd = request.form["new_psswd"]
        cnfrm_psswd = request.form["cnfrm_psswd"]
        check = check_psswd(old_psswd, userid)
        if check:
            equal = (new_psswd == cnfrm_psswd)
            if equal:
                set_psswd(new_psswd, userid)
                return redirect(url_for('home'))
    return render_template("change_password.html", check=check, equal=equal, signedin=True, id=session['userid'], name=session['name'])

@app.route("/viewproduct/")
def view_prod():
    if 'userid' not in session:
        return redirect(url_for('home'))
    return redirect(url_for('buy'))

@app.route("/viewproduct/<id>/")
def view_product(id):
    if 'userid' not in session:
        return redirect(url_for('signup'))
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    rec_items = recommended_items(id)
    return render_template('view_product.html', pname=name, quantity=quantity, category=category, cost_price=cost_price, sell_price=sell_price, sell_id=sellID, sell_name=sell_name, desp=desp, prod_id=id, rec_items=rec_items, signedin=True, id=session['userid'], name=session['name'])

@app.route("/buy/", methods=["POST", "GET"])
def buy():
    if 'userid' not in session:
        return redirect(url_for('signup'))
    if request.method=="POST":
        data = request.form
        srchBy = data["search method"]
        category = None if srchBy=='by keyword' else data["category"]
        keyword = data["keyword"]
        results = search_products(srchBy, category, keyword)
        return render_template('search_products.html', after_srch=True, results=results, signedin=True, id=session['userid'], name=session['name'])
    return render_template('search_products.html', after_srch=False, signedin=True, id=session['userid'], name=session['name'])

@app.route("/buy/<id>/", methods=['POST', 'GET'])
def buy_product(id):
    if 'userid' not in session:
        return redirect(url_for('signup'))
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, _, sell_price, _, desp, _) = tup
    if request.method=="POST":
        data = request.form
        total = int(data['qty'])*float(sell_price)
        return redirect(url_for('buy_confirm', total=total, quantity=data['qty'], id=id))
    return render_template('buy_product.html', pname=name,name=session['name'], category=category, desp=desp, quantity=quantity, price=sell_price, signedin=True, id=session['userid'])

@app.route("/buy/<id>/confirm/", methods=["POST", "GET"])
def buy_confirm(id):
    if 'userid' not in session:
        return redirect(url_for('signup'))
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    if 'total' not in request.args or 'quantity' not in request.args:
        abort(404)
    total = request.args['total']
    qty = request.args['quantity']
    if request.method=="POST":
        choice = request.form['choice']
        if choice=="PLACE ORDER":
            place_order(id, session['userid'], qty)
            return redirect(url_for('my_orders'))
        elif choice=="CANCEL":
            return redirect(url_for('buy_product', id=id))
    items = ((name, qty, total),)
    return render_template('buy_confirm.html', items=items, total=total, signedin=True, id=session['userid'], name=session['name'])

@app.route("/buy/myorders/")
def my_orders():
    if 'userid' not in session:
        return redirect(url_for('signup'))
    res = cust_orders(session['userid'])
    return render_template('my_orders.html', orders=res, signedin=True, id=session['userid'], name=session['name'])

@app.route("/cancel/<orderID>/")
def cancel_order(orderID):
    if 'userid' not in session:
        return redirect(url_for('signup'))
    res = get_order_details(orderID)
    if len(res)==0:
        abort(404)
    custID = res[0][0]
    sellID = res[0][1]
    status = res[0][2]
    if custID!=session['userid']:
        abort(403)
    if status!="PLACED":
        abort(404)
    change_order_status(orderID, "CANCELLED")
    return redirect(url_for('my_orders'))


@app.route("/buy/cart/", methods=["POST", "GET"])
def my_cart():
    if "userid" in session:
        #print("cart in session")
        cart = get_cart(session['userid'])
        #print(cart)
        items= [i[0] for i in cart]
        rec_items=cart_recommendations(items)
        #print(rec_items)
        if request.method=="POST":
            data = request.form
            qty = {}
            for i in data:
                if i.startswith("qty"):
                    qty[i[3:]]=data[i]      #qty[prodID]=quantity
            update_cart(session['userid'], qty)
            return redirect("/buy/cart/confirm/")
        return render_template("my_cart.html", signedin=True, id=session['userid'], name=session['name'], cart=cart, rec_items=rec_items)
    else:
        return redirect(url_for('signup'))
    
@app.route("/buy/cart/confirm/", methods=["POST", "GET"])
def cart_purchase_confirm():
    if 'userid' not in session:
        return redirect(url_for('signup'))
    if request.method=="POST":
        choice = request.form['choice']
        if choice=="PLACE ORDER":
            cart_purchase(session['userid'])
            return redirect(url_for('my_orders'))
        elif choice=="CANCEL":
            return redirect(url_for('my_cart'))
    cart = get_cart(session['userid'])
    items = [(i[1], i[3], float(i[2])*float(i[3])) for i in cart]
    total = 0
    for i in cart:
        total += float(i[2])*int(i[3])
    return render_template('buy_confirm.html', signedin=True, id=session['userid'], name=session['name'], items=items, total=total)

@app.route("/buy/cart/<prodID>/")
def add_to_cart(prodID):
    #print(prodID)
    if 'userid' not in session:
        return redirect(url_for('signup'))
    add_product_to_cart(prodID, session['userid'])
    return redirect(url_for('view_product', id=prodID))

@app.route("/buy/cart/delete/")
def delete_cart():
    if 'userid' not in session:
        return redirect(url_for('signup'))
    empty_cart(session['userid'])
    return redirect(url_for('my_cart'))

@app.route("/buy/cart/delete/<prodID>/")
def delete_prod_cart(prodID):
    if 'userid' not in session:
        return redirect(url_for('signup'))
    remove_from_cart(session['userid'], prodID)
    return redirect(url_for('my_cart'))


app.config['SECRET_KEY'] = os.urandom(17)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True
sess.init_app(app)
if __name__=="__main__":
	app.run(hostname='192.168.43.163')
