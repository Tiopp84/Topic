"""
T30 - Custom HTTPS/TLS Client (validate cert day du)
Chay: python3 client_tls.py
Minh hoa: handshake -> lay cipher + cert -> gui HTTP GET -> nhan reply.
Neu server dung attacker.crt -> se loi CERTIFICATE_VERIFY_FAILED (chong MITM).
"""
import socket
import ssl
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.join(BASE, "ca.crt")
HOST, PORT = "127.0.0.1", 8443

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_verify_locations(CA)   # chi tin MiniCA cua nhom
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.check_hostname = True       # bat buoc khop CN/SAN=localhost

# Ket noi toi 127.0.0.1 nhung SNI/hostname phai la "localhost" de khop cert.
with socket.create_connection((HOST, PORT)) as sock:
    with ctx.wrap_socket(sock, server_hostname="localhost") as ssock:
        print(f"[CLIENT] TLS version : {ssock.version()}")
        print(f"[CLIENT] Cipher       : {ssock.cipher()}")
        cert = ssock.getpeercert()
        print(f"[CLIENT] Peer subject : {cert.get('subject')}")
        print(f"[CLIENT] Peer issuer  : {cert.get('issuer')}")
        print(f"[CLIENT] SAN          : {cert.get('subjectAltName')}")
        print(f"[CLIENT] Valid        : {cert.get('notBefore')} -> {cert.get('notAfter')}")
        ssock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        data = b""
        while True:
            chunk = ssock.recv(4096)
            if not chunk:
                break
            data += chunk
        print("[CLIENT] ---- Server reply ----")
        print(data.decode(errors="replace"))
        print("[CLIENT] OK: cert hop le, du lieu duoc ma hoa (xem Wireshark: Application Data).")
