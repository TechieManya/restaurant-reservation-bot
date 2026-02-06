"""Restaurant Reservation Bot - CLI entry point."""

from bot import process_input

WELCOME = """
Welcome to Restaurant Reservation Bot!
I can help you book a table, view our menu, or cancel a reservation.
Type 'help' for commands, 'quit' to exit.
"""


def main():
    print(WELCOME)
    state = {}
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        response, state = process_input(user_input, state)
        
        if response is None:
            print("Goodbye!")
            break
        
        if "\n" in response:
            print(f"\n{response}")
        else:
            print(f"\nBot: {response}")


if __name__ == "__main__":
    main()
