from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
try:
    Username = env_vars["Username"]
    Assistantname = env_vars["Assistantname"]
    GroqAPIKey = env_vars["GroqAPIKey"]
except KeyError as e:
    raise Exception(f"Missing environment variable: {e}")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn’t exist.
chatlog_path = "Data/ChatLog.json"
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open(chatlog_path, "w") as f:
        dump(messages, f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    return "\n".join([line for line in Answer.split("\n") if line.strip()])

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    current_date_time = datetime.datetime.now()
    return f"Real-time Information:\nDay: {current_date_time.strftime('%A')}\nDate: {current_date_time.strftime('%d')}\nMonth: {current_date_time.strftime('%B')}\nYear: {current_date_time.strftime('%Y')}\nTime: {current_date_time.strftime('%H')} hours, {current_date_time.strftime('%M')} minutes, {current_date_time.strftime('%S')} seconds.\n"

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    # Load the chat log from the JSON file.
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
    except (FileNotFoundError, ValueError):
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Add Google search results to the system chatbot messages.
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Generate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = AnswerModifier(Answer)

    # Append the answer to the chat log and save it.
    messages.append({"role": "assistant", "content": Answer})
    with open(chatlog_path, "w") as f:
        dump(messages, f)

    return Answer

# If this file is run directly, start the interactive chatbot loop.
if __name__ == "__main__":
    while True:
        user_input = input("Enter your query (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting program.")
            break
        response = RealtimeSearchEngine(user_input)
        print("\nAssistant's Response:\n", response)
