# T30 — Kịch bản Demo TLS Chain of Trust (MiniCA vs Attacker)

**Thời lượng:** ~10–12 phút | **Môi trường:** 1 máy Linux, không cần root (dùng 127.0.0.1)

---

## 0. Mục tiêu demo

Sau demo, người xem hiểu được 3 điều:

1. **Trust của TLS dựa trên chuỗi tin cậy (chain of trust)** — client tin cert của server
   vì nó được ký bởi một CA nằm trong truststore, KHÔNG phải vì CN/SAN giống nhau.
2. **MITM với cert giả sẽ bị chặn ngay ở bước xác minh chuỗi** — trước cả khi nói đến hostname.
3. SAN chỉ là bước kiểm tra *thứ hai*; bước kiểm tra *đầu tiên* là issuer có được tin không.

**Chốt slide:** "Attacker copy cả CN=localhost vào cert của mình vẫn fail —
vì trust dựa trên chain, không phải trust dựa trên tên."

---

## 1. Chuẩn bị (chạy trước khi trình bày)

```bash
cd ~/Documents/"Kì 1 năm 4"/LTM/Test
./generate_certs.sh          # sinh ca/server/attacker cert + key
python3 cert_inspect.py      # xem nội dung cert
```

Server và client chỉ ở trên 127.0.0.1:8443 — mở **3 terminal**:

| Terminal | Vai trò |
| --- | --- |
| 1 | server thật trên:8443 (dùng server.crt do MiniCA ký) |
| 2 | server của attacker (dùng attacker.crt, cùng script server_tls.py) |
| 3 | client victim (client_tls.py) |

---

## 2. PHẦN A — Inspect chứng chỉ (1 phút)

```bash
python3 cert_inspect.py
```

Điểm nhấn khi trình bày:

| Cert | Issuer | SAN | CA:TRUE? | Nói gì trên slide |
| --- | --- | --- | --- | --- |
| `ca.crt` | MiniCA (self-signed) | không có | True | **Bình thường**: CA không cần SAN, client tin nó qua subject/fingerprint |
| `server.crt` | CN=MiniCA (do CA ký) | localhost, www.localhost, 127.0.0.1 | False | Cert "hợp lệ": đúng CA + có SAN=localhost |
| `attacker.crt` | O=Attacker (self-signed) | không có | True | Cert "lạ": cùng CN nhưng issuer khác — issuer không nằm trong truststore |

> Giải thích nhanh nếu bị hỏi "sao CA không có SAN": hostname checking áp cho
> cert của *server* (client kiểm tra xem tên nó gọi có trong cert không). CA
> cert được dùng để làm điểm neo tin cậy, không "trả lời" cho hostname nào cả.

### 2b. Xác minh chuỗi bằng openssl (minh chứng trực quan nhất)

```bash
openssl verify -CAfile ca.crt server.crt     # => OK
openssl verify -CAfile ca.crt attacker.crt   # => error 20 ... / self-signed hoặc unable to get local issuer certificate
```

→ Đây chính là logic mà `client_tls.py` sẽ lặp lại bằng Python API ở phần sau.

---

## 3. PHẦN B — Phiên TLS hợp lệ (1 phút)

**Terminal 1:**
```bash
python3 server_tls.py                     # mặc định dùng server.crt
```

**Terminal 3:**
```bash
python3 client_tls.py
```

Kết quả mong đợi — chỉ ra 3 dòng quan trọng (máy có OpenSSL 3.x sẽ negotiate TLS 1.3):

```
[SERVER] Handshake OK with ...
         cipher=('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
[CLIENT] TLS version : TLSv1.3
[CLIENT] Peer issuer : CN=MiniCA,O=LTM-T30,C=VN          <- đúng CA đã load
[CLIENT] SAN         : ('localhost', 'www.localhost', ('127.0.0.1',))
[CLIENT] OK: cert hop le, du lieu duoc ma hoa
```

**Kịch bản trình bày:** "Client chỉ tin duy nhất file `ca.crt` (1 dòng
`load_verify_locations`). Server chỉ cần một cert được CA này ký. Ba điều kiện
cùng đạt: chain OK + hostname/SAN OK → handshake OK."

---

## 4. PHẦN C — Attacker MITM (trọng tâm, ~3 phút)

### Bước 1 — Server thật "ra khỏi mạng"
Trong Terminal 1, nhấn `Ctrl+C` để tắt server. (Ghi chú xuất trình: trong thực tế
attacker không thể tắt server, mà dùng DNS-spoof / ARP-spoof để redirect traffic
về mình — nói 1 câu cho kỹ.)

### Bước 2 — Attacker chiếm cổng 8443 với cert giả
**Terminal 2:**
```bash
python3 server_tls.py attacker.crt attacker.key
```
Output: `[SERVER] Cert: attacker.crt` — attacker đang nghe ngay tại
127.0.0.1:8443, tại vị trí client định gọi "localhost".

