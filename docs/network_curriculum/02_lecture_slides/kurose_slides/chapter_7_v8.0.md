# Slide Bài Giảng: Chapter 7 v8.0

> **Nguồn gốc:** Slide chính thức của tác giả Kurose & Ross (Chapter_7_v8.0.pptx)

---

### Slide 2: Wireless and Mobile Networks: context

* Wireless and Mobile Networks: 7-
* 2
* more wireless (mobile) phone subscribers than fixed (wired) phone subscribers
* (10-to-1 in 2019)
* !
* more mobile-broadband-connected devices than fixed-broadband-connected devices devices (
* 5-1 in 2019)
* !
* 4G/5G cellular networks now embracing Internet protocol stack, including SDN
* two important (but different) challenges
* wireless:
* communication over wireless link
* mobility:
* handling the mobile user who changes point of attachment to network
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 3: Chapter 7 outline

* Introduction
* Wireless
* Wireless Links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols
* Wireless and Mobile Networks: 7-
* 3
* style.visibility
* style.visibility

---

### Slide 4: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 4
* wired network
* infrastructure

---

### Slide 5: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 5
* wired network
* infrastructure
* wireless hosts
* laptop, smartphone, IoT
* run applications
* may be stationary (non-mobile) or mobile
* wireless does
* not
* always mean mobility!

---

### Slide 6: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 6
* wired network
* infrastructure
* base station
* typically connected to wired network
* relay - responsible for sending packets between wired network and wireless host(s) in its
* “
* area
* ”
* e.g., cell towers,  802.11 access points

---

### Slide 7: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 7
* wired network
* infrastructure
* wireless link
* typically used to connect mobile(s) to base station, also used as backbone link
* multiple access protocol coordinates link access
* various transmission rates and distances, frequency bands

---

### Slide 8: Characteristics of selected wireless links

* Wireless and Mobile Networks: 7-
* 8
* Indoor
* Outdoor
* Midrange
* outdoor
* Long range
* outdoor
* 10-30m
* 50-200m
* 200m-4Km
* 4Km-15Km
* 2 Mbps
* 4G LTE
* 802.11ac
* 802.11n
* 802.11g
* 802.11b
* 3.5 Gbps
* 600 Mbps
* 54 Mbps
* 11 Mbps
* Bluetooth
* 802.11ax
* 14 Gbps
* 5G
* 10 Gbps
* 802.11 af,ah

---

### Slide 9: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 9
* wired network
* infrastructure
* infrastructure mode
* base station connects mobiles into wired network
* handoff: mobile changes base station providing connection into wired network

---

### Slide 10: Elements of a wireless network

* Wireless and Mobile Networks: 7-
* 10
* ad hoc mode
* no base stations
* nodes can only transmit to other nodes within link coverage
* nodes organize themselves into a network: route among themselves

---

### Slide 11: Wireless network taxonomy

* Wireless and Mobile Networks: 7-
* 11
* single hop
* multiple hops
* infrastructure
* (e.g., APs)
* no
* infrastructure
* host connects to  base station (WiFi, cellular) which connects to  larger Internet
* no base station, no connection to larger
* Internet (Bluetooth, ad hoc nets)
* host may have to relay through several wireless nodes to connect to larger
* Internet:
* mesh net
* no base station, no connection to larger  Internet. May have to relay to reach other  a given wireless node MANET, VANET

---

### Slide 12: Chapter 7 outline

* Introduction
* Link Layer: 6-
* 12
* Wireless
* Wireless links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols

---

### Slide 13: Wireless link characteristics

* (1)
* Wireless and Mobile Networks: 7-
* 13
* important
* differences from wired link ….
* decreased signal strength
* :
* radio signal attenuates as it propagates through matter (path loss)
* interference from other sources:
* wireless network frequencies (e.g., 2.4 GHz) shared by many devices (e.g., WiFi, cellular, motors): interference
* multipath propagation:
* radio signal reflects off objects ground, arriving at destination at slightly different times
* …. make communication across (even a point to point) wireless link much more “difficult”
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 14: Wireless link characteristics

* (2)
* Wireless and Mobile Networks: 7-
* 14
* SNR: signal-to-noise ratio
* larger SNR – easier to extract signal from noise (a “good thing”)
* SNR versus BER tradeoffs
* given physical layer:
* increase power -> increase SNR->decrease BER
* given SNR:
* choose physical layer that meets BER requirement, giving highest throughput
* SNR may change with mobility: dynamically adapt physical layer (modulation technique, rate)
* 10
* 20
* 30
* 40
* QAM256 (8 Mbps)
* QAM16 (4 Mbps)
* BPSK (1 Mbps)
* SNR(dB)
* BER
* 10
* -1
* 10
* -2
* 10
* -3
* 10
* -5
* 10
* -6
* 10
* -7
* 10
* -4
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 15: Wireless link characteristics

