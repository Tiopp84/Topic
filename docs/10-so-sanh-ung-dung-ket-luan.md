# 10 — So sánh, ứng dụng, kết luận và hướng phát triển

> Thuộc Slide 12-13 roadmap. Đọc xong bạn chốt bài trong 1 phút thật ấn tượng.

## 1. TLS vs IPsec vs SSH (bảng so sánh hay bị hỏi)

| Tiêu chí | TLS | IPsec | SSH |
|----------|-----|-------|-----|
| Tầng | L4-L7 (trên TCP, cho từng app) | L3 (bọc toàn bộ IP, VPN) | L7 (đăng nhập/quản trị máy) |
| Xác thực | PKI/cert quy mô web | Pre-shared key / cert máy | Key thủ công (known_hosts) |
| Dùng khi nào? | Web, mail, IoT, API | VPN site-to-site, remote access | Admin server, git, tunnel |
| Ưu điểm | Triển khai theo app, dễ scale | Trong suốt với app | Đơn giản, không cần CA |
| Ví dụ | HTTPS, SMTPS, MQTTS | Cisco/strongSwan VPN | OpenSSH, GitHub SSH |

Câu chốt: "TLS bảo vệ từng ứng dụng, IPsec bảo vệ cả đường ống, SSH bảo vệ phiên quản trị."

## 2. Ứng dụng thực tế quanh bạn

- Web: HTTPS (443) — mọi login, banking, thương mại điện tử.
- Mail/chat: SMTPS/IMAPS, Signal/WhatsApp (TLS + Signal protocol).
- File/VPN: FTPS, OpenVPN (dùng TLS handshake để xác thực).
- IoT: MQTT over TLS (cảm biến, camera) — bản nhẹ dùng ChaCha20 vì CPU yếu.
- VoIP/streaming: SRTP/QUIC đều mượn ý tưởng TLS.

## 3. Hướng phát triển (phần innovation để ghi điểm)

1. **TLS 1.3 + QUIC/HTTP-3:** gộp handshake TLS vào UDP, 0-1 RTT cho cả kết nối + bảo mật, chống head-of-line blocking. Google/Facebook đã dùng đại trà.
2. **Encrypted Client Hello (ECH):** mã hóa luôn SNI/domain (phần plain cuối cùng của 1.3) → nhà mạng không biết bạn vào web nào.
3. **Post-Quantum Crypto (PQC):** máy tính lượng tử đe dọa RSA/ECDH. NIST đã chuẩn hóa Kyber (KEM) + Dilithium (chữ ký); TLS tương lai sẽ có cipher suite lai cổ điển + lượng tử. Nói câu này là vượt mặt hầu hết nhóm khác.

## 4. Kết luận 1 phút (đọc nguyên văn khi chốt)

> "Không có TLS, Internet chỉ là bưu thiếp ai cũng đọc được. Có TLS, nó thành thư niêm phong chỉ người nhận mở được — và có con dấu CA đảm bảo đúng người gửi. Nhóm em đã chứng minh điều đó bằng custom client/server: handshake để tin nhau, hybrid crypto để giấu tin, validation để từ chối kẻ giả mạo. Hướng tới là QUIC, ECH và mật mã hậu lượng tử."

Ba takeaway để mỗi người nói một câu:
- Người 1: Handshake = tin ai.
- Người 2: Encryption = giấu gì.
- Người 3: Validation = tin thế nào.

## Tóm tắt 3 dòng

- TLS/IPsec/SSH khác tầng và mô hình tin cậy, bổ sung nhau.
- TLS ở khắp nơi: web, mail, VPN, IoT, QUIC.
- Tương lai: QUIC + ECH + post-quantum.

## Tự kiểm tra

1. Khi nào dùng TLS thay vì IPsec/SSH?
2. QUIC cải gì so với TLS-over-TCP?
3. Vì sao cần post-quantum cho TLS?
