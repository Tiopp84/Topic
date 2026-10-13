# 03 — Vị trí và kiến trúc TLS

> Thuộc Slide 4 roadmap. Đọc xong bạn vẽ được stack và kể tên 4 sub-protocol.

## 1. TLS nằm ở đâu?

```
┌─────────────────────────┐
│ HTTP / SMTP / FTP / MQTT│  ← ứng dụng (L7)
├─────────────────────────┤
│ TLS (Handshake+Record)  │  ← TOPIC NÀY (khoảng L5-L6)
├─────────────────────────┤
│ TCP                     │  ← vận chuyển tin cậy (L4)
├─────────────────────────┤
│ IP                      │  ← định tuyến (L3)
└─────────────────────────┘
```

Hệ quả:
- Mọi giao thức trên TCP đều có thể "bọc TLS": HTTP→HTTPS (443), SMTP→SMTPS (465), IMAP→IMAPS (993), FTP→FTPS, MQTT→MQTTS.
- TLS không thay thế TCP (vẫn cần bắt tay 3 bước, chia gói, truyền lại). Nó **nằm trên TCP**, dùng TCP như ống vận chuyển.
- Vì nằm giữa nên lập trình viên chỉ cần thay `socket` bằng `ssl.wrap_socket` là có bảo mật, không cần sửa logic HTTP (xem file 08).

Công thức nói nhanh: **HTTPS = HTTP + TLS + TCP + IP.**

## 2. Hai lớp lớn của TLS

### a) TLS Handshake Protocol — "đàm phán và làm quen"
- Thương lượng: phiên bản (1.2 hay 1.3?), cipher suite nào cả hai cùng hỗ trợ?
- Xác thực: server đưa certificate, client kiểm tra (file 07).
- Tạo khóa phiên (session keys) để dùng sau này (file 04-06).
- Chỉ chạy lúc mở kết nối (vài KB đầu), sau đó nghỉ.

### b) TLS Record Protocol — "đóng gói và vận chuyển"
- Mọi dữ liệu (kể cả handshake) đều đi qua Record để gửi.
- Mỗi Record gồm: `ContentType (1 byte) + Version (2) + Length (2) + Payload (tối đa 16KB) + MAC/Tag`.
- Quy trình gửi: phân mảnh → (nén — TLS 1.3 bỏ) → thêm số thứ tự chống replay → MAC/mã hóa → gửi qua TCP.
- Quy trình nhận làm ngược lại, sai MAC/tag là vứt gói và báo Alert.

## 3. Bốn sub-protocol (phân biệt bằng ContentType)

| Type | Tên | Vai trò | Ví dụ message |
|------|-----|---------|---------------|
| 22 | Handshake | Đàm phán, xác thực, tạo khóa | ClientHello, ServerHello, Certificate, Finished |
| 20 | ChangeCipherSpec (chỉ 1.2) | Báo "từ giờ mã hóa" | 1 byte `0x01` |
| 21 | Alert | Báo lỗi/cảnh báo | `close_notify`, `handshake_failure`, `bad_certificate` |
| 23 | Application Data | Dữ liệu ứng dụng đã mã hóa | HTTP GET/Response mã hóa |

Trên Wireshark bạn sẽ thấy đúng 4 loại này ở cột Info. Mẹo demo: lọc `tls.handshake` để chỉ xem đàm phán, lọc `tls.app_data` để xem dữ liệu mã hóa.

## 4. SNI — chi tiết nhỏ nhưng hay bị hỏi

Server Name Indication là extension trong ClientHello, chứa tên miền (ví dụ `www.bank.com`) ở dạng **plain-text**. Vì một IP server có thể host nhiều web (virtual hosting), server cần biết client muốn web nào để đưa đúng certificate.

Hệ quả: kẻ nghe lén dù không đọc được nội dung, vẫn biết bạn vào domain nào. Giải pháp mới là ECH (Encrypted Client Hello) trong TLS 1.3 + QUIC (xem file 10).

## Tóm tắt 3 dòng

- TLS nằm giữa TCP và ứng dụng → bọc cái gì cũng thành bản "Secure".
- Handshake lo đàm phán + tạo khóa; Record lo đóng gói + mã hóa mọi thứ.
- 4 loại bản tin: Handshake (22), ChangeCipherSpec (20), Alert (21), AppData (23).

## Tự kiểm tra

1. Vẽ lại stack và giải thích vì sao HTTP không cần sửa mà vẫn thành HTTPS?
2. Record Protocol làm những bước nào trước khi gửi?
3. SNI là gì và vì sao nó lộ thông tin?
