# Thực Hành Mạng: Wireshark_SSL_v8.0

> **Nguồn gốc:** Wireshark Lab (Kurose & Ross Top-Down Approach)
> **File PDF gốc:** `/home/cornar/Computer-Network/Computer-Networking-a-Top-Down-Approach/labs/Wireshark_SSL_v8.0.pdf`

---

### Trang 1

Wireshark Lab:
SSL v8.0
Supplement to Computer Networking: A Top-Down
Approach, 8th ed., J.F. Kurose and K.W. Ross
“Tell me and I forget. Show me and I remember. Involve me and I
understand.” Chinese proverb
© 2005-2020, J.F Kurose and K.W. Ross, All Rights Reserved

In this lab, we’ll investigate the Secure Sockets Layer (SSL) protocol, focusing on the
SSL records sent over a TCP connection. We’ll do so by analyzing a trace of the SSL
records sent between your host and an e-commerce server. We’ll investigate the various
SSL record types as well as the fields in the SSL messages. You may want to review
Section 8.6 in the text1. We are currently developing a Wireshark Lab that will cover
TLS – whose treatment in the 8th edition of our text replaces the coverage of SSL.

1

References to figures and sections for this SSL lab are for the 7th edition of our text, Computer Networks,
A Top-down Approach, 7th ed., J.F. Kurose and K.W. Ross, Addison-Wesley/Pearson, 2016.

### Trang 2

1. Capturing packets in an SSL session
The first step is to capture the packets in an SSL session. To do this, you should go to
your favorite e-commerce site and begin the process of purchasing an item (but
terminating before making the actual purpose!). After capturing the packets with
Wireshark, you should set the filter so that it displays only the Ethernet frames that
contain SSL records sent from and received by your host. (An SSL record is the same
thing as an SSL message.) You should obtain something like screenshot on the previous
page.
If you have difficulty creating a trace, you should download the zip file
http://gaia.cs.umass.edu/wireshark-labs/wireshark-traces.zip and extract the ssl-etherealtrace-1 packet trace.

2. A look at the captured trace
Your Wireshark GUI should be displaying only the Ethernet frames that have SSL
records. It is important to keep in mind that an Ethernet frame may contain one or more
SSL records. (This is very different from HTTP, for which each frame contains either one
complete HTTP message or a portion of a HTTP message.) Also, an SSL record may not

### Trang 3

completely fit into an Ethernet frame, in which case multiple frames will be needed to
carry the record.
Whenever possible, when answering a question below, you should hand in a printout of
the packet(s) within the trace that you used to answer the question asked. Annotate the
printout2 to explain your answer. To print a packet, use File->Print, choose Selected
packet only, choose Packet summary line, and select the minimum amount of packet
detail that you need to answer the question
1. For each of the first 8 Ethernet frames, specify the source of the frame (client or
server), determine the number of SSL records that are included in the frame, and
list the SSL record types that are included in the frame. Draw a timing diagram
between client and server, with one arrow for each SSL record.
2. Each of the SSL records begins with the same three fields (with possibly different
values). One of these fields is “content type” and has length of one byte. List all
three fields and their lengths.
ClientHello Record:
3. Expand the ClientHello record. (If your trace contains multiple ClientHello
records, expand the frame that contains the first one.) What is the value of the
content type?
4. Does the ClientHello record contain a nonce (also known as a “challenge”)? If so,
what is the value of the challenge in hexadecimal notation?
5. Does the ClientHello record advertise the cyber suites it supports? If so, in the
first listed suite, what are the public-key algorithm, the symmetric-key algorithm,
and the hash algorithm?
ServerHello Record:
6. Locate the ServerHello SSL record. Does this record specify a chosen cipher
suite? What are the algorithms in the chosen cipher suite?
7. Does this record include a nonce? If so, how long is it? What is the purpose of the
client and server nonces in SSL?
8. Does this record include a session ID? What is the purpose of the session ID?
9. Does this record contain a certificate, or is the certificate included in a separate
record. Does the certificate fit into a single Ethernet frame?
Client Key Exchange Record:

2

What do we mean by “annotate”? If you hand in a paper copy, please highlight where in the printout
you’ve found the answer and add some text (preferably with a colored pen) noting what you found in what
you ‘ve highlight. If you hand in an electronic copy, it would be great if you could also highlight and
annotate.

### Trang 4

10. Locate the client key exchange record. Does this record contain a pre-master
secret? What is this secret used for? Is the secret encrypted? If so, how? How long
is the encrypted secret?
Change Cipher Spec Record (sent by client) and Encrypted Handshake Record:
11. What is the purpose of the Change Cipher Spec record? How many bytes is the
record in your trace?
12. In the encrypted handshake record, what is being encrypted? How?
13. Does the server also send a change cipher record and an encrypted handshake
record to the client? How are those records different from those sent by the client?
Application Data
14. How is the application data being encrypted? Do the records containing
application data include a MAC? Does Wireshark distinguish between the
encrypted application data and the MAC?
15. Comment on and explain anything else that you found interesting in the trace.

