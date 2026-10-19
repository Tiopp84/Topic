
from cryptography import x509
from cryptography.hazmat.backends import default_backend

for f in ["ca.crt", "server.crt", "attacker.crt"]:
    print("=" * 60)
    print(f"File: {f}")
    try:
        data = open(f, "rb").read()
    except FileNotFoundError:
        print("  (chua sinh cert, chay ./generate_certs.sh truoc)")
        continue

    cert = x509.load_pem_x509_certificate(data, default_backend())
    print(f"  Subject : {cert.subject.rfc4514_string()}")
    print(f"  Issuer  : {cert.issuer.rfc4514_string()}")
    print(f"  Valid   : {cert.not_valid_before_utc} -> {cert.not_valid_after_utc}")

    # Basic Constraints:_CA bat buoc co CA:TRUE, server cert thi CA:FALSE
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        print(f"  CA      : {bc.ca}")
    except x509.ExtensionNotFound:
        print("  CA      : (khong co basicConstraints)")

    # SAN chi cert voi HOSTNAME moi can (server/attacker). CA khong can.
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        hosts = ", ".join(str(n.value) for n in san)
        print(f"  SAN     : {hosts}")
    except x509.ExtensionNotFound:
        print("  SAN     : (khong co - binh thuong voi CA cert)")
