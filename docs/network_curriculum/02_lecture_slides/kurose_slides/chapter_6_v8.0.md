# Slide Bài Giảng: Chapter 6 v8.0

> **Nguồn gốc:** Slide chính thức của tác giả Kurose & Ross (Chapter_6_v8.0.pptx)

---

### Slide 2: Link layer and LANs: our goals

* understand principles behind link layer services:
* error detection, correction
* sharing a broadcast channel: multiple access
* link layer addressing
* local area networks: Ethernet, VLANs
* datacenter networks
* instantiation, implementation of various link layer technologies
* Link Layer: 6-
* 2
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 3: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 3
* style.visibility
* style.visibility

---

### Slide 4: Link layer: introduction

* terminology:
* hosts and routers: nodes
* communication channels that connect adjacent nodes along communication path: links
* wired
* wireless
* LANs
* layer-2 packet:
* frame
* , encapsulates datagram
* mobile network
* enterprise
* network
* national or global ISP
* datacenter
* network
* link layer
* has responsibility of
* transferring datagram from one node
* to
* physically adjacent
* node over a li
* nk
* Link Layer: 6-
* 4
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 5: Link layer: context

* datagram transferred by different link protocols over different links:
* e.g.,
* WiFi
* on first link, Ethernet on next link
* each  link protocol provides different services
* e.g., may or may not provide reliable data transfer over link
* transportation analogy:
* trip from Princeton to Lausanne
* limo: Princeton to JFK
* plane: JFK to Geneva
* train: Geneva to Lausanne
* tourist =
* datagram
* transport segment =
* communication link
* transportation mode =
* link-layer
* protocol
* travel agent =
* routing algorithm
* Link Layer: 6-
* 5

---

### Slide 6: Link layer: services

* framing, link access:
* encapsulate datagram into frame, adding header, trailer
* channel access if shared medium
* “MAC” addresses in frame headers identify source, destination (
* different from IP address!)
* reliable delivery between adjacent nodes
* we already know how to do this!
* seldom used on low bit-error links
* wireless links: high error rates
* Q:
* why both link-level and end-end reliability?
* …
* …
* Link Layer: 6-
* 6

---

### Slide 7: Link layer: services (more)

* flow control:
* pacing between adjacent sending and receiving nodes
* error detection:
* errors caused by signal attenuation, noise.
* receiver detects errors, s
* ignals retransmission, or drops frame
* error correction:
* receiver identifies
* and corrects
* bit error(s) without retransmission
* half-duplex and full-duplex:
* with half duplex, nodes at both ends of link can transmit, but not at same time
* …
* …
* Link Layer: 6-
* 7

---

### Slide 8: Where is the link layer implemented?

* in each-and-every host
* link layer implemented in
* network interface card
* (NIC) or on a chip
* Ethernet,
* WiFi
* card or chip
* implements link, physical layer
* attaches into host’s system buses
* combination of hardware, software, firmware
* controller
* physical
* cpu
* memory
* host bus
* (e.g., PCI)
* network interface
* application
* transport
* network
* link
* link
* physical
* Link Layer: 6-
* 8
* style.visibility

---

### Slide 9: controller

* physical
* memory
* CPU
* Interfaces communicating
* controller
* physical
* cpu
* memory
* application
* transport
* network
* link
* link
* physical
* application
* transport
* network
* link
* link
* physical
* sending side:
* encapsulates datagram in frame
* adds error checking bits, reliable data transfer, flow control, etc.
* receiving side:
* looks for errors, reliable data transfer, flow control, etc.
* extracts datagram, passes to upper layer at receiving side
* link
* h
* link
* h
* datagram
* datagram
* datagram
* Link Layer: 6-
* 9
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y

---

### Slide 10: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 10

---

### Slide 11: Error detection

* Link Layer: 6-
* 11
* EDC: error detection and correction bits (e.g., redundancy)
* D:  data protected by error checking, may include header fields
* Error detection not 100% reliable!
* protocol may miss some errors, but rarely
* larger EDC field yields better detection and correction
* datagram
* D
* EDC
* d data bits
* b
* it-error prone link
* D’
* EDC’
* all
* bits in D’
* OK
* ?
* N
* detected
* error
* otherwise
* datagram
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 12: Parity checking

* Link Layer: 6-
* 12
* single bit parity
* :
* detect single bit errors
* 0111000110101011
* 1
* parity
* bit
* d data bits
* two-dimensional bit parity:
* detect
* and correct
* single bit errors
* d
* 1,1
* d
* 2,1
* d
* i,1
* . . .
* d
* 1,j+1
* d
* 2,j+1
* d
* i,j+1
* . . .
* . . .
* d
* 1,j
* d
* 2,j
* d
* i,j
* . . .
* d
* i+1,1
* d
* i+1,j+1
* d
* i+1,j
* . . .
* . . .
* . . .
* . . .
* row parity
* column
* parity
* 0 1 1 1 0  1
* 1 0 1 0 1  1
* 1 1 1 1 0  0
* 1 0 1 0 1  0
* no errors:
* 0 1 1 1 0  1
* 1 0 1 0 1  1
* 1
* 0
* 1 1 0  0
* 1 0 1 0 1  0
* parity
* error
* parity
* error
* detected
* and
* correctable
* single-bit
* error:
* Even parity:
* set parity bit so there is an even number of 1’s
* * Check out the online interactive exercises for more examples: h
* ttp://gaia.cs.umass.edu/kurose_ross/interactive/
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 13: Internet checksum (review)

* sender
* :
* treat contents of UDP segment
* (including UDP header fields and IP addresses)
* as sequence of 16-bit integers
* checksum:
* addition
* (one’
* s complement sum)
* of segment content
* checksum value put into UDP checksum field
* receiver
* :
* compute checksum of received segment
* check if computed checksum equals checksum field value:
* not equal - error detected
* equal - no error detected.
* But maybe errors nonetheless?
* More later ….
* Goal
* :
* detect
* errors (
* i.e.,
* flipped bits) in transmitted segment
* Transport Layer: 3-
* 13
* style.visibility

---

### Slide 14: Cyclic Redundancy Check (CRC)

