# 04 — Handshake TLS 1.2 từng bước (trọng tâm 1)

> Thuộc Slide 5 roadmap. Đây là phần quan trọng nhất — phải hiểu để vẽ lại sequence mà không nhìn tài liệu.

## 1. Mục đích của handshake (4 việc)

1. Thống nhất phiên bản + cipher suite.
2. Server chứng minh "tôi là thật" bằng certificate.
3. Hai bên tạo chung khóa phiên (session keys) mà kẻ nghe lén không biết.
4. Xác nhận không ai sửa các message đàm phán (Finished verify).

## 2. Sơ đồ đầy đủ (2-RTT = 2 vòng đi-về)

```
Client                                               Server
  |--- ClientHello ----------------------------------->|
  |    version max, random_C (32B), cipherSuites, SNI  |
  |                                                   |
  |<-- ServerHello ------------------------------------|
  |    version chốt, random_S, cipherSuite chọn        |
  |<-- Certificate ------------------------------------|
  |    chain leaf→intermediate (không gồm root)       |
  |<-- ServerKeyExchange (nếu dùng ECDHE) -------------|
  |    tham số DH tạm + chữ ký bằng private key server|
  |<-- ServerHelloDone --------------------------------|
  |                                                   |
  |--- ClientKeyExchange ----------------------------->|
  |    pre-master secret (RSA: mã hóa bằng pubkey;     |
  |    ECDHE: public value của client)                |
  |--- ChangeCipherSpec ------------------------------>|
  |    "từ giờ tôi mã hóa" (1 byte)                   |
  |--- Finished (đã mã hóa) -------------------------->|
  |    hash toàn bộ handshake để server kiểm tra      |
  |                                                   |
  |<-- ChangeCipherSpec -------------------------------|
  |<-- Finished (đã mã hóa) ---------------------------|
  |                                                   |
  |=== Application Data (AES-GCM) =====================|
```

RTT (round-trip time) là 1 lần đi-về. TLS 1.2 cần 2-RTT trước khi gửi dữ liệu thật → chậm hơn 1.3.

## 3. Giải thích từng message như kể chuyện

- **ClientHello:** "Chào, em hỗ trợ TLS 1.2, đây là số ngẫu nhiên random_C, danh sách cipher em biết, em muốn vào domain X (SNI)." random_C (28 byte ngẫu nhiên + 4 byte timestamp) có 2 tác dụng: chống replay (mỗi phiên khác nhau) và góp nguyên liệu sinh khóa.
- **ServerHello:** "Chào, ta chốt TLS 1.2, cipher `ECDHE_RSA_AES128_GCM_SHA256`, đây là random_S của ta."
- **Certificate:** server gửi chain cert để client validate (chi tiết file 07). Kẻ giả mạo không có private key khớp nên không qua được bước sau.
- **ServerKeyExchange (chỉ khi ECDHE):** server gửi tham số Diffie-Hellman tạm (ephemeral) và ký bằng private key RSA → client tin rằng tham số này đúng của server, không bị MITM tráo.
- **ServerHelloDone:** "Ta nói xong, tới lượt em."
- **ClientKeyExchange:** client gửi pre-master secret. Hai trường hợp:
  - RSA static: client sinh 48 byte ngẫu nhiên, mã hóa bằng public key trong cert → chỉ server có private key mới mở được. Cách này **không có forward secrecy** (lộ private key là giải mã được hết quá khứ).
  - ECDHE: hai bên trao public value, cùng tính ra pre-master bằng Diffie-Hellman → kẻ nghe lén thấy public value cũng không tính ra được nhờ bài toán log rời rạc. Cách này **có forward secrecy**.
- **ChangeCipherSpec + Finished:** client báo "đổi sang chế độ mã hóa" rồi gửi hash toàn bộ hội thoại (đã mã hóa bằng khóa mới). Server giải mã, tự tính hash so sánh → nếu khớp nghĩa là không ai sửa message giữa đường và hai bên đã cùng khóa.

## 4. Sinh khóa phiên (đọc để trả lời câu hỏi khó)

```
master_secret = PRF(pre_master, "master secret", random_C + random_S)  [48 bytes]
key_block     = PRF(master_secret, "key expansion", random_S + random_C)
→ cắt ra: client_write_key, server_write_key, client_IV, server_IV (+ MAC keys nếu không phải AEAD)
```

PRF của TLS 1.2 là P_SHA256 (HMAC-SHA256 lặp). Ý tưởng: trộn pre-master (chỉ 2 bên biết) với 2 số random (ai cũng thấy) → khóa cuối vừa bí mật vừa mới mỗi phiên. Kẻ nghe lén thấy random_C/S cũng vô dụng vì thiếu pre-master.

## 5. Vì sao Finished quan trọng?

Nếu attacker sửa ClientHello để ép cipher yếu (downgrade), hash ở Finished của hai bên sẽ lệch nhau → handshake thất bại. Đây là "con dấu niêm phong" của toàn bộ đàm phán.

## Tóm tắt 3 dòng

- 1.2 handshake = chào hỏi → đưa cert → trao pre-master → đổi chế độ mã hóa → xác nhận Finished.
- random_C/S chống replay + góp sinh khóa; pre-master là bí mật cốt lõi.
- Finished dùng hash để phát hiện mọi sửa đổi đàm phán.

## Tự kiểm tra

1. Kể lại 8 message theo thứ tự mà không nhìn?
2. RSA static và ECDHE khác nhau ở điểm nào, cái nào có PFS?
3. Vì sao kẻ nghe lén thấy hết random mà vẫn không ra khóa?
