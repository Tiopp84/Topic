# 05 — Handshake TLS 1.3: nhanh hơn, gọn hơn, an toàn hơn

> Thuộc Slide 6 roadmap. Đọc xong bạn so sánh được 1.2 vs 1.3 trong 1 phút.

## 1. Động lực cải tiến

TLS 1.2 có 3 nhược điểm lớn:
1. **Chậm:** 2-RTT mới gửi được dữ liệu. Trên mạng di động RTT 100ms → mất 200ms chỉ để bắt tay, chưa kể TCP handshake.
2. **Phức tạp:** quá nhiều tùy chọn (renegotiation, compression, RSA static, CBC...) → mỗi tùy chọn là một bề mặt tấn công.
3. **Lộ metadata:** certificate gửi ở dạng plain → ai cũng biết server là ai; SNI cũng plain.

TLS 1.3 (RFC 8446, 2018) giải quyết cả ba bằng cách **đoán trước và dọn dẹp**.

## 2. Sơ đồ 1-RTT (so với 2-RTT của 1.2)

```
Client                                               Server
  |--- ClientHello ----------------------------------->|
  |    version, random_C, key_share (ECDHE đoán trước)|
  |    cipherSuites (chỉ 5 AEAD), SNI                 |
  |                                                   |
  |<-- ServerHello + key_share ------------------------|
  |<-- EncryptedExtensions (đã mã hóa!) ---------------|
  |<-- Certificate (đã mã hóa!) -----------------------|
  |<-- Finished (đã mã hóa!) --------------------------|
  |                                                   |
  |--- Finished (đã mã hóa) -------------------------->|
  |=== Application Data ==============================|
```

Điểm mấu chốt: client **đoán trước** server sẽ chọn ECDHE nhóm nào (ví dụ x25519) và gửi luôn public value trong ClientHello. Nếu đoán đúng (hầu hết trường hợp vì server advertise nhóm hỗ trợ), server tính ra shared secret ngay và **mã hóa luôn từ message thứ hai**. Không còn ServerKeyExchange, ChangeCipherSpec, ServerHelloDone riêng lẻ.

Nếu đoán sai, server yêu cầu HelloRetryRequest (thêm 1-RTT) — hiếm khi xảy ra.

## 3. Ba cải tiến phải nhớ

### a) Tốc độ: 1-RTT + 0-RTT resumption
- Kết nối mới: 1-RTT (giảm một nửa so với 1.2).
- Kết nối lại (resumption bằng PSK/ticket): client gửi luôn Application Data kèm ClientHello → **0-RTT**. Đánh đổi: dữ liệu 0-RTT có thể bị replay nếu app không cẩn thận (ví dụ lệnh chuyển tiền không được dùng 0-RTT). Khi trình bày, nói "0-RTT nhanh nhưng chỉ dùng cho GET idempotent".

### b) Dọn dẹp cipher: chỉ còn 5, tất cả AEAD + PFS
```
TLS_AES_128_GCM_SHA256
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_CCM_SHA256 (+ CCM_8)
```
Không còn: RSA static, CBC, RC4, DES/3DES, SHA1, MD5, compression, renegotiation. Ít lựa chọn → ít sai lầm cấu hình → thư viện code gọn hơn (~50% code handshake bị xóa trong OpenSSL).

### c) Bảo mật metadata: mã hóa sớm
- Từ ServerHello trở đi (trừ vài byte) đều mã hóa → certificate không còn plain → kẻ nghe lén không biết server dùng cert nào.
- SNI vẫn plain trong ClientHello (vì server cần để chọn cert) → giải pháp tiếp theo là ECH (xem file 10).

## 4. Sinh khóa bằng HKDF (thay PRF)

TLS 1.3 dùng HKDF (HMAC-based Key Derivation Function, RFC 5869) theo chuỗi:

```
early secret → handshake secret → master secret
   ↓                ↓                   ↓
 0-RTT keys   handshake traffic keys  application traffic keys
```

Mỗi giai đoạn dùng salt và label khác nhau ("derived", "c hs traffic"...). Hiểu đơn giản: thay vì một PRF tự chế như 1.2, 1.3 dùng chuẩn HKDF đã được chứng minh an toàn, tách khóa riêng cho từng mục đích (handshake vs application, client vs server) → lộ một khóa không ảnh hưởng khóa khác (key separation).

## 5. Bảng so sánh để bê lên slide

| Tiêu chí | TLS 1.2 | TLS 1.3 |
|----------|---------|---------|
| RTT handshake mới | 2 | 1 (0-RTT khi nối lại) |
| Cipher suites | ~30+ (nhiều yếu) | 5 (toàn AEAD) |
| Key exchange | RSA static hoặc (EC)DHE | Chỉ (EC)DHE (bắt buộc PFS) |
| Certificate | plain-text | mã hóa |
| Renegotiation/compression | có (nguồn bug) | bỏ |
| Sinh khóa | PRF tự chế | HKDF chuẩn |

## Tóm tắt 3 dòng

- 1.3 đoán trước key_share → 1-RTT, nối lại 0-RTT.
- Chỉ giữ AEAD + (EC)DHE → nhanh, gọn, bắt buộc forward secrecy.
- Mã hóa certificate sớm; sinh khóa bằng HKDF tách bạch từng mục đích.

## Tự kiểm tra

1. Vì sao 1.3 chỉ cần 1-RTT?
2. 0-RTT nguy hiểm khi nào?
3. Kể tên 3 thứ 1.3 đã loại bỏ và lý do?
