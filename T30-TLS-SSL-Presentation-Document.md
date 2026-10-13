# T30: Network Security Protocols - TLS/SSL Implementation
### Tài liệu Presentation đầy đủ | Môn: Lập Trình Mạng (LTM)

> Thời lượng đề xuất: 12-15 phút thuyết trình + 5 phút demo + 5 phút Q&A
> Ngôn ngữ demo: Python (`ssl` + `socket` + `cryptography`) — có gợi ý bản Java / C

---

## PHẦN 1: OUTLINE SLIDE (15 SLIDES)

| Slide | Tiêu đề | Thời gian | Key message |
|-------|---------|-----------|-------------|
| 1 | Cover: Tiêu đề + nhóm + GV | 30s | Giới thiệu topic T30 |
| 2 | Agenda + Vấn đề: HTTP plain-text nguy hiểm thế nào? | 1' | Motivation |
| 3 | Lịch sử: SSL 1.0 → SSL 3.0 → TLS 1.0 → 1.2 → 1.3 (RFC 8446) | 1' | Bối cảnh |
| 4 | Vị trí TLS trong mô hình TCP/IP + Kiến trúc 2 lớp | 1' | Record / Handshake / Alert / ChangeCipherSpec |
| 5 | Handshake TLS 1.2 (10 bước, 2-RTT) – Sơ đồ sequence | 2' | Trọng tâm 1 |
| 6 | Handshake TLS 1.3 (1-RTT, 0-RTT, bỏ RSA static) | 1'30 | Cải tiến |
| 7 | Encryption: Hybrid – Asymmetric + Symmetric + CipherSuite | 1'30 | Trọng tâm 2 |
| 8 | Certificate Validation: X.509, CA Chain, Verify | 1'30 | Trọng tâm 3 |
| 9 | Demo Architecture: Custom HTTPS Client/Server | 30s | Dẫn vào demo |
| 10 | Live Demo: Handshake + Wireshark + Chống MITM | 4' | Wow-factor |
| 11 | Attacks & Phòng chống: POODLE, BEAST, Heartbleed, Downgrade | 1' | Chiều sâu |
| 12 | So sánh TLS vs IPsec vs SSH + Ứng dụng thực tế | 1' | Mở rộng |
| 13 | Kết luận + Innovation + Hướng phát triển (QUIC, ECH) | 1' | Chốt |
| 14 | Q&A – Câu hỏi dự kiến | – | Backup |
| 15 | References + Cảm ơn | – | Backup |

---

## PHẦN 2: NỘI DUNG CHI TIẾT TỪNG SLIDE (Kèm lời thuyết trình)

### SLIDE 1 – COVER
**Hiển thị:**
```
T30: NETWORK SECURITY PROTOCOLS
TLS/SSL Implementation – Handshake, Encryption, Certificate Validation
Môn Lập Trình Mạng | Nhóm ... | GV ...
```

**Nói (30s):**
> "Xin chào thầy và các bạn, nhóm em trình bày topic T30 – Giao thức bảo mật mạng, tập trung vào TLS/SSL – nền tảng của mọi kết nối HTTPS mà chúng ta dùng mỗi ngày."

### SLIDE 2 – VẤN ĐỀ: TẠI SAO CẦN TLS?
**Nội dung:**
- HTTP gửi plain-text: user/pass, cookie, thẻ tín dụng bị sniff bằng Wireshark dễ dàng.
- 3 mối đe dọa: **Eavesdropping (nghe lén) – Tampering (sửa đổi) – Impersonation (giả mạo server).**
- 3 mục tiêu TLS giải quyết: **Confidentiality – Integrity – Authentication.**
- Số liệu: >95% web traffic hiện nay là HTTPS (Google Transparency Report 2025-2026).

**Nói:**
> "Nếu dùng HTTP thuần, chỉ cần ngồi chung WiFi quán cafe, attacker dùng Wireshark là thấy hết password. TLS sinh ra để khắc phục đúng 3 điều này."

**Minh họa đề xuất:** Chụp 2 gói Wireshark: 1 gói HTTP thấy `password=123456`, 1 gói HTTPS chỉ thấy `Application Data` mã hóa.

### SLIDE 3 – LỊCH SỬ PHÁT TRIỂN
```
1994 SSL 1.0 (Netscape, chưa release) → 1995 SSL 2.0 (lỗi) → 1996 SSL 3.0
1999 TLS 1.0 (RFC 2246) → 2006 TLS 1.1 → 2008 TLS 1.2 (RFC 5246, dùng rộng rãi nhất)
2018 TLS 1.3 (RFC 8446) → Hiện tại: TLS 1.2 + 1.3, SSL 2.0/3.0 đã bị cấm (RFC 7568)
```

