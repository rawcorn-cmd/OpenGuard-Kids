# Slide Bài Giảng: Chapter 8 v8.0

> **Nguồn gốc:** Slide chính thức của tác giả Kurose & Ross (Chapter_8_v8.0.pptx)

---

### Slide 2: Security: overview

* Security: 8-
* 2
* Chapter goals:
* understand principles of network security:
* cryptography and its
* many
* uses beyond “
* confidentiality”
* authentication
* message integrity
* security in practice:
* firewalls and intrusion detection systems
* security in application, transport, network, link layers
* style.visibility
* style.visibility
* style.visibility

---

### Slide 3: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Message integrity, authentication
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 3

---

### Slide 4: What is network security?

* Security: 8-
* 4
* confidentiality:
* only sender, intended receiver should “
* understand” message contents
* sender encrypts message
* receiver decrypts message
* authentication:
* sender, receiver want to confirm identity of each other
* message integrity:
* sender, receiver want to ensure message not altered (in transit, or afterwards) without detection
* access and availability
* :
* services must be accessible and available to users
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 5: Friends and enemies: Alice, Bob, Trudy

* Security: 8-
* 5
* well-known in network security world
* Bob, Alice (lovers!) want to communicate “
* securely”
* Trudy (intruder) may intercept, delete, add messages
* secure
* sender
* secure
* receiver
* channel
* data, control messages
* data
* data
* Alice
* Bob
* Trudy

---

### Slide 6: Friends and enemies: Alice, Bob, Trudy

* Who might Bob and Alice be?
* … well,
* real-life
* Bobs and Alices!
* Web browser/server for electronic transactions (e.g., on-line purchases)
* on-line banking client/server
* DNS servers
* BGP routers exchanging routing table updates
* other examples?

---

### Slide 7: There are bad guys (and girls) out there!

* Q:
* What can a “
* bad guy” do?
* A:
* A lot! (recall section 1.6)
* eavesdrop:
* intercept messages
* actively
* insert
* messages into connection
* impersonation:
* can fake (spoof) source address in packet (or any field in packet)
* hijacking:
* “take over” ongoing connection by removing sender or receiver, inserting himself in place
* denial of service:
* prevent service from being used by others (e.g.,  by overloading resources)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 8: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Message integrity, authentication
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 8

---

### Slide 9: The language of cryptography

* m:
* plaintext message
* K
* A
* (m):
* ciphertext, encrypted with key K
* A
* m = K
* B
* (K
* A
* (m))
* plaintext
* plaintext
* ciphertext
* K
* A
* encryption
* algorithm
* decryption
* algorithm
* Alice’
* s
* encryption
* key
* Bob
* ’s
* decryption
* key
* K
* B
* Security: 8-
* 9

---

### Slide 10: Breaking an encryption scheme

* cipher-text only attack:
* Trudy has ciphertext she can analyze
* two approaches:
* brute force: search through all
* keys
* statistical analysis
* known-plaintext attack:
* Trudy has plaintext corresponding to ciphertext
* e.g.,
* in monoalphabetic cipher, Trudy determines pairings for a,l,i,c,e,b,o,
* chosen-plaintext attack:
* Trudy can get ciphertext for chosen plaintext
* Security: 8-
* 10

---

### Slide 11: Symmetric key cryptography

* plaintext
* plaintext
* K
* S
* encryption
* algorithm
* decryption
* algorithm
* K
* S
* ciphertext
* K  (m)
* S
* symmetric key crypto
* : Bob and Alice share same (symmetric) key: K
* e.g.,
* key is knowing substitution pattern in mono alphabetic substitution cipher
* Q:
* how do Bob and Alice agree on key value?
* Security: 8-
* 11

---

### Slide 12: Simple encryption scheme

* substitution cipher:
* substituting one thing for another
* monoalphabetic cipher: substitute one letter for another
* plaintext:  abcdefghijklmnopqrstuvwxyz
* ciphertext:  mnbvcxzasdfghjklpoiuytrewq
* Plaintext: bob. i love you. alice
* ciphertext: nkn. s gktc wky. mgsbc
* e.g.:
* Encryption key:
* mapping from set of 26 letters
* to set of 26 letters
* Security: 8-
* 12

---

### Slide 13: A more sophisticated encryption approach

* Security: 8-
* 13
* n substitution ciphers, M
* 1
* ,M
* 2
* ,…,M
* n
* cycling pattern:
* e.g., n=4: M
* 1
* ,M
* 3
* ,M
* 4
* ,M
* 3
* ,M
* 2
* ;   M
* 1
* ,M
* 3
* ,M
* 4
* ,M
* 3
* ,M
* 2
* ;
* ..
* for each new plaintext symbol, use subsequent substitution pattern in cyclic pattern
* dog: d from M
* 1
* , o from M
* 3
* , g from M
* 4
* Encryption key:
* n substitution ciphers, and cyclic pattern
* key need not be just n-bit pattern

---

### Slide 14: Symmetric key crypto: DES

* Security: 8-
* 14
* DES: Data Encryption Standard
* US encryption standard [NIST 1993]
* 56-bit symmetric key, 64-bit plaintext input
* block cipher with cipher block chaining
* how secure is DES?
* DES Challenge: 56-bit-key-encrypted phrase  decrypted (brute force) in less than a day
* no known good analytic attack
* making DES more secure:
* 3DES: encrypt 3 times with 3 different keys

---

### Slide 15: AES: Advanced Encryption Standard

* Security: 8-
* 15
* symmetric-key NIST standard, replaced DES (Nov 2001)
* processes data in 128 bit blocks
* 128, 192, or 256 bit keys
* brute force decryption (try each key) taking 1 sec on DES, takes 149 trillion years for AES

---

### Slide 16: Public Key Cryptography

* Security: 8-
* 16
* symmetric key crypto:
* requires sender, receiver know shared secret key
* Q: how to agree on key in first place (particularly if never “
* met”)?
* public key crypto
* radically
* different approach [Diffie-Hellman76, RSA78]
* sender, receiver do
* not
* share secret key
* public
* encryption key
* known to
* all
* private
* decryption key known only to receiver
* style.visibility
* style.visibility

---

### Slide 17: Public Key Cryptography

* Security: 8-
* 17
* m = K
* (
* K  (m)
* )
* B
* +
* B
* -
* plaintext
* encryption
* algorithm
* decryption
* algorithm
* K  (m)
* B
* +
* ciphertext
* plaintext
* message, m
* K
* B
* +
* Bob
* ’
* s
* public
* key
* Bob
* ’s
* private
* key
* K
* B
* -
* Wow
* - public key cryptography revolutionized 2000-year-old (previously only symmetric key) cryptography!
* similar ideas emerged at roughly same time, independently in US and UK (classified)
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 18: Public key encryption algorithms

