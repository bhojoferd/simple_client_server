import socket
import sys

DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5000


def recv_line(sock: socket.socket) -> str:
    """Receive until newline."""
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            # connection closed
            return data.decode("utf-8", errors="replace")
        data += chunk
        if chunk == b"\n":
            return data.decode("utf-8", errors="replace")


def main():
    # Usage:
    #   python3 client.py
    #   python3 client.py 127.0.0.1 5000
    ip = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_IP
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_PORT

    print(f"Simple Name DB Client -> {ip}:{port}")
    print("Commands: ADD <name>, DEL <name>, LIST, HELP, QUIT")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        # read welcome line
        print(recv_line(s).strip())

        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue

            s.sendall((cmd + "\n").encode("utf-8"))

            # read 1 response line from server
            resp = recv_line(s).strip()
            print(resp)

            if cmd.upper() == "QUIT":
                break


if __name__ == "__main__":
    main()
