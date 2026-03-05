# 📚 Digital Library System


A full-stack **Flask-based Library Management System** that automates book circulation, fine calculation, and secure online fine payment using **Razorpay** with **role-based authentication**.


## 🚀 Overview

This system streamlines library operations by providing separate dashboards for **students** and **librarians**.

- Students can borrow/return books and pay fines online
- Librarians manage inventory and monitor transactions

It demonstrates real-world backend concepts:

- Authentication & authorization  
- Transactional workflows  
- Payment gateway integration  
- Environment-based configuration  
- Modular architecture  

## ✨ Key Features

### 🔐 Authentication & Authorization
- Secure user registration & login
- Password hashing using **bcrypt**
- Role-based access control (Student / Librarian)
- Protected routes using custom decorators
- Session management

### 🎓 Student Functionalities
- View available books
- Borrow books (with borrowing limit)
- Return books
- Automatic fine calculation for late returns
- Pay fines online via **Razorpay**
- View borrow history
- View payment history

### 🛠 Librarian Functionalities
- Add new books
- Manage book inventory
- Track issued & returned books
- View all payment transactions

### 💳 Razorpay Integration
- Order creation
- Secure payment signature verification
- Transaction storage
- Fine reset after successful payment

## 🔄 Application Workflow

1. User registers and logs in  
2. Student borrows a book  
3. Late return → fine calculated automatically  
4. Razorpay order is created  
5. Payment is completed & verified  
6. Fine cleared & transaction stored  

## 🏗 Tech Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- Jinja2

### Database
- SQLite / MySQL

### Security
- bcrypt
- Environment variables

### Payment Gateway
- Razorpay

```text
digital-library-system/
│
├── app.py                 # Main Flask application
├── config.py              # Environment & Razorpay configuration
├── database.py            # Database connection
├── init_db.py             # Database initialization
├── requirements.txt
├── .env.example
│
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   └── librarian_dashboard.html
│
└── static/
    └── style.css
```


        

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
RAZORPAY_KEY_ID=your_key_here
RAZORPAY_KEY_SECRET=your_secret_here
FLASK_SECRET_KEY=your_secret_here
```


## 🛠 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Ssanjayadav/digital-library-system.git
cd digital-library-system
```

### 2️⃣ Create & activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

Create a `.env` file using `.env.example`

### 5️⃣ Initialize the database

```bash
python init_db.py
```

### 6️⃣ Run the application

```bash
python app.py
```


## 🔑 Demo Credentials

### Student
Email: `student@test.com`  
Password: `123456`

### Librarian
Email: `admin@test.com`  
Password: `123456`

## 🔐 Security Implementations

- Password hashing using bcrypt  
- Role-based route protection  
- Razorpay signature verification  
- Secrets stored in environment variables  
- `.env` excluded via `.gitignore`  

---

## 🎯 Key Learning Outcomes

- Implemented role-based authentication in Flask  
- Designed complete borrow → return → fine → payment workflow  
- Integrated a real payment gateway  
- Managed secure environment configuration  
- Built modular backend architecture  

---

## 🌍 Real-World Use Case

Suitable for:

- Schools  
- Colleges  
- Private libraries  

to automate book management and fine collection.

## 🔮 Future Enhancements

- Email notifications for due dates  
- Book search & filtering  
- REST API version  
- Docker deployment  
- Admin analytics dashboard  


## 👨‍💻 Author

**Sanjay Yadav**

---

## 📄 License

This project is for educational purposes.