* (3)
* Wireless and Mobile Networks: 7-
* 15
* Multiple wireless senders, receivers create additional problems (beyond multiple access):
* A
* B
* C
* Hidden terminal problem
* B, A hear each other
* B, C hear each other
* A, C can not hear each other means A, C unaware of their interference at B
* A
* B
* C
* A
* ’
* s signal
* strength
* space
* C
* ’
* s signal
* strength
* Signal attenuation:
* B, A hear each other
* B, C hear each other
* A, C can not hear each other interfering at B
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 16: Code Division Multiple Access (CDMA)

* Wireless and Mobile Networks: 7-
* 16
* unique
* “
* code
* ”
* assigned to each user; i.e., code set partitioning
* all users share same frequency, but each user has own
* “
* chipping
* ”
* sequence (i.e., code) to encode data
* allows multiple users to
* “
* coexist
* ”
* and transmit simultaneously with minimal interference (if codes are “orthogonal”)
* encoding:
* inner product:
* (original data) X (chipping sequence)
* decoding:
* summed
* inner-product:
* (encoded data) X (chipping sequence)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 17: CDMA encode/decode

* Wireless and Mobile Networks: 7-
* 17
* slot 1
* slot 0
* d
* 1
* = -1
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* Z
* i,m
* = d
* i
* .
* c
* m
* d
* 0
* = 1
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* slot 0
* channel
* output
* slot 1
* channel
* output
* channel output Z
* i,m
* sender
* code
* data
* bits
* slot 1
* slot 0
* d
* 1
* = -1
* d
* 0
* = 1
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* 1
* 1
* 1
* 1
* 1
* -
* 1
* -
* 1
* -
* 1
* -
* slot 0
* channel
* output
* slot 1
* channel
* output
* receiver
* code
* received
* input
* D
* i
* =
* S
* Z
* i,m
* .
* c
* m
* m=1
* M
* M
* … but this isn’t really useful yet!
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 18: CDMA: two-sender interference

* Wireless and Mobile Networks: 7-
* 18
* using same code as sender 1, receiver recovers sender 1’s original data from summed channel data!
* Sender 1
* Sender 2
* channel sums together transmissions by sender 1 and 2
* … now
* that’s
* useful!
* style.visibility
* style.visibility

---

### Slide 19: Chapter 7 outline

* Introduction
* Link Layer: 6-
* 19
* Wireless
* Wireless links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols

---

### Slide 20: IEEE 802.11 Wireless LAN

* Wireless and Mobile Networks: 7-
* 20
* {5C22544A-7EE6-4342-B048-85BDC9FD1C3A}
* IEEE 802.11 standard
* Year
* Max data rate
* Range
* Frequency
* 802.11b
* 1999
* 11 Mbps
* 30 m
* 2.4 Ghz
* 802.11g
* 2003
* 54 Mbps
* 30m
* 2.4 Ghz
* 802.11n  (WiFi 4)
* 2009
* 600
* 70m
* 2.4, 5 Ghz
* 802.11ac (WiFi 5)
* 2013
* 3.47Gpbs
* 70m
* 5 Ghz
* 802.11ax (WiFi 6)
* 2020
* (exp.)
* 14 Gbps
* 70m
* 2.4, 5 Ghz
* 802.11af
* 2014
* 35 – 560 Mbps
* 1 Km
* unused TV bands (54-790 MHz)
* 802.11ah
* 2017
* 347Mbps
* 1 Km
* 900 Mhz
* all use CSMA/CA for multiple access, and have base-station and ad-hoc network versions

---

### Slide 21: 802.11 LAN architecture

* Wireless and Mobile Networks: 7-
* 21
* wireless host communicates with base station
* base station = access point (AP
* )
* Basic Service Set (BSS)
* (aka “cell”) in infrastructure mode contains:
* wireless hosts
* access point (AP): base station
* ad hoc mode: hosts only
* BSS 1
* BSS 2
* Internet
* switch
* or router
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 22: 802.11: Channels, association

* Wireless and Mobile Networks: 7-
* 22
* spectrum divided into channels at different frequencies
* AP admin chooses frequency for AP
* interference possible: channel can be same as that chosen by neighboring AP!
* arriving host: must
* associate
* with an AP
* scans channels, listening for
* beacon frames
* containing AP
* ’
* s name (SSID) and MAC address
* selects AP to associate with
* then may perform authentication [Chapter 8]
* then typically run DHCP to get IP address in AP’s subnet
* BSS
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 23: 802.11: passive/active scanning

