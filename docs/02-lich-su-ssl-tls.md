# 02 — Lịch sử SSL/TLS: vì sao "SSL" đã chết mà ai cũng gọi?

> Thuộc Slide 3 roadmap. Đọc xong bạn kể được dòng thời gian và giải thích "web dùng SSL hay TLS?"

## 1. Dòng thời gian

```
1994  SSL 1.0  (Netscape, nội bộ, chưa phát hành — lỗi nặng)
1995  SSL 2.0  (phát hành, sau đó phát hiện nhiều lỗ hổng)
1996  SSL 3.0  (viết lại gần như toàn bộ, nền tảng cho TLS)
1999  TLS 1.0  (RFC 2246 — thực chất là SSL 3.1 đổi tên vì IETF chuẩn hóa)
2006  TLS 1.1  (RFC 4346 — vá lỗi CBC, thêm IV rõ)
2008  TLS 1.2  (RFC 5246 — thêm AEAD như GCM, SHA-256, dùng phổ biến nhất suốt 10 năm)
2014  POODLE giết SSL 3.0 (RFC 7568 cấm dùng SSL 3.0)
2018  TLS 1.3  (RFC 8446 — viết lại handshake, nhanh + an toàn hơn hẳn)
2026  Thực tế: chỉ dùng TLS 1.2 và 1.3. SSL 2.0/3.0, TLS 1.0/1.1 bị trình duyệt từ chối.
```

## 2. Vì sao đổi tên SSL → TLS?

SSL do Netscape (hãng tư nhân) tạo ra. Khi IETF (tổ chức chuẩn Internet) tiếp nhận để chuẩn hóa mở, họ đổi tên thành TLS (Transport Layer Security) vì lý do pháp lý/thương hiệu. Về kỹ thuật, TLS 1.0 ≈ SSL 3.1. Nên khi ai đó nói "chứng chỉ SSL", "cổng SSL", thực chất 99% là TLS.

Câu trả lời chuẩn khi bị hỏi: **"SSL đã deprecated, cái đang chạy là TLS, gọi SSL chỉ là thói quen."**

## 3. Mỗi phiên bản sửa cái gì? (Hiểu để giải thích, không cần thuộc RFC)

- **SSL 2.0:** cùng một khóa vừa mã hóa vừa MAC, không chống replay tốt → bỏ.
- **SSL 3.0:** tách MAC và encrypt, thêm Finished để chống sửa handshake. Nhưng CBC padding + không có AEAD → sau này dính POODLE.
- **TLS 1.0/1.1:** vá dần CBC (BEAST), nhưng vẫn giữ cipher yếu (RC4, DES, SHA1) vì tương thích ngược.
- **TLS 1.2:** bước nhảy lớn — cho phép cipher suite AEAD (AES-GCM), hash SHA-2, đàm phán linh hoạt. Là phiên bản "gánh" Internet giai đoạn 2010-2020.
- **TLS 1.3:** dọn dẹp triệt để — xóa ~50% thứ thừa: RSA key exchange tĩnh, CBC, RC4, SHA1, compression, renegotiation. Kết quả: handshake nhanh hơn (1-RTT), code ít hơn → ít bug hơn, bắt buộc forward secrecy.

Bài học lịch sử hay để nói: **tương thích ngược là kẻ thù của bảo mật**. Giữ cipher yếu để "máy cũ vẫn vào được" chính là nguyên nhân của các đòn downgrade (FREAK, LOGJAM — xem file 09).

## 4. RFC là gì? Cần nhớ số nào?

RFC (Request for Comments) là văn bản chuẩn của Internet. Khi trình bày, chỉ cần nhớ 3 số:

- RFC 5246 — TLS 1.2
- RFC 8446 — TLS 1.3 (quan trọng nhất)
- RFC 5280 — X.509 certificate

Ghi 3 số này lên slide cuối là đủ uy tín, không cần liệt kê dài.

## Tóm tắt 3 dòng

- SSL 1.0→3.0 (Netscape) → TLS 1.0→1.3 (IETF chuẩn hóa).
- Hiện tại chỉ TLS 1.2 và 1.3 được dùng; SSL đã bị cấm vì POODLE.
- TLS 1.3 = dọn rác + nhanh hơn + bắt buộc an toàn hơn.

## Tự kiểm tra

1. TLS 1.0 thực chất là gì?
2. Vì sao vẫn gọi "SSL" dù đang dùng TLS?
3. TLS 1.3 đã loại bỏ những gì và vì sao?
