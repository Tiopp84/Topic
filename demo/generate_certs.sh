#!/bin/bash
# T30 Demo - Sinh CA + Server cert + Attacker cert (giả mạo để demo MITM)
set -e
cd "$(dirname "$0")"

echo "[*] Generating Mini CA..."
openssl req -x509 -newkey rsa:2048 -sha256 -days 365 -nodes \
  -keyout ca.key -out ca.crt \
  -subj "/C=VN/O=LTM-T30/CN=MiniCA"

echo "[*] Generating Server key + CSR (CN=localhost, SAN=localhost)..."
openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr \
  -subj "/C=VN/O=LTM-T30/CN=localhost"
cat > server.ext <<EOF
subjectAltName=DNS:localhost,DNS:www.localhost,IP:127.0.0.1
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 365 -sha256 -extfile server.ext

echo "[*] Generating ATTACKER self-signed cert (CN=localhost nhưng CA lạ)..."
openssl req -x509 -newkey rsa:2048 -sha256 -days 365 -nodes \
  -keyout attacker.key -out attacker.crt \
  -subj "/C=VN/O=Attacker/CN=localhost"

rm -f server.csr server.ext ca.srl
echo "[OK] Files: ca.crt ca.key server.crt server.key attacker.crt attacker.key"
openssl x509 -in server.crt -noout -subject -issuer -dates
