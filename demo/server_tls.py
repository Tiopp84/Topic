"""
T30 - Custom HTTPS/TLS Server (Python socket + ssl)
Chay: python3 server_tls.py [certfile] [keyfile]
Mac dinh dung server.crt/server.key (do MiniCA ky).
De demo MITM: python3 server_tls.py attacker.crt attacker.key
"""
import socket
import ssl
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CERT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "server.crt")
KEY = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "server.key")
HOST, PORT = "127.0.0.1", 8443

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # cho phep 1.2 + 1.3
ctx.load_cert_chain(CERT, KEY)
# Chon cipher manh, uu tien PFS (ECDHE + AEAD). TLS 1.3 cipher tu dong.
try:
    ctx.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384")
except Exception as e:
    print(f"[warn] set_ciphers: {e}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[SERVER] Listening on {HOST}:{PORT} with TLS 1.2+ ...")
    print(f"[SERVER] Cert: {CERT}")
    with ctx.wrap_socket(sock, server_side=True) as ssock:
        while True:
            conn, addr = ssock.accept()
            print(f"[SERVER] Handshake OK with {addr}")
            print(f"         cipher={conn.cipher()} version={conn.version()}")
            try:
                data = conn.recv(4096)
                print(f"[SERVER] recv ({len(data)} bytes): {data[:200]!r}")
                body = b"Hello Secure World over TLS! (T30 demo)"
                resp = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
                        b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                        b"Connection: close\r\n\r\n" + body)
                conn.sendall(resp)
            except Exception as e:
                print(f"[SERVER] error: {e}")
            finally:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                conn.close()
