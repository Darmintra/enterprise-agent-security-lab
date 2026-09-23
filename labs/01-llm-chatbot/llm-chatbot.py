from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline

revision_id = "fe8a4ea1ffedaf415f4da2f062534de366a451e6"

model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    revision=revision_id,
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=False,
)

tokenizer = AutoTokenizer.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    revision=revision_id
)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    return_full_text=False,
    max_new_tokens=500,
    do_sample=False
)

print("What do you want?")
user_input = input()

messages = [{"role":"user", "content": user_input}]
response = generator(messages)

print(response[0]["generated_text"])

while True:
    print("-" *100) # Horizontal separator
    print("What do you want?")
    user_input = input("\033[92mType something, or X to exit: \033[0m") # Ask the user for input in green color
    if user_input in ['X', 'x']: # If user types X or x, exit the program
        print("Exiting.")
        break
    else:
        messages = [{"role":"user", "content": user_input}]
        response = generator(messages)
        print(response[0]["generated_text"])
