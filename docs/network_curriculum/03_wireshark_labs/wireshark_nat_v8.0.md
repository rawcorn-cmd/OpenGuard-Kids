# Thực Hành Mạng: Wireshark_NAT_v8.0

> **Nguồn gốc:** Wireshark Lab (Kurose & Ross Top-Down Approach)
> **File PDF gốc:** `/home/cornar/Computer-Network/Computer-Networking-a-Top-Down-Approach/labs/Wireshark_NAT_v8.0.pdf`

---

### Trang 1

Wireshark Lab:
NAT v8.0
Supplement to Computer Networking: A Top-Down
Approach, 8th ed., J.F. Kurose and K.W. Ross
“Tell me and I forget. Show me and I remember. Involve me
and I understand.” Chinese proverb
© 2005-2020, J.F Kurose and K.W. Ross, All Rights Reserved

In this lab, we’ll investigate the behavior of the NAT protocol. This lab will be different
from our other Wireshark labs, where we’ve captured a trace file at a single Wireshark
measurement point. Because we’re interested in capturing packets at both the input and
output sides of the NAT device, we’ll need to capture packets at two locations. Also,
because many students don’t have easy access to a NAT device or to two computers on
which to take Wireshark measurements, this isn’t a lab that is easily done “live” by a
student. Therefore in this lab, you will use Wireshark trace files that we’ve captured for
you. Before beginning this lab, you’ll probably want to review the material on NAT
section 4.3.4 in the text1.

1. NAT Measurement Scenario
In this lab, we’ll capture
home network
packets from a simple web
ISP network
NAT router
request from a client PC in a
home network to a
www.google.com server.
Within the home network,
the home network router
trace file: NAT_home_side
trace file: NAT_ISP_side
provides a NAT service, as
discussed in Chapter 4.
Figure 1: NAT trace collection scenario
Figure 1 shows our
Wireshark trace-collection scenario. As in our other Wireshark labs, we collect a
Wireshark trace on the client PC in our home network. This file is called
NAT_home_side2. Because we are also interested in the packets being sent by the NAT
1

References to figures and sections are for the 8th edition of our text, Computer Networks, A Top-down
Approach, 8th ed., J.F. Kurose and K.W. Ross, Addison-Wesley/Pearson, 202o.
2
Download the zip file http://gaia.cs.umass.edu/wireshark-labs/wireshark-traces.zip and extract the files
need for this lab.

### Trang 2

router into the ISP, we’ll collect a second trace file at a PC (not shown) tapping into the
link from the home router into the ISP network, as shown in Figure 1. (The hub device
shown on the ISP side of the router is used to tap into the link between the NAT router
and the first hop router in the ISP). Client-to-server packets captured by Wireshark at
this point will have undergone NAT translation. The Wireshark trace file captured on the
ISP side of the home router is called NAT_ISP_side.
Open the NAT_home_side file and answer the following questions. You might find it
useful to use a Wireshark filter so that only frames containing HTTP messages are
displayed from the trace file.
Whenever possible, when answering a question below, you should hand in a printout of
the packet(s) within the trace that you used to answer the question asked. Annotate the
printout3 to explain your answer. To print a packet, use File->Print, choose Selected
packet only, choose Packet summary line, and select the minimum amount of packet
detail that you need to answer the question
1. What is the IP address of the client?
2. The client actually communicates with several different Google servers in order to
implement “safe browsing.” (See extra credit section at the end of this lab). The
main Google server that will serve up the main Google web page has IP address
64.233.169.104. In order to display only those frames containing HTTP messages
that are sent to/from this Google, server, enter the expression “http && ip.addr ==
64.233.169.104” (without quotes) into the Filter: field in Wireshark .
3. Consider now the HTTP GET sent from the client to the Google server (whose IP
address is IP address 64.233.169.104) at time 7.109267. What are the source and
destination IP addresses and TCP source and destination ports on the IP datagram
carrying this HTTP GET?
4. At what time4 is the corresponding 200 OK HTTP message received from the
Google server? What are the source and destination IP addresses and TCP source
and destination ports on the IP datagram carrying this HTTP 200 OK message?
5. Recall that before a GET command can be sent to an HTTP server, TCP must first
set up a connection using the three-way SYN/ACK handshake. At what time is
the client-to-server TCP SYN segment sent that sets up the connection used by
the GET sent at time 7.109267? What are the source and destination IP addresses
and source and destination ports for the TCP SYN segment? What are the source
and destination IP addresses and source and destination ports of the ACK sent in
response to the SYN. At what time is this ACK received at the client? (Note: to
find these segments you will need to clear the Filter expression you entered above
in step 2. If you enter the filter “tcp”, only TCP segments will be displayed by
Wireshark).
3

What do we mean by “annotate”? If you hand in a paper copy, please highlight where in the printout
you’ve found the answer and add some text (preferably with a colored pen) noting what you found in what
you ‘ve highlight. If you hand in an electronic copy, it would be great if you could also highlight and
annotate.
4
Specify time using the time since the beginning of the trace (rather than absolute, wall-clock time).

### Trang 3

In the following we’ll focus on the two HTTP messages (GET and 200 OK) and the TCP
SYN and ACK segments identified above. Our goal below will be to locate these two
HTTP messages and two TCP segments in the trace file (NAT_ISP_side) captured on the
link between the router and the ISP. Because these captured frames will have already
been forwarded through the NAT router, some of the IP address and port numbers will
have been changed as a result of NAT translation.
Open the NAT_ISP_side. Note that the time stamps in this file and in NAT_home_side
are not synchronized since the packet captures at the two locations shown in Figure 1
were not started simultaneously. (Indeed, you should discover that the timestamps of a
packet captured at the ISP link is actually less that the timestamp of the packet captured
at the client PC).
6. In the NAT_ISP_side trace file, find the HTTP GET message was sent from the
client to the Google server at time 7.109267 (where t=7.109267 is time at which
this was sent as recorded in the NAT_home_side trace file). At what time does
this message appear in the NAT_ISP_side trace file? What are the source and
destination IP addresses and TCP source and destination ports on the IP datagram
carrying this HTTP GET (as recording in the NAT_ISP_side trace file)? Which
of these fields are the same, and which are different, than in your answer to
question 3 above?
7. Are any fields in the HTTP GET message changed? Which of the following fields
in the IP datagram carrying the HTTP GET are changed: Version, Header Length,
Flags, Checksum. If any of these fields have changed, give a reason (in one
sentence) stating why this field needed to change.
8. In the NAT_ISP_side trace file, at what time is the first 200 OK HTTP message
received from the Google server? What are the source and destination IP
addresses and TCP source and destination ports on the IP datagram carrying this
HTTP 200 OK message? Which of these fields are the same, and which are
different than your answer to question 4 above?
9. In the NAT_ISP_side trace file, at what time were the client-to-server TCP SYN
segment and the server-to-client TCP ACK segment corresponding to the
segments in question 5 above captured? What are the source and destination IP
addresses and source and destination ports for these two segments? Which of
these fields are the same, and which are different than your answer to question 5
above?
Figure 4.25 in the text shows the NAT translation table in the NAT router.
10. Using your answers to 1-8 above, fill in the NAT translation table entries for
HTTP connection considered in questions 1-8 above.
Extra Credit: The trace files investigated above have additional connections to Google
servers above and beyond the HTTP GET, 200 OK request/response studied above. For
example, in the NAT_home_side trace file, consider the client-to-server GET at time

### Trang 4

1.572315, and the GET at time 7.573305. Research the use of these two HTTP messages
and write a half page explanation of the purpose of each of these messages.

