from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config['MONGO_URI'] = 'mongodb+srv://expenseTracker:expenseTracker@expensetracker.7jvyp.mongodb.net/yourdbname?retryWrites=true&w=majority'
mongo = PyMongo(app)

# Predefined categories
EXPENSE_CATEGORIES = [
    'Transportation', 'Food', 'Education', 'Fuel', 'Rent', 'EMI', 'Shopping', 'Other'
]

INCOME_CATEGORIES = [
    'Salary', 'Bonus', 'Investments', 'Freelancing', 'Other'
]

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists!')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('home'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    expenses = list(mongo.db.expenses.find({'user_id': session['user_id']}))
    total_income = sum(float(e['amount']) for e in expenses if e.get('category') in INCOME_CATEGORIES)
    total_expense = sum(float(e['amount']) for e in expenses if e.get('category') in EXPENSE_CATEGORIES)
    balance = total_income - total_expense

    return render_template('home.html', total_income=total_income, total_expense=total_expense,
                           balance=balance, expenses=expenses)

@app.route('/view_transactions')
def view_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    expenses = list(mongo.db.expenses.find({'user_id': session['user_id']}))
    return render_template('transactions.html', expenses=expenses)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            category = request.form['category']
            date_str = request.form['date']
            
            # Parse the date
            expense_date = datetime.strptime(date_str, '%Y-%m-%d')

            mongo.db.expenses.insert_one({
                'user_id': session['user_id'],
                'amount': amount,
                'category': category,
                'date': expense_date
            })
            flash('Expense added successfully!')
            return redirect(url_for('home'))
        except ValueError:
            flash('Please enter valid data for amount and date.')
    return render_template('add_expense.html', categories=EXPENSE_CATEGORIES)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            category = request.form['category']
            date_str = request.form['date']
            
            # Parse the date
            income_date = datetime.strptime(date_str, '%Y-%m-%d')

            mongo.db.expenses.insert_one({
                'user_id': session['user_id'],
                'amount': amount,
                'category': category,
                'date': income_date
            })
            flash('Income added successfully!')
            return redirect(url_for('home'))
        except ValueError:
            flash('Please enter valid data for amount and date.')
    return render_template('add_income.html', categories=INCOME_CATEGORIES)

@app.route('/monthly_expense')
def monthly_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Grouping by month and year for user's expenses
    monthly_data = mongo.db.expenses.aggregate([
        {
            "$match": {"user_id": session['user_id']}
        },
        {
            "$group": {
                "_id": {
                    "month": {"$month": "$date"},
                    "year": {"$year": "$date"}
                },
                "total_expense": {
                    "$sum": {
                        "$cond": [{"$in": ["$category", EXPENSE_CATEGORIES]}, "$amount", 0]
                    }
                },
                "total_income": {
                    "$sum": {
                        "$cond": [{"$in": ["$category", INCOME_CATEGORIES]}, "$amount", 0]
                    }
                }
            }
        },
        {
            "$sort": {"_id.year": -1, "_id.month": -1}
        }
    ])

    # Format the monthly_data to include month names
    formatted_data = []
    months = []
    expenses = []
    incomes = []

    for item in monthly_data:
        month = item['_id']['month']
        year = item['_id']['year']
        total_expense = item['total_expense']
        total_income = item['total_income']
        
        # Store data for the chart
        months.append(datetime(year, month, 1).strftime('%B %Y'))  # Get month name and year
        expenses.append(total_expense)
        incomes.append(total_income)

        formatted_data.append({
            'month': datetime(year, month, 1).strftime('%B'),  # Get month name
            'year': year,
            'total_expense': total_expense,
            'total_income': total_income
        })

    return render_template('monthly_expense.html', monthly_data=formatted_data, months=months, expenses=expenses, incomes=incomes)

@app.route('/delete_transaction/<transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    mongo.db.expenses.delete_one({'_id': ObjectId(transaction_id)})
    flash('Transaction deleted successfully!')
    return redirect(url_for('view_transactions'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
