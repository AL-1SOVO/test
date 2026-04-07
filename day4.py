import json
def get_ai_response(user_input):
    try:
        raise ConnectionError("Failed to connect to AI service.")
        print("loading...")
        return f"ai get your imformation:{user_input}"
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, I encountered an error."

def start_chat():
    filename = "chat_history.json"
    print("start chat with ai, type 'exit' to end the chat.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chat ended.")
            break

        ai_response = get_ai_response(user_input)
        print(f"AI: {ai_response}")

        chat_history = {
            "user": user_input,
            "ai": ai_response
        }

        with open(filename, 'a') as file:
            json.dump(chat_history, file)
            file.write('\n')
if __name__ == "__main__":
    start_chat()