* Security: 8-
* 18
* requirements:
* RSA:
* Rivest, Shamir, Adelson algorithm
* 1
* need K  ( ) and K  ( ) such that
* B
* B
* .
* .
* +
* -
* K  (K   (m))  =  m
* B
* B
* -
* +
* given public key K  , it should be impossible to compute private key K
* B
* B
* 2
* +
* -
* style.visibility
* style.visibility
* style.visibility

---

### Slide 19: Prerequisite: modular arithmetic

* Security: 8-
* 19
* x mod n = remainder of x when divide by n
* facts:
* [(a mod n) + (b mod n)] mod n = (a+b) mod n
* [(a mod n) - (b mod n)] mod n = (a-b) mod n
* [(a mod n) * (b mod n)] mod n = (a*b) mod n
* thus
* (a mod n)
* d
* mod n = a
* d
* mod n
* example: x=14, n=10, d=2:
* (x mod n)
* d
* mod n = 4
* 2
* mod 10 = 6
* x
* d
* = 14
* 2
* = 196   x
* d
* mod 10  = 6

---

### Slide 20: RSA: getting ready

* Security: 8-
* 20
* message: just a bit pattern
* bit pattern can be uniquely represented by an integer number
* thus, encrypting a message is equivalent to encrypting a number
* example:
* m= 10010001. This message is uniquely represented by the decimal number 145.
* to encrypt m, we encrypt the corresponding number, which gives a new number (the ciphertext).

---

### Slide 21: RSA: Creating public/private key pair

* Security: 8-
* 21
* 1.
* choose two large prime numbers
* p, q.
* (e.g., 1024 bits each)
* 2.
* compute
* n
* = pq,  z = (p-1)(q-1
* )
* 3.
* choose
* e
* (
* with
* e<n)
* that has no common factors  with z (
* e, z
* are “
* relatively prime”).
* 4.
* choose
* d
* such that
* ed-1
* is  exactly divisible by
* z
* .  (in other words:
* ed
* mod
* z  = 1
* ).
* 5.
* public
* key is
* (
* n,e
* ).
* private
* key is
* (
* n,d
* ).
* K
* B
* +
* K
* B
* -

---

### Slide 22: RSA: encryption, decryption

* Security: 8-
* 22
* 0.
* given (
* n,e
* ) and (
* n,d
* ) as computed above
* 1.
* to encrypt message
* m (<n)
* , compute
* c = m
* mod
* n
* e
* 2.
* to decrypt received bit pattern,
* c
* , compute
* m = c
* mod
* n
* d
* m  =  (m
* mod
* n)
* e
* mod
* n
* d
* magic happens!
* c

---

### Slide 23: RSA example:

* Security: 8-
* 23
* Bob chooses
* p=5, q=7
* .  Then
* n=35, z=24
* .
* e=5
* (so
* e, z
* relatively prime).
* d=29
* (so
* ed-1
* exactly divisible by z).
* bit pattern
* m
* m
* e
* c = m  mod  n
* e
* 0000l000
* 12
* 24832
* 17
* encrypt:
* encrypting 8-bit messages.
* c
* m = c  mod  n
* d
* 17
* 481968572106750915091411825223071697
* 12
* c
* d
* decrypt:
* style.visibility
* style.visibility

---

### Slide 24: Why does RSA work?

* Security: 8-
* 24
* must show that c
* d
* mod n = m,  where c = m
* e
* mod n
* fact: for any x and y: x
* y
* mod n = x
* (y mod z)
* mod n
* where n= pq and z = (p-1)(q-1)
* thus,
* c
* d
* mod n = (m
* e
* mod n)
* d
* mod n
* = m
* ed
* mod n
* = m
* (ed mod z)
* mod n
* = m
* 1
* mod n
* = m
* style.visibility

---

### Slide 25: RSA: another important property

* Security: 8-
* 25
* The following property will be
* very
* useful later:
* K
* (
* K  (m)
* )
* =  m
* B
* B
* -
* +
* K
* (
* K  (m)
* )
* B
* B
* +
* -
* =
* use public key first, followed by private key
* use private key first, followed by public key
* result is the same!

---

### Slide 26: Security: 8-

* 26
* follows directly from modular arithmetic:
* (m
* e
* mod n)
* d
* mod n = m
* ed
* mod n
* = m
* de
* mod n
* = (m
* d
* mod n)
* e
* mod n
* Why
* ?
* K
* (
* K  (m)
* )
* =  m
* B
* B
* -
* +
* K
* (
* K  (m)
* )
* B
* B
* +
* -
* =

---

### Slide 27: Why is RSA secure?

* Security: 8-
* 27
* suppose you know Bob’
* s public key (n,e). How hard is it to determine d?
* essentially need to find factors of n without knowing the two factors p and q
* fact: factoring a big number is hard

---

### Slide 28: RSA in practice: session keys

* Security: 8-
* 28
* exponentiation in RSA is computationally intensive
* DES is at least 100 times faster than RSA
* use public key crypto to establish secure connection, then establish second key – symmetric session key – for encrypting data
* session key, K
* S
* Bob and Alice use RSA to exchange a symmetric session key K
* S
* once both have K
* S
* , they use symmetric key cryptography

---

### Slide 29: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication
* , message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 29

---

### Slide 30: Authentication

* Security: 8-
* 30
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap1.0:
* Alice says
* “
* I am Alice
* ”
* failure scenario??
* “I am Alice
* ”

---

### Slide 31: Authentication

* Security: 8-
* 31
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap1.0:
* Alice says
* “
* I am Alice
* ”
* in a network, Bob can not
* “
* see
* ”
* Alice, so Trudy simply declares herself to be Alice
* “
* I am Alice
* ”
* style.visibility
* style.visibility

---

### Slide 32: Authentication: another try

* Security: 8-
* 32
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap2.0:
* Alice says
* “
* I am Alice
* ”
* in an IP packet containing her source IP address
* “
* I am Alice
* ”
* Alice’s
* IP address
* failure scenario??

---

### Slide 33: Authentication: another try

* Security: 8-
* 33
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap2.0:
* Alice says
* “
* I am Alice
* ”
* in an IP packet containing her source IP address
* “
* I am Alice
* ”
* Alice’s
* IP address
* Trudy can create
* a packet “spoofing”
* Alice’s address

---

### Slide 34: Authentication: a third try

* Security: 8-
* 34
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap3.0:
* Alice says
* “
* I am Alice
* ”
* Alice says “I am Alice” and sends her secret password to “prove” it.
* “
* I am Alice
* ”
* Alice’s
* IP addr
* Alice’s
* password
* failure scenario??
* Alice’s
* IP addr
* OK

