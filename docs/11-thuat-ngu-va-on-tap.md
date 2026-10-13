# 11 — Thuật ngữ (Glossary) và câu hỏi ôn tập

> Thuộc Slide 14-15 roadmap. Dùng file này 1 ngày trước trình bày để tự test.

## 1. Glossary — 20 thuật ngữ phải thuộc

| Thuật ngữ | Nhớ nhanh |
|-----------|-----------|
| Plain-text / Ciphertext | chưa mã hóa / đã mã hóa |
| Symmetric / Asymmetric | 1 khóa chung / cặp khóa công-khasi |
| RSA / ECDHE | mã hóa bằng số nguyên tố / trao khóa đường cong elliptic tạm thời |
| AES-GCM / ChaCha20-Poly1305 | mã hóa khối AEAD (nhanh, có tag chống sửa) |
| AEAD | mã hóa + xác thực trong 1 bước |
| PFS (Forward Secrecy) | lộ key hôm nay không lộ hôm qua |
| Cipher suite | bộ 4: KeyEx_Auth_WITH_Bulk_Hash |
| Handshake / Record / Alert | đàm phán / vận chuyển / báo lỗi |
| RTT / 1-RTT / 0-RTT | số vòng đi-về; 1.3 nhanh hơn 1.2 |
| X.509 / SAN / CN | chuẩn cert / tên mở rộng / tên chung |
| CA / Chain / Root / Intermediate / Leaf | hãng cấp cert / chuỗi / gốc / trung gian / lá |
| Private/Public key | khóa giữ kín / khóa công khai |
| Signature / Verify | ký bằng private / check bằng public |
| PRF / HKDF | hàm sinh khóa của 1.2 / 1.3 |
| SNI / ECH | tên domain gửi plain / bản mã hóa SNI |
| MITM / Downgrade / Replay | đứng giữa / ép cipher yếu / gửi lại gói cũ |
| CRL / OCSP / Stapling | danh sách thu hồi / hỏi CA / server đính kèm OCSP |
| HSTS / Pinning / CT logs | ép HTTPS / ghim key / log minh bạch cert |
| QUIC / PQC | TLS trên UDP / mật mã chống lượng tử |

## 2. Ba mươi câu tự kiểm tra (đáp án ngắn)

**Nhóm A — Hiểu (file 01-03):**
1. Ba mối đe dọa và ba mục tiêu CIA là gì? → Nghe lén/sửa/giả mạo ↔ Bí mật/toàn vẹn/xác thực.
2. Vì sao hash password rồi gửi vẫn không an toàn? → Replay lại hash là đăng nhập được.
3. SSL hay TLS đang chạy? → TLS; SSL đã cấm, gọi SSL là thói quen.
4. TLS 1.3 bỏ gì? → RSA static, CBC, RC4, SHA1, compression, renegotiation.
5. HTTPS = gì + gì? → HTTP + TLS + TCP + IP.
6. 4 sub-protocol và type? → Handshake 22, CCS 20, Alert 21, AppData 23.
7. SNI lộ gì? → Domain ở dạng plain trong ClientHello.

**Nhóm B — Trọng tâm (file 04-07):**
8. Kể 8 message handshake 1.2? → CH→SH→Cert→SKE→SHD→CKE→CCS+Fin→CCS+Fin.
9. random_C/S để làm gì? → Chống replay + góp sinh khóa.
10. RSA static vs ECDHE? → Static không PFS, ECDHE có PFS (khóa tạm mỗi phiên).
11. Vì sao thấy random mà không ra khóa? → Thiếu pre-master bí mật.
12. Finished để làm gì? → Hash toàn bộ handshake, phát hiện sửa đổi.
13. Vì sao 1.3 chỉ 1-RTT? → Đoán trước key_share gửi luôn.
14. 0-RTT nguy hiểm khi nào? → Replay lệnh không idempotent (chuyển tiền).
15. Đọc `ECDHE_RSA_AES128_GCM_SHA256`? → Trao đổi ECDHE, xác thực RSA, mã hóa AES-GCM, hash SHA256.
16. AEAD khác CBC+HMAC? → AEAD gộp mã hóa+xác thực + tag, chống padding oracle.
17. Cert chứa gì? → Subject/SAN, issuer, public key, hạn, signature, extensions.
18. Chain of Trust? → Root (có sẵn) ký Intermediate ký Leaf.
19. 6 bước validate? → Hạn, hostname, chữ ký chain, revocation, ràng buộc, CT/pinning.
20. Vì sao self-signed báo đỏ? → Không chain về root tin cậy.
21. Ba dòng code chống MITM? → trust CA + CERT_REQUIRED + check_hostname.

**Nhóm C — Demo, tấn công, mở rộng (file 08-10):**
22. SAN vì sao bắt buộc? → Browser/Python chỉ check SAN, bỏ qua CN.
23. Trên Wireshark phân biệt handshake/AppData? → Filter tls.handshake vs tls.app_data.
24. BEAST/POODLE do gì? → CBC/SSL3 cũ → fix bằng AEAD + cấm SSL3.
25. Heartbleed là lỗi gì? → Bug OpenSSL heartbeat đọc quá buffer, lộ RAM.
26. Ba cách chống downgrade? → Min-version 1.2+, FALLBACK_SCSV, Finished.
27. TLS vs IPsec vs SSH? → App (L7) vs ống IP (L3) vs quản trị (key tay).
28. QUIC là gì? → TLS 1.3 trên UDP, nhanh, hết head-of-line blocking.
29. ECH giải quyết gì? → Mã hóa SNI/domain còn plain của 1.3.
30. PQC vì sao cần? → Lượng tử bẻ RSA/ECDH → cần Kyber/Dilithium.

## 3. Checklist ngày trình bày

- [ ] Đọc roadmap 1 lượt + mỗi file đọc phần "Tóm tắt 3 dòng".
- [ ] Tự trả lời 30 câu trên, câu nào vấp thì mở lại file tương ứng.
- [ ] Chạy demo 2 màn (thành công + MITM) ít nhất 1 lần, lưu log backup.
- [ ] Phân công: ai nói handshake, ai nói mã hóa, ai nói cert+demo.

*Thuộc 20 thuật ngữ + 30 câu này là cân mọi câu hỏi thầy và nhóm bạn.*