**Điểm nhấn:**
- SSL đã chết về mặt kỹ thuật, nhưng tên "SSL" vẫn bị dùng quen miệng → thực chất là TLS.
- TLS 1.3 loại bỏ: RSA key exchange tĩnh, CBC, SHA1, RC4, compression → chống POODLE/BEAST.
- Bắt buộc Perfect Forward Secrecy (PFS).

### SLIDE 4 – VỊ TRÍ & KIẾN TRÚC TLS
**Vị trí stack:**
```
[ HTTP / FTP / SMTP ]
[ TLS – Handshake, Record ]  ← Topic này
[ TCP ]
[ IP ]
```

**2 lớp chính:**
1. **TLS Handshake Protocol:** thương lượng phiên bản, cipher suite, xác thực, tạo khóa.
2. **TLS Record Protocol:** phân mảnh, nén (TLS 1.3 bỏ), MAC/encrypt, gửi đi. Max 16KB/fragment.

Các sub-protocol: Handshake (22), ChangeCipherSpec (20, chỉ 1.2), Alert (21: close_notify, handshake_failure), Application Data (23).

**Nói:**
> "TLS nằm giữa TCP và HTTP, nên mới có tên HTTPS = HTTP over TLS. Mọi thứ HTTP làm được, TLS bọc lại và mã hóa."

### SLIDE 5 – HANDSHAKE TLS 1.2 CHI TIẾT (TRỌNG TÂM 1)
**Sequence 10 bước, 2-RTT:**

```
Client                                    Server
  | ---- ClientHello --------------------> |
  |      (version, random_C, cipherSuites, SNI) |
  | <--- ServerHello --------------------- |
  |      (version chọn, random_S, cipherSuite) |
  | <--- Certificate --------------------- |
  | <--- ServerKeyExchange (nếu ECDHE) --- |
  | <--- ServerHelloDone ----------------- |
  | ---- ClientKeyExchange --------------> |
  |      (pre-master secret, mã hóa bằng RSA/ECDH) |
  | ---- ChangeCipherSpec + Finished ----> |
  | <--- ChangeCipherSpec + Finished ----- |
  | ==== Application Data (mã hóa AES) === |
```

**Cách sinh khóa (RSA vs ECDHE):**
- `master_secret = PRF(pre_master, "master secret", random_C + random_S)`
- `key_block = PRF(master_secret, "key expansion", ...)` → chia thành client_write_key, server_write_key, IV, MAC keys.

**Nói:**
> "Hai số random chống replay attack. Pre-master chỉ client và server biết. Từ đó suy ra khóa phiên dùng AES. Kẻ nghe lén có bắt hết gói cũng không giải mã được nếu không có private key."

### SLIDE 6 – HANDSHAKE TLS 1.3 (CẢI TIẾN)
**Khác biệt lớn:**
- Chỉ **1-RTT** (so với 2-RTT của 1.2), hỗ trợ **0-RTT resumption** cho kết nối lại siêu nhanh.
- Client đoán trước key share (ECDHE) gửi luôn trong ClientHello → server trả về ngay, giảm 1 vòng.
- Bỏ renegotiation, bỏ RSA static → bắt buộc (EC)DHE → **Forward Secrecy 100%**.
- Mã hóa luôn cả certificate (EncryptedExtensions) → chống lộ SNI/metadata một phần.
- 5 cipher suites duy nhất, tất cả AEAD: `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`, ...

**Nói:**
> "TLS 1.3 nhanh hơn, gọn hơn, an toàn hơn. Lý do chính Google/Facebook chuyển hết sang 1.3 và QUIC."

### SLIDE 7 – ENCRYPTION: HYBRID CRYPTO (TRỌNG TÂM 2)
**Ý tưởng:** Dùng cái mạnh của cả hai:
- **Asymmetric (RSA-2048 / ECDHE P-256, X25519):** chậm (~1000x) nhưng giải quyết trao đổi khóa an toàn, xác thực.
- **Symmetric (AES-128-GCM / AES-256-GCM / ChaCha20-Poly1305):** nhanh, mã hóa bulk data.