* Wireless and Mobile Networks: 7-
* 23
* AP 2
* AP 1
* H1
* BBS 2
* BBS 1
* 1
* 2
* 3
* 1
* passive scanning:
* beacon frames sent from APs
* association Request frame sent: H1 to selected AP
* association Response frame sent from  selected AP to H1
* AP 2
* AP 1
* H1
* BBS 2
* BBS 1
* 1
* 2
* 2
* 3
* 4
* active  scanning:
* Probe Request frame broadcast from H1
* Probe Response frames sent from APs
* Association Request frame sent: H1 to selected AP
* Association Response frame sent from selected AP to H1
* style.visibility

---

### Slide 24: IEEE 802.11: multiple access

* Wireless and Mobile Networks: 7-
* 24
* avoid collisions: 2
* +
* nodes
* transmitting at same time
* 802.11: CSMA - sense before transmitting
* don’t collide with detected ongoing transmission by another node
* 802.11:
* no
* collision detection!
* difficult to sense collisions: high transmitting signal, weak received signal due to fading
* can’t sense all collisions in any case: hidden terminal, fading
* goal:
* avoid collisions:
* CSMA/
* C
* ollision
* A
* voidance
* space
* A
* B
* C
* A
* B
* C
* A
* ’
* s signal
* strength
* C
* ’
* s signal
* strength
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 25: IEEE 802.11 MAC Protocol: CSMA/CA

* Wireless and Mobile Networks: 7-
* 25
* 802.11 sender
* 1
* if sense channel idle
* for
* DIFS
* then
* transmit entire frame (no CD)
* sender
* receiver
* DIFS
* data
* SIFS
* ACK
* 802.11 receiver
* if frame received OK
* return ACK after
* SIFS
* (ACK needed due to hidden terminal problem)
* 2 if sense channel busy then
* start random backoff time
* timer counts down while channel idle
* transmit when timer expires
* if no ACK, increase random backoff interval, repeat 2
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 26: Avoiding collisions (more)

* Wireless and Mobile Networks: 7-
* 26
* idea:
* sender
* “
* reserves
* ”
* channel use for data frames using small reservation packets
* sender first transmits
* small
* request-to-send
* (RTS) packet to BS using CSMA
* RTSs may still collide with each other (but they’re short)
* BS broadcasts
* clear-to-send
* CTS in response to RTS
* CTS heard by all nodes
* sender transmits data frame
* other stations defer transmissions

---

### Slide 27: Collision Avoidance: RTS-CTS exchange

* Wireless and Mobile Networks: 7-
* 27
* AP
* A
* B
* RTS(A)
* RTS(B)
* RTS(A)
* CTS(A)
* CTS(A)
* DATA (A)
* ACK(A)
* ACK(A)
* reservation collision
* defer
* time
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 28: 802.11 frame: addressing

* Wireless and Mobile Networks: 7-
* 28
* 2
* 2
* 6
* 6
* 6
* 2
* 6
* 0 - 2312
* 4
* Address 1:
* MAC address of wireless host or AP  to receive this frame
* Address 4:
* used only in ad hoc mode
* frame
* control
* duration
* address
* 1
* address
* 2
* address
* 4
* address
* 3
* payload
* CRC
* seq
* control
* Address 2:
* MAC address
* of wireless host or AP
* transmitting this frame
* Address 3:
* MAC address of router interface to which AP is attached

---

### Slide 29: 802.11 frame: addressing

* Wireless and Mobile Networks: 7-
* 29
* Internet
* H1
* R1
* AP MAC addr
* address 1
* address 2
* address 3
* 802.
* 11 WiFi
* frame
* R1 MAC addr
* H1 MAC addr
* R1 MAC addr
* MAC dest addr
* MAC source addr
* 802.
* 3 Ethernet
* frame
* H2 MAC addr
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 30: 802.11 frame: addressing

* Wireless and Mobile Networks: 7-
* 30
* 2
* 2
* 6
* 6
* 6
* 2
* 6
* 0 - 2312
* 4
* frame
* control
* duration
* address
* 1
* address
* 2
* address
* 4
* address
* 3
* payload
* CRC
* seq
* control
* duration of reserved
* transmission time (RTS/CTS)
* frame sequence # (for reliable data transfer)
* 2
* 2
* 4
* 1
* 1
* 1
* 1
* 1
* 1
* 1
* 1
* type
* from
* AP
* subtype
* to
* AP
* more
* frag
* WEP
* more
* data
* power
* mgt
* retry
* rsvd
* protocol
* version
* frame type (RTS, CTS, ACK, data)
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 31: 802.11: mobility within same subnet

* Wireless and Mobile Networks: 7-
* 31
* H1 remains in same IP subnet: IP address can remain same
* H1
* BBS 2
* BBS 1
* switch: which AP is associated with H1?
* self-learning (Ch. 6): switch will see frame from H1 and “remember” which switch port can be used to reach H1
* style.visibility
* style.visibility

---

