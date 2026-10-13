# T30 — Bộ tài liệu đọc hiểu chi tiết (Docs)

> **Roadmap chính:** [`../T30-TLS-SSL-Presentation-Document.md`](../T30-TLS-SSL-Presentation-Document.md) — file này là bản đồ tổng thể (outline 15 slides, kịch bản nói, demo nhanh, Q&A).
> Thư mục `docs/` này là **bộ tài liệu đọc hiểu chi tiết**, mỗi file giải thích cặn kẽ một phần kiến thức để bất kỳ thành viên nào cũng tự học và trình bày được.

## Cách dùng

1. Đọc roadmap trước (15 phút) để nắm khung.
2. Đọc theo thứ tự 01 → 11 (mỗi file ~15-20 phút).
3. Vừa đọc vừa chạy code trong `../demo/` ở file 08.
4. Trước hôm trình bày, làm file 11 (ôn tập) để tự kiểm tra.

## Danh mục tài liệu

| File | Nội dung | Tương ứng Slide roadmap |
|------|----------|-------------------------|
| `01-van-de-va-muc-tieu-an-toan.md` | Vì sao cần TLS: nghe lén, sửa đổi, giả mạo; 3 mục tiêu CIA | Slide 2 |
| `02-lich-su-ssl-tls.md` | SSL 1.0 → TLS 1.3, RFC, vì sao "SSL" đã chết mà vẫn gọi | Slide 3 |
| `03-vi-tri-va-kien-truc-tls.md` | Vị trí TLS trong TCP/IP, Record/Handshake/Alert | Slide 4 |
| `04-handshake-tls-1-2.md` | Handshake TLS 1.2 từng bước, sinh khóa PRF | Slide 5 |
| `05-handshake-tls-1-3.md` | Handshake TLS 1.3: 1-RTT, 0-RTT, HKDF | Slide 6 |
| `06-ma-hoa-va-cipher-suite.md` | Hybrid crypto, AES-GCM, ECDHE, PFS, đọc cipher suite | Slide 7 |
| `07-chung-chi-so-va-validation.md` | X.509, chain of trust, 6 bước validate, lỗi thường gặp | Slide 8 |
| `08-demo-doc-hieu-code.md` | Đọc hiểu từng dòng server/client, cert, Wireshark, MITM | Slide 9-10 |
| `09-tan-cong-va-phong-chong.md` | POODLE, BEAST, Heartbleed, Downgrade, best practice | Slide 11 |
| `10-so-sanh-ung-dung-ket-luan.md` | TLS vs IPsec vs SSH, ứng dụng, QUIC/ECH/PQC, kết luận | Slide 12-13 |
| `11-thuat-ngu-va-on-tap.md` | Glossary + 30 câu tự kiểm tra + đáp án | Slide 14-15 |

## Quy ước

- Thuật ngữ tiếng Anh giữ nguyên (ClientHello, cipher suite, SAN...) kèm giải thích tiếng Việt.
- Sơ đồ dùng ASCII để dễ copy lên slide.
- Mỗi file kết thúc bằng **Tóm tắt 3 dòng** + **Tự kiểm tra** để đảm bảo hiểu.