**Giải mã CipherSuite ví dụ:**
```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
 |____|   |__|  |___________| |_____|
 KeyEx  Auth   Bulk Encrypt   Hash/MAC
```
- KeyEx: ECDHE (Ephemeral → mỗi phiên khóa khác nhau → PFS)
- Auth: RSA (certificate)
- Bulk: AES_128_GCM (AEAD: vừa mã hóa vừa chống sửa đổi, không cần MAC riêng)
- Hash: SHA256 (cho PRF/HKDF)

**TLS 1.3 dùng HKDF:** `early secret → handshake secret → master secret → traffic keys`.

**Nói:**
> "Nếu chỉ dùng RSA thì lộ private key là lộ hết quá khứ. ECDHE sinh khóa tạm mỗi phiên nên lộ 1 phiên không ảnh hưởng phiên khác – gọi là Perfect Forward Secrecy."

### SLIDE 8 – CERTIFICATE VALIDATION (TRỌNG TÂM 3)
**X.509 Certificate chứa:** Subject (CN/SAN: google.com), Issuer (CA), Public Key, Validity (NotBefore/NotAfter), Signature của CA, Extensions (KeyUsage, SAN).

**Chain of Trust:**
```
Root CA (tự ký, cài sẵn trong OS/browser)
  └─ Intermediate CA
       └─ Server Cert (leaf)
```

**6 bước validate client phải làm:**
1. Kiểm tra hạn (expiry) + tên miền khớp SAN/CN + SNI.
2. Verify chữ ký từng nấc bằng public key của CA cha.
3. Kiểm tra revocation: CRL / OCSP / OCSP Stapling.
4. Kiểm tra KeyUsage / BasicConstraints (CA:TRUE?).
5. Kiểm tra trong CT logs (Certificate Transparency) chống cert giả.
6. (Nâng cao) Pinning / DANE.

**Demo lỗi hay gặp:** `CERTIFICATE_VERIFY_FAILED: self-signed`, `hostname mismatch`, `expired`, `untrusted issuer`.

**Nói:**
> "Mã hóa mà không xác thực thì vẫn bị Man-in-the-Middle. Hacker tự tạo cert giả mạo ngân hàng, nếu client không validate chain về Root CA tin cậy thì sẽ bị lừa."

### SLIDE 9 – DEMO ARCHITECTURE
```
[ Custom HTTPS Server: Python socket + ssl.SSLContext(PROTOCOL_TLS_SERVER) ]
   - load_cert_chain(server.crt, server.key)
   - verify_mode = CERT_REQUIRED (mutual TLS demo) / CERT_NONE
   - cipher: ECDHE-RSA-AES128-GCM-SHA256, TLS 1.2 + 1.3
[ Custom HTTPS Client: ssl.SSLContext(PROTOCOL_TLS_CLIENT) ]
   - load_verify_locations(ca.crt), check_hostname=True
   - getpeercert() → in SAN, issuer, expiry
[ Attacker script: MITM với self-signed cert → client từ chối ]
+ Wireshark filter: tls.handshake / http
```

**Kịch bản demo 3 phút:**
1. Chạy server → client kết nối thành công → in cipher + cert + gửi "Hello Secure World".
2. Bật Wireshark: chỉ thấy ClientHello/ServerHello/Certificate + Application Data mã hóa.
3. Chạy attacker (cert giả) → client báo `SSL: CERTIFICATE_VERIFY_FAILED` → chứng minh chống MITM.

### SLIDE 10 – LIVE DEMO (chạy thật)
*Xem file `demo/` kèm theo. Lệnh chạy ở Phần 4 bên dưới.*

Dự phòng nếu mạng lỗi: quay video trước, hoặc show log mẫu đã lưu.

### SLIDE 11 – TẤN CÔNG NỔI TIẾNG & PHÒNG CHỐNG
| Tấn công | Nguyên nhân | Bài học / Fix |
|----------|-------------|---------------|
| **POODLE (2014)** | SSL 3.0 CBC padding | Cấm SSL 3.0, dùng AEAD |
| **BEAST (2011)** | TLS 1.0 CBC IV đoán được | Dùng TLS 1.2+ GCM |
| **Heartbleed (2014)** | Bug OpenSSL heartbeat | Update, revoke cert |
| **Downgrade (FREAK/LOGJAM)** | Ép dùng RSA_EXPORT 512-bit | Bỏ cipher yếu, TLS_FALLBACK_SCSV |
| **MITM + cert giả** | User bỏ qua cảnh báo | HSTS, CT logs, pinning |