---

### Slide 35: Authentication: a third try

* Security: 8-
* 35
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap3.0:
* Alice says
* “
* I am Alice
* ”
* Alice says “I am Alice” and sends her secret password to “prove” it.
* “
* I am Alice
* ”
* Alice’s
* IP addr
* Alice’s
* password
* Alice’s
* IP addr
* OK
* “
* I am Alice
* ”
* Alice’s
* IP addr
* Alice’s
* password
* playback attack:
* Trudy records Alice’s packet
* and later
* plays it back to Bob
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 36: Authentication: a modified third try

* Security: 8-
* 36
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap3.0:
* Alice says
* “
* I am Alice
* ”
* Alice says “I am Alice” and sends her encrypted secret password to “prove” it.
* “
* I am Alice
* ”
* Alice’s
* IP addr
* encrypted
* password
* failure scenario??
* Alice’s
* IP addr
* OK

---

### Slide 37: Authentication: a modified third try

* Security: 8-
* 37
* Goal:
* Bob wants Alice to “
* prove” her identity to him
* Protocol ap3.0:
* Alice says
* “
* I am Alice
* ”
* Alice says “I am Alice” and sends her encrypted secret password to “prove” it.
* “
* I am Alice
* ”
* Alice’s
* IP addr
* encrypted
* password
* Alice’s
* IP addr
* OK
* “
* I am Alice
* ”
* Alice’s
* IP addr
* encrypted
* password
* playback attack still works:
* Trudy records Alice’s packet
* and later plays it back to Bob
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 38: Authentication: a fourth try

* Security: 8-
* 38
* Goal:
* avoid playback attack
* protocol ap4.0:
* to prove Alice “live”, Bob sends Alice nonce, R
* Alice must return R, encrypted with shared secret key
* nonce:
* number (R) used only
* once-in-a-lifetime
* Failures, drawbacks?
* “I am Alice”
* R
* K    (R)
* A-B
* Bob know Alice is live, and only Alice knows key to encrypt nonce, so it must be Alice!
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 39: Authentication: ap5.0

* Security: 8-
* 39
* ap4.0 requires shared symmetric key  - can we authenticate using public key techniques?
* ap5.0:
* use nonce, public key cryptography
* “I am Alice”
* R
* K   (R)
* A
* -
* Send me your public key
* K   (R)
* A
* +
* Bob computes
* and knows only Alice could have the private key, that encrypted R such that
* (K  (R)) = R
* A
* -
* K
* A
* +
* (K  (R)) = R
* A
* -
* K
* A
* +
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 40: Authentication: ap5.0 – there’s still a flaw!

* Security: 8-
* 40
* man (or woman) in the middle attack:
* Trudy poses as Alice (to Bob) and as Bob (to Alice)
* I am Alice
* I am Alice
* Send me your public key
* Send me your public key
* T
* m = K  (K   (m))
* +
* T
* -
* Trudy recovers m:
* sends m to Alice encrypted with Alice’s public key
* T
* K   (R)
* -
* R
* T
* K
* +
* T
* K
* +
* (K   (R)) =  R,
* T
* -
* Bob computes
* authenticating
* Trudy as Alice
* R
* A
* K   (R)
* -
* K
* +
* A
* K   (m)
* +
* T
* Bob sends a personal message, m to Alice
* A
* K  (m)
* +
* A
* m = K  (K   (m))
* +
* A
* -
* Trudy recovers Bob’s m:
* and she and Bob meet a week later in person and discuss m, not knowing Trudy knows m
* ?
* Where are mistakes made here?
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

### Slide 41: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 41

---

### Slide 42: Digital signatures

* Security: 8-
* 42
* cryptographic technique analogous to hand-written signatures:
* sender (Bob) digitally signs document: he is document owner/creator.
* verifiable, nonforgeable:
* recipient (Alice) can prove to someone that Bob, and no one else (including Alice), must have signed document
* simple digital signature for message m:
* Bob signs m by encrypting with his private key K
* B
* , creating “
* signed” message, K
* B
* -
* (m)
* Bob
* ’
* s message, m
* Public key
* encryption
* algorithm
* Bob’s private
* key
* K
* B
* -
* m,K
* B
* -
* (m)
* Dear Alice
* Oh, how I have missed you. I think of you all the time! …(blah blah blah)
* Bob
* Dear Alice
* Oh, how I have missed you. I think of you all the time! …(blah blah blah)
* Bob
* K
* B
* -
* (m)

---

### Slide 43: Digital signatures

* Security: 8-
* 43
* -
* Alice thus verifies that:
* Bob signed m
* no one else signed m
* Bob signed m and not m’
* non-repudiation:
* Alice can take m, and signature K
* B
* (m) to court and prove that Bob signed m
* -
* suppose Alice receives msg m, with signature: m, K
* B
* (m)
* Alice verifies m signed by Bob by applying Bob’
* s public key K
* B
* to K
* B
* (m) then checks K
* B
* (K
* B
* (m) ) = m.
* If K
* B
* (K
* B
* (m) ) = m, whoever signed m must have used Bob’
* s private key
* -
* -
* -
* +
* +
* +
* style.visibility

---

### Slide 44: Message digests

* Security: 8-
* 44
* Hash function properties:
* many-to-1
* produces fixed-size msg digest (fingerprint)
* given message digest
* x
* , computationally infeasible to find
* m
* such that
* x = H(m)
* large
* message
* m
* H: Hash
* Function
* H(m)
* computationally expensive to public-key-encrypt long messages
* goal:
* fixed-length, easy- to-compute digital “
* fingerprint”
* apply hash function H to
* m
* , get fixed size message digest,
* H(m)

---

### Slide 45: Internet checksum: poor crypto hash function

* Security: 8-
* 45
* Internet checksum has some properties of hash function:
* produces fixed length digest (16-bit sum) of message
* is many-to-one
* but given message with given hash value, it is easy to find another message with same hash value:
* I O U 1
* 0 0 . 9
* 9 B O B
* 49 4F 55 31
* 30 30 2E 39
* 39 42 D2 42
* message
* ASCII format
* B2 C1 D2 AC
* I O U
* 9
* 0 0 .
* 1
* 9 B O B
* 49 4F 55
* 39
* 30 30 2E
* 31
* 39 42 D2 42
* message
* ASCII format
* B2 C1 D2 AC
* different messages
* but identical checksums
* !

---

### Slide 46: Digital signature = signed message digest