### Slide 32: 802.11: advanced capabilities

* Wireless and Mobile Networks: 7-
* 32
* Rate adaptation
* base station, mobile dynamically change transmission rate (physical layer modulation technique) as mobile moves, SNR varies
* 10
* 20
* 30
* 40
* SNR(dB)
* BER
* 10
* -1
* 10
* -2
* 10
* -3
* 10
* -5
* 10
* -6
* 10
* -7
* 10
* -4
* QAM256 (8 Mbps)
* QAM16 (4 Mbps)
* BPSK (1 Mbps)
* operating point
* 1.
* SNR decreases, BER increase as node moves away from base station
* 2.
* When BER becomes too high, switch to lower transmission rate but with lower BER
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y

---

### Slide 33: 802.11: advanced capabilities

* Wireless and Mobile Networks: 7-
* 33
* power management
* node-to-AP:
* “
* I am going to sleep until next beacon frame
* ”
* AP knows not to transmit frames to this node
* node wakes up before next beacon frame
* beacon frame: contains list of mobiles with AP-to-mobile frames waiting to be sent
* node will stay awake if AP-to-mobile frames to be sent; otherwise sleep again until next beacon frame
* style.visibility
* style.visibility

---

### Slide 34: Personal area networks: Bluetooth

* Wireless and Mobile Networks: 7-
* 34
* less than 10 m diameter
* replacement for cables (mouse, keyboard, headphones)
* ad hoc: no infrastructure
* 2.4-2.5 GHz ISM radio band, up to 3 Mbps
* master controller / clients devices:
* master polls clients, grants requests for client transmissions
* radius of
* coverage
* C
* C
* C
* P
* P
* P
* P
* M
* C
* master device
* client device
* parked device (inactive)
* P
* M

---

### Slide 35: Personal area networks: Bluetooth

* Wireless and Mobile Networks: 7-
* 35
* TDM,
* 625
* m
* sec sec. slot
* FDM: sender uses
* 79 frequency channels in known, pseudo-random order slot-to-slot (spread spectrum)
* other devices/equipment not in piconet only interfere in some slots
* parked mode:
* clients can “go to sleep” (park) and later wakeup (to preserve battery)
* boo
* tstrapping:
* nodes self-assemble (plug and play) into piconet
* radius of
* coverage
* C
* C
* C
* P
* P
* P
* P
* M
* C
* master device
* client device
* parked device (inactive)
* P
* M

---

### Slide 36: Chapter 7 outline

* Introduction
* Link Layer: 6-
* 36
* Wireless
* Wireless links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols

---

### Slide 37: 4G/5G cellular networks

* Wireless and Mobile Networks: 7-
* 37
* the
* solution for wide-area mobile Internet
* widespread deployment/use:
* more mobile-broadband-connected devices than fixed-broadband-connected devices devices (5-1 in 2019)!
* 4G availability: 97% of time in Korea (90% in US)
* transmission rates up to 100’s Mbps
* technical standards: 3rd Generation Partnership Project (3GPP)
* wwww.3gpp.org
* 4G: Long-Term Evolution (LTE)standard
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 38: 4G/5G cellular networks

* Wireless and Mobile Networks: 7-
* 38
* similarities
* to wired Internet
* edge/core distinction, but both below to same carrier
* global cellular network: a network of networks
* widespread use of protocols we’ve studied: HTTP, DNS, TCP, UDP, IP, NAT, separation of data/control planes, SDN, Ethernet, tunneling
* interconnected to wired Internet
* differences
* from wired Internet
* different wireless link layer
* mobility as a 1
* st
* class service
* user “identity” (via SIM card)
* business model: users subscribe to a cellular provider
* strong notion of “home network” versus roaming on visited nets
* global access, with authentication infrastructure, and inter-carrier settlements
* style.visibility

---

### Slide 39: Mobile device

* (
* UE
* )
* Base station
* (eNode-B)
* Elements of 4G LTE architecture
* Wireless and Mobile Networks: 7-
* 39
* radio access
* network
* all-IP Enhanced Packet Core (EPC)
* Mobility Management Entity (
* MME
* )
* Serving Gateway (
* S-GW
* )
* Home Subscriber Service (
* HSS
* )
* PDN gateway (
* P-GW
* )
* to
* Internet
* …
* Mobile device:
* smartphone, tablet, laptop, IoT, ... with 4G LTE radio
* 64-bit International Mobile Subscriber Identity (IMSI), stored on SIM (Subscriber Identity Module) card
* LTE jargon: User Equipment (UE)
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 40: Elements of 4G LTE architecture

