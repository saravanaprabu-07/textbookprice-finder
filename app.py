from flask import Flask, render_template, request, redirect, session
import json, os, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_FILE = os.path.join(BASE_DIR, "users.json")
BOOK_FILE = os.path.join(BASE_DIR, "books.json")
LOGIN_FILE = os.path.join(BASE_DIR, "logins.json")

# ---------- FILE ----------
def load_file(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file) as f:
        return json.load(f)

def save_file(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------- EMAIL ALERT ----------
def notify_admin(user_email):
    try:
        sender = os.environ.get("EMAIL_USER")
        password = os.environ.get("EMAIL_PASS")

        if not sender or not password:
            print("Email not configured")
            return

        msg = MIMEText(f"🔔 {user_email} just logged in")
        msg["Subject"] = "Login Alert"
        msg["From"] = sender
        msg["To"] = sender

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Email error:", e)

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_file(USER_FILE)
        email = request.form["email"]
        password = request.form["password"]

        for u in users:
            if u["email"] == email:
                return "User already exists"

        users.append({
            "email": email,
            "password": password,
            "role": "user"
        })

        save_file(USER_FILE, users)
        return redirect("/")

    return render_template("signup.html")

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_file(USER_FILE)
        email = request.form["email"]
        password = request.form["password"]

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user"] = email
                session["role"] = u["role"]

                logins = load_file(LOGIN_FILE)
                logins.append({"email": email})
                save_file(LOGIN_FILE, logins)

                notify_admin(email)

                return redirect("/home")

        return "Invalid Login"

    return render_template("login.html")

# ---------- HOME ----------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    books = load_file(BOOK_FILE)
    search = request.args.get("search", "").lower()

    if search:
        books = [
            b for b in books
            if search in b["title"].lower()
            or search in b["subject"].lower()
            or search in str(b["price"])
        ]

    return render_template("index.html", books=books)

# ---------- ADD BOOK ----------
@app.route("/add_book", methods=["POST"])
def add_book():
    if session.get("role") != "admin":
        return "Access Denied"

    books = load_file(BOOK_FILE)

    new = {
        "id": len(books) + 1,
        "title": request.form["title"],
        "author": request.form["author"],
        "subject": request.form["subject"],
        "price": int(request.form["price"]),
        "holder": request.form["holder"]
    }

    books.append(new)
    save_file(BOOK_FILE, books)

    return redirect("/home")

# ---------- DELETE BOOK ----------
@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):
    if session.get("role") != "admin":
        return "Access Denied"

    books = load_file(BOOK_FILE)

    books = [b for b in books if b["id"] != book_id]

    # reset IDs
    for i, b in enumerate(books):
        b["id"] = i + 1

    save_file(BOOK_FILE, books)

    return redirect("/home")

# ---------- VIEW LOGINS ----------
@app.route("/view_logins")
def view_logins():
    if session.get("role") != "admin":
        return "Access Denied"

    logins = load_file(LOGIN_FILE)
    return render_template("logins.html", logins=logins)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