* Security: 8-
* 46
* digital
* signature
* (encrypt)
* +
* Bob sends digitally signed message:
* large
* message
* m
* H: Hash
* Function
* H(m)
* Alice verifies signature, integrity of digitally signed message:
* H: Hash
* function
* H(m)
* H(m)
* large
* message
* m
* Bob’s
* private
* key
* K
* B
* -
* K
* B
* (H(m))
* -
* encrypted
* message digest
* K
* B
* (H(m))
* -
* encrypted
* message digest
* digital
* signature
* (decrypt)
* Bob’s
* public
* key
* K
* B
* +
* ?
* equal
* style.visibility

---

### Slide 47: Hash function algorithms

* Security: 8-
* 47
* MD5 hash function widely used (RFC 1321)
* computes 128-bit message digest in 4-step process.
* arbitrary 128-bit string x, appears difficult to construct msg m whose MD5 hash is equal to x
* SHA-1 is also used
* US standard [
* NIST, FIPS PUB 180-1]
* 160-bit message digest

---

### Slide 48: Authentication: ap5.0 – let’s fix it!!

* Security: 8-
* 48
* Recall the problem:
* Trudy poses as Alice (to Bob) and as Bob (to Alice)
* I am Alice
* I am Alice
* Send me your public key
* Send me your public key
* T
* m = K  (K   (m))
* +
* T
* -
* Trudy recovers m:
* sends m to Alice encrypted with Alice’s public key
* T
* K   (R)
* -
* R
* T
* K
* +
* T
* K
* +
* (K   (R)) =  R,
* T
* -
* Bob computes
* authenticating
* Trudy as Alice
* R
* A
* K   (R)
* -
* K
* +
* A
* K   (m)
* +
* T
* Bob sends a personal message, m to Alice
* A
* K  (m)
* +
* A
* m = K  (K   (m))
* +
* A
* -
* Trudy recovers Bob’s m:
* and she and Bob meet a week later in person and discuss m, not knowing Trudy knows m
* ?
* Where are mistakes made here?
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

### Slide 49: Need for certified public keys

* Security: 8-
* 49
* motivation: Trudy plays pizza prank on Bob
* Trudy creates e-mail order:
* Dear Pizza Store, Please deliver to me four pepperoni pizzas. Thank you, Bob
* Trudy signs order with her private key
* Trudy sends order to Pizza Store
* Trudy sends to Pizza Store her public key, but says it
* ’s Bob’s public key
* Pizza Store verifies signature; then delivers four pepperoni pizzas to Bob
* Bob doesn’
* t even like pepperoni
* style.visibility

---

### Slide 50: Public key Certification Authorities (CA)

* Security: 8-
* 50
* certification authority (CA):
* binds public key to particular entity, E
* entity (person, website, router) registers its public key with CE provides
* “proof of identity” to CA
* CA creates certificate binding identity E to E’s public key
* certificate containing E’
* s public key digitally signed by CA: CA says “this is E’s public key”
* Bob
* ’
* s
* identifying information
* K
* B
* +
* certificate for Bob’
* s public key, signed by CA
* Bob’s
* public
* key
* K
* B
* +
* digital
* signature
* (encrypt)
* CA’s
* private
* key
* K
* CA
* -

---

### Slide 51: Public key Certification Authorities (CA)

* Security: 8-
* 51
* Bob
* ’s
* public
* key
* K
* B
* +
* K
* B
* +
* when Alice wants Bob
* ’s public key
* :
* gets Bob
* ’s certificate (Bob or elsewhere)
* apply CA
* ’s public key to Bob
* ’
* s certificate, get Bob’s public key
* CA’s
* public
* key
* K
* CA
* +
* digital
* signature
* (decrypt)

---

### Slide 52: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 52

---

### Slide 53: Secure e-mail: confidentiality

* Security: 8-
* 53
* Alice wants to send
* confidential
* e-mail, m, to Bob.
* K
* S
* ( )
* .
* K
* B
* ( )
* .
* +
* K
* S
* (m )
* K
* B
* (K
* S
* )
* +
* m
* K
* S
* K
* S
* K
* B
* +
* Internet
* K
* S
* ( )
* .
* K
* B
* ( )
* .
* -
* K
* B
* -
* K
* S
* m
* K
* S
* (m )
* K
* B
* (K
* S
* )
* +
* Alice:
* generates random
* symmetric
* private key, K
* S
* encrypts message with K
* S
* (for efficiency)
* also encrypts K
* S
* with Bob’
* s public key
* sends both K
* S
* (m) and K
* +
* B
* (K
* S
* ) to Bob
* +
* -

---

### Slide 54: Secure e-mail: confidentiality

* (more)
* Security: 8-
* 54
* Alice wants to send
* confidential
* e-mail, m, to Bob.
* K
* S
* ( )
* .
* K
* B
* ( )
* .
* +
* K
* S
* (m )
* K
* B
* (K
* S
* )
* +
* m
* K
* S
* K
* S
* K
* B
* +
* Internet
* K
* S
* ( )
* .
* K
* B
* ( )
* .
* -
* K
* B
* -
* K
* S
* m
* K
* S
* (m )
* K
* B
* (K
* S
* )
* +
* +
* -
* Bob:
* uses his private key to decrypt and recover K
* S
* uses K
* S
* to decrypt K
* S
* (m) to recover m

---

### Slide 55: Secure e-mail:

* integrity, authentication
* Security: 8-
* 55
* Alice wants to send m to Bob, with
* message integrity
* ,
* authentication
* H( )
* .
* K
* A
* ( )
* .
* -
* H(m )
* K
* A
* (H(m))
* -
* m
* K
* A
* -
* m
* K
* A
* ( )
* .
* +
* K
* A
* +
* K
* A
* (H(m))
* -
* m
* H( )
* .
* H(m )
* compare
* Internet
* +
* -
* Alice digitally signs hash of her message with her private key, providing integrity and authentication
* sends both message (in the clear) and digital signature

---

### Slide 56: Secure e-mail:

* integrity, authentication
* Security: 8-
* 56
* Alice sends m to Bob, with
* confidentiality,
* message integrity
* ,
* authentication
* H( )
* .
* K
* A
* ( )
* .
* -
* K
* A
* (H(m))
* -
* m
* K
* A
* -
* m
* Internet
* +
* K
* S
* ( )
* .
* K
* B
* ( )
* .
* +
* K
* S
* (m )
* K
* B
* (K
* S
* )
* +
* K
* S
* K
* B
* +
* K
* S
* +
* message integrity
* ,
* authentication
* confidentiality
* Alice uses three keys:
* her private key, Bob’
* s public key, new symmetric key
* What are Bob’s complementary actions?

---

### Slide 57: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 57

---

### Slide 58: Transport-layer security (TLS)