* Wireless and Mobile Networks: 7-
* 40
* Mobility Management Entity (
* MME
* )
* Serving Gateway (
* S-GW
* )
* Home Subscriber Service (
* HSS
* )
* PDN gateway (
* P-GW
* )
* …
* to
* Internet
* Mobile device
* (
* UE
* )
* Base station
* (eNode-B)
* Base station:
* at “edge” of carrier’s network
* manages wireless radio resources, mobile devices in its coverage area (“cell”)
* coordinates device authentication with other elements
* similar to WiFi AP but:
* active role in user mobility
* coordinates with nearly base stations to optimize radio use
* LTE jargon: eNode-B
* style.visibility

---

### Slide 41: Elements of 4G LTE architecture

* Wireless and Mobile Networks: 7-
* 41
* Mobility Management Entity (
* MME
* )
* Serving Gateway (
* S-GW
* )
* Home Subscriber Service (
* HSS
* )
* PDN gateway (
* P-GW
* )
* …
* to
* Internet
* Mobile device
* (
* UE
* )
* Base station
* (eNode-B)
* Home Subscriber Service
* stores info about mobile devices for which the HSS’s network is their “home network”
* works with MME in device authentication
* style.visibility

---

### Slide 42: Elements of 4G LTE architecture

* Wireless and Mobile Networks: 7-
* 42
* Mobility Management Entity (
* MME
* )
* Serving Gateway (
* S-GW
* )
* Home Subscriber Service (
* HSS
* )
* PDN gateway (
* P-GW
* )
* …
* to
* Internet
* Mobile device
* (
* UE
* )
* Base station
* (eNode-B)
* Serving Gateway (S-GW), PDN Gateway (P-GW)
* lie on data path from mobile to/from Internet
* P-GW
* gateway to mobile cellular network
* Looks like nay other internet gateway router
* provides NAT services
* other routers:
* extensive use of tunneling
* style.visibility

---

### Slide 43: Elements of 4G LTE architecture

* Wireless and Mobile Networks: 7-
* 43
* Mobility Management Entity (
* MME
* )
* Serving Gateway (
* S-GW
* )
* Home Subscriber Service (
* HSS
* )
* PDN gateway (
* P-GW
* )
* …
* to
* Internet
* Mobile device
* (
* UE
* )
* Base station
* (eNode-B)
* Mobility Management Entity
* device authentication (device-to-network, network-to-device) coordinated with mobile home network HSS
* mobile device management:
* device handover between cells
* tracking/paging device location
* path (tunneling) setup from mobile device to P-GW
* style.visibility

---

### Slide 44: LTE: data plane control plane separation

* Wireless and Mobile Networks: 7-
* 44
* control plane
* new protocols for mobility management , security, authentication (later)
* MME
* HSS
* base station
* P-GW
* S-GW
* base station
* P-GW
* S-GW
* data plane
* new protocols at link, physical layers
* IP tunnels
* extensive use of tunneling to facilitate mobility
* style.visibility
* style.visibility

---

### Slide 45: IP

* Packet Data
* Convergence
* Radio Link
* Medium Access
* Physical
* LTE data plane protocol stack: first hop
* Wireless and Mobile Networks: 7-
* 45
* data
* plane
* P-GW
* S-GW
* Application
* Transport
* IP
* Packet Data
* Convergence
* Radio Link
* Medium Access
* Physical
* Link
* base station
* LTE link layer protocols:
* Packet Data Convergence: header compression, encryption
* Radio Link Control (RLC) Protocol: fragmentation/reassembly, reliable data transfer
* Medium Access:
* requesting, use of radio transmission slots
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 46: IP

* Packet Data
* Convergence
* Radio Link
* Medium Access
* Physical
* LTE data plane protocol stack: first hop
* Wireless and Mobile Networks: 7-
* 46
* Application
* Transport
* IP
* Packet Data
* Convergence
* Radio Link
* Medium Access
* Physical
* Link
* base station
* LTE radio access network:
* downstream
* channel:
* FDM, TDM within frequency channel (OFDM - orthogonal frequency division multiplexing)
* “orthogonal”: minimal interference between channels
* upstream:
* FDM, TDM similar to OFDM
* each active mobile device allocated two or more 0.5 ms time slots over 12 frequencies
* scheduling algorithm not standardized – up to operator
* 100’s Mbps per device possible
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 47: IP

* Packet Data
* Convergence
* Radio Link
* Medium Access
* Physical
* GTP-U
* UDP
* IP
* link
* Physical
* LTE data plane protocol stack:  packet core
* Wireless and Mobile Networks: 7-
* 47
* GTP-U
* UDP
* IP
* link
* Physical
* GTP-U
* UDP
* IP
* link
* Physical
* P-GW
* S-GW
* base station
* \
* tunneling:
* mobile datagram encapsulated using GPRS Tunneling Protocol (GTP), sent inside UDP datagram to S-GW
* S-GW re-tunnels datagrams to P-GW
* supporting mobility: only tunneling endpoints change when mobile user moves
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 48: LTE data plane: associating with a BS

