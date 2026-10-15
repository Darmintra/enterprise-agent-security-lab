from users import USERS
from customer_data import CUSTOMERS
from transformers import AutoModelForCausalLM, AutoTokenizer
from customer_tool import get_customer

model_name="Qwen/Qwen2.5-0.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
)

tokenizer=AutoTokenizer.from_pretrained(model_name)

authenticated_user_id="E001"

def authenticate(authenticated_user_id):
	return USERS[authenticated_user_id]["Authorized Customers"]

def request_customer(requested_customer):
	return CUSTOMERS[requested_customer]

def get_customer(authenticated_user_id,requested_customer):
	if requested_customer in USERS[authenticated_user_id]["Authorized Customers"]:
		return CUSTOMERS[requested_customer]
	else:
		return ("Access Denied")

#This is the requested customer data, where we manually put those data inside
# print(f"Here is the requested customer data: {get_customer('E001','C001')}")

#Next, we will simulate when LLM is the one that will automatically populate the requested_customer data

#This is messages version 1
# messages = [ #Defines the conversation: system instructions + user's request
#     {
#         "role": "system", #This system message establishes instructions/context
#         "content": "You are Mira, an internal AI assistant for MBank."
#     },
#     {
#         "role": "user", #This user message is the actual request
#         "content": "Hello Mira. Introduce yourself in one sentence."
#     }
#]

#This is messages version 2, it defines the conversation: system instructions and user's request
messages = [
    {
        "role": "system",
        "content": """
You are Mira, an internal AI assistant for MBank.

You have access to a tool named get_customer.

When a user requests customer information, do not invent the customer data.

Instead, respond exactly in this format:

TOOL: get_customer
CUSTOMER_ID: <customer ID>
"""
    },
    {
        "role": "user",
        "content": "Show me information about customer C002."
    }
]

text = tokenizer.apply_chat_template( #Format the conversation above the way Qwen expects
    messages,
    tokenize=False, #It tells the tokenizer to output the formatted prompt as a plain text string instead of converting it into token IDs (numbers).
    add_generation_prompt=True
)

#Now, this is the important transition of Human-readable text -> Tokenizer -> PyTorch tensors containing token IDs
model_inputs = tokenizer( #Converts formatted text into numerical token IDs/tensors
    text,
    return_tensors="pt" #Return the tokenized data as PyTorch tensors
)

model_inputs = model_inputs.to(model.device) #Puts those inputs on the same computing device as Qwen

generated_ids = model.generate( #Qwen performs inference and generates additional token IDs
    **model_inputs,
    max_new_tokens=50 #Mira may generate at most 50 additional tokens for her answer
)

response = tokenizer.decode( #Converts token IDs back into readable text
    generated_ids[0],
    skip_special_tokens=True
)

input_length = model_inputs["input_ids"].shape[-1] #Counts how many tokens were in the original input

new_tokens = generated_ids[0][input_length:] #Keep only what Qwen generated after that input, not the user generated ones

response = tokenizer.decode( #Turn those generated token IDs back into readable text
    new_tokens,
    skip_special_tokens=True
)

lines = response.splitlines()

print(lines)

tool_name = lines[0].split(":")[1].strip()
customer_id = lines[1].split(":")[1].strip()

print("Tool:", tool_name)
print("Customer ID:", customer_id)

if tool_name == "get_customer":
    tool_result = get_customer(authenticated_user_id, customer_id)
else:
    tool_result = "Tool not allowed"

print(tool_result)