### Bước 3 — Victim kết nối
**Terminal 3:**
```bash
python3 client_tls.py
```

Kết quả mong đợi — handshake **FAIL** nhưng log gọn (không traceback):

```
[CLIENT] XX HANDSHAKE FAILED - cert khong duoc tin cay
[CLIENT]    reason : CERTIFICATE_VERIFY_FAILED
[CLIENT]    detail : self-signed certificate
[CLIENT]    code   : 18
[CLIENT]    -> issuer khong nam trong truststore (ca.crt)
[CLIENT]    -> dung lai o buoc chain-of-trust, chua check hostname/SAN
```

Phía server attacker cũng log gọn và **không crash**:

```
[SERVER] Handshake REJECTED by client ('127.0.0.1', 40540)
[SERVER]   reason : TLSV1_ALERT_UNKNOWN_CA
[SERVER]   -> client khong tin cert nay (chain-of-trust fail)
```

### Bước 4 (tùy chọn nâng cao) — Attacker có SAN vẫn fail
Nếu còn thời gian, tạo thêm cert giả có đủ SAN:

```bash
openssl req -x509 -newkey rsa:2048 -sha256 -days 365 -nodes \
  -keyout attacker2.key -out attacker2.crt \
  -subj "/C=VN/O=Attacker/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

Sau đó chạy lại server attacker với `attacker2.crt` + `attacker2.key`, client
vẫn báo **cùng một lỗi CERTIFICATE_VERIFY_FAILED** (self-signed certificate).

→ Chứng minh: **SAN có khớp cũng vô nghĩa nếu issuer không được tin**. Chain
chain-check xảy ra trước hostname-check. (Điều này cũng giải thích tại sao
`cert_inspect.py` hiển thị attacker.crt không có SAN — `openssl req -x509`
không tự thêm SAN cho cert self-signed.)

### Bước 5 — Giải thích line-of-defense trong client_tls.py (≥ 30 giây trên slide)

Ba dòng code chính là lớp phòng thủ theo đúng RFC 5280:

```python
ctx.verify_mode = ssl.CERT_REQUIRED    # lớp 1: cert phải do CA trong truststore ký
ctx.check_hostname = True              # lớp 2: SAN phải khớp hostname đang gọi
ctx.load_verify_locations(CA)          # truststore: chỉ tin duy nhất MiniCA
```

Attacker fail ngay **lớp 1 (CERTIFICATE_VERIFY_FAILED)** — ở bước kiểm tra issuer,
chưa tới lớp 2.

---

## 5. (Bonus ~2 phút) — Điều gì xảy ra nếu client "lười"?

Sao chép `client_tls.py` thành `client_bad.py` và thêm:

```python
ctx.check_hostname = False      # lười hostname-check
ctx.verify_mode = ssl.CERT_NONE # chấp nhận mọi cert
```

Chạy lại với attacker đang chiếm cổng:

```bash
python3 server_tls.py attacker.crt attacker.key    # terminal 2 (đang chạy)
python3 client_bad.py                              # terminal 3
```

→ Kết nối **thành công**, client không hề biết MITM đang diễn ra. Minh họa
tình huống thực tế: khi người ta disable verify để "fix nhanh" một số cảnh báo,
chính là tạo lỗ hổng MITM.

**Kết băng slide:** `check_hostname=False` + `CERT_NONE` = tự tay mở đường cho MITM.

---

## 6. (Bonus) Wireshark — trực quan hoá "dữ liệu được mã hoá"

```bash
sudo tcpdump -i lo port 8443 -X -c 30
```

- Phiên **hợp lệ** (server.crt): dữ liệu trông như rác — Application Data được
  AES-GCM mã hoá.
- Đối chiếu với server **plain-text** (chạy `nc -l -p 8443`): bạn thấy đầy đủ
  HTTP GET + "Hello ...". Một câu là xong điểm slide.

---

## 7. Troubleshooting nhanh trong lúc demo

| Triệu chứng | Nguyên nhân | Fix |
| --- | --- | --- |
| Client fail cả khi dùng server.crt | đồng hồ VM bị lệch → cert expire/future | chạy lại `./generate_certs.sh` |
| Server báo Address already in use | server cũ chưa chết | `lsof -i :8443` → `kill <pid>` |
| Client báo unknown CA | sai đường dẫn ca.crt trong client_tls.py | kiểm tra `CA = os.path.join(BASE, "ca.crt")` |
| Attacker server không lên được | sai cặp cert/key | đúng cặp `attacker.crt` + `attacker.key` |

---

## 8. Tổng kết — 3 câu chốt slide

1. TLS không biết ai *là* ai; TLS chỉ biết cert được *ai ký*.
2. Attacker ký bằng CA của chính mình → **chain verification fail trước hostname check**.
3. SAN chỉ có ý nghĩa sau khi trust chain đã được xác thực — nó chống "đúng CA
   nhưng cert cho host khác", không phải chống "CA giả".


rm -f /tmp/sslkeys.log