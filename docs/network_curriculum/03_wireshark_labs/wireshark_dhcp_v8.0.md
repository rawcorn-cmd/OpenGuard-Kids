# Thực Hành Mạng: Wireshark_DHCP_v8.0

> **Nguồn gốc:** Wireshark Lab (Kurose & Ross Top-Down Approach)
> **File PDF gốc:** `/home/cornar/Computer-Network/Computer-Networking-a-Top-Down-Approach/labs/Wireshark_DHCP_v8.0.pdf`

---

### Trang 1

Wireshark Lab:
DHCP v8.0
Supplement to Computer Networking: A Top-Down
Approach, 8th ed., J.F. Kurose and K.W. Ross
“Tell me and I forget. Show me and I remember. Involve me
and I understand.” Chinese proverb
© 2005-2020, J.F Kurose and K.W. Ross, All Rights Reserved

In this lab, we’ll take a quick look at DHCP. DHCP is covered in Section 4.4.3 of the
text1. Recall that DHCP is used extensively in corporate, university and home-network
wired and wireless LANs to dynamically assign IP addresses to hosts (as well as to
configure other network configuration information).
This lab is brief, as we’ll only examine the DHCP packets captured by a host. If you also
have administrative access to your DHCP server, you may want to repeat this lab after
making some configuration changes (such as the lease time). If you have a router at
home, you most likely can configure your DHCP server. Because many linux/Unix
machines (especially those that serve many users) have a static IP address and because
manipulating DHCP on such machines typically requires super-user privileges, we’ll only
present a Windows version of this lab below.

DHCP Experiment
In order to observe DHCP in action, we’ll perform several DHCP-related commands and
capture the DHCP messages exchanged as a result of executing these commands. Do the
following2:
1. Begin by opening the Windows Command Prompt application (which can be
found in your Accessories folder). As shown in Figure 1, enter
“ipconfig /release”. The executable for ipconfig is in C:\windows\system32. This
command releases your current IP address, so that your host’s IP address becomes
0.0.0.0.
1

References to figures and sections are for the 8th edition of our text, Computer Networks, A Top-down
Approach, 8th ed., J.F. Kurose and K.W. Ross, Addison-Wesley/Pearson, 2020.
2
If you are unable to run Wireshark live on a computer, you can download the zip file
http://gaia.cs.umass.edu/wireshark-labs/wireshark-traces.zip and extract the file dhcp-ethereal-trace-1. The
traces in this zip file were collected by Wireshark running on one of the author’s computers, while
performing the steps indicated in the Wireshark lab. Once you have downloaded the trace, you can load it
into Wireshark and view the trace using the File pull down menu, choosing Open, and then selecting the
dhcp-ethereal-trace-1 trace file. You can then use this trace file to answer the questions below.

### Trang 2

2. Start up the Wireshark packet sniffer, as described in the introductory Wireshark
lab and begin Wireshark packet capture.
3. Now go back to the Windows Command Prompt and enter “ipconfig /renew”.
This instructs your host to obtain a network configuration, including a new IP
address. In Figure 1, the host obtains the IP address 192.168.1.108
4. Wait until the “ipconfig /renew” has terminated. Then enter the same command
“ipconfig /renew” again.
5. When the second “ipconfig /renew” terminates, enter the command
“ipconfig/release” to release the previously-allocated IP address to your computer.
6. Finally, enter “ipconfig /renew” to again be allocated an IP address for your
computer.
7. Stop Wireshark packet capture.

### Trang 3

Figure 1 Command Prompt window showing sequence of ipconfig commands that you
should enter.

### Trang 4

Now let’s take a look at the resulting Wireshark window. To see only the DHCP packets,
enter into the filter field “bootp”. (DHCP derives from an older protocol called BOOTP.
Both BOOTP and DHCP use the same port numbers, 67 and 68. To see DHCP packets in
the current version of Wireshark, you need to enter “bootp” and not “dhcp” in the filter.)
We see from Figure 2 that the first ipconfig renew command caused four DHCP packets
to be generated: a DHCP Discover packet, a DHCP Offer packet, a DHCP Request
packet, and a DHCP ACK packet.

Figure 2 Wireshark window with first DHCP packet – the DHCP Discover packet –
expanded.

### Trang 5

What to Hand In:
You should hand in a screen shot of the Command Prompt window similar to Figure 1
above. Whenever possible, when answering a question below, you should hand in a
printout of the packet(s) within the trace that you used to answer the question asked.
Annotate the printout3 to explain your answer. To print a packet, use File->Print, choose
Selected packet only, choose Packet summary line, and select the minimum amount of
packet detail that you need to answer the question.
Answer the following questions:
1. Are DHCP messages sent over UDP or TCP?
2. Draw a timing datagram illustrating the sequence of the first four-packet
Discover/Offer/Request/ACK DHCP exchange between the client and server. For
each packet, indicated the source and destination port numbers. Are the port
numbers the same as in the example given in this lab assignment?
3. What is the link-layer (e.g., Ethernet) address of your host?
4. What values in the DHCP discover message differentiate this message from the
DHCP request message?
5. What is the value of the Transaction-ID in each of the first four
(Discover/Offer/Request/ACK) DHCP messages? What are the values of the
Transaction-ID in the second set (Request/ACK) set of DHCP messages? What is
the purpose of the Transaction-ID field?
6. A host uses DHCP to obtain an IP address, among other things. But a host’s IP
address is not confirmed until the end of the four-message exchange! If the IP
address is not set until the end of the four-message exchange, then what values are
used in the IP datagrams in the four-message exchange? For each of the four
DHCP messages (Discover/Offer/Request/ACK DHCP), indicate the source and
destination IP addresses that are carried in the encapsulating IP datagram.
7. What is the IP address of your DHCP server?
8. What IP address is the DHCP server offering to your host in the DHCP Offer
message? Indicate which DHCP message contains the offered DHCP address.
9. In the example screenshot in this assignment, there is no relay agent between the
host and the DHCP server. What values in the trace indicate the absence of a relay
agent? Is there a relay agent in your experiment? If so what is the IP address of
the agent?
10. Explain the purpose of the router and subnet mask lines in the DHCP offer
message.
11. In the DHCP trace file noted in footnote 2, the DHCP server offers a specific IP
address to the client (see also question 8. above). In the client’s response to the

3

What do we mean by “annotate”? If you hand in a paper copy, please highlight where in the printout
you’ve found the answer and add some text (preferably with a colored pen) noting what you found in what
you ‘ve highlight. If you hand in an electronic copy, it would be great if you could also highlight and
annotate.

### Trang 6

first server OFFER message, does the client accept this IP address? Where in the
client’s RESPONSE is the client’s requested address?
12. Explain the purpose of the lease time. How long is the lease time in your
experiment?
13. What is the purpose of the DHCP release message? Does the DHCP server issue
an acknowledgment of receipt of the client’s DHCP request? What would happen
if the client’s DHCP release message is lost?
14. Clear the bootp filter from your Wireshark window. Were any ARP packets sent
or received during the DHCP packet-exchange period? If so, explain the purpose
of those ARP packets.