**Best practice 2026:** Chỉ bật TLS 1.2+, cipher AEAD + PFS, HSTS, OCSP stapling, redirect HTTP→HTTPS, tự động renew (Let's Encrypt).

### SLIDE 12 – SO SÁNH & ỨNG DỤNG
- **TLS vs IPsec:** TLS bảo vệ từng app (L4-L7, dễ deploy), IPsec bảo vệ toàn bộ IP (L3, VPN).
- **TLS vs SSH:** TLS dùng cert/PKI (web scale), SSH dùng key thủ công (admin).
- Ứng dụng: HTTPS, SMTPS/IMAPS, FTPS, VPN (OpenVPN), VoIP (SRTP), IoT (MQTT over TLS), QUIC (TLS 1.3 tích hợp).

### SLIDE 13 – KẾT LUẬN & INNOVATION
- Hiểu secure communication = **Handshake (tin ai) + Encryption (giấu gì) + Validation (tin thế nào).**
- Innovation của nhóm: custom implementation giúp nhìn thấy bytes thật của handshake, không chỉ lý thuyết.
- Hướng phát triển: TLS 1.3 + QUIC/HTTP3, Encrypted Client Hello (ECH) chống lộ SNI, Post-Quantum Crypto (Kyber/Dilithium).

**Câu chốt:**
> "Không có TLS, Internet chỉ là bưu thiếp ai cũng đọc được. Có TLS, nó thành thư niêm phong chỉ người nhận mở được – và có con dấu đảm bảo đúng người gửi."

---

## PHẦN 3: SƠ ĐỒ VẼ LÊN SLIDE (Mô tả để vẽ PowerPoint)

1. **Sơ đồ Handshake 1.2:** 2 cột Client/Server, 8 mũi tên như Phần 2 Slide 5. Tô đỏ `random_C/S`, `pre-master`.
2. **Sơ đồ Hybrid Crypto:** Hộp trái "RSA/ECDH (chậm, an toàn)" → mũi tên "trao khóa phiên" → hộp phải "AES-GCM (nhanh)" → "Application Data".
3. **Chain of Trust:** 3 khối xếp tầng Root → Intermediate → Leaf, kèm dấu tick xanh mỗi nấc verify.

---

## PHẦN 4: HƯỚNG DẪN DEMO CHI TIẾT (Chạy trong 5 phút)

### 4.1. Chuẩn bị (làm trước ở nhà)
```bash
cd demo
chmod +x generate_certs.sh
./generate_certs.sh
# sinh ra: ca.key/ca.crt, server.key/server.crt, attacker.key/attacker.crt
pip install cryptography  # chỉ cần nếu chạy cert_inspect.py
python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### 4.2. Chạy demo chuẩn
Terminal 1:
```bash
python3 server_tls.py
# Output: Listening on 127.0.0.1:8443 with TLS 1.2+ ...
```
Terminal 2:
```bash
python3 client_tls.py
# Output: Cipher: TLS_AES_256_GCM_SHA384, TLSv1.3
#         Peer cert subject: CN=localhost, issuer: MiniCA ...
#         Server reply: Hello Secure World over TLS!
```

Terminal 3 (Wireshark):
```
Filter: tls || tcp.port==8443
Thấy: Client Hello → Server Hello → Certificate → ... → Application Data
Chuột phải 1 gói Application Data → Follow → TCP Stream → chỉ thấy bytes mã hóa.
```

### 4.3. Demo tấn công MITM (điểm ăn điểm cao nhất)
```bash
# Sửa server_tls.py dùng attacker.crt hoặc chạy:
python3 server_tls.py attacker.crt attacker.key
python3 client_tls.py
# Kỳ vọng: ssl.SSLCertVerificationError: self-signed / unable to get local issuer
```
Giải thích: client đã `load_verify_locations(ca.crt)` + `check_hostname=True` nên từ chối cert giả. Nếu tắt verify (`CERT_NONE`) thì sẽ bị lừa → minh họa tầm quan trọng của validation.

### 4.4. Backup nếu demo lỗi
- Chụp sẵn log thành công + log lỗi vào slide.
- Quay video màn hình 30s chạy 2 terminal.
- Câu chữa cháy: "Do giới hạn firewall phòng học, em show log Wireshark đã bắt trước ở nhà, bản chất gói tin hoàn toàn tương tự."

---

## PHẦN 5: KỊCH BẢN NÓI 12 PHÚT (Chia người)

**Người 1 (0-4'):** Slide 1-4. Mở đầu + motivation + lịch sử + kiến trúc. Punchline: HTTP là bưu thiếp, HTTPS là thư niêm phong.

**Người 2 (4-8'):** Slide 5-7. Handshake 1.2 → 1.3 → Encryption. Vẽ tay sequence lên bảng nếu được hỏi sâu. Nhấn mạnh random, pre-master, ECDHE-PFS, cipher suite.

**Người 3 (8-12'):** Slide 8-11. Certificate validation + Live demo + Attacks. Người này chạy lệnh, đọc log Wireshark, cố tình chạy attacker để show lỗi.

**Kết (1'):** Cả nhóm: Slide 13. Mỗi người 1 câu takeaway.

Mẹo: Đặt câu hỏi tương tác giữa chừng: "Ai từng bấm 'Proceed to unsafe site'? Đó chính là bỏ qua bước validation!"

---

## PHẦN 6: 12 CÂU HỎI Q&A DỰ KIẾN + TRẢ LỜI NGẮN

1. **TLS khác SSL thế nào?** SSL đã deprecated, TLS là chuẩn tiếp nối (RFC). Gọi "SSL" chỉ là thói quen.
2. **Tại sao cần cả asymmetric lẫn symmetric?** Asymmetric chậm, chỉ dùng trao khóa/xác thực; symmetric nhanh, mã hóa dữ liệu lớn.
3. **Forward Secrecy là gì?** ECDHE sinh khóa tạm mỗi phiên → lộ long-term key không lộ quá khứ. RSA static không có.
4. **TLS 1.2 vs 1.3 khác gì?** 1.3: 1-RTT (nhanh), bỏ cipher yếu, bắt buộc PFS, mã hóa cert.
5. **Client validate cert thế nào?** Check expiry, hostname, verify signature chain về Root CA, CRL/OCSP.
6. **Self-signed cert sao browser báo đỏ?** Vì không chain về Root CA tin cậy trong trust store.
7. **MITM vượt TLS bằng cách nào?** Cert giả + lừa user bỏ qua cảnh báo, hoặc cài Root CA độc, hoặc downgrade. Fix: HSTS, pinning, CT.
8. **Cipher suite đọc thế nào?** Ví dụ `ECDHE_RSA_AES128_GCM_SHA256` = trao đổi ECDHE + xác thực RSA + mã hóa AES-GCM + hash SHA256.
9. **TLS có chống replay không?** Có: random + sequence number trong record + session ticket chống reuse. 0-RTT của 1.3 cần chống replay ở tầng app.
10. **Heartbleed là gì?** Bug OpenSSL đọc quá giới hạn buffer qua heartbeat extension, lộ RAM gồm private key. Fix: patch + revoke.
11. **SNI là gì, lộ gì?** Server Name Indication gửi hostname ở ClientHello (plain) để server chọn cert. Fix mới: ECH mã hóa SNI.
12. **QUIC liên quan gì TLS?** QUIC (HTTP/3) tích hợp sẵn TLS 1.3 handshake trong UDP, giảm latency.

---

## PHẦN 7: TÀI LIỆU THAM KHẢO (ghi vào slide cuối)

- RFC 8446 – TLS 1.3; RFC 5246 – TLS 1.2; RFC 5280 – X.509.
- OWASP TLS Cheat Sheet; Mozilla SSL Configuration Generator.
- Illustarted TLS 1.3 (tls13.xargs.org) – hình handshake cực đẹp.
- Sách: *Bulletproof SSL and TLS* – Ivan Ristić; *Network Security Essentials* – Stallings.
- Tool: Wireshark, OpenSSL (`openssl s_client -connect`), Let's Encrypt.

---

## PHẦN 8: CHECKLIST TRƯỚC NGÀY TRÌNH BÀY

- [ ] PowerPoint 15 slides theo outline trên, font lớn, ít chữ nhiều hình.
- [ ] Chạy thử demo 3 lần ở nhà, lưu log + pcap Wireshark backup.
- [ ] Sinh cert trước, copy `ca.crt/server.crt/server.key/attacker.*` vào USB.
- [ ] Test tắt WiFi trường (chạy localhost không cần mạng).
- [ ] Phân công người nói + người bấm slide + người gõ lệnh.
- [ ] In 1 trang cheat Q&A mang theo.

*Chúc nhóm trình bày tốt! Nếu cần, hãy mở file demo/ để chạy thử ngay.*
