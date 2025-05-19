from flask import Flask, render_template, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

# Mock user account data
accounts = {
    "123456": {
        "name": "Dhruvi Nanotkar",
        "balance": 5000.00,
        "transactions": [
            {"date": "2023-05-01", "description": "Salary", "amount": 3000.00},
            {"date": "2023-05-05", "description": "Grocery", "amount": -150.00},
            {"date": "2023-05-10", "description": "Transfer to Jane", "amount": -500.00},
        ],
        "card_status": "active",
        "loans": [
            {"type": "personal", "amount": 10000.00, "emi": 925.00, "due_date": "15th monthly"}
        ]
    },
    "654321": {
        "name": "Vaishnavi Naik",
        "balance": 12000.50,
        "transactions": [
            {"date": "2023-05-02", "description": "Deposit", "amount": 2000.00},
            {"date": "2023-05-08", "description": "Online Shopping", "amount": -320.50},
        ],
        "card_status": "blocked",
        "loans": []
    }
}

def handle_account_balance(account_number):
    if not account_number:
        return "Please provide your account number to check your balance. Example: 'What's my balance for account 123456'?"
    
    if account_number in accounts:
        account = accounts[account_number]
        return f"Your current balance for account {account_number} is ${account['balance']:.2f}."
    else:
        return "Account not found. Please check your account number and try again."

def handle_recent_transactions(account_number):
    if not account_number:
        return "Please provide your account number to view transactions. Example: 'Show transactions for account 123456'"
    
    if account_number in accounts:
        account = accounts[account_number]
        transactions = account["transactions"][-3:]  # Get last 3 transactions
        
        if not transactions:
            return "No recent transactions found for this account."
            
        response = f"Recent transactions for account {account_number}:<br>"
        for tx in transactions:
            response += f"{tx['date']}: {tx['description']} - ${tx['amount']:.2f}<br>"
        return response
    else:
        return "Account not found. Please check your account number and try again."

def handle_card_status(account_number):
    if not account_number:
        return "Please provide your account number to check card status. Example: 'What's my card status for account 123456'?"
    
    if account_number in accounts:
        status = accounts[account_number]["card_status"]
        name = accounts[account_number]["name"]
        
        if status == "active":
            return f"Dear {name}, your card linked to account {account_number} is active and ready to use."
        elif status == "blocked":
            return f"Dear {name}, your card linked to account {account_number} is currently blocked. Please visit a branch or call customer support."
        else:
            return f"Your card status is: {status}"
    else:
        return "Account not found. Please check your account number and try again."

def handle_loan_info(account_number):
    if not account_number:
        return "Please provide your account number to check loan information. Example: 'What are my loans for account 123456'?"
    
    if account_number in accounts:
        account = accounts[account_number]
        loans = account["loans"]
        
        if not loans:
            return f"You currently have no active loans with account {account_number}."
            
        response = f"Loan information for account {account_number}:<br>"
        for loan in loans:
            response += f"Type: {loan['type'].title()}, Amount: ${loan['amount']:.2f}, "
            response += f"EMI: ${loan['emi']:.2f}, Due Date: {loan['due_date']}<br>"
        return response
    else:
        return "Account not found. Please check your account number and try again."

def handle_transfer_money():
    return ("For security reasons, I can't process transfers directly. "
            "Please use our mobile app or online banking for transfers. "
            "Would you like me to explain how to make a transfer?")

def handle_exchange_rate():
    rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.72,
        "JPY": 110.25,
        "CAD": 1.21
    }
    
    response = "Current exchange rates (USD base):<br>"
    for currency, rate in rates.items():
        response += f"1 USD = {rate} {currency}<br>"
    return response

def handle_branch_locations():
    branches = [
        {"location": "Main Branch", "address": "123 Financial St, New York", "hours": "9AM-5PM Mon-Fri"},
        {"location": "Downtown Branch", "address": "456 Commerce Ave, New York", "hours": "10AM-6PM Mon-Fri, 10AM-2PM Sat"},
        {"location": "Westside ATM Center", "address": "789 Urban Blvd, New York", "hours": "24/7"}
    ]
    
    response = "Our branch locations:<br>"
    for branch in branches:
        response += f"{branch['location']}: {branch['address']} (Hours: {branch['hours']})<br>"
    return response

def handle_customer_support():
    return ("For customer support, please call our 24/7 helpline at 1-800-XYZ-BANK (1-800-999-2265) "
            "or email us at support@xyzbank.com. Our representatives will be happy to assist you.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message'].lower()
    context = request.json.get('context', {})
    
    # Greeting detection
    if any(word in user_input for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return jsonify({
            "response": "Hello! Welcome to XYZ Bank's virtual assistant. How can I help you today?",
            "quick_replies": [
                "Check my balance",
                "View transactions",
                "Card information",
                "Loan details"
            ]
        })
    
    # Farewell detection
    if any(word in user_input for word in ["bye", "goodbye", "see you", "exit"]):
        return jsonify({
            "response": "Thank you for banking with XYZ Bank. Have a great day!",
            "farewell": True
        })
    
    # Account number detection
    account_match = re.search(r'account (\d+)', user_input)
    account_number = account_match.group(1) if account_match else context.get('account')
    
    # Determine intent and generate response
    if any(word in user_input for word in ["balance", "how much do i have"]):
        response = handle_account_balance(account_number)
        quick_replies = [
            f"Show transactions for account {account_number}" if account_number else "Show my transactions",
            "Exchange rates",
            "Branch locations"
        ]
    elif any(word in user_input for word in ["transaction", "history", "statement"]):
        response = handle_recent_transactions(account_number)
        quick_replies = [
            f"Check balance for account {account_number}" if account_number else "Check my balance",
            "Transfer money",
            "Customer support"
        ]
    elif any(word in user_input for word in ["card", "debit", "credit"]):
        response = handle_card_status(account_number)
        quick_replies = [
            "Report lost card",
            "Unblock my card",
            "Request new card"
        ]
    elif any(word in user_input for word in ["loan", "emi", "repayment"]):
        response = handle_loan_info(account_number)
        quick_replies = [
            "Apply for new loan",
            "Make loan payment",
            "View payment schedule"
        ]
    elif any(word in user_input for word in ["transfer", "send money"]):
        response = handle_transfer_money()
        quick_replies = [
            "Transfer between my accounts",
            "Send to another bank",
            "International transfer"
        ]
    elif any(word in user_input for word in ["exchange", "currency", "forex"]):
        response = handle_exchange_rate()
        quick_replies = [
            "Order foreign currency",
            "View historical rates",
            "Currency calculator"
        ]
    elif any(word in user_input for word in ["branch", "location", "atm"]):
        response = handle_branch_locations()
        quick_replies = [
            "Nearest branch to me",
            "ATM locations",
            "Business hours"
        ]
    elif any(word in user_input for word in ["support", "help", "contact"]):
        response = handle_customer_support()
        quick_replies = [
            "Call me back",
            "Live chat with agent",
            "Schedule appointment"
        ]
    else:
        response = "I'm not sure I understand. Could you please rephrase your question?"
        quick_replies = [
            "Check my balance",
            "View transactions",
            "Card information"
        ]
    
    return jsonify({
        "response": response,
        "quick_replies": quick_replies,
        "context": {"account": account_number}
    })

if __name__ == '__main__':
    app.run(debug=True)