* more powerful error-detection coding
* D:
* data bits
* (given, think of these as a binary number)
* G:
* bit pattern (generator), of
* r+1
* bits
* (given)
* Link Layer: 6-
* 14
* goal:
* choose
* r
* CRC bits,
* R
* , such that <D,R> exactly divisible by G (mod 2)
* receiver knows G, divides <D,R> by G.  If non-zero remainder: error detected!
* can detect all burst errors less than r+1 bits
* widely used in practice (Ethernet, 802.11
* WiFi
* )
* r
* CRC bits
* d data bits
* D
* R
* <D,R> = D  2
* r
* XOR  R
* *
* bit pattern
* formula for bit pattern
* style.visibility
* style.visibility
* style.visibility

---

### Slide 15: Link Layer: 6-

* 15
* Cyclic Redundancy Check (CRC): example
* We want:
* D
* .
* 2
* r
* XOR  R =
* nG
* * Check out the online interactive exercises for more examples: h
* ttp://gaia.cs.umass.edu/kurose_ross/interactive/
* D
* .
* 2
* r
* G
* R
* = remainder
* [
* ]
* or equivalently:
* D
* .
* 2
* r
* =
* nG
* XOR  R
* or equivalently:
* if we divide D
* .
* 2
* r
* by G, want remainder R to satisfy:
* 1  0  0  1
* 1  0  1  0
* 1  0  1
* 0  0  0
* 1  0  0  1
* 1  0  0  1
* 1  0  0  1
* 0  0  0
* 1  1  0
* 1  1  0  0
* 1  0  1  0
* 0  1  1
* 0  1  1
* D
* R
* 1  0  0  1
* G
* 0  0  0
* 1  0  1  1  1  0
* 2
* r
* *
* 1
* 0
* 1
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

### Slide 16: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 16

---

### Slide 17: Multiple access links, protocols

* Link Layer: 6-
* 17
* two types of “links
* ”
* :
* point-to-point
* point-to-point link between Ethernet switch, host
* PPP for dial-up access
* broadcast (shared wire or medium)
* old-fashioned Ethernet
* upstream HFC in cable-based access network
* 802.11 wireless LAN, 4G/4G. satellite
* shared wire (e.g.,
* cabled Ethernet)
* shared radio:
* WiFi
* shared radio: satellite
* humans at a cocktail party
* (shared air, acoustical)
* shared radio: 4G/5G

---

### Slide 18: Multiple access protocols

* Link Layer: 6-
* 18
* single shared broadcast channel
* two or more simultaneous transmissions by nodes: interference
* collision
* if node receives two or more signals at the same time
* distributed algorithm that determines how nodes share channel, i.e., determine when node can transmit
* communication about channel sharing must use channel itself!
* no out-of-band channel for coordination
* multiple access protocol

---

### Slide 19: An ideal multiple access protocol

* Link Layer: 6-
* 19
* given:
* multiple access channel (MAC) of rate
* R
* bps
* desiderata:
* 1.
* when one node wants to transmit, it can send at rate
* R
* .
* 2. when M nodes want to transmit, each can send at average rate
* R/M
* 3. fully decentralized:
* no special node to coordinate transmissions
* no synchronization of clocks, slots
* 4. simple

---

### Slide 20: MAC protocols: taxonomy

* Link Layer: 6-
* 20
* three broad classes:
* channel partitioning
* divide channel into smaller
* “
* pieces
* ”
* (time slots, frequency, code)
* allocate piece to node for exclusive use
* random access
* channel not divided, allow collisions
* “
* recover
* ”
* from collisions
* “taking turns
* ”
* nodes take turns, but nodes with more to send can take longer turns
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 21: Channel partitioning MAC protocols: TDMA

* Link Layer: 6-
* 21
* TDMA: time division multiple access
* access to channel in “rounds”
* each station gets fixed length slot (length = packet transmission time) in each round
* unused slots go idle
* example: 6-station LAN, 1,3,4 have packets to send, slots 2,5,6 idle
* 1
* 3
* 4
* 1
* 3
* 4
* 6-slot
* frame
* 6-slot
* frame

---

### Slide 22: Channel partitioning MAC protocols: FDMA

* Link Layer: 6-
* 22
* FDMA: frequency division multiple access
* channel spectrum divided into frequency bands
* each station assigned fixed frequency band
* unused transmission time in frequency bands go idle
* example: 6-station LAN, 1,3,4 have packet to send, frequency bands 2,5,6 idle
* frequency bands
* time
* FDM cable

---

### Slide 23: Random access protocols

* Link Layer: 6-
* 23
* when node has packet to send
* transmit at full channel data rate R.
* no
* a priori
* coordination among nodes
* two or more transmitting nodes:
* “
* collision
* ”
* random access MAC protocol
* specifies:
* how to detect collisions
* how to recover from collisions (e.g., via delayed retransmissions)
* examples of random access MAC protocols:
* ALOHA, slotted ALOHA
* CSMA, CSMA/CD, CSMA/CA
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

### Slide 24: Slotted ALOHA

* Link Layer: 6-
* 24
* assumptions
* :
* all frames same size
* time divided into equal size slots (time to transmit 1 frame)
* nodes start to transmit only slot beginning
* nodes are synchronized
* if 2 or more nodes transmit in slot, all nodes detect collision
* operation:
* when node obtains fresh frame, transmits in next slot
* if no collision:
* node can send new frame in next slot
* if collision:
* node retransmits frame in each subsequent slot with probability
* p
* until success
* randomization
* –
* why
* ?
* style.visibility
* style.visibility

---

### Slide 25: Slotted ALOHA

* Link Layer: 6-
* 25
* Pros:
* single active node can continuously transmit at full rate of channel
* highly decentralized: only slots in nodes need to be in sync
* simple
* Cons:
* collisions, wasting slots
* idle slots
* nodes may be able to detect collision in less than time to transmit packet
* clock synchronization
* 1
* 1
* 1
* 1
* 2
* 3
* 2
* 2
* 3
* 3
* node 1
* node 2
* node 3
* C
* C
* C
* S
* S
* S
* E
* E
* E
* C
* : collision
* S
* : success
* E
* : empty

---

### Slide 26: efficiency:

* long-run  fraction of successful slots  (many nodes, all with many frames to send)
* suppose:
* N
* nodes with many frames to send, each transmits in slot with probability
* p
* prob that given node has success in a slot  =
* p(1-p)
* N-1
* prob that
* any
* node has a success =
* Np(1-p)
* N-1
* max efficiency: find
* p*
* that maximizes
* Np(1-p)
* N-1
* for many nodes, take limit of
* Np*(1-p*)
* N-1
* as
* N
* goes to infinity, gives
* :
* max efficiency = 1/e = .37
* at best:
* channel used for useful  transmissions 37% of time!
* Slotted ALOHA: efficiency
* Link Layer: 6-
* 26
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

