# 01 — Vấn đề và mục tiêu an toàn mạng

> Thuộc Slide 2 roadmap. Đọc xong bạn phải trả lời được: "Không có TLS thì chuyện gì xảy ra?"

## 1. Bối cảnh: HTTP là giao thức "nói to"

HTTP gửi mọi thứ dưới dạng plain-text qua TCP. Ví dụ một form đăng nhập:

```
POST /login HTTP/1.1
Host: example.com

username=admin&password=123456&card=9704-xxxx
```

Bất kỳ ai ngồi cùng đường mạng (WiFi công cộng, switch bị ARP spoofing, nhà mạng, quản trị viên proxy) đều có thể dùng Wireshark/tcpdump để bắt gói tin và đọc trực tiếp. Không cần hack gì cao siêu.

Thí nghiệm gợi ý trên slide: bắt 2 phiên, một HTTP port 80 và một HTTPS port 443. Phiên HTTP → chuột phải Follow TCP Stream → thấy toàn bộ nội dung. Phiên HTTPS → chỉ thấy `Client Hello`, `Server Hello`, `Certificate`, sau đó toàn `Application Data` là bytes ngẫu nhiên.

## 2. Ba mối đe dọa cơ bản

| Mối đe dọa | Tên tiếng Anh | Ví dụ cụ thể |
|------------|---------------|--------------|
| Nghe lén | Eavesdropping / Sniffing | Lộ password, cookie phiên đăng nhập, số thẻ |
| Sửa đổi | Tampering | Chèn quảng cáo, đổi số tiền chuyển khoản, chèn mã độc vào file tải về |
| Giả mạo | Impersonation / Spoofing | Dựng web giả `vietcombank-secure.com` lừa nhập OTP |

Ba mối đe dọa này tương ứng với ba mục tiêu an ninh mà TLS phải đạt được.

## 3. Ba mục tiêu của TLS (CIA)

1. **Confidentiality — Tính bí mật:** chỉ người gửi và người nhận đọc được. Đạt bằng mã hóa (encryption).
2. **Integrity — Tính toàn vẹn:** phát hiện mọi sửa đổi trên đường đi. Đạt bằng MAC / AEAD (ví dụ GCM tag).
3. **Authentication — Tính xác thực:** client chắc chắn đang nói chuyện đúng server thật, không phải kẻ mạo danh. Đạt bằng chứng chỉ số (certificate) và chữ ký số.

Nhiều người mới học chỉ nhớ "TLS = mã hóa", bỏ quên 2 mục tiêu còn lại. Thực tế: **mã hóa mà không xác thực thì vô nghĩa**, vì kẻ tấn công MITM chỉ cần đứng giữa, mã hóa riêng với từng bên là đọc được hết. Vì vậy certificate validation (file 07) quan trọng ngang với encryption (file 06).

## 4. Vì sao không tự nghĩ giải pháp đơn giản?

Các ý tưởng ngây thơ thường gặp và vì sao thất bại:

- "Mã hóa password bằng MD5 rồi gửi là xong?" → Kẻ nghe lén lấy hash, replay lại là đăng nhập được, không cần biết password gốc.
- "Dùng WiFi có password là an toàn?" → Password WiFi chỉ chống người ngoài, không chống người cùng mạng hoặc chủ WiFi.
- "Dùng VPN là đủ?" → VPN chỉ dời điểm tin cậy từ WiFi sang nhà cung cấp VPN, còn từ VPN đến web server vẫn trần trụi nếu không có TLS.

TLS giải quyết tận gốc ở tầng ứng dụng, giữa đúng client và đúng server, không phụ thuộc mạng trung gian có tin cậy hay không (mô hình "zero-trust network").

## 5. Số liệu để nói trên slide

- >95% lưu lượng web hiện nay là HTTPS (Google Transparency Report).
- Các trình duyệt đánh dấu HTTP là "Not Secure".
- PCI-DSS (thanh toán thẻ), GDPR đều bắt buộc mã hóa khi truyền dữ liệu nhạy cảm.

## Tóm tắt 3 dòng

- HTTP trần trụi → lộ, sửa, giả mạo đều dễ.
- TLS sinh ra để đạt 3 mục tiêu: bí mật + toàn vẹn + xác thực.
- Xác thực (đúng server) quan trọng ngang với mã hóa (giấu nội dung).

## Tự kiểm tra

1. Vì sao chỉ mã hóa password ở phía client rồi gửi vẫn không an toàn?
2. Phân biệt eavesdropping, tampering, impersonation bằng 1 ví dụ mỗi loại?
3. Vì sao nói "mã hóa không xác thực là vô nghĩa"?
