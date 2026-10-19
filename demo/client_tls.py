
import socket
import ssl
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.join(BASE, "ca.crt")
HOST, PORT = "127.0.0.1", 8443

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_verify_locations(CA)   # chi tin MiniCA cua nhom
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.check_hostname = True       # bat buoc khop CN/SAN=localhost


def die(msg):
    print(f"[CLIENT] XX {msg}")
    sys.exit(1)


try:
    # Ket noi toi 127.0.0.1 nhung SNI/hostname phai la "localhost" de khop cert.
    sock = socket.create_connection((HOST, PORT), timeout=5)
except ConnectionRefusedError:
    die("khong ket noi duoc server (chua chay server_tls.py?)")
except OSError as e:
    die(f"loi ket noi: {e}")

try:
    ssock = ctx.wrap_socket(sock, server_hostname="localhost")
except ssl.SSLCertVerificationError as e:
    print("[CLIENT] XX HANDSHAKE FAILED - cert khong duoc tin cay")
    print(f"[CLIENT]    reason : {e.reason}")
    print(f"[CLIENT]    detail : {e.verify_message}")
    print(f"[CLIENT]    code   : {e.verify_code}")
    print("[CLIENT]    -> issuer khong nam trong truststore (ca.crt)")
    sys.exit(1)
except ssl.SSLError as e:
    die(f"TLS handshake loi: {e}")
except OSError as e:
    die(f"socket loi trong handshake: {e}")

with ssock:
    try:
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
    except (ssl.SSLError, OSError) as e:
        die(f"loi khi trao doi du lieu: {e}")