### Slide 27: Pure ALOHA

* Link Layer: 6-
* 27
* unslotted Aloha: simpler, no synchronization
* when
* frame first arrives: transmit immediately
* collision probability increases with no synchronization:
* frame sent at t
* 0
* collides with other frames sent in [t
* 0
* -1,t
* 0
* +1]
* t
* 0
* + 1
* t
* 0
* - 1
* t
* 0
* will overlap
* with end of
* i’s frame
* will overlap
* with start of
* i’s frame
* pure Aloha efficiency: 18% !
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 28: CSMA (carrier sense multiple access)

* Link Layer: 6-
* 28
* simple
* CSMA:
* listen before transmit:
* if channel sensed idle:
* transmit entire frame
* if channel sensed busy:
* defer transmission
* human analogy: don
* ’
* t interrupt others!
* CSMA/CD:
* CSMA with
* collision detection
* collisions
* detected
* within short time
* colliding transmissions aborted, reducing channel wastage
* collision detection easy in wired, difficult with wireless
* human analogy: the polite conversationalist
* style.visibility

---

### Slide 29: CSMA: collisions

* Link Layer: 6-
* 29
* collisions
* can
* still occur with carrier sensing:
* propagation delay means  two nodes may not hear each other
* ’
* s just-started transmission
* collision:
* entire packet transmission time wasted
* distance & propagation delay play role in in determining collision probability
* spatial layout of nodes
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 30: CSMA/CD:

* Link Layer: 6-
* 30
* CSMA/CS reduces the amount of time wasted in collisions
* transmission aborted on collision detection
* spatial layout of nodes

---

### Slide 31: Ethernet CSMA/CD algorithm

* Link Layer: 6-
* 31
* NIC receives datagram from network layer, creates frame
* If NIC senses channel:
* if
* idle:
* start frame transmission.
* if
* busy:
* wait until channel idle, then transmit
* If NIC transmits entire frame without collision, NIC is done with frame !
* If NIC detects another transmission while sending:  abort, send jam signal
* After aborting, NIC enters
* binary (exponential)
* backoff
* :
* after
* m
* th
* collision, NIC chooses
* K
* at random from
* {0,1,2, …, 2
* m
* -1}
* . NIC waits
* K
* ·
* 512 bit times, returns to Step 2
* more collisions: longer
* backoff
* interval
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

### Slide 32: CSMA/CD efficiency

* Link Layer: 6-
* 32
* T
* prop
* = max prop delay between 2 nodes in LAN
* t
* trans
* = time to transmit max-size frame
* efficiency goes to 1
* as
* t
* prop
* goes to 0
* as
* t
* trans
* goes to infinity
* better performance than ALOHA: and simple, cheap, decentralized
* !

---

### Slide 33: “Taking turns” MAC protocols

* Link Layer: 6-
* 33
* channel partitioning MAC protocols:
* share channel
* efficiently
* and
* fairly
* at high load
* inefficient at low load: delay in channel access, 1/N bandwidth allocated even if only 1 active node!
* random access MAC protocols
* efficient at low load: single node can fully utilize channel
* high load: collision overhead
* “
* taking turns
* ”
* protocols
* look for best of both worlds!

---

### Slide 34: “Taking turns” MAC protocols

* Link Layer: 6-
* 34
* polling:
* master node “invites” other nodes to transmit in turn
* typically used with “dumb” devices
* concerns:
* polling overhead
* latency
* single point of failure (master)
* master
* slaves
* poll
* data
* data
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility

---

### Slide 35: “Taking turns” MAC protocols

* Link Layer: 6-
* 35
* token passing:
* control
* token
* passed from one node to next sequentially.
* token message
* concerns:
* token overhead
* latency
* single point of failure (token)
* T
* data
* (nothing
* to send)
* T
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* ppt_x
* ppt_y
* style.visibility

---

### Slide 36: Cable access network: FDM, TDM

* and
* random access!
* Link Layer: 6-
* 36
* cable headend
* CMTS
* ISP
* cable modem
* termination system
* cable
* modem
* splitter
* …
* …
* Internet frames, TV channels, control  transmitted
* downstream at different frequencies
* multiple
* downstream (broadcast)
* FDM channels: up to 1.6 Gbps/channel
* single CMTS transmits into channels
* multiple
* upstream channels (up to 1 Gbps/channel)
* multiple access:
* all
* users contend (random access) for certain upstream channel time slots; others assigned TDM
* style.visibility
* style.visibility

---

### Slide 37: Cable access network:

* Link Layer: 6-
* 37
* DOCSIS:
* data over cable service interface
* specificaiton
* FDM over upstream, downstream frequency channels
* TDM upstream: some slots assigned, some have contention
* downstream MAP frame: assigns upstream slots
* request for upstream slots (and data) transmitted random access (binary backoff) in selected slots
* Residences with cable modems
* Downstream channel i
* Upstream channel j
* MAP frame for
* Interval [t1, t2]
* t
* 1
* t
* 2
* Assigned minislots containing cable modem
* upstream data frames
* Minislots containing
* minislots request frames
* cable headend
* CMTS
* style.visibility
* style.visibility

---

### Slide 38: Summary of

* MAC
* protocols
* Link Layer: 6-
* 38
* channel partitioning,
* by time, frequency or code
* Time Division, Frequency Division
* random access
* (dynamic),
* ALOHA, S-ALOHA, CSMA, CSMA/CD
* carrier sensing: easy in some technologies (wire), hard in others (wireless)
* CSMA/CD used in Ethernet
* CSMA/CA used in 802.11
* taking turns
* polling from central site, token passing
* Bluetooth, FDDI,  token ring

---

### Slide 39: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 39

---

### Slide 40: MAC addresses

* Link Layer: 6-
* 40
* 32-bit IP address:
* network-layer
* address for interface
* used for layer 3 (network layer) forwarding
* e.g.: 128.119.40.136
* MAC (or LAN or physical or Ethernet) address:
* function:
* used “locally” to get frame from one interface to another physically-connected interface (same subnet, in IP-addressing sense)
* 48-bit MAC address (for most LANs) burned in NIC ROM, also sometimes software settable
* hexadecimal (base 16) notation
* (each
* “
* numeral
* ”
* represents 4 bits)
* e.g.: 1A-2F-BB-76-09-AD
* style.visibility
* style.visibility