* Wireless and Mobile Networks: 7-
* 48
* data
* plane
* P-GW
* S-GW
* base station
* BS broadcasts primary synch signal every 5 ms on all frequencies
* BSs from multiple carriers may be broadcasting synch signals
* 1
* mobile finds a primary synch signal, then locates 2
* nd
* synch signal on this freq.
* mobile then finds info broadcast by BS: channel bandwidth, configurations; BS’s cellular carrier info
* mobile may get info from multiple base stations, multiple cellular networks
* 2
* mobile selects which BS to associate with (
* e.g.,
* preference for home carrier)
* 3
* more steps still needed to authenticate, establish state, set up data plane
* 4
* 1
* 2
* 3
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 49: LTE mobiles: sleep modes

* Wireless and Mobile Networks: 7-
* 49
* data
* plane
* Z
* Z
* ZZ...
* as in WiFi, Bluetooth: LTE mobile may put radio to “sleep” to conserve battery:
* light sleep
* : after 100’s msec of inactivity
* wake up periodically (100’s msec) to check for downstream transmissions
* deep sleep:
* after 5-10 secs of inactivity
* mobile may change cells while deep sleeping – need to re-establish association
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 50: Global cellular network: a network of IP networks

* Wireless and Mobile Networks: 7-
* 50
* …
* visited
* mobile
* carrier network
* …
* public Internet
* and
* inter-carrier IPX
* …
* P-GW
* P-GW
* home
* mobile
* carrier network
* Home
* Subscriber
* Server
* in home network
* roaming in visited network
* SIM card: global identify info in home network
* all IP:
* carriers interconnect with each other, and public internet at exchange points
* legacy 2G, 3G: not all IP, handled otherwise
* home network HSS:
* identify & services info, while in home network and roaming
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 51: On to 5G!

* Wireless and Mobile Networks: 7-
* 51
* goal:
* 10x increase in peak bitrate, 10x decrease in latency, 100x increase in traffic capacity over 4G
* 5G NR (new radio):
* two frequency bands:
* FR1 (450 MHz–6 GHz)
* and FR2
* (24 GHz–52 GHz):
* millimeter wave frequencies
* not backwards-compatible with 4G
* MIMO: multiple directional antennae
* millimeter wave frequencies:
* much higher data rates, but over shorter distances
* pico-cells: cells diameters: 10-100 m
* massive, dense deployment of new base stations required
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 52: Chapter 7 outline

* Introduction
* Link Layer: 6-
* 52
* Wireless
* Wireless links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols

---

### Slide 53: spectrum of mobility, from the

* network
* perspective:
* What is mobility?
* Wireless and Mobile Networks: 7-
* 53
* no mobility
* high mobility
* device moves
* between networks, but
* powers down
* while moving
* device moves within same AP in
* one provider
* network
* device moves
* among multiple
* provider networks,
* while maintaining
* ongoing connections
* device moves among APs in
* one provider
* network
* We’re interested in these!
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 54: Mobility approaches