* Security: 8-
* 58
* widely deployed security protocol above the transport layer
* supported by almost all browsers, web servers: https (port 443)
* provides:
* confidentiality:
* via
* symmetric encryption
* integrity:
* via
* cryptographic hashing
* authentication:
* via
* public key cryptography
* all techniques we have studied!
* history:
* early research, implementation:
* secure network programming, secure sockets
* secure socket layer (SSL) deprecated
* [2015]
* TLS
* 1.3
* : RFC 8846 [2018]
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

### Slide 59: Transport-layer security (TLS)

* Security: 8-
* 59
* widely deployed security protocol above the transport layer
* supported by almost all browsers, web servers: https (port 443)
* provides:
* confidentiality:
* via
* symmetric encryption
* integrity:
* via
* cryptographic hashing
* authentication:
* via
* public key cryptography
* all techniques we have studied!
* history:
* early research, implementation:
* secure network programming, secure sockets
* secure socket layer (SSL) deprecated
* [2015]
* TLS
* 1.3
* : RFC 8846 [2018]
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

### Slide 60: Transport-layer security: what’s needed?

* Security: 8-
* 60
* handshake:
* Alice, Bob use their certificates, private keys to authenticate each other, exchange or create shared secret
* key derivation
* :
* Alice, Bob use shared secret to derive set of keys
* data transfer:
* stream data transfer: data as a series of records
* not just one-time transactions
* connection closure:
* special messages to securely close connection
* let’s
* build
* a toy TLS protocol,
* t-tls,
* to see what’s needed!
* we’ve seen the “pieces” already:
* style.visibility
* style.visibility
* style.visibility

---

### Slide 61: client request

* server reply
* t-tls hello
* public key certificate
* K
* B
* +
* (MS) = EMS
* TCP SYN
* SYNACK
* ACK
* t-tls: initial handshake
* t-tls handshake phase:
* Bob establishes TCP connection with Alice
* Bob verifies that Alice is really Alice
* Bob sends Alice a master secret key (MS), used to generate all other keys for TLS session
* potential issues:
* 3 RTT before client can start receiving data (including TCP handshake)
* Security: 8-
* 61

---

### Slide 62: t-tls: cryptographic keys

* Security: 8-
* 62
* considered bad to use same key for more than one cryptographic function
* different keys for message authentication code (MAC) and encryption
* four keys:
* K
* c
* : encryption key for data sent from client to server
* M
* c
* : MAC key for data sent from client to server
* K
* s
* : encryption key for data sent from server to client
* M
* s
* : MAC key for data sent from server to client
* keys derived from key derivation function (KDF)
* takes master secret and (possibly) some additional random data to create new keys

---

### Slide 63: t-tls: encrypting data

* Security: 8-
* 63
* recall: TCP provides data
* byte
* stream
* abstraction
* Q:
* can we encrypt data in-stream as written into TCP socket?
* A:
* where would MAC go? If at end, no message integrity until all data received and connection closed!
* solution:
* break stream in series of “records”
* each client-to-server record carries a MAC, created using M
* c
* receiver can act on each record as it arrives
* data
* MAC
* length
* t-tls record encrypted using symmetric key, K
* c,
* passed to TCP:
* K
* c
* (
* )
* style.visibility

---

### Slide 64: t-tls: encrypting data