---

### Slide 41: MAC addresses

* Link Layer: 6-
* 41
* each interface on LAN
* has unique 48-bit
* MAC
* address
* has a locally unique 32-bit IP address (as we’ve seen)
* 1A-2F-BB-76-09-AD
* 58-23-D7-FA-20-B0
* 0C-C4-11-6F-E3-98
* 71-65-F7-2B-08-53
* LAN
* (wired or wireless)
* 137.196.7/24
* 137.196.7.78
* 137.196.7.14
* 137.196.7.88
* 137.196.7.23

---

### Slide 42: MAC addresses

* Link Layer: 6-
* 42
* MAC address allocation administered by IEEE
* manufacturer buys portion of MAC address space (to assure uniqueness)
* analogy:
* MAC address: like Social Security Number
* IP address: like postal address
* MAC flat address: portability
* can move interface from one LAN to another
* recall IP address
* not
* portable: depends on IP subnet to which node is attached
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 43: ARP: address resolution protocol

* Link Layer: 6-
* 43
* ARP table:
* each IP node (host, router) on LAN has table
* Question:
* how to determine interface’s MAC address, knowing its IP address?
* 1A-2F-BB-76-09-AD
* 58-23-D7-FA-20-B0
* 0C-C4-11-6F-E3-98
* 71-65-F7-2B-08-53
* LAN
* 137.196.7.78
* 137.196.7.14
* 137.196.7.88
* 137.196.7.23
* ARP
* ARP
* ARP
* ARP
* IP/MAC address mappings for some LAN nodes:
* < IP address; MAC address; TTL>
* TTL (Time To Live): time after which address mapping will be forgotten (typically 20 min)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 44: ARP protocol in action

* Link Layer: 6-
* 44
* 58-23-D7-FA-20-B0
* 137.196.7.14
* B
* C
* D
* TTL
* 71-65-F7-2B-08-53
* 137.196.7.23
* A
* ARP table in
* A
* IP
* addr
* MAC
* addr
* TTL
* example: A wants to send datagram to B
* B
* ’
* s MAC address not in A
* ’
* s ARP table, so A uses ARP to find B’s MAC address
* A
* broadcasts ARP query, containing B's IP
* addr
* destination MAC address = FF-FF-FF-FF-FF-FF
* all nodes on LAN receive ARP query
* 1
* Source MAC:
* 71-65-F7-2B-08-53
* Source IP:
* 137.196.7.23
* Target IP address:
* 137.196.7.14
* …
* 1
* Ethernet frame (sent to
* FF-FF-FF-FF-FF-FF)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 45: ARP protocol in action

* Link Layer: 6-
* 45
* 58-23-D7-FA-20-B0
* 137.196.7.14
* B
* C
* D
* TTL
* 71-65-F7-2B-08-53
* 137.196.7.23
* A
* ARP table in
* A
* IP
* addr
* MAC
* addr
* TTL
* example: A wants to send datagram to B
* B
* ’
* s MAC address not in A
* ’
* s ARP table, so A uses ARP to find B’s MAC address
* B
* replies to A with ARP response, giving its MAC address
* 2
* Target IP address:
* 137.196.7.14
* Target MAC address:
* 58-23-D7-FA-20-B0
* …
* 2
* ARP message into Ethernet frame (sent to
* 71-65-F7-2B-08-53
* )
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 46: ARP protocol in action

* Link Layer: 6-
* 46
* 58-23-D7-FA-20-B0
* 137.196.7.14
* B
* C
* D
* TTL
* 71-65-F7-2B-08-53
* 137.196.7.23
* A
* ARP table in
* A
* IP
* addr
* MAC
* addr
* TTL
* example: A wants to send datagram to B
* B
* ’
* s MAC address not in A
* ’
* s ARP table, so A uses ARP to find B’s MAC address
* A
* receives B’s reply, adds B entry into its local ARP table
* 3
* 137.196.
* 7.14
* 58-23-D7-FA-20-B0
* 500
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 47: Routing to another subnet: addressing

* Link Layer: 6-
* 47
* walkthrough
* : sending a  datagram from
* A
* to
* B
* via
* R
* focus on addressing – at IP (datagram) and MAC layer (frame) levels
* R
* A
* B
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* assume that:
* A knows B’s IP address
* A knows IP address of first hop router, R
* (how?)
* A knows R’s MAC address
* (how?)
* style.visibility
* style.visibility

---

### Slide 48: Routing to another subnet: addressing

* Link Layer: 6-
* 48
* R
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* A
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* B
* IP
* Eth
* Phy
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* A creates IP datagram with IP source A, destination B
* A creates link-layer frame containing A-to-B IP datagram
* R's
* MAC address is frame’s destination
* MAC src: 74-29-9C-E8-FF-55
* MAC dest:
* E6-E9-00-17-BB-4B
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 49: Routing to another subnet: addressing

* Link Layer: 6-
* 49
* R
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* A
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* B
* IP
* Eth
* Phy
* frame sent from A to R
* IP
* Eth
* Phy
* frame received at R, datagram removed, passed up to IP
* MAC src: 74-29-9C-E8-FF-55
* MAC dest: E6-E9-00-17-BB-4B
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 50: Routing to another subnet: addressing

* Link Layer: 6-
* 50
* R
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* A
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* B
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* MAC src:
* 1A-23-F9-CD-06-9B
* MAC dest:
* 49-BD-D2-C7-56-2A
* R determines outgoing interface, passes datagram with IP source A, destination B to link layer
* R creates link-layer frame
* containing A-to-B IP datagram. Frame destination address:
* B's MAC address
* IP
* Eth
* Phy
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 51: Routing to another subnet: addressing

* Link Layer: 6-
* 51
* R
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* A
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* B
* IP
* Eth
* Phy
* IP
* Eth
* Phy
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* MAC src:
* 1A-23-F9-CD-06-9B
* MAC dest:
* 49-BD-D2-C7-56-2A
* transmits link-layer frame
* R determines outgoing interface, passes datagram with IP source A, destination B to link layer
* R creates link-layer frame
* containing A-to-B IP datagram. Frame destination address:
* B's MAC address
* style.visibility
* ppt_x
* ppt_y

---

### Slide 52: Routing to another subnet: addressing

