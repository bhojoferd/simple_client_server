import socket
import threading
from datetime import datetime
import os

HOST = "0.0.0.0"
PORT = 5000

DB_FILE = "database.txt"
LOG_FILE = "logs.txt"

lock = threading.Lock()
names = set()


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_transaction(action: str, name: str) -> None:
    # Only ADD/DEL are logged (as required)
    line = f"[{timestamp()}] {action}: {name}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def is_valid_name(name: str) -> bool:
    # DO NOT ACCEPT entries with numeric characters
    return name != "" and not any(ch.isdigit() for ch in name)


def load_database() -> None:
    global names
    if not os.path.exists(DB_FILE):
        # create empty file if missing
        open(DB_FILE, "a", encoding="utf-8").close()
        names = set()
        return

    loaded = set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            n = line.strip()
            if n:
                loaded.add(n)
    names = loaded


def save_database() -> None:
    # write all names (one per line)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for n in sorted(names):
            f.write(n + "\n")


def handle_command(cmd: str) -> str:
    """
    Commands:
      ADD <name>
      DEL <name>
      LIST
      HELP
      QUIT
    """
    parts = cmd.strip().split(" ", 1)
    action = parts[0].upper()

    if action == "HELP":
        return (
            "OK Commands: ADD <name> | DEL <name> | LIST | HELP | QUIT\n"
        )

    if action == "LIST":
        with lock:
            if not names:
                return "OK (empty)\n"
            return "OK " + ", ".join(sorted(names)) + "\n"

    if action in ("ADD", "DEL"):
        if len(parts) < 2:
            return "ERR Missing name. Example: ADD Juan\n"

        name = parts[1].strip()

        # validation rule: reject numeric characters
        if not is_valid_name(name):
            raise ValueError("Invalid name: numeric characters are not allowed.")

        with lock:
            if action == "ADD":
                if name in names:
                    return "ERR Name already exists.\n"
                names.add(name)
                save_database()
                log_transaction("ADD", name)
                return "OK Added.\n"

            if action == "DEL":
                if name not in names:
                    return "ERR Name not found.\n"
                names.remove(name)
                save_database()
                log_transaction("DEL", name)
                return "OK Deleted.\n"

    if action == "QUIT":
        return "OK Bye.\n"

    return "ERR Unknown command. Type HELP\n"


def client_thread(conn: socket.socket, addr):
    try:
        conn.sendall(b"OK Connected. Type HELP\n")
        buffer = b""

        while True:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data

            # process lines
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                cmd = line.decode("utf-8", errors="replace")

                try:
                    resp = handle_command(cmd)
                except ValueError as ve:
                    resp = f"ERR {ve}\n"
                except Exception as e:
                    resp = f"ERR Server error: {type(e).__name__}: {e}\n"

                conn.sendall(resp.encode("utf-8"))

                if cmd.strip().upper() == "QUIT":
                    return

    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    load_database()
    print(f"Loaded {len(names)} names from {DB_FILE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)

        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
            t.start()


if __name__ == "__main__":
    main()