* Wireless and Mobile Networks: 7-
* 54
* let network (routers) handle it:
* routers advertise well-known name, address (e.g., permanent 32-bit IP address), or number (e.g., cell #) of visiting mobile node via usual routing table exchange
* Internet routing could do this already
* with no
* changes! Routing tables indicate where each mobile located via longest prefix match!

---

### Slide 55: Mobility approaches

* Wireless and Mobile Networks: 7-
* 55
* let network (routers) handle it:
* routers advertise well-known name, address (e.g., permanent 32-bit IP address), or number (e.g., cell #) of visiting mobile node via usual routing table exchange
* Internet routing could do this already
* with no
* changes! Routing tables indicate where each mobile located via longest prefix match!
* let end-systems handle it:
* functionality at the “edge”
* indirect routing:
* communication from correspondent to mobile goes through home network, then forwarded to remote mobile
* direct routing:
* correspondent gets foreign address of mobile, send directly to mobile
* not
* scalable
* to billions of
* mobiles
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 56: Contacting a mobile friend:

* Wireless and Mobile Networks: 7-
* 56
* search all phone books?
* expect her to let you know where he/she is?
* I wonder where Alice moved to?
* Consider friend frequently changing locations, how do you find him/her?
* call his/her parents?
* Facebook!
* The importance of having a “home”:
* a definitive source of information about you
* a place where people can find out where you are
* style.visibility
* style.visibility

---

### Slide 57: Home network, visited network: 4G/5G

* Wireless and Mobile Networks: 7-
* 57
* …
* visited
* mobile
* carrier network
* …
* public Internet
* and
* inter-carrier IPX
* …
* P-GW
* P-GW
* home
* mobile
* carrier network
* Home
* Subscriber
* Server
* in home network
* roaming in visited network
* SIM card:
* global
* identify info including  home network
* home network:
* (paid) service plan with cellular provider, e.g., Verizon, Orange
* home network HSS stores identify & services info
* visited network:
* any network other than your home network
* service agreement with other networks: to provide access to visiting mobile
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 58: Home network, visited network: ISP/WiFi

* Wireless and Mobile Networks: 7-
* 58
* …
* …
* public Internet
* …
* authentication
* access
* server
* attach
* attach
* authentication
* access
* server
* ISP/WiFi: no notion of global  “home”
* credentials from ISP (e.g., username, password) stored on device or with user
* ISPs may have national, international presence
* different networks: different credentials
* some exceptions (e.g., eduroam)
* architectures exist (mobile IP) for 4G-like mobility, but not used
* style.visibility
* style.visibility
* style.visibility

---

### Slide 59: Home network, visited network: generic

* Wireless and Mobile Networks: 7-
* 59
* Home gateway
* Home Network
* e.g.,: 128.119/16
* Home network  gateway
* Permanent IP:
* 128.119.40.186
* IMSI
* 78:4f:43:98:d9:27
* Visited network  gateway
* NAT IP:
* 10.0.0.99
* IMSI
* 78:4f:43:98:d9:27
* public or  private Internet
* Home
* Subscriber
* Server
* Mobility manager
* Mobility manager
* Correspondent
* Visited Network
* e.g.,: 79.129/16
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 60: Wireless and Mobile Networks: 7-

* 60
* Home gateway
* Home network  gateway
* Permanent IP:
* 128.119.40.186
* IMSI
* 78:4f:43:98:d9:27
* Visited network  gateway
* NAT IP:
* 10.0.0.99
* IMSI
* 78:4f:43:98:d9:27
* public or  private Internet
* Home
* Subscriber
* Server
* Mobility manager
* Mobility manager
* end result:
* visited mobility manager knows about mobile
* home HSS knows location of mobile
* 2
* visited mobility manager
* registers
* mobile’s location with home HSS
* mobile
* associates
* with visited mobility manager
* 1
* Registration: home needs to know where you are!
* Home Network
* e.g.,: 128.119/16
* Visited Network
* e.g.,: 79.129/16
* style.visibility
* style.visibility
* style.visibility

---

### Slide 61: Mobility with indirect routing

* Wireless and Mobile Networks: 7-
* 61
* Home gateway
* Home network  gateway
* Permanent IP:
* 128.119.40.186
* IMSI
* 78:4f:43:98:d9:27
* Visited network  gateway
* NAT IP:
* 10.0.0.99
* IMSI
* 78:4f:43:98:d9:27
* public or  private Internet
* Home
* Subscriber
* Server
* Mobility manager
* Mobility manager
* Correspondent
* 1
* correspondent uses
* home
* address as datagram destination address
* home gateway receives datagram, forwards (tunnels)  to remote gateway
* Home Network
* e.g.,: 128.119/16
* Visited Network
* e.g.,: 79.129/16
* 2
* 3
* 4a
* 4b
* visited gateway router forwards to mobile
* visited gateway router forwards reply to correspondent via home network (4a) or directly (4b)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 62: triangle routing:

* inefficient when correspondent and mobile are in same network
* Mobility with indirect routing: comments
* Wireless and Mobile Networks: 7-
* 62
* mobile moves among visited networks: transparent to correspondent!
* registers in new visited network
* new visited network registers with home HSS
* datagrams continue to be forwarded from home network to mobile in new network
* on-going (e.g., TCP) connections between correspondent and mobile can be maintained!

---

### Slide 63: Mobility with direct routing

* Wireless and Mobile Networks: 7-
* 63
* Home gateway
* Permanent IP:
* 128.119.40.186
* IMSI
* 78:4f:43:98:d9:27
* Visited network  gateway
* NAT IP:
* 10.0.0.99
* IMSI
* 78:4f:43:98:d9:27
* public or  private Internet
* Home
* Subscriber
* Server
* Mobility manager
* Mobility manager
* Correspondent
* 1
* correspondent contacts
* home
* HSS, gets mobile’s visited network
* Home Network
* e.g.,: 128.119/16
* Visited Network
* e.g.,: 79.129/16
* 4
* visited gateway router forwards to mobile
* 2
* 3
* Correspondent addresses datagram to visited network address
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 64: Mobility with direct routing: comments

* Wireless and Mobile Networks: 7-
* 64
* overcomes triangle routing inefficiencies
* non-transparent to correspondent:
* correspondent must get care-of-address from home agent
* what if mobile changes visited network?
* can be handled, but with additional complexity

---

### Slide 65: Chapter 7 outline

* Introduction
* Link Layer: 6-
* 65
* Wireless
* Wireless links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols

---

### Slide 66: Mobility manager

* Mobility in 4G networks: major mobility tasks
* Wireless and Mobile Networks: 7-
* 66
* Visited network
* P-GW
* Streaming server
* Home
* network
* Internet
* base station
* MME
* 1
* 2
* 3
* 4
* Home
* Subscriber
* Server
* S-GW
* P-GW
* base station association
* :
* covered earlier
* mobile  provides IMSI
* – identifying itself, home network
* 1
* control-plane configuration:
* MME, home HSS establish control-plane state -  mobile is in visited network
* 2
* data-plane configuration:
* MME configures forwarding tunnels for mobile
* visited, home network establish tunnels from home P-GW to mobile
* 3
* mobile handover:
* mobile device changes its point of attachment to visited network
* 4
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 67: Mobility manager

* Mobile communicates with local MME via BS control-plane channel
* MME uses mobile’s IMSI info to contact mobile’s home HSS
* retrieve authentication, encryption, network service information
* home HHS knows mobile now resident in visited network
* BS, mobile select parameters for BS-mobile data-plane radio channel
* Configuring LTE control-plane elements
* Wireless and Mobile Networks: 7-
* 67
* Visited network
* P-GW
* Home
* network
* base station
* MME
* 2
* Home
* Subscriber
* Server
* S-GW
* P-GW
* style.visibility

---

### Slide 68: Mobility manager

* Configuring data-plane tunnels for mobile
* Wireless and Mobile Networks: 7-
* 68
* P-GW
* Streaming server
* Internet
* base station
* MME
* Home
* Subscriber
* Server
* S-GW
* P-GW
* Visited network
* Home
* network
* S-GW to BS tunnel
* : when mobile changes base stations, simply change endpoint IP address of tunnel
* S-GW to home P-GW tunnel:
* implementation of indirect routing
* tunneling via GTP
* (GPRS tunneling protocol):
* mobile’s datagram to streaming server encapsulated using GTP inside UDP, inside datagram

---

### Slide 69: Handover between BSs in same cellular network

* Wireless and Mobile Networks: 7-
* 69
* P-GW
* S-GW
* MME
* source BS
* 1
* 3
* 2
* data path
* before
* handover
* data path
* after
* handover
* 1
* current (source) BS selects target BS, sends
* Handover Request message
* to target BS
* 2
* target BS pre-allocates radio time slots, responds with HR ACK with info for mobile
* 3
* source BS informs mobile of new BS
* mobile can now send via new BS - handover
* looks
* complete to mobile
* 4
* source BS stops sending datagrams to mobile, instead forwards to new BS (who forwards to mobile over radio channel)
* target BS
* 4
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 70: Handover between BSs in same cellular network

* Wireless and Mobile Networks: 7-
* 70
* 1
* 6
* 3
* 5
* 5
* 2
* 5
* target BS informs MME that it is new BS for mobile
* MME instructs S-GW to change tunnel endpoint to be (new) target BS
* 6
* target BS ACKs back to source BS: handover complete, source BS can release resources
* P-GW
* S-GW
* MME
* source BS
* target BS
* 4
* 7
* 7
* mobile’s datagrams now flow through new tunnel from target BS to S-GW
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 71: mobile IP architecture standardized ~20 years ago

* [RFC 5944]
* long before ubiquitous smartphones, 4G support for Internet protocols
* did not see wide deployment/use
* perhaps WiFi for Internet, and 2G/3G phones for voice were “good enough” at the time
* mobile IP architecture:
* indirect routing to node (via home network) using tunnels
* mobile IP home agent: combined roles of 4G HSS and home P-GW
* mobile IP foreign agent: combined roles of 4G MME and S-GW
* protocols for agent discovery in visited network, registration of visited location in home network via ICMP extensions
* Mobile IP
* Wireless and Mobile Networks: 7-
* 71

---

### Slide 72: logically, impact

* should
* be minimal …
* best effort service model remains unchanged
* TCP and UDP can (and do) run over wireless, mobile
* … but performance-wise:
* packet loss/delay due to bit-errors (discarded packets, delays for link-layer retransmissions), and handover loss
* TCP interprets loss as congestion, will decrease congestion window un-necessarily
* delay impairments for real-time traffic
* bandwidth a scare resource for wireless links
* Wireless, mobility: impact on higher layer protocols
* Wireless and Mobile Networks: 7-
* 72

---

### Slide 73: Chapter 7 summary

* Wireless
* Wireless Links and network characteristics
* WiFi: 802.11 wireless LANs
* Cellular networks: 4G and 5G
* Mobility
* Mobility management: principles
* Mobility management: practice
* 4G/5G networks
* Mobile IP
* Mobility: impact on higher-layer protocols
* Wireless and Mobile Networks: 7-
* 73
* style.visibility
* style.visibility

---