* Link Layer: 6-
* 52
* R
* 1A-23-F9-CD-06-9B
* 222.222.222.220
* 111.111.111.110
* E6-E9-00-17-BB-4B
* CC-49-DE-D0-AB-7D
* 111.111.111.112
* 111.111.111.111
* 74-29-9C-E8-FF-55
* A
* 222.222.222.222
* 49-BD-D2-C7-56-2A
* 222.222.222.221
* 88-B2-2F-54-1A-0F
* B
* IP
* Eth
* Phy
* IP
* Eth
* Phy
* B receives frame, extracts IP datagram destination B
* B passes datagram up protocol stack to IP
* IP src: 111.111.111.111
* IP dest: 222.222.222.222
* style.visibility
* ppt_x
* ppt_y
* style.visibility

---

### Slide 53: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 53

---

### Slide 54: Ethernet

* Link Layer: 6-
* 54
* “
* dominant
* ”
* wired LAN technology:
* first widely used LAN technology
* simpler, cheap
* kept up with speed race: 10 Mbps – 400 Gbps
* single chip, multiple speeds (e.g., Broadcom  BCM5761)
* Metcalfe’s Ethernet sketch
* https://
* www.uspto.gov
* /learning-and-resources/journeys-innovation/audio-stories/defying-doubters

---

### Slide 55: Ethernet: physical topology

* Link Layer: 6-
* 55
* bus:
* popular through mid 90s
* all nodes in same collision domain (can collide with each other)
* bus:
* coaxial cable
* switched
* switched:
* prevails today
* active link-layer 2
* switch
* in center
* each
* “
* spoke
* ”
* runs a (separate) Ethernet protocol (nodes do not collide with each other)
* style.visibility
* style.visibility

---

### Slide 56: Ethernet frame structure

* Link Layer: 6-
* 56
* sending interface encapsulates IP datagram (or other network layer protocol packet) in
* Ethernet frame
* dest.
* address
* source
* address
* data (payload)
* CRC
* preamble
* type
* preamble:
* used to synchronize receiver, sender clock rates
* 7 bytes of 10101010 followed by one byte of 10101011

---

### Slide 57: Ethernet frame structure

* (more)
* Link Layer: 6-
* 57
* dest.
* address
* source
* address
* data (payload)
* CRC
* preamble
* type
* addresses:
* 6 byte source, destination MAC addresses
* if adapter receives frame with matching destination address, or with broadcast address (e.g., ARP packet), it passes data in frame to network layer protocol
* otherwise, adapter discards frame
* type:
* indicates higher layer protocol
* mostly IP but others possible, e.g., Novell IPX, AppleTalk
* used to demultiplex up at receiver
* CRC:
* cyclic redundancy check at receiver
* error detected: frame is dropped
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

### Slide 58: Ethernet: unreliable, connectionless

* Link Layer: 6-
* 58
* connectionless:
* no handshaking between sending and receiving NICs
* unreliable:
* receiving NIC doesn’t send ACKs or NAKs to sending NIC
* data in dropped frames recovered only if initial sender uses higher layer
* rdt
* (e.g., TCP), otherwise dropped data lost
* Ethernet’s MAC protocol: unslotted
* CSMA/CD with binary
* backoff
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 59: 802.3 Ethernet standards: link & physical layers

* Link Layer: 6-
* 59
* different physical layer media: fiber, cable
* application
* transport
* network
* link
* physical
* MAC protocol
* and frame format
* 100BASE-TX
* 100BASE-T4
* 100BASE-FX
* 100BASE-T2
* 100BASE-SX
* 100BASE-BX
* fiber physical layer
* copper (twister pair) physical layer
* many
* different Ethernet standards
* common MAC protocol and frame format
* different speeds: 2 Mbps, 10 Mbps, 100 Mbps, 1Gbps, 10 Gbps, 40 Gbps
* style.visibility
* style.visibility
* style.visibility

---

### Slide 60: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 60

---

### Slide 61: Ethernet switch

* Link Layer: 6-
* 61
* Switch is a
* link-layer
* device: takes an
* active
* role
* store, forward Ethernet frames
* examine incoming frame’s MAC address,
* selectively
* forward  frame to one-or-more outgoing links when frame is to be forwarded on segment, uses CSMA/CD to access segment
* transparent:
* hosts
* unaware
* of presence of switches
* plug-and-play, self-learning
* switches do not need to be configured
* style.visibility
* style.visibility
* style.visibility

---

### Slide 62: Switch: multiple simultaneous transmissions

* Link Layer: 6-
* 62
* switch with six interfaces (
* 1,2,3,4,5,6
* )
* A
* A
* ’
* B
* B
* ’
* C
* C
* ’
* 1
* 2
* 3
* 4
* 5
* 6
* hosts have dedicated, direct connection to switch
* switches buffer packets
* Ethernet protocol used on
* each
* incoming link, so:
* no collisions; full duplex
* each link is its own collision domain
* switching:
* A-to-A’ and B-to-B
* ’
* can transmit simultaneously, without collisions
* style.visibility
* style.visibility
* style.visibility

---

### Slide 63: Switch: multiple simultaneous transmissions

* Link Layer: 6-
* 63
* switch with six interfaces (
* 1,2,3,4,5,6
* )
* A
* A
* ’
* B
* B
* ’
* C
* C
* ’
* 1
* 2
* 3
* 4
* 5
* 6
* hosts have dedicated, direct connection to switch
* switches buffer packets
* Ethernet protocol used on
* each
* incoming link, so:
* no collisions; full duplex
* each link is its own collision domain
* switching:
* A-to-A’ and B-to-B
* ’
* can transmit simultaneously, without collisions
* but A-to-A’ and C to A’ can
* not
* happen simultaneously
* style.visibility

---

### Slide 64: Switch forwarding table

* Link Layer: 6-
* 64
* A
* A
* ’
* B
* B
* ’
* C
* C
* ’
* 1
* 2
* 3
* 4
* 5
* 6
* Q:
* how does switch know A’ reachable via interface 4, B’ reachable via interface 5?
* A:
* each switch has a
* switch table,
* each entry:
* (MAC address of host, interface to reach host, time stamp)
* looks like a routing table!
* Q:
* how are entries created, maintained in switch table?
* something like a routing protocol?
* style.visibility
* style.visibility

---

### Slide 65: Switch: self-learning