* (more)
* Security: 8-
* 64
* possible attacks on data stream?
* re-ordering:
* man-in middle intercepts TCP segments and reorders (manipulating sequence #s in unencrypted TCP header)
* replay
* solutions:
* use TLS sequence numbers (data, TLS-seq-# incorporated into MAC)
* use nonce

---

### Slide 65: t-tls: connection close

* Security: 8-
* 65
* data
* MAC
* length
* type
* K
* c
* (
* )
* truncation attack:
* attacker forges TCP connection close segment
* one or both sides thinks there is less data than there actually is
* solution:
* record types, with one type for closure
* type 0 for data; type 1 for close
* MAC now computed using data, type, sequence #

---

### Slide 66: Transport-layer security (TLS)

* Security: 8-
* 66
* IP
* TCP
* TLS
* HTTP/2
* IP
* UDP
* QUIC
* HTTP/2
* (slimmed)
* Network
* Transport
* Application
* HTTP/2 over TCP
* HTTP/3
* HTTP/2 over QUIC
* (which incorporates TLS)
* over UDP
* IP
* TCP
* HTTP
* 1.0
* HTTP/2 over TCP
* TLS provides an API that
* any
* application can use
* an HTTP view of TLS:
* style.visibility
* style.visibility
* style.visibility

---

### Slide 67: “cipher suite”: algorithms that can be used for key generation, encryption, MAC, digital signature

* TLS: 1.3
* (2018)
* :
* more limited cipher suite choice than TLS 1.2
* (2008)
* only 5 choices, rather than 37 choices
* requires
* Diffie-Hellman (DH) for key exchange, rather than DH or RSA
* combined encryption and authentication algorithm (“authenticated encryption”) for data rather than serial encryption, authentication
* 4 based on AES
* HMAC uses SHA (256 or 284) cryptographic hash function
* TLS: 1.3 cipher suite
* Security: 8-
* 67

---

### Slide 68: TLS 1.3 handshake: 1 RTT

* Security: 8-
* 68
* client hello:
* supported cipher suites
* DH key agreement protocol, parameters
* 1
* server hello:
* selected cipher suite
* DH key agreement protocol, parameters
* 2
* 3
* client
* server
* client TLS hello msg:
* guesses
* key agreement protocol, parameters
* indicates cipher suites it supports
* 1
* server TLS hello msg chooses
* key agreement protocol, parameters
* cipher suite
* server-signed certificate
* 2
* client:
* checks server certificate
* generates key
* can now make application request (e.g.., HTTPS GET)
* 3
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 69: TLS 1.3 handshake: 0 RTT

* Security: 8-
* 69
* client hello:
* supported cipher suites
* DH key agreement protocol, parameters
* application data
* server hello:
* selected cipher suite
* DH key agreement protocol, parameters
* application data (reply)
* client
* server
* initial hello message contains encrypted application data!
* “resuming” earlier connection between client and server
* application data encrypted using “resumption master secret” from earlier connection
* vulnerable to replay attacks!
* maybe OK for get HTTP GET or client requests not modifying server state
* style.visibility
* style.visibility

---

### Slide 70: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 70

---

### Slide 71: provides datagram-level encryption, authentication, integrity

* for both user traffic and control traffic (e.g., BGP, DNS messages)
* two “modes”:
* IP Sec
* Security: 8-
* 71
* transport mode:
* only
* datagram
* payload
* is encrypted, authenticated
* tunnel mode:
* entire datagram is encrypted, authenticated
* encrypted datagram encapsulated in new datagram with new IP header, tunneled to destination
* payload
* payload
* payload
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

### Slide 72: Two IPsec protocols

* Security: 8-
* 72
* Authentication Header (AH) protocol
* [RFC 4302]
* provides source authentication & data integrity but
* not
* confidentiality
* Encapsulation Security Protocol (ESP)
* [RFC 4303]
* provides source authentication, data integrity,
* and confidentiality
* more widely used than AH

---

### Slide 73: SA

* Security associations (SAs)
* Security: 8-
* 73
* before sending data,
* security association (SA)
* established from sending to receiving entity  (directional)
* ending, receiving entitles maintain
* state information
* about SA
* recall: TCP endpoints also maintain state info
* IP is connectionless; IPsec is connection-oriented!
* 193.68.2.23
* 200.168.1.100
* R1 stores for SA:
* 32-bit identifier:
* Security Parameter Index (SPI)
* origin SA interface
* (200.168.1.100)
* destination SA interface
* (193.68.2.23)
* type of encryption used
* encryption key
* type of integrity check used
* authentication key
* style.visibility

---

### Slide 74: IPsec datagram

* Security: 8-
* 74
* new IP
* header
* ESP
* header
* original
* IP hdr
* Original IP
* datagram payload
* ESP
* trailer
* ESP
* auth
* padding
* pad
* length
* next
* header
* SPI
* Seq
* #
* encrypted
* authenticated
* ESP trailer: padding for block ciphers
* ESP header:
* SPI, so receiving entity knows what to do
* sequence number, to thwart replay attacks
* MAC in ESP auth field created with shared secret key
* tunnel mode
* ESP

---

### Slide 75: ESP tunnel mode: actions

* Security: 8-
* 75
* at R1:
* appends ESP trailer to original datagram (which includes original header fields!)
* encrypts result using algorithm & key specified by SA
* appends
* ESP header
* to front of this encrypted quantity
* creates authentication MAC using algorithm and key specified in SA
* appends MAC forming
* payload
* creates new IP header, new IP header fields, addresses to tunnel endpoint
* payload
* payload
* R1

---

### Slide 76: IPsec sequence numbers

* Security: 8-
* 76
* for new SA, sender initializes seq. # to 0
* each time datagram is sent on SA:
* sender increments seq # counter
* places value in seq # field
* goal:
* prevent attacker from sniffing and replaying a packet
* receipt of duplicate, authenticated IP packets may disrupt service
* method:
* destination checks for duplicates
* doesn’t keep track of
* all
* received packets; instead uses a window

---

### Slide 77: Security Policy Database (SPD)

* Security: 8-
* 77
* policy: for given datagram, sender needs to know if it should use IP sec
* policy stored in
* security policy database (SPD)
* needs to know which SA to use
* may use: source and destination IP address; protocol number
* Security Assoc. Database (SAD)
* endpoint holds SA state in
* security association database (SAD)
* when sending IPsec datagram, R1 accesses SAD to determine how to process datagram
* when IPsec datagram arrives to R2, R2 examines SPI in IPsec datagram, indexes SAD with SPI, processing
* datagram accordingly.
* SPD:
* “what” to do
* SAD: “
* how” to do it
* IPsec security databases

---

### Slide 78: Security: 8-

* 78
* Summary: IPsec services
* Trudy sits somewhere between R1, R2. she doesn’
* t know the keys
* will Trudy be able to see original contents of datagram? How about source, dest IP address, transport protocol, application port?
* flip bits without detection?
* masquerade as R1 using R1
* ’s IP address?
* replay a datagram?

---

### Slide 79: Security: 8-

* 79
* IKE: Internet Key Exchange
* previous examples:
* manual establishment of IPsec SAs in IPsec endpoints:
* Example SA:
* SPI: 12345
* Source IP: 200.168.1.100
* Dest IP: 193.68.2.23
* Protocol: ESP
* Encryption algorithm: 3DES-cbc
* HMAC algorithm: MD5
* Encryption key: 0x7aeaca…
* HMAC key:0xc0291f…
* manual keying is impractical for VPN with 100s of endpoints
* instead use
* IPsec IKE (Internet Key Exchange
* )

---

### Slide 80: Security: 8-

* 80
* IKE: PSK and PKI
* authentication (prove who you are) with either
* pre-shared secret (PSK) or
* with PKI (pubic/private keys and certificates).
* PSK: both sides start with secret
* run IKE to authenticate each other and to generate IPsec SAs (one in each direction), including encryption, authentication keys
* PKI: both sides start with public/private key pair, certificate
* run IKE to authenticate each other, obtain IPsec SAs (one in each direction).
* similar with handshake in SSL.

---

### Slide 81: Security: 8-

* 81
* IKE phases
* IKE has two phases
* phase 1:
* establish bi-directional IKE SA
* note: IKE SA different from IPsec SA
* aka ISAKMP security association
* phase 2:
* ISAKMP is used to securely negotiate IPsec pair of SAs
* phase 1 has two modes: aggressive mode and main mode
* aggressive mode uses fewer messages
* main mode provides identity protection and is more flexible

---

### Slide 82: Security: 8-

* 82
* IPsec summary
* IKE message exchange for algorithms, secret keys, SPI numbers
* either AH or ESP protocol  (or both)
* AH provides integrity, source authentication
* ESP protocol (with AH) additionally provides encryption
* IPsec peers can be two end systems, two routers/firewalls, or a router/firewall and
* an end system

---

### Slide 83: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* 802.11 (WiFi)
* 4G/5G
* Operational security: firewalls and IDS
* Security: 8-
* 83

---

### Slide 84: Security: 8-

* 84
* 802.11: authentication, encryption
* Arriving mobile must:
* associate with access point: (establish) communication over wireless link
* authenticate to network
* AP
* AS
* Authentication Server
* wired network
* mobile

---

### Slide 85: Security: 8-

* 85
* 802.11: authentication, encryption
* AP
* AS
* Authentication Server
* wired network
* 1
* discovery of security capabilities:
* AP advertises its presence, forms of authentication and encryption provided
* device requests specific forms authentication, encryption desired
* although device, AP already exchanging messages, device not yet authenticated, does not have encryption keys
* 1
* mobile
* discovery of security capabilities

---

### Slide 86: Security: 8-

* 86
* 802.11: authentication, encryption
* AP
* AS
* Authentication Server
* mobile
* wired network
* 1
* mutual authentication and shared symmetric key derivation:
* AS, mobile already have shared common secret (e.g., password)
* AS, mobile use shared secret, nonces (prevent relay attacks), cryptographic hashing (ensure message integrity) to authenticating each other
* AS, mobile derive symmetric session key
* discovery of security capabilities
* 2
* 2
* mutual authentication, key derivation

---

### Slide 87: Initial shared secret

* Security: 8-
* 87
* 802.11: WPA3 handshake
* AS generates
* Nonce
* AS
* , sends to mobile
* mobile receives
* Nonce
* AS
* generates
* Nonce
* M
* generates symmetric shared session key
* K
* M-AP
* using
* Nonce
* AS
* , Nonce
* M
* ,
* and initial shared secret
* sends
* Nonce
* M
* ,
* and
* HMAC-signed value using Nonce
* AS
* and initial shared secret
* AS derives symmetric shared session key
* K
* M-AP
* a
* Nonce
* AS
* b
* Nonce
* M
* , HMAC(f(K
* AS-M
* ,
* Nonce
* AS
* )
* )
* derive session key K
* M-AP
* using  initial-shared-secret,
* Nonce
* AS
* ,
* Nonce
* M
* Initial shared secret
* a
* b
* c
* derive session key K
* M-AP
* using  initial shared secret ,
* Nonce
* AS
* ,
* Nonce
* M
* c
* AS
* Authentication Server
* mobile
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

### Slide 88: Security: 8-

* 88
* 802.11: authentication, encryption
* AP
* AS
* Authentication Server
* mobile
* wired network
* 1
* discovery of security capabilities
* 2
* mutual authentication, key derivation
* 3
* 3
* Shared symmetric key distribution
* shared symmetric session key distribution (e.g., for AES encryption)
* same key derived at mobile, AS
* AS informs AP of the shared symmetric session
* style.visibility

---

### Slide 89: Security: 8-

* 89
* 802.11: authentication, encryption
* AP
* AS
* Authentication Server
* mobile
* wired network
* 1
* discovery of security capabilities
* 2
* 4
* mutual authentication, key derivation
* 3
* shared symmetric key distribution
* encrypted communication between mobile and remote host via AP
* same key derived at mobile, AS
* AS informs AP of the shared symmetric session
* 4
* encrypted communication over WiFi

---

### Slide 90: Security: 8-

* 90
* 802.11: authentication, encryption
* AP
* AS
* Authentication Server
* mobile
* wired network
* EAP TLS
* EAP
* EAP over LAN (EAPoL)
* IEEE 802.11
* RADIUS
* UDP/IP
* Extensible Authentication Protocol (EAP)
* [RFC 3748]
* defines end-to-end request/response protocol between mobile device, AS
* style.visibility

---

### Slide 91: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* 802.11 (WiFi)
* 4G/5G
* Operational security: firewalls and IDS
* Security: 8-
* 91

---

### Slide 92: Security: 8-

* 92
* Authentication, encryption in 4G LTE
* Visited network
* mobile
* Base station (BS)
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* arriving mobile must:
* associate with BS: (establish) communication over 4G wireless link
* authenticate
* itself to network, and authenticate network
* notable differences from WiFi
* mobile’s SIMcard provides global identity, contains shared keys
* services in visited network depend on (paid) service subscription in home network

---

### Slide 93: Security: 8-

* 93
* Authentication, encryption in 4G LTE
* mobile, BS use derived session key K
* BS-M
* to encrypt communications over 4G link
* MME in visited network + HHS in home network, together play role of WiFi AS
* ultimate authenticator is HSS
* trust and business relationship between visited and home networks
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M

---

### Slide 94: Security: 8-

* 94
* Authentication, encryption in 4G LTE
* a
* attach
* attach
* AUTH_REQ (IMSI, VN info)
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M
* authentication request to home network HSS
* mobile sends attach message (containing its IMSI, visited network info) relayed from BS to visited MME to home HHS
* IMSI identifies mobile’s home network
* a
* style.visibility
* style.visibility

---

### Slide 95: Security: 8-

* 95
* Authentication, encryption in 4G LTE
* HSS use shared-in-advance secret key, K
* HSS-M
* , to derive authentication token,
* auth_token
* , and expected authentication response token,
* xres
* HSS
* auth_token
* contains info encrypted by HSS using K
* HSS-M
* , allowing mobile to know that whoever computed
* auth_token
* knows shared-in-advance secret
* mobile has authenticated network
* visited HSS keeps
* xres
* HSS
* for later use
* b
* b
* AUTH_RESP (auth token,xres
* HSS
* ,keys)
* auth token
* auth token
* a
* attach
* attach
* AUTH_REQ (IMSI, VN info)
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility
* style.visibility

---

### Slide 96: Security: 8-

* 96
* Authentication, encryption in 4G LTE
* authentication response from mobile:
* mobile computes
* res
* M
* using its secret key to make same cryptographic calculation that HSS made to compute
* xres
* HSS
* and sends
* res
* M
* to MME
* c
* b
* AUTH_RESP (auth token,xres
* HSS
* ,keys)
* auth token
* auth token
* a
* attach
* attach
* AUTH_REQ (IMSI, VN info)
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M
* res
* M
* c
* style.visibility
* style.visibility

---

### Slide 97: Security: 8-

* 97
* Authentication, encryption in 4G LTE
* mobile is authenticated by network:
* MMS compares mobile-computed value of
* res
* M
* with the HSS-computed value of
* xres
* HSS
* . If they match, mobile is authenticated ! (why?)
* MMS informs BS that mobile is authenticated, generates keys for BS
* d
* b
* AUTH_RESP (auth token,xres
* HSS
* ,keys)
* auth token
* auth token
* a
* attach
* attach
* AUTH_REQ (IMSI, VN info)
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M
* res
* M
* c
* d
* OK, keys
* OK
* style.visibility
* style.visibility
* style.visibility

---

### Slide 98: Security: 8-

* 98
* Authentication, encryption in 4G LTE
* b
* AUTH_RESP (auth token,xres
* HSS
* ,keys)
* auth token
* auth token
* a
* attach
* attach
* AUTH_REQ (IMSI, VN info)
* Base station (BS)
* Visited network
* mobile
* Mobility Management Entity (
* MME
* )
* Home network
* Home Subscriber Service (
* HSS
* )
* K
* HSS-M
* K
* BS-M
* K
* HSS-M
* res
* M
* c
* d
* OK, keys
* OK
* e
* key derivation
* e
* mobile, BS determine keys for encrypting data, control frames over 4G wireless channel
* AES can be used
* style.visibility

---

### Slide 99: 4G

* : MME in visited network makes authentication decision
* 5G:
* home network provides authentication decision
* visited MME plays “middleman” role but can still reject
* Security: 8-
* 99
* Authentication, encryption: from 4G to 5G
* 4G:
* uses shared-in-advance keys
* 5G:
* keys not shared in advance for IoT
* 4G:
* device IMSI transmitted in cleartext to BS
* 5G:
* public key crypto used to encrypt IMSI
* style.visibility
* style.visibility

---

### Slide 100: Chapter 8 outline

* What is network security?
* Principles of cryptography
* Authentication,
* message integrity
* Securing e-mail
* Securing TCP connections: TLS
* Network layer security: IPsec
* Security in wireless and mobile networks
* Operational security: firewalls and IDS
* Security: 8-
* 100

---

### Slide 101: Security: 8-

* 101
* Firewalls
* isolates organization’
* s internal network from larger Internet, allowing some packets to pass, blocking others
* administered
* network
* public
* Inter
* net
* firewall
* trusted “good guys”
* untrusted “bad guys”
* firewall

---

### Slide 102: Security: 8-

* 102
* Firewalls: why
* prevent denial of service attacks:
* SYN flooding: attacker establishes many bogus TCP connections, no resources left for
* “
* real
* ”
* connections
* prevent illegal modification/access of internal data
* e.g., attacker replaces CIA
* ’
* s homepage with something else
* allow only authorized access to inside network
* set of authenticated users/hosts
* three types of firewalls:
* stateless packet filters
* stateful packet filters
* application gateways

---

### Slide 103: Security: 8-

* 103
* Stateless packet filtering
* Should arriving packet be allowed in? Departing packet let out?
* internal network connected to Internet via router
* firewall
* filters
* packet-by-packet
* ,
* decision to forward/drop packet based on
* :
* source IP address, destination IP address
* TCP/UDP source, destination port numbers
* ICMP message type
* TCP SYN, ACK bits

---

### Slide 104: Security: 8-

* 104
* Stateless packet filtering: example
* Should arriving packet be allowed in? Departing packet let out?
* example 1:
* block incoming and outgoing datagrams with IP protocol field = 17 and with either source or dest port = 23
* result:
* all incoming, outgoing UDP flows and telnet connections are blocked
* example 2:
* block inbound TCP segments with ACK=0
* result:
* prevents external clients from making TCP connections with internal clients, but allows internal clients to connect to outside
* style.visibility
* style.visibility

---

### Slide 105: Security: 8-

* 105
* Stateless packet filtering: more examples
* Policy
* Firewall Setting
* no outside Web access
* drop all outgoing packets to any IP address, port 80
* no incoming TCP connections, except those for institution
* ’
* s public Web server only.
* drop all incoming TCP SYN packets to any IP except 130.207.244.203, port 80
* prevent Web-radios from eating up the available bandwidth.
* drop all incoming UDP packets - except DNS and router broadcasts.
* prevent your network from being used for a smurf DoS attack.
* drop all ICMP packets going to a
* “
* broadcast
* ”
* address (e.g. 130.207.255.255)
* prevent your network from being tracerouted
* drop all outgoing ICMP TTL expired traffic

---

### Slide 106: Security: 8-

* 106
* Access Control Lists
* action
* source
* address
* dest
* address
* protocol
* source
* port
* dest
* port
* flag
* bit
* allow
* 222.22/16
* outside of
* 222.22/16
* TCP
* > 1023
* 80
* any
* allow
* outside of
* 222.22/16
* 222.22/16
* TCP
* 80
* > 1023
* ACK
* allow
* 222.22/16
* outside of
* 222.22/16
* UDP
* > 1023
* 53
* ---
* allow
* outside of
* 222.22/16
* 222.22/16
* UDP
* 53
* > 1023
* ----
* deny
* all
* all
* all
* all
* all
* all
* ACL:
* table of rules, applied top to bottom to incoming packets: (action, condition) pairs: looks like OpenFlow forwarding (Ch. 4)!

---

### Slide 107: Security: 8-

* 107
* Stateful packet filtering
* stateless packet filter
* :
* heavy handed tool
* admits packets that “
* make no sense,” e.g., dest port = 80, ACK bit set, even though no TCP connection established:
* action
* source
* address
* dest
* address
* protocol
* source
* port
* dest
* port
* flag
* bit
* allow
* outside of
* 222.22/16
* 222.22/16
* TCP
* 80
* > 1023
* ACK
* stateful packet filter:
* track status of every TCP connection
* track connection setup (SYN), teardown (FIN): determine whether incoming, outgoing packets
* “makes sense”
* timeout inactive connections at firewall: no longer admit packets

---

### Slide 108: Security: 8-

* 108
* Stateful packet filtering
* action
* source
* address
* dest
* address
* proto
* source
* port
* dest
* port
* flag
* bit
* check connection
* allow
* 222.22/16
* outside of
* 222.22/16
* TCP
* > 1023
* 80
* any
* allow
* outside of
* 222.22/16
* 222.22/16
* TCP
* 80
* > 1023
* ACK
* x
* allow
* 222.22/16
* outside of
* 222.22/16
* UDP
* > 1023
* 53
* ---
* allow
* outside of
* 222.22/16
* 222.22/16
* UDP
* 53
* > 1023
* ----
* x
* deny
* all
* all
* all
* all
* all
* all
* ACL augmented to indicate need to check connection state table before admitting packet

---

### Slide 109: Security: 8-

* 109
* Application gateways
* filter packets on application data as well as on IP/TCP/UDP fields.
* example:
* allow select internal users to telnet outside
* 1.
* require all telnet users to telnet through gateway.
* 2.
* for authorized users, gateway sets up telnet connection to dest host
* gateway relays data between 2 connections
* 3.
* router filter blocks all telnet connections not originating from gateway
* application
* gateway
* host-to-gateway
* telnet session
* router and filter
* gateway-to-remote
* host telnet session

---

### Slide 110: Security: 8-

* 110
* Limitations of firewalls, gateways
* IP spoofing:
* router can
* ’t know if data “really” comes from claimed source
* if multiple app
* s need special treatment, each has own app. gateway
* client software must know how to contact gateway
* e.g., must set IP address of proxy in Web browser
* filters often use all or nothing policy for UDP
* tradeoff:
* degree of communication with outside world, level of security
* many highly protected sites still suffer from attacks

---

### Slide 111: Security: 8-

* 111
* Intrusion detection systems
* packet filtering:
* operates on TCP/IP headers only
* no correlation check among sessions
* IDS: intrusion detection system
* deep packet inspection:
* look at packet contents (e.g., check character strings in packet against database of known virus, attack strings)
* examine correlation
* among multiple packets
* port scanning
* network mapping
* DoS attack

---

### Slide 112: Security: 8-

* 112
* Intrusion detection systems
* Web
* server
* FTP
* server
* DNS
* server
* Internet
* demilitarized
* zone
* firewall
* IDS
* sensors
* multiple IDSs: different types of checking at different locations
* internal
* network

---

### Slide 113: Security: 8-

* 113
* Network Security (summary)
* basic techniques…...
* cryptography (symmetric and public key)
* message integrity
* end-point authentication
* …. used in many different security scenarios
* secure email
* secure transport (TLS)
* IP sec
* 802.11, 4G/5G
* operational security: firewalls and IDS

---

