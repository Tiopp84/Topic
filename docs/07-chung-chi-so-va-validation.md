# 07 — Chứng chỉ số X.509 và Certificate Validation (trọng tâm 3)

> Thuộc Slide 8 roadmap. Đọc xong bạn giải thích được vì sao browser báo đỏ và vì sao demo attacker bị từ chối.

## 1. Certificate là gì? (Chứng minh thư của server)

File `server.crt` (định dạng PEM — base64 giữa `-----BEGIN CERTIFICATE-----`) chứa:

| Trường | Ví dụ trong demo | Ý nghĩa |
|--------|------------------|---------|
| Subject (CN + SAN) | CN=localhost, SAN=localhost, 127.0.0.1 | "Tôi là ai" — client kiểm tra có khớp domain đang vào không |
| Issuer | CN=MiniCA | "Ai cấp cho tôi" |
| Public Key | RSA 2048-bit | Khóa công khai để client mã hóa/verify |
| Validity | 13/10/2026 → 13/10/2027 | Hạn dùng |
| Signature | bytes ký bởi MiniCA | Con dấu chống giả |
| Extensions | KeyUsage, ExtendedKeyUsage=serverAuth, BasicConstraints | Ràng buộc: được làm server, không được ký tiếp |

Xem bằng lệnh: `openssl x509 -in server.crt -text -noout` hoặc chạy `python3 cert_inspect.py`.

## 2. Chain of Trust — chuỗi niềm tin

```
Root CA (tự ký, cài sẵn trong Windows/macOS/browser)  ← neo tin cậy
  └─ Intermediate CA (được root ký)
       └─ Leaf / Server cert (được intermediate ký, CN=domain thật)
```

Server khi handshake chỉ gửi **leaf + intermediate**, không gửi root (client đã có root trong trust store). Client verify ngược: dùng public key intermediate để check chữ ký leaf → dùng public key root để check intermediate → root có trong máy và còn hạn → tin.

Demo của nhóm rút gọn còn 2 nấc (MiniCA đóng vai root, server.crt là leaf) để dễ hiểu. Bản chất y hệt Let’s Encrypt/DigiCert ngoài đời, chỉ khác tên.

## 3. Sáu bước client phải làm (nhớ để trả lời vấn đáp)

1. **Hạn + tên miền:** `notBefore ≤ now ≤ notAfter`; SAN (hoặc CN fallback) phải chứa đúng hostname/SNI. Sai → lỗi `hostname mismatch` / `expired`.
2. **Verify chữ ký từng nấc:** giải mã signature bằng public key của cha, so hash. Sai → `unable to get local issuer` / `self-signed`.
3. **Revocation:** cert có bị thu hồi không? Kiểm tra CRL (danh sách đen) hoặc OCSP (hỏi trực tiếp CA). Bản xịn dùng OCSP Stapling (server đính kèm câu trả lời OCSP vào handshake để nhanh + riêng tư).
4. **Ràng buộc:** BasicConstraints (CA:TRUE mới được ký con), KeyUsage (server cert phải có digitalSignature/keyEncipherment), ExtendedKeyUsage (serverAuth).
5. **Transparency:** tìm trong CT logs (Google/Browser yêu cầu) để phát hiện CA cấp lén cert giả.
6. **Chính sách bổ sung:** pinning (app chỉ tin 1 public key — Zalo/banking hay dùng), DANE (lưu fingerprint trên DNSSEC), HSTS (ép luôn dùng HTTPS).

Trong `client_tls.py`, 3 dòng này làm bước 1+2:
```python
ctx.load_verify_locations("ca.crt")  # trust store = MiniCA
ctx.verify_mode = ssl.CERT_REQUIRED   # bắt buộc verify
ctx.check_hostname = True             # bắt buộc khớp SAN
```
Tắt 1 trong 3 dòng là mở cửa cho MITM (xem file 08).

## 4. Các lỗi kinh điển và ý nghĩa (bảng để bê lên slide backup)

| Lỗi Python/browser | Nguyên nhân | Cách fix demo |
|--------------------|-------------|---------------|
| `CERTIFICATE_VERIFY_FAILED: self-signed` | server dùng attacker.crt tự ký, không chain về ca.crt | Chạy lại server với server.crt đúng |
| `hostname doesn't match` | vào bằng IP nhưng cert chỉ có DNS, hoặc ngược lại | Dùng SNI `localhost`, SAN có cả DNS+IP |
| `certificate has expired` | quá hạn | `./generate_certs.sh` lại |
| `unable to get local issuer` | thiếu intermediate / sai CA | `load_verify_locations` đúng ca.crt |

## Tóm tắt 3 dòng

- Cert = ID + public key + chữ ký CA; chain Root→Intermediate→Leaf là neo niềm tin.
- Validate = check hạn + tên miền + chữ ký chain + revocation + ràng buộc.
- Trong code: trust store + CERT_REQUIRED + check_hostname, thiếu 1 là bị MITM.

## Tự kiểm tra

1. Vẽ chain 3 nấc và nêu mỗi nấc ai ký cho ai?
2. Vì sao self-signed luôn bị báo đỏ dù cũng mã hóa được?
3. OCSP Stapling giải quyết vấn đề gì của OCSP thường?