* Link Layer: 6-
* 65
* A
* A
* ’
* B
* B
* ’
* C
* C
* ’
* 1
* 2
* 3
* 4
* 5
* 6
* switch
* learns
* which hosts can be reached through which interfaces
* A A
* ’
* Source: A
* Dest: A
* ’
* MAC addr   interface    TTL
* Switch table
* (initially empty)
* A
* 1
* 60
* when frame received, switch “learns”  location of sender: incoming LAN segment
* records sender/location pair in switch table
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility

---

### Slide 66: Switch: frame filtering/forwarding

* Link Layer: 6-
* 66
* when  frame received at switch:
* 1.
* record incoming link, MAC address of sending host
* 2. index switch table using MAC destination address
* 3. if
* entry found for destination
* then {
* if
* destination on segment from which frame arrived
* then
* drop frame
* else
* forward frame on interface indicated by entry
* }
* else
* flood  /* forward on all interfaces except arriving interface */
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 67: A

* A
* ’
* B
* B
* ’
* C
* C
* ’
* 1
* 2
* 3
* 4
* 5
* 6
* Self-learning, forwarding: example
* Link Layer: 6-
* 67
* A A
* ’
* Source: A
* Dest: A
* ’
* MAC addr   interface    TTL
* switch table
* (initially empty)
* A
* 1
* 60
* A A
* ’
* A A
* ’
* A A
* ’
* A A
* ’
* A A
* ’
* A
* ’
* A
* A
* ’
* 4
* 60
* frame destination, A’, location unknown:
* flood
* destination A location known:
* selectively send
* on just one link
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y

---

### Slide 68: Interconnecting switches

* Link Layer: 6-
* 68
* self-learning switches can be connected together:
* Q:
* sending from A to G - how does S
* 1
* know to forward frame destined to G via S
* 4
* and S
* 3
* ?
* A:
* self learning! (works exactly the same as in single-switch case!)
* A
* B
* S
* 1
* C
* D
* E
* F
* S
* 2
* S
* 4
* S
* 3
* H
* I
* G
* style.visibility
* style.visibility

---

### Slide 69: Self-learning multi-switch example

* Link Layer: 6-
* 69
* Suppose C sends frame to I, I responds to C
* Q:
* show switch tables and packet forwarding in S
* 1
* , S
* 2
* , S
* 3
* , S
* 4
* A
* B
* S
* 1
* C
* D
* E
* F
* S
* 2
* S
* 4
* S
* 3
* H
* I
* G

---

### Slide 70: Small institutional network

* Link Layer: 6-
* 70
* to external
* network
* router
* IP subnet
* mail server
* web server

---

### Slide 71: Switches vs. routers

* Link Layer: 6-
* 71
* application
* transport
* network
* link
* physical
* network
* link
* physical
* link
* physical
* switch
* datagram
* application
* transport
* network
* link
* physical
* frame
* frame
* frame
* datagram
* 6-
* 71
* both are store-and-forward:
* routers
* :
* network-layer devices (examine network-layer headers)
* switches:
* link-layer devices (examine link-layer headers)
* both have forwarding tables:
* routers:
* compute tables using routing algorithms, IP addresses
* switches:
* learn forwarding table using flooding, learning, MAC addresses
* style.visibility

---

### Slide 72: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 72

---

### Slide 73: Virtual LANs (VLANs): motivation

* Link Layer: 6-
* 73
* Computer
* Science
* EE
* Q:
* what happens as LAN sizes scale, users change point of attachment?
* single broadcast domain:
* scaling:
* all layer-2 broadcast traffic (ARP, DHCP, unknown MAC) must cross entire LAN
* efficiency, security
* , privacy issues

---

### Slide 74: Virtual LANs (VLANs): motivation

* Link Layer: 6-
* 74
* administrative issues:
* CS user moves office to EE -
* physically
* attached to EE switch, but wants to remain
* logically
* attached to CS switch
* Computer
* Science
* EE
* single broadcast domain:
* scaling:
* all layer-2 broadcast traffic (ARP, DHCP, unknown MAC) must cross entire LAN
* efficiency, security, privacy, efficiency issues
* Q:
* what happens as LAN sizes scale, users change point of attachment?
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility

---

### Slide 75: 1

* 8
* 2
* 7
* 9
* 16
* 10
* 15
* Port-based VLANs
* Link Layer: 6-
* 75
* switch(es) supporting VLAN capabilities can be configured to define multiple
* virtual
* LANS over single physical LAN infrastructure.
* Virtual Local Area Network (VLAN)
* port-based VLAN:
* switch ports grouped (by switch management software) so that
* single
* physical switch ……
* …
* EE (VLAN ports 1-8)
* CS (VLAN ports 9-15)
* …
* … operates as
* multiple
* virtual switches
* 1
* 8
* 2
* 7
* EE (VLAN ports 1-8)
* …
* 9
* 16
* 10
* 15
* …
* CS (VLAN ports 9-15)
* style.visibility

---

### Slide 76: 1

* 8
* 2
* 7
* 9
* 16
* 10
* 15
* Port-based VLANs
* Link Layer: 6-
* 76
* …
* EE (VLAN ports 1-8)
* CS (VLAN ports 9-15)
* …
* traffic isolation:
* frames to/from ports
* 1
* -8 can
* only
* reach ports
* 1
* -8
* can also define VLAN based on MAC addresses of endpoints, rather than switch port
* dynamic membership
* :
* ports can be dynamically assigned among VLANs
* forwarding between VLANS:
* done via routing (just as with separate switches)
* in practice vendors sell combined switches plus routers
* style.visibility
* style.visibility
* style.visibility

---

### Slide 77: 1

* 8
* 2
* 7
* 9
* 16
* 10
* 15
* VLANS spanning multiple switches
* Link Layer: 6-
* 77
* …
* EE (VLAN ports 1-8)
* CS (VLAN ports 9-15)
* …
* 5
* 8
* 2
* 7
* …
* 16
* 1
* 6
* 3
* 4
* Ports 2,3,5 belong to EE VLAN
* Ports 4,6,7,8 belong to CS VLAN
* trunk port:
* carries frames between VLANS defined over multiple physical switches
* frames forwarded within VLAN between switches can’t be vanilla 802.1 frames (must carry VLAN ID info)
* 802.1q protocol adds/removed additional header fields for frames forwarded between trunk ports
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 78: 802.1Q VLAN frame format

