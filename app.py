from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection
from datetime import datetime
import razorpay
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
import random
import bcrypt
from functools import wraps
import os
import razorpay.errors

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                return "Access denied"

            return f(*args, **kwargs)
        return wrapper
    return decorator


app = Flask(__name__)

 # used for sessions

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY is not set in environment variables")
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise ValueError("Razorpay keys are not set in environment variables")



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        # password = request.form["password"]
        raw_password = request.form["password"]
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


        role = request.form["role"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
          "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, role)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "student":
                return redirect(url_for("student_dashboard"))
            else:
                return redirect(url_for("librarian_dashboard"))
        else:
            return "Invalid email or password"

    return render_template("login.html")


@app.route("/student")
@login_required(role="student")
def student_dashboard():
    return render_template("student_dashboard.html")


@app.route("/librarian")
@login_required(role="librarian")
def librarian_dashboard():
    return render_template("librarian_dashboard.html")



@app.route("/add_book", methods=["GET", "POST"])
@login_required(role="librarian")
def add_book():
    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        category = request.form["category"]
        copies = request.form["copies"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (name, author, publisher, category, copies)
            VALUES (?, ?, ?, ?, ?)
        """, (name, author, publisher, category, copies))
        conn.commit()
        conn.close()

        return "Book added successfully!"

    return render_template("add_book.html")


@app.route("/books")
@login_required()
def view_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()

    return render_template("books.html", books=books)


@app.route("/borrow/<int:book_id>")
@login_required(role="student")
def borrow_book(book_id):
    # Only students can borrow
    # if session.get("role") != "student":
    #     return "Only students can borrow books."

    user_id = session.get("user_id")

    conn = get_connection()
    cursor = conn.cursor()

    # Check how many active borrows the user has
    cursor.execute("""
        SELECT COUNT(*) FROM borrows 
        WHERE user_id = ? AND status = 'borrowed'
    """, (user_id,))
    count = cursor.fetchone()[0]

    if count >= 3:
        conn.close()
        return "Borrow limit reached (Max 3 books allowed)."

    # Check book availability
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    if not book or book["copies"] <= 0:
        conn.close()
        return "Book not available."

    # Insert into borrows table
    borrow_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO borrows (user_id, book_id, borrow_date, status)
        VALUES (?, ?, ?, ?)
    """, (user_id, book_id, borrow_date, "borrowed"))

    # Reduce book copies
    cursor.execute("""
        UPDATE books SET copies = copies - 1 WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("view_books"))

@app.route("/my_borrows")
@login_required(role="student")
def my_borrows():
    # if session.get("role") != "student":
    #     return "Access denied."

    user_id = session.get("user_id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT borrows.id as borrow_id, 
               books.name, 
               borrows.borrow_date, 
               borrows.status,
               borrows.fine
        FROM borrows
        JOIN books ON borrows.book_id = books.id
        WHERE borrows.user_id = ?
    """, (user_id,))

    borrows = cursor.fetchall()
    conn.close()

    return render_template("my_borrows.html", borrows=borrows)


@app.route("/return/<int:borrow_id>")
@login_required(role="student")
def return_book(borrow_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM borrows WHERE id = ?", (borrow_id,))
    borrow = cursor.fetchone()

    if not borrow or borrow["status"] != "borrowed":
        conn.close()
        return "Invalid return request."

    book_id = borrow["book_id"]
    borrow_date = datetime.strptime(borrow["borrow_date"], "%Y-%m-%d")
    return_date = datetime.now()

    days_borrowed = (return_date - borrow_date).days

    fine = 0
    if days_borrowed > 7:
        fine = (days_borrowed - 7) * 10

    cursor.execute("""
        UPDATE borrows 
        SET status = 'returned', return_date = ?, fine = ?
        WHERE id = ?
    """, (return_date.strftime("%Y-%m-%d"), fine, borrow_id))

    cursor.execute("UPDATE books SET copies = copies + 1 WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()

    return f"Book returned successfully. Fine: ₹{fine}"

@app.route("/pay_fine/<int:borrow_id>", methods=["GET", "POST"])
@login_required(role="student")
def pay_fine(borrow_id):
    # if session.get("role") != "student":
    #     return "Access denied."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM borrows WHERE id = ?", (borrow_id,))
    borrow = cursor.fetchone()

    if not borrow or borrow["fine"] <= 0:
        conn.close()
        return "No fine to pay."

    if request.method == "POST":
        method = request.form["method"]
        amount = borrow["fine"]
        user_id = session.get("user_id")

        txn_id = "TXN" + str(random.randint(100000, 999999))
        date = datetime.now().strftime("%Y-%m-%d")

        # Insert into payments
        cursor.execute("""
            INSERT INTO payments (user_id, amount, status, method, transaction_id, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, "PAID", method, txn_id, date))

        # Reset fine to 0 after payment
        cursor.execute("""
            UPDATE borrows SET fine = 0 WHERE id = ?
        """, (borrow_id,))

        conn.commit()
        conn.close()

        return f"Payment successful! Transaction ID: {txn_id}"

    amount = borrow["fine"]
    conn.close()
    return render_template("pay_fine.html", amount=amount)



@app.route("/create_order/<int:borrow_id>")
@login_required(role="student")
def create_order(borrow_id):
    # if session.get("role") != "student":
    #     return "Access denied"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fine FROM borrows WHERE id = ?", (borrow_id,))
    record = cursor.fetchone()
    conn.close()

    if not record or record["fine"] <= 0:
        return "No fine to pay"

    amount = record["fine"] * 100  # Razorpay uses paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template("razorpay_checkout.html", order_id=order["id"], amount=record["fine"], key=RAZORPAY_KEY_ID, borrow_id=borrow_id)

@app.route("/payment_success")
@login_required()
def payment_success():
    payment_id = request.args.get("payment_id")
    order_id = request.args.get("order_id")
    borrow_id = request.args.get("borrow_id")

    user_id = session.get("user_id")

    conn = get_connection()
    cursor = conn.cursor()

    # Get fine
    cursor.execute("SELECT fine FROM borrows WHERE id = ?", (borrow_id,))
    fine = cursor.fetchone()["fine"]

    # Save payment
    cursor.execute("""
        INSERT INTO payments (user_id, amount, status, method, transaction_id, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, fine, "PAID", "Razorpay", payment_id, datetime.now().strftime("%Y-%m-%d")))

    # Reset fine
    cursor.execute("UPDATE borrows SET fine = 0 WHERE id = ?", (borrow_id,))

    conn.commit()
    conn.close()

    return f"Payment Successful! Transaction ID: {payment_id}"






@app.route("/verify_payment", methods=["POST"])
@login_required()
def verify_payment():
    payment_id = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")
    borrow_id = request.form.get("borrow_id")

    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed!"

    # Now safe to update DB
    user_id = session.get("user_id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT fine FROM borrows WHERE id = ?", (borrow_id,))
    fine = cursor.fetchone()["fine"]

    cursor.execute("""
        INSERT INTO payments (user_id, amount, status, method, transaction_id, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, fine, "PAID", "Razorpay", payment_id, datetime.now().strftime("%Y-%m-%d")))

    cursor.execute("UPDATE borrows SET fine = 0 WHERE id = ?", (borrow_id,))

    conn.commit()
    conn.close()

    return f"Payment verified successfully! Transaction ID: {payment_id}"




@app.route("/payment_history")
@login_required(role="student")
def payment_history():
    # if session.get("role") != "student":
    #     return "Access denied"

    user_id = session.get("user_id")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE user_id = ?", (user_id,))
    payments = cursor.fetchall()
    conn.close()

    return render_template("payment_history.html", payments=payments)



@app.route("/admin_payments")
@login_required(role="librarian")
def admin_payments():
    # if session.get("role") != "librarian":
    #     return "Access denied"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    conn.close()

    return render_template("admin_payments.html", payments=payments)

@app.route("/logout")
@login_required()
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
