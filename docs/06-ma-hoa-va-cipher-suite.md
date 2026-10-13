# 06 — Mã hóa Hybrid và Cipher Suite (trọng tâm 2)

> Thuộc Slide 7 roadmap. Đọc xong bạn đọc vanh vách `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` nghĩa là gì.

## 1. Vì sao phải "lai" (hybrid)?

- **Asymmetric (RSA, ECDH):** giải được bài toán "trao khóa giữa hai người chưa từng gặp" + xác thực, nhưng **chậm hơn ~1000 lần**, không thể mã hóa video/streaming bằng nó.
- **Symmetric (AES, ChaCha20):** nhanh (có hỗ trợ phần cứng AES-NI), mã hóa GB dữ liệu nhẹ nhàng, nhưng **cần chung khóa trước** — mà gửi khóa qua mạng trần thì lộ.

TLS kết hợp: dùng asymmetric **một lần lúc handshake** để thống nhất khóa phiên, rồi dùng symmetric **suốt phiên** để mã hóa dữ liệu lớn. Đây gọi là hybrid encryption.

## 2. Đọc cipher suite như đọc tên món ăn (4 thành phần)

Ví dụ TLS 1.2:

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    ─────┬──── ─┬─ ─────┬────────── ───┬───
         │      │        │              └─ Hash/PRF: SHA256 (sinh khóa, hash handshake)
         │      │        └─ Bulk cipher: AES-128-GCM (mã hóa dữ liệu thật, AEAD)
         │      └─ Auth: RSA (xác thực cert bằng chữ ký RSA)
         └─ KeyEx: ECDHE (trao đổi khóa Diffie-Hellman tạm thời)
```

Thêm ví dụ để luyện:
- `TLS_RSA_WITH_AES_256_CBC_SHA` → KeyEx RSA static (không PFS!) + AES-CBC (dễ dính BEAST/POODLE) → **yếu, cấm dùng**.
- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384` → ECDHE + cert ECDSA + AES-GCM → **mạnh, hiện đại**.

TLS 1.3 gọn hơn, tên chỉ còn bulk + hash (vì KeyEx/Auth cố định là ECDHE + chữ ký):
```
TLS_AES_256_GCM_SHA384  /  TLS_CHACHA20_POLY1305_SHA256
```

## 3. Từng khối mã hóa hiểu ở mức trình bày

### Key exchange: RSA static vs ECDHE
- **RSA static:** client mã hóa pre-master bằng public key server. Đơn giản nhưng 1 điểm chết: lộ private key server là giải mã được **toàn bộ quá khứ** đã bắt được.
- **ECDHE (Ephemeral):** mỗi phiên sinh cặp khóa DH tạm, vứt sau khi xong. Lộ private key dài hạn cũng không giải mã được quá khứ → gọi là **Perfect Forward Secrecy (PFS)**. Cái giá: tốn thêm 1 phép toán đường cong elliptic (rất rẻ trên CPU hiện nay).

Câu chốt khi bị hỏi: "PFS = mỗi phiên một khóa tạm, lộ hôm nay không lộ hôm qua."

### Bulk encryption: vì sao phải GCM/ChaCha20-Poly1305?
- AES-CBC cũ cần thêm HMAC riêng (MAC-then-Encrypt) → dễ sai thứ tự, dính padding oracle (POODLE).
- **AEAD (Authenticated Encryption with Associated Data)** như GCM, CCM, Poly1305 làm **mã hóa + xác thực trong một bước**, kèm tag (16 byte) để phát hiện sửa đổi. Nhanh hơn (song song hóa được) và an toàn hơn.
- ChaCha20-Poly1305 sinh ra cho máy không có AES-NI (điện thoại cũ, IoT) — nhanh bằng phần mềm thuần.

### Hash: SHA-256/384
Dùng trong PRF/HKDF và hash Finished. SHA1/MD5 đã bị tìm ra va chạm (collision) → cấm.

## 4. Demo liên hệ (để nói khi live demo)

Khi chạy `client_tls.py`, dòng in ra:
```
Cipher: ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
```
Giải thích: đang dùng AES-256-GCM, hash SHA-384, khóa 256-bit. Server ép `ECDHE-RSA-AES128-GCM` cho TLS 1.2 trong `server_tls.py` (`set_ciphers`) để đảm bảo dù client cũ cũng vẫn PFS + AEAD.

## Tóm tắt 3 dòng

- Hybrid = asymmetric trao khóa 1 lần + symmetric mã hóa cả phiên.
- Cipher suite 4 phần: KeyEx_Auth_WITH_Bulk_Hash; 1.3 chỉ còn Bulk_Hash.
- ECDHE cho PFS; AEAD (GCM/Poly1305) vừa giấu vừa chống sửa.

## Tự kiểm tra

1. Giải thích từng phần của `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`?
2. Vì sao RSA static không có PFS còn ECDHE có?
3. AEAD khác CBC+HMAC ở điểm nào?