* Link Layer: 6-
* 78
* 802.1 Ethernet frame
* dest.
* address
* source
* address
* data (payload)
* CRC
* preamble
* type
* 2-byte Tag Protocol Identifier
* (value: 81-00)
* Tag Control Information
* (12 bit VLAN ID field, 3 bit priority field like IP TOS)
* Recomputed
* CRC
* 802.1Q frame
* dest.
* address
* source
* address
* data (payload)
* CRC
* preamble
* type
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 79: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 79

---

### Slide 80: label

* Exp
* S
* TTL
* 20
* 3
* 1
* 5
* Multiprotocol label switching (MPLS)
* Link Layer: 6-
* 80
* goal:
* high-speed IP forwarding among network of MPLS-capable routers, using fixed length label
* (instead of shortest prefix matching)
* faster lookup using fixed length identifier
* borrowing ideas from Virtual Circuit (VC) approach
* but IP datagram still keeps IP address!
* remainder of Ethernet frame, including IP header with IP source, destination addresses
* MPLS header
* Ethernet
* header
* remainder of Ethernet frame, including IP header with IP source, destination addresses
* ppt_x
* ppt_y
* ppt_x
* ppt_y
* style.visibility
* style.visibility

---

### Slide 81: MPLS capable routers

* Link Layer: 6-
* 81
* a.k.a. label-switched router
* forward packets to outgoing interface based only on label value (
* don’t inspect IP address
* )
* MPLS forwarding table distinct from IP forwarding tables
* flexibility:
* MPLS forwarding decisions can
* differ
* from those of IP
* use destination
* and
* source addresses to route flows to same destination differently (traffic engineering)
* re-route flows quickly if link fails: pre-computed backup paths
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 82: MPLS versus IP paths

* Link Layer: 6-
* 82
* R2
* D
* R3
* R5
* A
* R6
* R4
* IP routing:
* path to destination determined by destination address alone
* IP router

---

### Slide 83: MPLS versus IP paths

* Link Layer: 6-
* 83
* R2
* D
* R3
* R5
* A
* R6
* IP router
* R4
* IP routing:
* path to destination determined by destination address alone
* IP/MPLS router
* IP/MPLS entry router (R4)  can use
* different
* MPLS routes to A based, e.g., on IP source address or other fields
* MPLS routing:
* path to destination can be based on source
* and
* destination address
* flavor of generalized forwarding
* (MPLS 10 years earlier)
* fast reroute:
* precompute backup routes in case of link failure
* R1
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 84: MPLS signaling

* Link Layer: 6-
* 84
* modify OSPF, IS-IS link-state flooding protocols to carry info used by MPLS routing:
* e.g., link bandwidth, amount of “reserved
* ”
* link bandwidth
* R2
* D
* R3
* R5
* A
* R6
* R4
* modified
* link state
* flooding
* RSVP-TE
* entry MPLS router uses RSVP-TE signaling protocol to set up MPLS forwarding at downstream routers
* R1
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 85: MPLS forwarding tables

* Link Layer: 6-
* 85
* in         out                 out
* label     label   dest    interface
* 6        -      A       0
* in         out                 out
* label     label   dest    interface
* 10      6      A       1
* 12      9      D       0
* in         out                 out
* label     label   dest    interface
* 8        6      A       0
* in         out                 out
* label     label   dest    interface
* 10      A       0
* 12      D       0
* 8      A       1
* R2
* D
* R3
* R5
* A
* R6
* R4
* R1
* 0
* 1
* 0
* 0
* 1
* 0
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 86: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 86

---

### Slide 87: Datacenter networks

* Link Layer: 6-
* 87
* 10’s to 100’s of thousands of hosts, often closely coupled, in close proximity:
* e-business (e.g. Amazon)
* content-servers (e.g., YouTube, Akamai, Apple, Microsoft)
* search engines, data mining (e.g., Google)
* challenges:
* multiple applications, each serving massive numbers of clients
* reliability
* managing/balancing load, avoiding processing, networking, data bottlenecks
* Inside a 40-ft Microsoft container, Chicago data center
* style.visibility

---

### Slide 88: Datacenter networks: network elements

* Link Layer: 6-
* 88
* Server racks
* 20- 40 server blades: hosts
* Top of Rack (TOR) switch
* one per rack
* 40-100Gbps Ethernet to blades
* Tier-2 switches
* connecting to  ~16 TORs below
* Tier-1 switches
* connecting to  ~16 T-2s below
* Border routers
* connections outside datacenter
* …
* …
* …
* …
* …
* …
* …
* …
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

### Slide 89: Datacenter networks: network elements

* Link Layer: 6-
* 89
* Facebook F16 data center network topology:
* https://engineering.fb.com/data-center-engineering/f16-minipack/    (posted 3/2019)

---

### Slide 90: Datacenter networks: multipath

* Link Layer: 6-
* 90
* 9
* 10
* 11
* 12
* 13
* 14
* 15
* 16
* two
* disjoint
* paths highlighted between racks 1 and 11
* rich interconnection among switches, racks:
* increased throughput between racks (multiple routing paths possible)
* increased reliability via redundancy

---

### Slide 91: …

* …
* …
* …
* …
* …
* …
* …
* Datacenter networks: application-layer routing
* Link Layer: 6-
* 91
* Load
* balancer
* Internet
* load balancer: application-layer routing
* receives external client requests
* directs workload within data center
* returns results to external client
* (hiding data center internals from client)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 92: link layer:

* RoCE
* : remote DMA (RDMA) over Converged Ethernet
* transport layer:
* ECN (explicit congestion notification) used in transport-layer congestion control (DCTCP, DCQCN)
* experimentation with hop-by-hop (backpressure) congestion control
* routing, management
* :
* SDN widely used within/among organizations’ datacenters
* place related services, data as close as possible (e.g., in same rack or nearby rack) to minimize tier-2, tier-1 communication
* Datacenter networks: protocol innovations
* Link Layer: 6-
* 92
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 93: Link layer, LANs: roadmap

* a day in the life of a web request
* introduction
* error detection, correction
* multiple access protocols
* LANs
* addressing, ARP
* Ethernet
* switches
* VLANs
* link virtualization: MPLS
* data center networking
* Link Layer: 6-
* 93

---

### Slide 94: Synthesis: a day in the life of a web request

