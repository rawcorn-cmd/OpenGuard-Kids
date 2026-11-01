# Slide Bài Giảng: Mô Hình Mạng OSI – TCP/IP

> **Nguồn:** Slide bài giảng chính khóa Khoa CNTT - HCMUS (`04 - OSI - TCPIP- T5.pdf`)

---

## Slide 1

```text
Mô hình mạng OSI – TCP/IP
```

---

## Slide 2

```text
NỘI DUNG
1.
2.
3.
4.

Giới thiệu
Mô hình OSI
Mô hình TCP/IP
Đóng gói dữ liệu

2
```

---

## Slide 3

```text
GIỚI THIỆU - 1

Chào, Tôi
tên A

Hi, My
name’s B

3
```

---

## Slide 4

```text
GIỚI THIỆU - 2

4
```

---

## Slide 5

```text
02/2009

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

5
```

---

## Slide 6

```text
02/2009

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

6
```

---

## Slide 7

```text
GIỚI THIỆU - 3

02/2009

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

Network

7
```

---

## Slide 8

```text
GIỚI THIỆU - 4

8
```

---

## Slide 9

```text
GIỚI THIỆU - 5
 Xem mạng như là 1 chồng các lớp (layer)
 Lớp N cung cấp các dịch vụ cho lớp N+1
 Mỗi lớp trao đổi với nhau theo 1 giao thức
 Ưu điểm:

Mỗi lớp có 1 chức năng riêng, lớp N sử dụng dịch vụ do
lớp N-1 cung cấp
 Giảm độ phức tạp khi xử lý dữ liệu
 Dễ quản lý
 Dễ mở rộng, dễ phát triển
 Đơn giản


9
```

---

## Slide 10

```text
GIỚI THIỆU - 5
SNA

Cần có 1 mô hình chung

ARPANET

GiẢI QUYẾT??

DECNET

10
```

---

## Slide 11

```text
NỘI DUNG
1.
2.
3.
4.

Giới thiệu
Mô hình OSI
Mô hình TCP/IP
Đóng gói dữ liệu

11
```

---

## Slide 12

```text
OSI MODEL - 1
 Mô hình OSI (Open Systems Interconnection):

do tổ chức ISO (International Organization for
Standardization) đề xuất từ 1977
 công bố lần đầu vào 1984
 Là khung sườn biểu diễn cách thông tin di chuyển trên mạng
như thế nào


12
```

---

## Slide 13

```text
OSI MODEL - 2

Application
(Upper) Layers

7

1

Application

Tầng ứng dụng

Presentation

Tầng trình bày

Session

Tầng phiên

Transport

Tầng vận chuyển

Network

Tầng mạng

Data link

Data Flow
Layers
Tầng liên (Lower)
kết

Physical

Tầng vật lý
13
```

---

## Slide 14

```text
OSI - 2

02/2009

A

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

B

Computer Network

14
```

---

## Slide 15

```text
OSI MODEL - 4

Application

Cung cấp các dịch vụ mạng

Presentation Cách biểu diễn dữ liệu
Session

Quản lý các phiên của ứng dụng

15
```

---

## Slide 16

```text
OSI MODEL - 5

Transport Truyền dữ liệu end-to-end
Network

Truyền dữ liệu host-host

Data link Truyền dữ liệu link-link
Physical

Truyền dữ liệu nhị phân

16
```

---

## Slide 17

```text
NỘI DUNG
1.
2.
3.
4.

Giới thiệu
Mô hình OSI
Mô hình TCP/IP
Đóng gói dữ liệu

17
```

---

## Slide 18

```text
MÔ HÌNH TCP/IP - 1
 TCP/IP - Transmission Control Protocol/Internet

Protocol
 Do Cerf và Kahn định nghĩa vào năm 1974
 Đặc tả chồng giao thức

18
```

---

## Slide 19

```text
MÔ HÌNH TCP/IP - 2
OSI

TCP/IP

Application

Presentation

Application

Session
Transport

Transport

Network

Internet

Data link

Host to Network
(Network Interface)

Physical

19
```

---

## Slide 20

```text
20
```

---

## Slide 21

```text
NỘI DUNG
1.
2.
3.
4.

Giới thiệu
Mô hình OSI
Mô hình TCP/IP
Đóng gói dữ liệu

21
```

---

## Slide 22

```text
ĐÓNG GÓI DỮ LIỆU - 1
 Đóng gói dữ liệu =

Encapsulation

 Là quá trình đóng gói dữ liệu với các thông tin của

giao thức trước khi chuyển đi

22
```

---

## Slide 23

```text
ĐÓNG GÓI DỮ LIỆU - 2
Application

Presentation

Upper Layer Data

Session

PDU
(Protocol Data Unit)
Segment

TCP Header

Upper Layer Data

Transport

IP Header

Data

Network

Packet

LLC Header

Data

Data Link

Frame

Physical

Bits

MAC Header

Data

0101110101001000010

FCS

FCS

23
```

---

## Slide 24

```text
ĐÓNG GÓI DỮ LIỆU - 3

24
```

---

## Slide 25

```text
PHÂN RÃ
Application
Presentation

Upper Layer Data

Session

Transport

Network

Upper Layer Data

TCP+ Upper Layer Data

IP + TCP + Upper Layer Data

Data Link
LLC Hdr + IP + TCP + Upper Layer Data

Physical

0101110101001000010

25
```

---

## Slide 26

```text
MINH HỌA
M

datagram Hn Ht

M

frame Hl Hn Ht

M

M

application
transport
network
link
physical
link
physical

switch

M
Ht

M

Hn Ht

M

Hl Hn Ht

M

destination

Hn Ht

M

application
transport
network
link
physical

Hl Hn Ht

M

network
link
physical

Hn H t

M

26
router

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

message
segment Ht

02/2009

source
```

---

## Slide 27

```text
TÀI LIỆU THAM KHẢO
02/2009

 Slide bài giảng của J.F Kurose and K.W. Ross về

Computer Networking: A Top Down Approach

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

27
```

---

## Slide 28

```text
FTP

Telnet

02/2009

Application

HTTP

Transmission
Media

Application

coaxial
cable

Telnet

fiber
optic

packet
radio

HTTP

FTP

Transport
& Network

Transmission
Media

Layered

coaxial
cable

fiber
optic

packet
radio

28

BM MMT&VT - KHOA CNTT - ĐH KHTN TP.HCM

No-layered
```

---

