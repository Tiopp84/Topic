# 08 — Đọc hiểu demo: từng dòng code, cert, Wireshark, MITM

> Thuộc Slide 9-10 roadmap. File này vừa đọc vừa chạy lệnh trong `../demo/`.

## 1. Tổng quan kiến trúc demo

```
┌─────────────┐   TCP 8443 + TLS    ┌─────────────┐
│ client_tls  │ ─────────────────── │ server_tls  │
│ trust: ca.crt│  ClientHello...     │ cert: server│
│ check_host  │  ...AppData(AES)    │ .crt+.key   │
└─────────────┘                     └─────────────┘
        ▲                                    ▲
        │ Wireshark: tls || tcp.port==8443   │
        │ attacker.crt → VERIFY_FAILED       │
```

Ba vai: CA (MiniCA), server thật, attacker (cert giả). Client chỉ tin MiniCA.

## 2. Sinh cert (`generate_certs.sh`) — đọc hiểu từng lệnh

1. `openssl req -x509 -newkey rsa:2048 ... -subj /CN=MiniCA` → tạo CA tự ký (vừa là subject vừa là issuer), hạn 365 ngày. Đây là "con dấu gốc".
2. Tạo server.key + server.csr (CN=localhost), kèm file `server.ext` chứa SAN (localhost, 127.0.0.1), keyUsage, serverAuth. **SAN là bắt buộc** vì browser/Python hiện nay bỏ qua CN, chỉ check SAN.
3. `openssl x509 -req -CA ca.crt -CAkey ca.key` → CA ký ra server.crt. Lệnh này mô phỏng Let’s Encrypt ký cho bạn.
4. Tạo attacker.crt tự ký (issuer = Attacker, không liên quan MiniCA) để demo MITM.

Chạy: `chmod +x generate_certs.sh && ./generate_certs.sh`, kiểm tra bằng `openssl x509 -in server.crt -noout -subject -issuer -dates`.

## 3. Server (`server_tls.py`) — từng khối

```python
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # nhận cả 1.2 và 1.3
ctx.load_cert_chain("server.crt", "server.key")
ctx.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256:...")  # ép PFS+AEAD cho 1.2
```
- `PROTOCOL_TLS_SERVER` tự bật chế độ server (không verify client mặc định — phù hợp web; muốn mutual TLS thì thêm `verify_mode=CERT_REQUIRED` + `load_verify_locations`).
- `minimum_version` cấm SSL/TLS cũ → chống downgrade ngay từ code.
- Phần còn lại là socket TCP thường (`bind/listen/accept`), chỉ khác ở `ctx.wrap_socket(sock, server_side=True)` biến socket trần thành socket TLS, và `conn.cipher()` / `conn.version()` để in ra cipher đang dùng (đọc lên slide).
- Trả về HTTP thủ công (status + Content-Length + body) để chứng minh "TLS bọc HTTP mà không cần sửa HTTP".

## 4. Client (`client_tls.py`) — từng khối

```python
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations("ca.crt")
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.check_hostname = True
ctx.wrap_socket(sock, server_hostname="localhost")
```
- `server_hostname="localhost"` vừa là SNI gửi đi vừa là tên để check SAN. Dù connect tới 127.0.0.1, vẫn phải ghi "localhost" thì cert mới khớp (vì SAN có localhost).
- `getpeercert()` trả dict có subject/issuer/SAN/notBefore/notAfter → in ra để thuyết trình viên chỉ vào: "đây là chain, đây là hạn".
- Gửi `GET / HTTP/1.1` rồi đọc tới khi server đóng → in reply.

## 5. Kịch bản chạy chuẩn (5 phút trên lớp)

```bash
# Terminal 1:
python3 server_tls.py
# Terminal 2:
python3 client_tls.py
# Kỳ vọng: TLSv1.3, TLS_AES_256_GCM_SHA384, subject CN=localhost, reply Hello Secure World
```
Mở Wireshark song song, filter `tls || tcp.port==8443`: chỉ ra ClientHello → ServerHello → Certificate → Finished → Application Data. Follow TCP Stream một gói AppData → toàn bytes ngẫu nhiên → "đây là mã hóa".

## 6. Kịch bản MITM (điểm nhấn)

```bash
# Terminal 1: server kẻ xấu dùng cert giả
python3 server_tls.py attacker.crt attacker.key
# Terminal 2: client vẫn chỉ tin MiniCA
python3 client_tls.py
# Kỳ vọng: ssl.SSLCertVerificationError: self-signed / unable to get local issuer
```
Giải thích 30 giây: attacker cũng mã hóa được (vẫn TLS!), nhưng **không có chữ ký của MiniCA** nên client từ chối. Nếu code cẩu thả (`CERT_NONE` hoặc `check_hostname=False`) thì sẽ bị lừa — đây là lỗi của hàng loạt app thật từng bị CVE.

## 7. Sự cố thường gặp

| Hiện tượng | Nguyên nhân | Fix |
|------------|-------------|-----|
| `Address already in use` | server cũ chưa kill | `kill %1` hoặc đổi PORT |
| `CERTIFICATE_VERIFY_FAILED` dù dùng cert đúng | quên `./generate_certs.sh` / sai ca.crt | sinh lại, check issuer |
| `hostname mismatch` | SNI là 127.0.0.1 thay vì localhost | giữ `server_hostname="localhost"` |
| Wireshark không thấy gì | bắt sai interface | chọn loopback/lo, filter tcp.port==8443 |

## Tóm tắt 3 dòng

- Cert: CA tự ký → ký server (có SAN) + tạo attacker giả để đối chứng.
- Code: server `load_cert_chain` + ép cipher PFS; client trust CA + bắt verify + check hostname.
- Demo 2 màn: thành công (thấy cipher + AppData mã hóa) và MITM thất bại (verify từ chối cert giả).

## Tự kiểm tra

1. Vì sao SAN bắt buộc mà chỉ CN là không đủ?
2. Ba dòng nào ở client chống MITM, tắt từng dòng thì sao?
3. Trên Wireshark phân biệt handshake và AppData bằng cách nào?