* Link Layer: 6-
* 94
* our journey down the protocol stack is now complete!
* application, transport, network, link
* putting-it-all-together: synthesis!
* goal:
* identify, review, understand protocols (at all layers) involved in seemingly simple scenario: requesting www page
* scenario:
* student attaches laptop to campus network, requests/receives
* www.google.com
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 95: A day in the life: scenario

* Link Layer: 6-
* 95
* Comcast network
* 68.80.0.0/13
* Google
* ’
* s network
* 64.233.160.0/19
* 64.233.169.105
* web server
* DNS server
* school network
* 68.80.2.0/24
* browser
* web page
* arriving mobile client attaches to network …
* requests web page:
* www.google.com
* scenario
* :
* Sounds
* simple!
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 96: A day in the life: connecting to the Internet

* Link Layer: 6-
* 96
* router has
* DHCP server
* arriving mobile:
* DHCP client
* connecting laptop needs to get its own IP address,
* addr
* of first-hop router,
* addr
* of DNS server: use
* DHCP
* DHCP
* UDP
* IP
* Eth
* Phy
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* UDP
* IP
* Eth
* Phy
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP request
* encapsulated
* in
* UDP
* , encapsulated in
* IP
* , encapsulated in
* 802.3
* Ethernet
* Ethernet frame
* broadcast
* (dest: FFFFFFFFFFFF) on LAN, received at router running
* DHCP
* server
* Ethernet
* demuxed
* to IP demuxed, UDP demuxed to DHCP
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
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 97: A day in the life: connecting to the Internet

* Link Layer: 6-
* 97
* router has
* DHCP server
* arriving mobile:
* DHCP client
* DHCP
* UDP
* IP
* Eth
* Phy
* DHCP
* UDP
* IP
* Eth
* Phy
* DHCP server formulates
* DHCP ACK
* containing client
* ’
* s IP address, IP address of first-hop router for client, name & IP address of DNS server
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* DHCP
* encapsulation at DHCP server, frame forwarded (
* switch learning
* ) through LAN, demultiplexing at client
* Client now has IP address, knows name & addr of DNS
* server, IP address of its first-hop router
* DHCP client receives DHCP ACK reply
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 98: A day in the life… ARP

* (before DNS, before HTTP)
* Link Layer: 6-
* 98
* router has
* ARP server
* arriving mobile:
* ARP client
* DNS
* UDP
* IP
* Eth
* Phy
* Eth
* Phy
* ARP
* before sending
* HTTP
* request, need IP address of
* www.google.com
* :
* DNS
* DNS
* DNS
* DNS
* DNS query created, encapsulated in UDP, encapsulated in IP, encapsulated in Eth.  To send frame to router, need MAC address of router interface:
* ARP
* ARP query
* broadcast, received by router, which replies with
* ARP reply
* giving MAC address of router interface
* client now knows MAC address of first hop router, so can now send frame containing DNS query
* ARP query
* ARP
* ARP reply
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility

---

### Slide 99: A day in the life… using DNS

* Link Layer: 6-
* 99
* DNS
* UDP
* IP
* Eth
* Phy
* DNS
* DNS
* DNS
* Comcast network
* 68.80.0.0/13
* DNS
* server
* DNS
* DNS
* DNS
* DNS
* DNS
* IP datagram containing DNS query forwarded via LAN switch from client to 1
* st
* hop router
* IP datagram forwarded from campus network into Comcast network, routed (tables created by
* RIP, OSPF, IS-IS
* and/or
* BGP
* routing protocols) to DNS server
* demux
* ed to DNS
* DNS replies to client with IP address of www.google.com
* DNS
* UDP
* IP
* Eth
* Phy
* DNS
* DNS
* DNS
* DNS
* DNS
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 100: A day in the life…TCP connection carrying HTTP

* Link Layer: 6-
* 100
* DNS
* DNS
* DNS
* Comcast network
* 68.80.0.0/13
* 64.233.169.105
* Google web server
* HTTP
* TCP
* IP
* Eth
* Phy
* HTTP
* to send HTTP request, client first opens
* TCP socket
* to web server
* TCP
* SYN segment
* (step 1 in TCP 3-way handshake)
* inter-domain routed to web server
* TCP
* connection established!
* SYN
* SYN
* SYN
* SYN
* TCP
* IP
* Eth
* Phy
* SYN
* SYN
* SYN
* SYNACK
* SYNACK
* SYNACK
* SYNACK
* SYNACK
* SYNACK
* SYNACK
* web server responds with
* TCP SYNACK
* (step 2 in TCP 3-way handshake)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 101: A day in the life… HTTP request/reply

* Link Layer: 6-
* 101
* DNS
* DNS
* DNS
* Comcast network
* 68.80.0.0/13
* 64.233.169.105
* Google web server
* HTTP
* TCP
* IP
* Eth
* Phy
* HTTP
* TCP
* IP
* Eth
* Phy
* HTTP
* HTTP request
* sent into TCP socket
* IP datagram containing HTTP request routed to www.google.com
* IP datagram containing HTTP reply routed back to client
* web server responds with
* HTTP reply
* (containing web page)
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* HTTP
* web page
* finally (!!!)
* displayed
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* ppt_x
* ppt_y
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 102: Chapter 6: Summary

* Link Layer: 6-
* 102
* principles behind data link layer services:
* error detection, correction
* sharing a broadcast channel: multiple access
* link layer addressing
* instantiation, implementation of various link layer technologies
* Ethernet
* switched LANS, VLANs
* virtualized networks as a link layer: MPLS
* synthesis: a day in the life of a web request
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

### Slide 103: Chapter 6: let’s take a breath

* Link Layer: 6-
* 103
* journey down protocol stack
* complete
* (except PHY)
* solid understanding of networking principles, practice!
* ….. could stop here …. but
* more
* interesting topics!
* wireless
* security
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 104: Additional Chapter 6 slides

* Network Layer: 5-
* 104

---

### Slide 105: Pure ALOHA efficiency

* Link Layer: 6-
* 105
* P(success by given node) = P(node transmits)
* P(no other node transmits in [t
* 0
* -1,t
* 0
* ]
* P(no other node transmits in [t
* 0
* -1,t
* 0
* ]
* = p
* .
* (1-p)
* N-1
* .
* (1-p)
* N-1
* =
* p
* .
* (1-p)
* 2(N-1)
* … choosing optimum p and then letting
* n
* = 1/(2e) = .18
* *
* *
* *
* even worse than slotted Aloha!

---

