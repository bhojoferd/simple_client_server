import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

def main():
    print("Simple Name DB Client")
    print("Commands: ADD <name>, DEL <name>, LIST, HELP, QUIT")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        # receive welcome
        welcome = s.recv(1024).decode("utf-8", errors="replace")
        print(welcome.strip())

        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue

            # send with newline so server knows end-of-command
            s.sendall((cmd + "\n").encode("utf-8"))

            resp = s.recv(4096).decode("utf-8", errors="replace")
            print(resp.strip())

            if cmd.upper() == "QUIT":
                break


if __name__ == "__main__":
    main()
