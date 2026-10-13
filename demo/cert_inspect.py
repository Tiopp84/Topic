"""Xem nhanh noi dung cert X.509 (dung de giai thich tren slide). Chay: python3 cert_inspect.py"""
from cryptography import x509
from cryptography.hazmat.backends import default_backend

for f in ["ca.crt", "server.crt", "attacker.crt"]:
    print("=" * 60)
    print(f"File: {f}")
    try:
        data = open(f, "rb").read()
        cert = x509.load_pem_x509_certificate(data, default_backend())
        print(f"  Subject : {cert.subject.rfc4514_string()}")
        print(f"  Issuer  : {cert.issuer.rfc4514_string()}")
        print(f"  Valid   : {cert.not_valid_before} -> {cert.not_valid_after}")
        print(f"  SAN     : {cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value if True else ''}")
    except FileNotFoundError:
        print("  (chua sinh cert, chay ./generate_certs.sh truoc)")
    except Exception as e:
        print(f"  (khong doc SAN: {e})")
