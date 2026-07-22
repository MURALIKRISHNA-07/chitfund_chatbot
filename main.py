from config.settings import GEMINI_API_KEY
from agents.conversation_agent import route

def main():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set")
        return

    print("Chit Fund Adviser - Type 'quit' to exit\n")
    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        history.append({"role": "user", "text": user_input})
        response = route(user_input, history)
        history.append({"role": "assistant", "text": response})

        print(f"\nAdviser: {response}\n")


if __name__ == "__main__":
    main()
