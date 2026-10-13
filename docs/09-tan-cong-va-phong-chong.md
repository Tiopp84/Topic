# 09 — Tấn công nổi tiếng và phòng chống

> Thuộc Slide 11 roadmap. Đọc xong bạn kể được 5 vụ và best practice 2026.

## 1. Tư duy chung: tấn công vào đâu?

TLS có 3 mặt: **thuật toán** (cipher), **cài đặt** (code OpenSSL), **con người** (bỏ qua cảnh báo). Mỗi vụ dưới đây là một mặt.

## 2. Năm vụ phải biết (bảng để bê lên slide)

| Vụ (năm) | Lỗi ở đâu? | Chuyện gì xảy ra? | Bài học / Fix |
|----------|------------|-------------------|---------------|
| **BEAST (2011)** | TLS 1.0 CBC dùng IV đoán được | Đoán từng byte cookie bằng chosen-plaintext | Dùng TLS 1.2+ với GCM (AEAD), không dùng CBC |
| **POODLE (2014)** | SSL 3.0 padding không check kỹ | Ép downgrade về SSL 3.0 rồi giải mã từng byte | Cấm SSL 3.0 (RFC 7568), dùng `TLS_FALLBACK_SCSV` |
| **Heartbleed (2014)** | Bug code OpenSSL heartbeat (đọc quá buffer) | Đọc trộm 64KB RAM server gồm private key, password | Update OpenSSL, revoke + cấp lại cert, không phải lỗi thiết kế TLS |
| **FREAK / LOGJAM (2015)** | Downgrade ép dùng RSA_EXPORT 512-bit / DH 512-bit | Bẻ khóa yếu trong vài giờ bằng precomputation | Bỏ cipher EXPORT, DH ≥2048-bit, server ký tham số DH |
| **MITM bằng cert giả** | Người dùng bấm "Proceed anyway" / CA bị hack (DigiNotar 2011) | Đứng giữa đọc hết dù vẫn "có ổ khóa" | HSTS, Certificate Transparency, pinning, không bao giờ bỏ qua cảnh báo |

Cách nhớ nhanh: **B-P-H-D-M** (Beast-Poodle-Heartbleed-Downgrade-Mitm).

## 3. Downgrade — đòn chung của nhiều vụ

Kẻ tấn công không bẻ cipher mạnh, mà **lừa hai bên dùng cipher yếu** bằng cách sửa ClientHello (xóa cipher mạnh khỏi danh sách). Phòng chống 3 lớp:
1. Client/server cấu hình `minimum_version = TLS 1.2` (như demo) → từ chối luôn phiên bản cũ.
2. `TLS_FALLBACK_SCSV` — tín hiệu "tôi đang thử lại, đừng downgrade tôi".
3. Finished hash (file 04) phát hiện sửa đổi → handshake thất bại thay vì dùng cipher yếu.

## 4. Best practice cấu hình 2026 (đọc để trả lời "triển khai sao cho đúng?")

- Chỉ bật TLS 1.2 + 1.3; tắt SSL 2.0/3.0, TLS 1.0/1.1.
- Cipher: chỉ AEAD + PFS (`ECDHE+AESGCM` / `CHACHA20-POLY1305`), tham khảo Mozilla SSL Generator.
- HSTS (`Strict-Transport-Security`) ép browser luôn HTTPS, chống SSL-stripping.
- OCSP Stapling + redirect HTTP→HTTPS + tự động renew (Let's Encrypt/Certbot).
- Log/monitor: CT logs, expiry alert trước 30 ngày.

## 5. Heartbleed nói kỹ hơn (hay bị hỏi vì nổi tiếng)

Heartbeat là extension để giữ kết nối ("mày còn sống không?"). Code OpenSSL tin độ dài do client gửi mà không kiểm tra với độ dài thật → client nói "trả tao 64KB" dù chỉ gửi 1 byte, server vẫn trả 64KB RAM kề bên (gồm key, session cookie). Fix: 1 dòng check bounds + update. Bài học: **lỗi cài đặt nguy hiểm không kém lỗi thuật toán**, nên dùng thư viện được audit và update đều.

## Tóm tắt 3 dòng

- BEAST/POODLE = cipher cũ (CBC/SSL3); FREAK/LOGJAM = ép cipher yếu; Heartbleed = bug code; MITM = lừa người/CA.
- Chống downgrade bằng min-version + FALLBACK_SCSV + Finished.
- Triển khai đúng = TLS 1.2+ + AEAD/PFS + HSTS + OCSP stapling + renew tự động.

## Tự kiểm tra

1. Vì sao giữ tương thích cipher cũ lại nguy hiểm?
2. Heartbleed là lỗi thiết kế hay cài đặt? Fix thế nào?
3. Liệt kê 3 cơ chế chống downgrade?
