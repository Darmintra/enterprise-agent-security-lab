from users import USERS
from customer_data import CUSTOMERS

def get_customer(user_id,customer_id):
	if customer_id in USERS[user_id]["Authorized Customers"]:
		return CUSTOMERS[customer_id]
	else:
		return ("Access Denied")