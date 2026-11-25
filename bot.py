#!/usr/bin/env python3
"""
Interactive Command-Line GPT Chatbot
Powered by OpenAI API
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

# Load environment variables from .env file
load_dotenv()


def get_api_key() -> str:
    """Retrieve OpenAI API key from environment or prompt user."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        print("\n🔑 OpenAI API Key not found in .env file.")
        try:
            api_key = input("Enter your OpenAI API Key (sk-...): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if not api_key:
            print("❌ Error: API key cannot be empty. Please check your key.")
            sys.exit(1)

        try:
            save = input("Do you want to save this key to .env for future use? (y/n): ").strip().lower()
            if save in ("y", "yes"):
                with open(".env", "a") as f:
                    f.write(f"\nOPENAI_API_KEY={api_key}\n")
                print("✅ Saved to .env!")
        except (KeyboardInterrupt, EOFError):
            pass

    return api_key


def main():
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

    # Configuration
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    system_prompt = "You are a helpful, knowledgeable, and concise AI assistant."

    conversation_history = [
        {"role": "system", "content": system_prompt}
    ]

    print("\n" + "=" * 55)
    print("🤖 Welcome to your Personal GPT Bot!")
    print(f"📦 Active Model: {model}")
    print("Commands:")
    print("  /clear          - Reset conversation memory")
    print("  /model <name>   - Change active model (e.g. /model gpt-4o)")
    print("  /system <text>  - Change system instructions")
    print("  /history        - View message count")
    print("  /exit or exit   - Quit chatbot")
    print("=" * 55 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        # Handle Commands
        cmd = user_input.lower()
        if cmd in ("exit", "quit", "/exit", "/quit"):
            print("Goodbye! 👋")
            break

        if cmd == "/clear":
            conversation_history = [{"role": "system", "content": system_prompt}]
            print("🧹 Conversation memory cleared!\n")
            continue

        if cmd.startswith("/model "):
            new_model = user_input.split(" ", 1)[1].strip()
            if new_model:
                model = new_model
                print(f"🔄 Switched model to: {model}\n")
            continue

        if cmd.startswith("/system "):
            system_prompt = user_input.split(" ", 1)[1].strip()
            conversation_history[0] = {"role": "system", "content": system_prompt}
            print(f"⚙️ System prompt updated!\n")
            continue

        if cmd == "/history":
            msg_count = len(conversation_history) - 1
            print(f"📊 Conversation contains {msg_count} messages.\n")
            continue

        if cmd == "/help":
            print("\nCommands:")
            print("  /clear         - Reset conversation memory")
            print("  /model <name>  - Change active model")
            print("  /system <text> - Change assistant persona/system prompt")
            print("  /history       - Show current message count")
            print("  /exit          - Exit the chat\n")
            continue

        # Append user message
        conversation_history.append({"role": "user", "content": user_input})

        print("\nGPT: ", end="", flush=True)

        try:
            # Stream response in real-time
            stream = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                stream=True,
            )

            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta

            print("\n")
            conversation_history.append({"role": "assistant", "content": full_reply})

        except AuthenticationError:
            print("\n❌ Error: Authentication failed. Please check that your OPENAI_API_KEY is valid.")
            conversation_history.pop()  # Rollback last user message
        except RateLimitError as e:
            print(f"\n⚠️ Rate limit exceeded or quota reached: {e}")
            conversation_history.pop()
        except APIConnectionError:
            print("\n❌ Network Error: Could not connect to OpenAI API. Check your internet connection.")
            conversation_history.pop()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            conversation_history.pop()


if __name__ == "__main__":
    main()
