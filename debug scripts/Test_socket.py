import socket
from threading import Thread
import time

# Host and port must match the game's configuration
HOST = '127.0.0.1'
PORT = 12346

# --- The predictable, hardcoded response ---
# This is built from three parts, just like in the real main.py
# Part 1: The message payload with per-paragraph emotions
payload = "This is a happy message|||joy&&&This is a sad message|||sadness"
# Part 2: The action to be taken
action = "play_game"

# We combine them with the "/g" separator to create the final, correctly formatted string
# This is the exact structure the game's parser is expecting.
RESPONSE_STRING = f"{payload}/g{action}"
# --- End of response definition ---

def handle_client(client_socket, address):
    """
    This function handles the connection for a single client (the game).
    """
    print(f"[NEW CONNECTION] {address} connected.")
    try:
        while True:
            # Wait to receive a message from the game.
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                # If the message is empty, the client has disconnected.
                print(f"[CONNECTION CLOSED] {address} disconnected.")
                break

            print(f"[RECEIVED from {address}] {message}")

            # --- MODIFIED LOGIC ---
            # The game sends multiple messages per turn. We only want to reply
            # to the one that contains the actual user input, which the game
            # formats with a "/g" separator. We ignore all other messages.
            if "/g" in message:
                # This is the message we were waiting for.
                # Send the hardcoded response back to the game.
                print(f"[SENDING to {address}] {RESPONSE_STRING}")
                client_socket.sendall(RESPONSE_STRING.encode('utf-8'))
            else:
                # This is a preliminary message like "chatbot/m" or "ok_ready".
                # We ignore it and do not send a reply.
                print("[IGNORING] This is not the main user message. Waiting for the next one.")
            # --- END MODIFICATION ---

    except ConnectionResetError:
        print(f"[CONNECTION RESET] {address} forcefully closed the connection.")
    except Exception as e:
        print(f"[ERROR] An error occurred with {address}: {e}")
    finally:
        # Clean up the connection
        client_socket.close()

def main():
    """
    Main function to set up and run the server.
    """
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the socket to be reused immediately after closing
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address
    server.bind((HOST, PORT))
    
    # Start listening for incoming connections
    server.listen()
    print(f"[*] Fake server listening on {HOST}:{PORT}")
    print("[*] Waiting for Monika After Story to connect...")
    print("[*] Press Ctrl+C to stop the server.")

    try:
        while True:
            # Wait for a connection
            client, address = server.accept()
            # Create a new thread to handle the client so the main loop isn't blocked
            thread = Thread(target=handle_client, args=(client, address))
            thread.start()
    except KeyboardInterrupt:
        print("\n[*] Server is shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
