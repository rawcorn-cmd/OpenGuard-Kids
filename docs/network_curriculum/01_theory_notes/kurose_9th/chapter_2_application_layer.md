# Chương 2: Application Layer
> **Giáo trình:** Computer Networking: A Top-Down Approach (9th Edition, 2026)  
> **Tác giả:** Jim Kurose, Keith Ross — Pearson Education  
> **Số trang bản gốc:** PDF trang 97 – 181 (Độ dài: 85 trang)  

---

> [!NOTE] ỨNG DỤNG TRỰC TIẾP VÀO ĐỒ ÁN OPENGUARD KIDS
> **Mục tiêu học tập & Áp dụng thực tiễn:**  
> Giao thức DNS (Port 53), HTTP/1.1/2/3, CNAME record rewrite cho SafeSearch, Web Caching, và kiến trúc Client-Server / P2P — Trọng tâm đồ án OpenGuard Kids (DNS Proxy & Web Dashboard).

---

Application Layer

Network applications are the raisons d’être of a computer network—if we
couldn’t conceive of any useful applications, there wouldn’t be any need for
networking infrastructure and protocols to support them. Since the Internet’s inception, many useful and entertaining applications have indeed been
created. These applications have been the driving force behind the Internet’s
success, used by people in homes, cars, schools, governments, and businesses
to make the Internet an integral part of their daily activities.
Internet applications include the classic text-based applications that
became popular in the 1970s and 1980s: text e-mail, remote access to computers, file transfers, and newsgroups. They include the killer application of the
mid-1990s, the World Wide Web, encompassing Web surfing, search, and electronic commerce. Since the beginning of new millennium, new and highly
compelling applications continue to emerge, including video conferencing
such as Zoom, Facetime, and Teams; user generated video such as YouTube;
and movies on demand such as Netflix; and multiplayer online games such as
Second Life and World of Warcraft. During this same period, we have seen the
emergence of a new generation of social networking applications—such as



TikTok, Facebook, Instagram, and X—which have created human networks on
top of the Internet’s network or routers and communication links. And most
recently, along with the arrival of the smartphone and the ubiquity of 4G/5G
wireless Internet access, there has been a profusion of location based mobile
apps, including popular check-in, dating, and road-traffic forecasting apps
(such as Yelp, Tinder, and Waze), mobile payment apps (such as WeChat and
Apple Pay) and messaging apps (such as WeChat and WhatsApp). Clearly,
there has been no slowing down of new and exciting Internet applications. Perhaps some of the readers of this text will create the next generation of killer
Internet applications!
In this chapter, we study the conceptual and implementation aspects of
network applications. We begin by defining key application-layer concepts,
including network services required by applications, clients and servers, processes, and transport-layer interfaces. We examine several network applications
in detail, including the Web, e-mail, DNS, and video streaming. We then cover
network application development, over both TCP and UDP. In particular, we
study the socket interface and walk through some simple client-server applications in Python. We also provide several fun and interesting socket
programming assignments at the end of the chapter.
The application layer is a particularly good place to start our study of protocols. It’s familiar ground. We’re acquainted with many of the applications
that rely on the protocols we’ll study. It will give us a good feel for what protocols are all about and will introduce us to many of the same issues that we’ll
see again when we study transport, network, and link layer protocols.


## 2.1 Principles of Network

Applications
Suppose you have an idea for a new network application. Perhaps this application will be a great service to humanity, or will please your professor, or will
bring you great wealth, or will simply be fun to develop and use. Whatever the
motivation may be, let’s now examine how you transform the idea into a realworld network application.
At the core of network application development is writing programs that
run on different end systems and communicate with each other over the network. For example, in the Web application there are two distinct programs that
communicate with each other: the browser program running in the user’s host
(desktop, laptop, tablet, smartphone, and so on); and the Web server program
running in the Web server host. As another example, in a Video on Demand
application such as Netflix (see Section 2.5), there is a Netflix-provided program running on the user’s smartphone, tablet, computer, or TV; and a Netflix
server program running on the Netflix server host. Servers often (but not
always) are housed in a data center, as shown in Figure 2.1.
Thus, when developing your new application, you need to write software
that will run on multiple end systems. This software could be written, for
example, in C, Java, or Python. Importantly, you do not need to write software


Application Layer

Figure 2.1 Communication for a network application takes place between end systems at the
application layer

that runs on network-core devices, such as routers or link-layer switches.
Indeed, even if you wanted to write application software for these networkcore devices, you wouldn’t be able to do so. As we learned in Chapter 1, and as
shown earlier in Figure 1.25, network-core devices do not function at the application layer but instead function at lower layers—specifically at the network
layer and below. This basic design—namely, confining application software to
the end systems—as shown in Figure 2.1, has facilitated the rapid development and deployment of a vast array of network applications.





### 2.1.1 Network Application Architectures

Before diving into software coding, you should have a broad architectural plan
for your application. Keep in mind that an application’s architecture is distinctly different from the network architecture (e.g., the five-layer Internet
architecture discussed in Chapter 1). From the application developer’s perspective, the network architecture is fixed and provides a specific set of services
to applications. The application architecture, on the other hand, is designed
by the application developer and dictates how the application is structured
over the various end systems. In choosing the application architecture, an
application developer will likely draw on one of the two predominant architectural paradigms used in modern network applications: the client-server
architecture or the peer-to-peer ( P2P ) architecture.
In a client-server architecture, there is an always-on host, called the server,
which services requests from many other hosts, called clients. A classic example
is the Web application for which an always-on Web server services requests
from browsers running on client hosts. When a Web server receives a request
for an object from a client host, it responds by sending the requested object to
the client host. Note that with the client-server architecture, clients do not
directly communicate with each other; for example, in the Web application, two
browsers do not directly communicate. Another characteristic of the clientserver architecture is that the server has a fixed, well-known address, called an
IP address (which we’ll discuss soon). Because the server has a fixed, wellknown address, and because the server is always on, a client can always contact
the server by sending a packet to the server’s IP address. Some of the betterknown applications with a client-server architecture include the Web, e-mail,
and video streaming. The client-server architecture is shown in Figure 2.2(a).
Often in a client-server application, a single-server host is incapable of
keeping up with all the requests from clients. For example, a popular socialnetworking site can quickly become overwhelmed if it has only one server
handling all of its requests. For this reason, a data center, housing a large number of hosts, is often used to create a powerful virtual server. The most popular
Internet services—such as generative AI (chatbots, text to image/video, and so on),
search engines (e.g., Google, Bing, Baidu), Internet commerce (e.g., Amazon,
eBay, Alibaba), Web-based e-mail (e.g., Gmail and Yahoo Mail), social media
(e.g., TikTok, Facebook, Instagram, X, and WeChat)—run in one or more data
centers. As discussed in Section 1.3.3, Google has more than 20 data centers
distributed around the world, which collectively handle search, YouTube,
Gmail, and other services. A data center can have hundreds of thousands of
servers, which must be powered and maintained. Additionally, the service
providers must pay recurring interconnection and bandwidth costs for sending data from their data centers.
In a P2P architecture, there is minimal (or no) reliance on dedicated servers in data centers. Instead the application exploits direct communication
between pairs of intermittently connected hosts, called peers. Peers are not
owned by a service provider, but are instead desktops and laptops controlled
by users, with most of the peers residing in homes, universities, and offices.
Because the peers communicate without passing through a dedicated server,


Application Layer

Figure 2.2 (a) Client-server architecture; (b) P2P architecture

the architecture is called peer-to-peer. An example of a popular P2P application is the file-sharing application BitTorrent.
One of the most compelling features of P2P architectures is their self-­
scalability. For example, in a P2P file-sharing application, although each peer
generates workload by requesting files, each peer also adds service capacity to
the system by distributing files to other peers. P2P architectures are also cost
effective, since they normally don’t require significant server infrastructure
and server bandwidth (in contrast with clients-server designs with datacenters). However, P2P applications face challenges of security, performance, and
reliability due to their highly decentralized structure. Because of these challenges, most applications today have a client-server architecture.


### 2.1.2 Processes Communicating

Before building your network application, you also need a basic understanding of how the programs, running in multiple end systems, communicate with
each other. In the jargon of operating systems, it is not actually programs but
processes that communicate. A process can be thought of as a program that is
running within an end system. When processes are running on the same end
system, they can communicate with each other with interprocess communication, using rules that are governed by the end system’s operating system. But
in this book, we are not particularly interested in how processes in the same
host communicate, but instead in how processes running on different hosts
(with potentially different operating systems) communicate.



Processes on two different end systems communicate with each other by
exchanging messages across the computer network. A sending process creates
and sends messages into the network; a receiving process receives these messages and possibly responds by sending messages back. Figure 2.1 illustrates
that processes communicating with each other reside in the application layer
of the five-layer protocol stack.

Client and Server Processes
A network application consists of pairs of processes that send messages to each
other over a network. For example, in the Web application a client browser
process exchanges messages with a Web server process. For each pair of communicating processes, we typically label one of the two processes as the client
and the other process as the server. With the Web, a browser is a client process
and a Web server is a server process. We define the client and server processes
as follows:

In the context of a communication session between a pair of
processes, the process that initiates the communication (that is,
initially contacts the other process at the beginning of the
­session) is labeled as the client. The process that waits to be
contacted to begin the session is the server.
For example, in the Web, a browser process initiates contact with a Web
server process; hence the browser process is the client and the Web server process is the server. When there’s no confusion, we’ll sometimes also use the
terminology “client side and server side of an application.” At the end of this
chapter, we’ll step through simple code for both the client and server sides of
network applications.

The Interface Between the Process
and the Computer Network
As noted above, most applications consist of pairs of communicating processes, with the two processes in each pair sending messages to each other.
Any message sent from one process to another must go through the underlying network. A process sends messages into, and receives messages from, the
network through a software interface called a socket. Let’s consider an analogy to help us understand processes and sockets. A process is analogous to a
house and its socket is analogous to its door. When a process wants to send a
message to another process on another host, it shoves the message out its door
(socket). This sending process assumes that there is a transportation infrastructure on the other side of its door that will transport the message to the door of
the destination process. Once the message arrives at the destination host, the
message passes through the receiving process’s door (socket), and the receiving process then acts on the message.
Figure 2.3 illustrates socket communication between two processes that
communicate over the Internet. (Figure 2.3 assumes that the underlying


Application Layer

Figure 2.3 Application processes, sockets, and underlying transport protocol

transport protocol used by the processes is the Internet’s TCP protocol.) As
shown in this figure, a socket is the interface between the application layer and
the transport layer within a host. It is also referred to as the Application
­Programming Interface (API) between the application and the network, since
the socket is the programming interface with which network applications are
built. The application developer has control of everything on the applicationlayer side of the socket but has little control of the transport-layer side of the
socket. The only control that the application developer has on the transportlayer side is (1) the choice of transport protocol and (2) perhaps the ability to
fix a few transport-layer parameters such as maximum buffer and maximum
segment sizes (to be covered in Chapter 3). Once the application developer
chooses a transport protocol (if a choice is available), the application is built
using the transport-layer services provided by that protocol. We’ll explore
sockets in some detail in Section 2.6.

Addressing Processes
In order to send postal mail to a particular destination, the destination needs to
have an address. Similarly, in order for a process running on one host to send
packets to a process running on another host, the receiving process needs to
have an address. To identify the receiving process, two pieces of information
need to be specified: (1) the address of the host and (2) an identifier that specifies the receiving process in the destination host.
In the Internet, the host is identified by its IP address. We’ll discuss IP
addresses in great detail in Chapter 4. For now, all we need to know is that an
IP address is a 32-bit quantity that we can think of as uniquely identifying the
host. In addition to knowing the address of the host to which a message is destined, the sending process must also identify the receiving process (more
specifically, the receiving socket) running in the host. This information is
needed because in general a host could be running many network applications. A destination port number serves this purpose. Popular applications



have been assigned specific port numbers. For example, a Web server is identified by port number 80. A mail server process (using the SMTP protocol) is
identified by port number 25. A list of well-known port numbers for all Internet standard protocols can be found at www.iana.org. We’ll examine port
numbers in detail in Chapter 3.


### 2.1.3 T

 ransport Services Available
to Applications
Recall that a socket is the interface between the application process and the
transport-layer protocol. The application at the sending side pushes messages through the socket. At the other side of the socket, the transport-layer
protocol has the responsibility of getting the messages to the socket of the
receiving process.
Many networks, including the Internet, provide more than one transportlayer protocol. When you develop an application, you must choose one of the
available transport-layer protocols. How do you make this choice? Most likely,
you would study the services provided by the available transport-layer protocols, and then pick the protocol with the services that best match your
application’s needs. The situation is similar to choosing either train or airplane
transport for travel between two cities. You have to choose one or the other, and
each transportation mode offers different services. (For example, the train offers
downtown pickup and drop-off, whereas the plane offers shorter travel time.)
What are the services that a transport-layer protocol can offer to applications invoking it? We can broadly classify the possible services along four
dimensions: reliable data transfer, throughput, timing, and security.

Reliable Data Transfer
As discussed in Chapter 1, packets can get lost within a computer network. For
example, a packet can overflow a buffer in a router, or can be discarded by a
host or router after having some of its bits corrupted. For many applications—
such as electronic mail, file transfer, Web document transfers, and financial
applications—data loss can have devastating consequences (in the latter case,
for either the bank or the customer!). Thus, to support these applications,
something has to be done to guarantee that the data sent by one end of the
application is delivered correctly and completely to the other end of the application. If a protocol provides such a guaranteed data delivery service, it is said
to provide reliable data transfer. One important service that a transport-layer
protocol can potentially provide to an application is process-to-process reliable
data transfer. When a transport protocol provides this service, the sending process can just pass its data into the socket and know with complete confidence
that the data will arrive without errors at the receiving process.
When a transport-layer protocol doesn’t provide reliable data transfer,
some of the data sent by the sending process may never arrive at the receiving
process. This may be acceptable for loss-tolerant applications, most notably
multimedia applications such as conversational audio/video that can tolerate


Application Layer

some amount of data loss. In these multimedia applications, lost data might
result in a small glitch in the audio/video—not a crucial impairment.

Throughput
In Chapter 1, we introduced the concept of available throughput, which, in the
context of a communication session between two processes along a network
path, is the rate at which the sending process can deliver bits to the receiving
process. Because other sessions will be sharing the bandwidth along the network path, and because these other sessions will be coming and going, the
available throughput can fluctuate with time. These observations lead to
another natural service that a transport-layer protocol could provide, namely,
guaranteed available throughput at some specified rate. With such a service,
the application could request a guaranteed throughput of r bits sec, and the
transport protocol would then ensure that the available throughput is always
at least r bits sec. Such a guaranteed throughput service would appeal to
many applications. For example, if an Internet telephony application encodes
voice at 32 kbps, it needs to send data into the network and have data delivered to the receiving application at this rate. If the transport protocol cannot
provide this throughput, the application would need to encode at a lower rate
(and receive enough throughput to sustain this lower coding rate) or may have
to give up, since receiving, say, half of the needed throughput is of little or no
use to this Internet telephony application. Applications that have throughput
requirements are said to be bandwidth-sensitive applications. Many current
multimedia applications are bandwidth sensitive, although some multimedia
applications may use adaptive coding techniques to encode digitized voice or
video at a rate that matches the currently available throughput.
While bandwidth-sensitive applications have specific throughput requirements, elastic applications can make use of as much, or as little, throughput as
happens to be available. Electronic mail, file transfer, and Web transfers are all
elastic applications. Of course, the more throughput, the better. There’s an adage
that says that one cannot be too rich, too thin, or have too much throughput!

Timing
A transport-layer protocol can also provide timing guarantees. As with
throughput guarantees, timing guarantees can come in many shapes and
forms. An example guarantee might be that every bit that the sender pumps
into the socket arrives at the receiver’s socket no more than 100 msec later.
Such a service would be appealing to interactive real-time applications, such as
Internet telephony, video conferencing, metaverses, and multiplayer games, all
of which require tight timing constraints on data delivery in order to be effective, see [Gauthier 1999; Ramjee 1994]. Long delays in Internet telephony, for
example, tend to result in unnatural pauses in the conversation; in a multiplayer game or virtual interactive metaverses, a long delay between taking an
action and seeing the response from the environment (for example, from
another player at the end of an end-to-end connection) makes the application
feel less realistic. For non-real-time applications, lower delay is always preferable to higher delay, but no tight constraint is placed on the end-to-end delays.




Security
Finally, a transport protocol can provide an application with one or more security services. For example, in the sending host, a transport protocol can encrypt
all data transmitted by the sending process, and in the receiving host, the
transport-layer protocol can decrypt the data before delivering the data to the
receiving process. Such a service would provide confidentiality between the
two processes, even if the data is somehow observed between sending and
receiving processes. A transport protocol can also provide other security services in addition to confidentiality, including data integrity and end-point
authentication, topics that we’ll cover in detail in Chapter 8.


### 2.1.4 Transport Services Provided by

the Internet
Up until this point, we have been considering transport services that a computer network could provide in general. Let’s now get more specific and
examine the type of transport services provided by the Internet. The Internet
(and, more generally, TCP/IP networks) makes two transport protocols available to applications, UDP and TCP. When you (as an application developer)
create a new network application for the Internet, one of the first decisions you
have to make is whether to use UDP or TCP. Each of these protocols offers a
different set of services to the invoking applications. Figure 2.4 shows the service requirements for some selected applications.

TCP Services
The TCP service model includes a connection-oriented service and a reliable
data transfer service. When an application invokes TCP as its transport protocol, the application receives both of these services from TCP.
* Connection-oriented service. TCP has the client and server exchange transport-layer control information with each other before the application-level
messages begin to flow. This so-called handshaking procedure alerts the

Figure 2.4

Requirements of selected
network applications


Application Layer

client and server, allowing them to prepare for an onslaught of packets.
After the handshaking phase, a TCP connection is said to exist between
the sockets of the two processes. The connection is a full-duplex connection in that the two processes can send messages to each other over the
connection at the same time. When the application finishes sending
­messages, it must tear down the connection. In Chapter 3, we’ll discuss
­connection-oriented service in detail and examine how it is implemented.
* Reliable data transfer service. The communicating processes can rely on TCP
to deliver all data sent without error and in the proper order. When one
side of the application passes a stream of bytes into a socket, it can count
on TCP to deliver the same stream of bytes to the receiving socket, with no
missing or duplicate bytes.
TCP also includes a congestion-control mechanism, a service for the general welfare of the Internet rather than for the direct benefit of the
communicating processes. The TCP congestion-control mechanism throttles a
sending process (client or server) when the network is congested between
sender and receiver. As we will see in Chapter 3, TCP congestion control also
attempts to limit each TCP connection to its fair share of network bandwidth.

UDP Services
UDP is a no-frills, lightweight transport protocol, providing minimal services.
UDP is connectionless, so there is no handshaking before the two processes
start to communicate. UDP provides an unreliable data transfer service—that
is, when a process sends a message into a UDP socket, UDP provides no guarantee that the message will ever reach the receiving process. Furthermore,
messages that do arrive at the receiving process may arrive out of order.

Focus on Security
Securing TCP
Neither TCP nor UDP provides any encryption—the data that the sending
process passes into its socket is the same data that travels over the network
to the destination process. So, for example, if the sending process sends a
password in cleartext (i.e., unencrypted) into its socket, the cleartext password
will travel over all the links between sender and receiver, potentially getting
sniffed and discovered at any of the intervening links. Because privacy and
other security issues have become critical for many applications, the Internet
community has developed an enhancement for TCP, called Transport Layer
Security (TLS) [RFC 5246]. TCP-enhanced-with-TLS not only does everything
that traditional TCP does but also provides critical process-to-process security
services, including encryption, data integrity, and end-point authentication.
We emphasize that TLS is not a third Internet transport protocol, on the
same level as TCP and UDP, but instead is an enhancement of TCP, with the
enhancements being implemented in the application layer. In particular, if an



application wants to use the services of TLS, it needs to include TLS code
(existing, highly optimized libraries and classes) in both the client and server
sides of the application. TLS has its own socket API that is similar to the
traditional TCP socket API. When an application uses TLS, the sending process
passes cleartext data to the TLS socket; TLS in the sending host then encrypts
the data and passes the encrypted data to the TCP socket. The encrypted
data travels over the Internet to the TCP socket in the receiving process. The
receiving socket passes the encrypted data to TLS, which decrypts the data.
Finally, TLS passes the cleartext data through its TLS socket to the receiving
process. We’ll cover TLS in some detail in Chapter 8.

UDP does not include a congestion-control mechanism, so the sending
side of UDP can pump data into the layer below (the network layer) at any rate
it pleases. (Note, however, that the actual end-to-end throughput may be less
than this rate due to the limited transmission capacity of intervening links or
due to congestion).

Services Not Provided by Internet Transport
Protocols
We have organized transport protocol services along four dimensions: reliable
data transfer, throughput, timing, and security. Which of these services are
provided by TCP and UDP? We have already noted that TCP provides reliable
end-to-end data transfer. And we also know that TCP can be easily enhanced
at the application layer with TLS to provide security services. But in our brief
description of TCP and UDP, conspicuously missing was any mention of
throughput or timing guarantees—services not provided by today’s Internet
transport protocols. Does this mean that time-sensitive applications such as
video conferencing cannot run in today’s Internet? The answer is clearly no—
the Internet has been hosting time-sensitive applications for many years. These
applications often work fairly well because they have been designed to cope,
to the greatest extent possible, with this lack of guarantee. Nevertheless, clever
design has its limitations when delay is excessive, or the end-to-end throughput is limited. In summary, today’s Internet can often provide satisfactory
service to time-sensitive applications, but it cannot provide any timing or
throughput guarantees.
Figure 2.5 indicates the transport protocols used by some popular Internet
applications. We see that e-mail, remote terminal access, the Web, and file
transfer all use TCP. These applications have chosen TCP primarily because
TCP provides reliable data transfer, guaranteeing that all data will eventually
get to its destination. Because video conferencing applications (such as Zoom)
can often tolerate some loss but require a minimal rate to be effective, developers of video conferencing applications usually prefer to run their applications
over UDP, thereby circumventing TCP’s congestion control mechanism and
packet overheads. But because many firewalls are configured to block (most
types of) UDP traffic, Internet telephony applications often are designed to use
TCP as a backup if UDP communication fails.


Application Layer

Figure 2.5 Popular
Internet applications,
their application-layer
protocols, and their
underlying transport
protocols


### 2.1.5 Application-Layer Protocols

We have just learned that network processes communicate with each other by
sending messages into sockets. But how are these messages structured? What
are the meanings of the various fields in the messages? When do the processes
send the messages? These questions bring us into the realm of applicationlayer protocols. An application-layer protocol defines how an application’s
processes, running on different end systems, pass messages to each other. In
particular, an application-layer protocol defines:
* The types of messages exchanged, for example, request messages and
response messages
* The syntax of the various message types, such as the fields in the message
and how the fields are delineated
* The semantics of the fields, that is, the meaning of the information in the
fields
* Rules for determining when and how a process sends messages and
responds to messages
Some application-layer protocols are specified in RFCs and are therefore
in the public domain. For example, the Web’s application-layer protocol, HTTP
(the HyperText Transfer Protocol [RFC 7230]), is available as an RFC. If a
browser developer follows the rules of the HTTP RFC, the browser will be able
to retrieve Web pages from any Web server that has also followed the rules of
the HTTP RFC. Many other application-layer protocols are proprietary and
intentionally not available in the public domain. For example, Zoom uses proprietary application-layer protocols.
It is important to distinguish between network applications and application-layer protocols. An application-layer protocol is only one piece of a
network application (albeit, a very important piece). Let’s look at a couple of
examples. The Web is a client-server application that allows users to obtain
documents from Web servers on demand. The Web application consists of
many components, including a standard for document formats (that is,
HTML), Web browsers (for example, Google Chrome and Microsoft Edge),
Web servers (for example, Apache and Microsoft servers), and an applicationlayer protocol. The Web’s application-layer protocol, HTTP, defines the format
and sequence of messages exchanged between browser and Web server. Thus,



HTTP is only one piece (albeit, a critical piece) of the Web application. As
another example, we’ll see in Section 2.5 that Netflix’s video service also has
many components, including servers that store and transmit videos, other
servers that manage billing and other client functions, clients (e.g., the Netflix
app on your smartphone, tablet, or computer), and an application-level DASH
protocol defines the format and sequence of messages exchanged between a
Netflix server and client. Thus, DASH is only one piece (albeit, a critical piece)
of the Netflix application.


### 2.1.6 Network Applications Covered

in This Book
New applications are being developed every day. Rather than covering a large
number of Internet applications in an encyclopedic manner, we have chosen to
focus on a small number of applications that are both pervasive and important.
In this chapter, we discuss four important applications: the Web, electronic
mail, directory service, and video streaming. We first discuss the Web, not only
because it is an enormously popular application, but also because its application-layer protocol, HTTP, is relatively straightforward and easy to understand.
We then discuss electronic mail, the Internet’s first killer application. E-mail is
more complex than the Web in the sense that it makes use of not one but several application-layer protocols. After e-mail, we cover DNS, which provides a
directory service for the Internet. Most users do not interact with DNS directly;
instead, users invoke DNS indirectly through other applications (including the
Web, file transfer, and electronic mail). DNS illustrates nicely how a piece of
core network functionality (network-name to network-address translation) can
be implemented at the application layer in the Internet. We complete our application study by discussing video streaming on demand, including distributing
stored video over content distribution networks.


## 2.2 The Web and HTTP

Until the early 1990s, the Internet was used primarily by researchers, academics, and university students to log in to remote hosts, to transfer files from local
hosts to remote hosts and vice versa, to receive and send news, and to receive
and send electronic mail. Although these applications were (and continue to
be) extremely useful, the Internet was essentially unknown outside of the academic and research communities. Then, in the early 1990s, a major new
application arrived on the scene—the World Wide Web [Berners-Lee 1994]. The
Web was the first Internet application that caught the general public’s eye. It
dramatically changed how people interact inside and outside their work environments. It elevated the Internet from just one of many data networks to
essentially the one and only data network.
Perhaps what appeals the most to users is that the Web operates on demand.
Users receive what they want, when they want it. This is unlike traditional
broadcast radio and television, which force users to tune in when the content


Application Layer

provider makes the content available. In addition to being available on
demand, the Web has many other compelling features that people love and
cherish. It is enormously easy for any individual to make information available
over the Web—everyone can become a publisher at extremely low cost. Hyperlinks and search engines help us navigate through an ocean of information.
Photos and videos stimulate our senses. Forms, JavaScript, video, and many
other devices enable us to interact with pages and sites. And the Web and its
protocols serve as a platform for generative AI, YouTube, Web-based e-mail
(such as Gmail), and most mobile Internet applications, including Instagram
and Google Maps.


### 2.2.1 Overview of HTTP

The HyperText Transfer Protocol (HTTP) is defined in [RFC 1945], [RFC 7230],
[RFC 7540] and [RFC 9114]. Today the vast majority of applications run over
HTTP, including Web browsing, video streaming, social media, and email
between clients and mail servers. Also, smartphone apps typically communicate with servers over HTTP.
HTTP is implemented in two programs: a client program and a server program. The client program and server program, executing on different end
systems, talk to each other by exchanging HTTP messages. HTTP defines the
structure of these messages and how the client and server exchange the messages. Before explaining HTTP in detail, we should review some Web
terminology.
A Web page (also called a document) consists of objects. An object is simply a file—such as an HTML file, a JPEG image, a Javascrpt file, a CCS style
sheet file, or a video clip—that is addressable by a single URL. Most Web pages
consist of a base HTML file and several referenced objects. For example, if a
Web page contains HTML text and five JPEG images, then the Web page has
six objects: the base HTML file plus the five images. The base HTML file references the other objects in the page with the objects’ URLs. Each URL has two
components: the hostname of the server that houses the object and the object’s
path name. For example, the URL
http://www.someSchool.edu/someDepartment/picture.gif
has www.someSchool.edu for a hostname and /someDepartment/
picture.gif for a path name. Because Web browsers (such as Chrome and
Edge) implement the client side of HTTP, in the context of the Web, we will use
the words browser and client interchangeably. Web servers, which implement the
server side of HTTP, house Web objects, each addressable by a URL. Popular
Web servers include Apache, Nginx, and Microsoft Internet Information Server.
HTTP defines how Web clients request Web pages from Web servers and
how servers transfer Web pages to clients. We discuss the interaction between
client and server in detail later, but the general idea is illustrated in Figure 2.6.
When a user requests a Web page (for example, clicks on a hyperlink), the
browser sends HTTP request messages for the objects in the page to the server.
The server receives the requests and responds with HTTP response messages
that contain the objects.




Figure 2.6 HTTP

request-response behavior

Depending on the HTTP version, HTTP can use either TCP or UDP as its
underlying transport protocol. Using UDP is a relatively new development.
We’ll first discuss HTTP assuming TCP is the underyling transport protocol.
We’ll then discuss HTTP over UDP in Section 2.2.7. The HTTP client first initiates a TCP connection with the server. Once the connection is established, the
browser and the server processes access TCP through their socket interfaces.
As described in Section 2.1, on the client side the socket interface is the door
between the client process and the TCP connection; on the server side it is the
door between the server process and the TCP connection. The client sends
HTTP request messages into its socket interface and receives HTTP response
messages from its socket interface. Similarly, the HTTP server receives request
messages from its socket interface and sends response messages into its socket
interface. Once the client sends a message into its socket interface, the message
is out of the client’s hands and is “in the hands” of TCP. Recall from Section 2.1
that TCP provides a reliable data transfer service to HTTP. This implies that
each HTTP request message sent by a client process eventually arrives intact at
the server; similarly, each HTTP response message sent by the server process
eventually arrives intact at the client. Here we see one of the great advantages of
a layered architecture—HTTP need not worry about lost data or the details of
how TCP recovers from loss or reordering of data within the network. That is
the job of TCP and the protocols in the lower layers of the protocol stack.
It is important to note that the server sends requested files to clients without
storing any state information about the client. If a particular client asks for the
same object twice in a period of a few seconds, the server does not respond by
saying that it just served the object to the client; instead, the server resends the
object, as it has completely forgotten what it did earlier. Because an HTTP server
maintains no information about the clients, HTTP is said to be a stateless protocol. We also remark that the Web uses the client-server application architecture,
as described in Section 2.1. A Web server is always on, with a fixed IP address,
and it services requests from potentially millions of different browsers.
HTTP has gone through many versions. The original version of HTTP,
HTTP 1.0, dates back to the early 1990s [RFC 1945]. Since then HTTP 1.1 [RFC
7320] and HTTP 2 [RFC 7540] have been widely deployed. HTTP 1.0,
HTTP 1.1, and HTTP 2 all run on top of TCP. More recently, HTTP 3 has been


Application Layer

standardized [RFC 9114] and is gaining traction. HTTP 3, discussed in
­ ection 2.2.7, runs over UDP.
S


### 2.2.2 Non-Persistent and Persistent

Connections
In many Internet applications, the client and server communicate for an
extended period of time, with the client making a series of requests and the
server responding to each of the requests. Depending on the application and
on how the application is being used, the series of requests may be made backto-back, periodically at regular intervals, or intermittently. When this
client-server interaction is taking place over TCP, the application developer
needs to make an important decision—should each request/response pair be
sent over a separate TCP connection, or should all of the requests and their corresponding responses be sent over the same TCP connection? In the former
approach, the application is said to use non-persistent connections; and in the
latter approach, persistent connections. To gain a deep understanding of this
design issue, let’s examine the advantages and disadvantages of persistent
connections in the context of a specific application, namely, HTTP, which can
use both non-persistent connections and persistent connections.

HTTP with Non-Persistent Connections
Let’s walk through the steps of transferring a Web page from server to client
for the case of non-persistent connections. Let’s suppose the page consists of a
base HTML file and 10 JPEG images, and that all 11 of these objects reside on
the same server. Further suppose the URL for the base HTML file is
http://www.someSchool.edu/someDepartment/home.index
Here is what happens:
1. The HTTP client process initiates a TCP connection to the server www.
someSchool.edu on port number 80, which is the default port number
for HTTP. Associated with the TCP connection, there will be a socket at the
client and a socket at the server.
2. The HTTP client sends an HTTP request message to the server via its
socket. The request message includes the path name /someDepartment/
home.index. (We will discuss HTTP messages in some detail below.)
3. The HTTP server process receives the request message via its socket,
retrieves the object /someDepartment/home.index from its storage
(RAM or disk), encapsulates the object in an HTTP response message, and
sends the response message to the client via its socket.
4. The HTTP server process tells TCP to close the TCP connection. (But TCP
doesn’t actually terminate the connection until it knows for sure that the
client has received the response message intact.)
5. The HTTP client receives the response message. The TCP connection terminates. The message indicates that the encapsulated object is an HTML



file. The client extracts the file from the response message, examines the
HTML file, and finds references to the 10 JPEG objects.
6. The first four steps are then repeated for each of the referenced JPEG
objects.
As the browser receives the Web page, it displays the page to the user.
Two different browsers may interpret (that is, display to the user) a Web page
in somewhat different ways. HTTP has nothing to do with how a Web page is
interpreted by a client. The HTTP specifications ([RFC 1945] and [RFC 7540])
define only the communication protocol between the client HTTP program
and the server HTTP program.
The steps above illustrate the use of non-persistent connections, where
each TCP connection is closed after the server sends the object—the connection does not persist for other objects. Note that each non-persistent TCP
connection transports exactly one request message and one response message.
Thus, in this example, when a user requests the Web page, 11 TCP connections are generated.
Before continuing, let’s do a back-of-the-envelope calculation to estimate
the amount of time that elapses from when a client requests the base HTML
file until the entire file is received by the client. To this end, we define the
round-trip time (RTT), which is the time it takes for a small packet to travel
from client to server and then back to the client. The RTT includes packetpropagation delays, packet-queuing delays in intermediate routers and
switches, and packet-processing delays. (These delays were discussed in
­Section 1.4.) Now consider what happens when a user clicks on a hyperlink. As
shown in Figure 2.7, this causes the browser to initiate a TCP connection
between the browser and the Web server; this involves a “three-way handshake”—the client sends a small TCP segment to the server, the server
acknowledges and responds with a small TCP segment, and, finally, the client
acknowledges back to the server. The first two parts of the three-way handshake take one RTT. After completing the first two parts of the handshake, the
client sends the HTTP request message combined with the third part of
the three-way handshake (the acknowledgment) into the TCP connection.
Once the request message arrives at the server, the server sends the HTML file
into the TCP connection. This HTTP request/response eats up another RTT.
Thus, roughly, the total response time is two RTTs plus the transmission time
at the server of the HTML file.

HTTP with Persistent Connections
Non-persistent connections have some shortcomings. First, a brand-new connection must be established and maintained for each requested object. For each of
these connections, TCP buffers must be allocated and TCP variables must be
kept in both the client and server. This can place a significant burden on the
Web server, which may be serving requests from hundreds of different clients
simultaneously. Second, as we just described, each object suffers a delivery
delay of two RTTs—one RTT to establish the TCP connection and one RTT to
request and receive an object.


Application Layer

Figure 2.7 Back-of-


the-envelope calculation
for the time needed to
request and receive an
HTML file

With persistent connections, as employed in HTTP 1.1 and HTTP 2, the
server leaves the TCP connection open after sending a response. Subsequent
requests and responses between the same client and server can be sent over the
same connection. In particular, an entire Web page (in the example above, the base
HTML file and the 10 images) can be sent over a single persistent TCP connection.
Moreover, multiple Web pages residing on the same server can be sent from the
server to the same client over a single persistent TCP connection. These requests
for objects can be made using “pipelining,” that is, back-to-back, without waiting
for replies to pending requests. Typically, the HTTP server closes a connection
when it isn’t used for a certain time (a configurable timeout interval). When the
server receives the back-to-back requests, it sends the objects back-to-back.


### 2.2.3 HTTP Message Format

The HTTP specifications [RFC 1945; RFC 7230; RFC 7540; RFC 9114] include the
definitions of the HTTP message formats. There are two types of HTTP messages,
request messages and response messages, both of which are discussed below.

HTTP Request Message
Below we provide a typical HTTP request message:
GET /somedir/page.html HTTP/1.1
Host: www.someschool.edu
Connection: close
User-agent: Mozilla/5.0
Accept-language: fr


We can learn a lot by taking a close look at this simple request message.
First of all, we see that the message is written in ordinary ASCII text, so that
your ordinary computer-literate human being can read it. Second, we see that
the message consists of five lines, each followed by a carriage return and a line
feed. The last line is followed by an additional carriage return and line feed.
Although this particular request message has five lines, a request message can
have many more lines or as few as one line. The first line of an HTTP request
message is called the request line; the subsequent lines are called the header
lines. The request line has three fields: the method field, the URL field, and the
HTTP version field. The method field can take on several different values,
including GET, POST, HEAD, PUT, and DELETE. The great majority of HTTP
request messages use the GET method. The GET method is used when the
browser requests an object, with the requested object identified in the URL
field. In this example, the browser is requesting the object /somedir/page.
html. The version is self-explanatory; in this example, the browser implements
version HTTP 1.1.
Now let’s look at the header lines in the example. The header line Host:
www.someschool.edu specifies the host on which the object resides. You
might think that this header line is unnecessary, as there is already a TCP connection in place to the host. But, as we’ll see in Section 2.2.5, the information
provided by the host header line is required by Web proxy caches. By including the Connection: close header line, the browser is telling the server
that it doesn’t want to bother with persistent connections; it wants the server to
close the connection after sending the requested object. The User-agent:
header line specifies the user agent, that is, the browser type that is making the
request to the server. Here the user agent is Mozilla/5.0, a Firefox browser.
This header line is useful because the server can actually send different versions of the same object to different types of user agents. (Each of the versions
is addressed by the same URL.) Finally, the Accept-language: header indicates that the user prefers to receive a French version of the object, if such an
object exists on the server; otherwise, the server should send its default version. The Accept-language: header is just one of many content negotiation
headers available in HTTP.
Having looked at an example, let’s now look at the general format of a
request message, as shown in Figure 2.8. We see that the general format closely
follows our earlier example. You may have noticed, however, that after the
header lines (and the additional carriage return and line feed) there is an
“entity body.” The entity body is empty with the GET method, but is used with
the POST method. An HTTP client often uses the POST method when the user
fills out a form—for example, when a user provides search words to a search
engine. With a POST message, the user is still requesting a Web page from the
server, but the specific contents of the Web page depend on what the user
entered into the form fields. If the value of the method field is POST, then the
entity body contains what the user entered into the form fields.
We would be remiss if we didn’t mention that a request generated with a
form does not necessarily have to use the POST method. Instead, HTML forms
often use the GET method and include the inputted data (in the form fields) in
the requested URL. For example, if a form uses the GET method, has two fields,


Application Layer

Figure 2.8 General


format of an HTTP request
message

and the inputs to the two fields are monkeys and bananas, then the URL will
have the structure www.somesite.com/animalsearch?monkeys&
bananas. In your day-to-day Web surfing, you have probably noticed extended
URLs of this sort.
The HEAD method is similar to the GET method. When a server receives a
request with the HEAD method, it responds with an HTTP message but it leaves
out the requested object. Application developers often use the HEAD method
for debugging. The PUT method is often used in conjunction with Web publishing tools. It allows a user to upload an object to a specific path (directory)
on a specific Web server. The PUT method is also used by applications that
need to upload objects to Web servers. The DELETE method allows a user, or
an application, to delete an object on a Web server.

HTTP Response Message
Below we provide a typical HTTP response message. This response message
could be the response to the example request message just discussed.
HTTP/1.1 200 OK
Connection: close
Date: Mon, 21 Oct 2024 18:58:21 GMT
Server: Apache/2.2.3 (CentOS)
Last-Modified: Sun, 20 Oct 2024 13:20:46 GMT
Content-Length: 6821
Content-Type: text/html
(data data data data data ...)
Let’s take a careful look at this response message. It has three sections: an initial status line, six header lines, and then the entity body. The entity body is the
meat of the message—it contains the requested object itself (represented by data
data data data data ...). The status line has three fields: the protocol version field, a status code, and a corresponding status message. In this example, the
status line indicates that the server is using HTTP 1.1 and that everything is OK
(that is, the server has found, and is sending, the requested object).


Now let’s look at the header lines. The server uses the Connection:
close header line to tell the client that it is going to close the TCP connection
after sending the message. The Date: header line indicates the time and date
when the HTTP response was created and sent by the server. Note that this is
not the time when the object was created or last modified; it is the time when
the server retrieves the object from its file system, inserts the object into the
response message, and sends the response message. The Server: header line
indicates that the message was generated by an Apache Web server; it is analogous to the User-agent: header line in the HTTP request message. The
Last-Modified: header line indicates the time and date when the object was
created or last modified. The Last-Modified: header, which we will soon
cover in more detail, is critical for object caching, both in the local client and in
network cache servers (also known as proxy servers). The Content-Length:
header line indicates the number of bytes in the object being sent. The
­C ontent-Type: header line indicates that the object in the entity body is
HTML text. (The object type is officially indicated by the Content-Type:
header and not by the file extension.)
Having looked at an example, let’s now examine the general format of a
response message, which is shown in Figure 2.9. This general format of the
response message matches the previous example of a response message. Let’s
say a few additional words about status codes and their phrases. The status
code and associated phrase indicate the result of the request. Some common
status codes and associated phrases include:
* 200 OK: Request succeeded and the information is returned in the
response.
* 301 Moved Permanently: Requested object has been permanently
moved; the new URL is specified in Location: header of the response
message. The client software will automatically retrieve the new URL.
* 400 Bad Request: This is a generic error code indicating that the request
could not be understood by the server.

Figure 2.9 General
format of an HTTP
response message


Application Layer

* 404 Not Found: The requested document does not exist on this server.
* 505 HTTP Version Not Supported: The requested HTTP protocol
version is not supported by the server.
How would you like to see a real HTTP request message from your computer and the HTTP response sent in return by the Web server? It’s easy to do,
and we recommend you give it a try! From a command line prompt on your
computer, enter:
curl -v http://gaia.cs.umass.edu/kurose_ross/index.php
The curl command above will send an HTTP GET request to the gaia.
cs.umass.edu Web server to retrieve the HTML content /kurose_ross/
index.php, which is the authors’ homepage for this textbook. The verbose
option (-v) will cause the text content of the HTTP GET request message and
the response received to be displayed as text. Of course, if you want to see
what the received response looks like when it’s formatted and displayed, just
enter the URL above into your favorite Web browser.
In this section, we discussed a number of header lines that can be used
within HTTP request and response messages. The HTTP specification defines
many, many more header lines that can be inserted by browsers, Web servers,
and network cache servers. We have covered only a small number of the totality of header lines. We’ll cover a few more below and another small number
when we discuss network Web caching in Section 2.2.5.
How does a browser decide which header lines to include in a request
message? How does a Web server decide which header lines to include in a
response message? A browser will generate header lines as a function of the
browser type and version, the user configuration of the browser and whether
the browser currently has a cached, but possibly out-of-date, version of the
object. Web servers behave similarly: There are different products, versions,
and configurations, all of which influence which header lines are included in
response messages.


### 2.2.4 User-Server Interaction: Cookies

We mentioned above that an HTTP server is stateless. This simplifies server
design and has permitted engineers to develop high-performance Web servers
that can handle thousands of simultaneous TCP connections. However, it is
often desirable for a Web site to identify users, either because the server wishes
to restrict user access or because it wants to serve content as a function of the
user identity. For these purposes, HTTP uses cookies. Cookies, defined in [RFC
6265], allow sites to keep track of users. Most major commercial Web sites use
cookies today.
As shown in Figure 2.10, cookie technology has four components: (1) a
cookie header line in the HTTP response message; (2) a cookie header line in
the HTTP request message; (3) a cookie file kept on the user’s end system and
managed by the user’s browser; and (4) a back-end database at the Web site.
Using Figure 2.10, let’s walk through an example of how cookies work. Suppose Susan, who always accesses the Web using Google Chrome from her




Figure 2.10 Keeping user state with cookies

home PC, contacts Amazon.com for the first time. Let us suppose that in the
past she has already visited the eBay site. When the request comes into the
Amazon Web server, the server creates a unique identification number and creates an entry in its back-end database that is indexed by the identification
number. The Amazon Web server then responds to Susan’s browser, including
in the HTTP response a Set-cookie: header, which contains the identification number. For example, the header line might be:
Set-cookie: 1678
When Susan’s browser receives the HTTP response message, it sees the Setcookie: header. The browser then appends a line to the special cookie file that
it manages. This line includes the hostname of the server and the identification
number in the Set-cookie: header. Note that the cookie file already has an
entry for eBay, since Susan has visited that site in the past. As Susan continues
to browse the Amazon site, each time she requests a Web page, her browser
consults her cookie file, extracts her identification number for this site, and
puts a cookie header line that includes the identification number in the HTTP


Application Layer

request. Specifically, each of her HTTP requests to the Amazon server includes
the header line:
Cookie: 1678
In this manner, the Amazon server is able to track Susan’s activity at the
­A mazon site. Although the Amazon Web site does not necessarily know
Susan’s name, it knows exactly which pages user 1678 visited, in which order,
and at what times! Amazon uses cookies to provide its shopping cart service—­
Amazon can maintain a list of all of Susan’s intended purchases, so that she
can pay for them collectively at the end of the session.
If Susan returns to Amazon’s site, say, one week later, her browser will
continue to put the header line Cookie: 1678 in the request messages.
­Amazon also recommends products to Susan based on Web pages she has visited at Amazon in the past. If Susan also registers herself with
Amazon—providing full name, e-mail address, postal address, and credit card
information—Amazon can then include this information in its database,
thereby associating Susan’s name with her identification number (and all of
the pages she has visited at the site in the past!). This is how Amazon and other
e-commerce sites provide “one-click shopping”—when Susan chooses to purchase an item during a subsequent visit, she doesn’t need to re-enter her name,
credit card number, or address.
From this discussion, we see that cookies can be used to identify a user.
The first time a user visits a site, the user can provide a user identification (possibly his or her name). During the subsequent sessions, the browser passes a
cookie header to the server, thereby identifying the user to the server. Cookies
can thus be used to create a user session layer on top of stateless HTTP. For
example, when a user logs in to a Web-based e-mail application, the browser
sends cookie information to the server, permitting the server to identify the
user throughout the user’s session with the application.
Although cookies often simplify the Internet shopping experience for the
user, they are controversial because they can also be considered as an invasion
of privacy. As we just saw, using a combination of cookies and user-supplied
account information, a Web site can learn a lot about a user and potentially sell
this information to a third party.


### 2.2.5 Browser Caching

We learned earlier in Figure 2.7 that the minimum delay from when your
browser first requests an object from a Web server and when your browser
receives that object is 2RTT—one RTT to establish a TCP connection between
your browser and the server, and another RTT to send the HTTP request and
receive the HTTP response. We’ll learn shortly that the most recent version of
HTTP ( HTTP 3 ) has been optimized to require just one RTT to request a web
page in many cases. But can we cut that this delay to something even less that
one RTT? Wouldn’t a delay of zero be great? Although this might seem to defy
the law of physics, this can indeed happen with browser caching, a technique
implemented in all modern Web browsers, and used extensively in the Web.
One estimate is that 75% of Web requests receive HTTP responses with the



types of explicit browser caching instructions that we’ll study below [Web
almanac 2021].
With browser caching, a Web browser locally stores the content of recently
received Web objects in its browser cache. When a user requests a Web object,
the browser first checks to see if that object is stored in its local browser cache.
If so, it may immediately display that Web object, without making a new
request to the Web server (and incurring the subsequent request/response
delay), since the browser has already requested and received that object earlier
from the Web server.
Although browser caching can reduce user-perceived response times and
decrease the amount of HTTP traffic carried over the Internet (advantages
we’ll explore in the end-of-chapter problems), it introduces an important new
challenge—how does the browser know whether the object currently housed
in the Web server has been modified since the copy was cached at the client?
Certain types of Web objects such as images, JavaScript files, and CSS files
change infrequently; other objects such as text may change frequently. How is
the browser to know whether the contents in its cache are up-to-date or stale?
Fortunately, the HTTP protocol provides fields in both the HTTP GET and
response messages to help the server and a browser manage browser caching
[RFC 7232]:
* Cache-Control. The Cache-Control field in an HTTP response message
lets the server specify how the content in the HTTP reply message
should be cached. The Cache Control:no-store directive instructs
the browser to not cache/store the content locally. In this case, the browser
will always have to re-request the content from the server. Alternatively, a
server can explicitly instruct the browser about the amount of time that an
object can remain in the cache. For example, the Cache-Control: maxage=3600 directive tells the browser that the content can be cached for
3600 seconds, but after that must be re-requested from the server. Many
other Cache-Control directives are defined in [RFC 7232].
* If-Modified-Since. HTTP also provides a mechanism in the client-to-server
HTTP message, known as a conditional GET message, to facilitate caching. The conditional GET message is the usual HTTP GET message that
also include an If-Modified-Since: header line. With a conditional
GET, the client explicitly requests an object, but lets the server know that it
has that object in its browser cache and when that object was added to its
cache. The HTTP server in turn will reply with the full object if that object
has changed in the intervening time; otherwise, it will simply let the
browser know that its (browser cache) copy is still current and does not
send the object again.
To illustrate how the conditional GET operates, let’s walk through an
example. Suppose that a browser has previously requested an object, say
kiwi.jpg, has that object in its cache and has recorded the time when kiwi.
jpg was added to its cache. When a user later requests this object again, however, the browser is uncertain as to whether or not this cached copy is still
current. This can happen because the server never provided cache-control
information, the server earlier provided a cache-control directive with a


Application Layer

max-age that has expired, or the server directed the browser to cache the
object but also directed the browser to always explicitly check with the server
on the object’s freshness. In this case, the browser sends a conditional GET to
the server:
GET /fruit/kiwi.jpg HTTP/1.1
Host: www.exotiquecuisine.com
If-modified-since: Fri, 13 Sep 2024 09:23:24
The value of the If-modified-since: header line indicates that the object in
the browser’s cache was received on 13 Sep 2024 at 9:23:24. This conditional
GET is telling the server to send the object only if the object has been modified
since the specified date. Suppose the object has not been modified since 13 Sep
2024 09:23:24. In this case, the Web server sends an HTTP response message:
HTTP/1.1 304 Not Modified
Date: Fri, 8 Nov 2024 12:07:29
Server: Apache/2.4.62 (Unix)
(empty entity body)
We see in this case, that the Web server still sends a response message but does
not include the requested object in the response message. The 304 Not Modified in the status line tells the browser that copy of the object in the browsers cache in current and therefore the cached copy of the object can be used.
Including the requested object would only waste bandwidth and increase userperceived response time, particularly if the object is large.


### 2.2.6 HTTP 2

HTTP 2 [RFC 7540], standardized in 2015, was the first new version of HTTP
since HTTP 1.1, which was standardized in 1997. Since standardization,
HTTP 2 has taken off, with about 35% of the top 10 million websites supporting HTTP 2 in 2024 [W3Techs]. Most browsers—including Google Chrome,
Microsoft Edge, Safari, Opera, and Firefox—also support HTTP 2. Usage in
recent years has declined some due to the emergence of HTTP 3, discussed in
Seciton 2.2.7.
The primary goals for HTTP 2 are to reduce perceived latency by enabling
request and response multiplexing over a single TCP connection, provide
request prioritization and server push, and provide efficient compression of
HTTP header fields. HTTP 2 does not change HTTP methods, status codes,
URLs, or header fields. Instead, HTTP 2 changes how the data is formatted
and transported between the client and server.
To motivate the need for HTTP 2, recall that HTTP 1.1 uses persistent
TCP connections, allowing a Web page to be sent from server to client over a
single TCP connection. By having only one TCP connection per Web page, the
number of sockets at the server is reduced and each transported Web page gets
a fair share of the network bandwidth (as discussed below). But developers of
Web browsers quickly discovered that sending all the objects in a Web page
over a single TCP connection has a Head of Line (HOL) blocking problem. To
understand HOL blocking, consider a Web page that includes an HTML base



page, a large video clip near the top of Web page, and many small objects
below the video. Further suppose there is a low-to-medium speed bottleneck
link (for example, a low-speed wireless link) on the path between server and
client. Using a single TCP connection, the video clip will take a long time to
pass through the bottleneck link, while the small objects are delayed as they
wait behind the video clip; that is, the video clip at the head of the line blocks
the small objects behind it. HTTP 1.1 browsers typically work around this
problem by opening multiple parallel TCP connections, thereby having
objects in the same web page sent in parallel to the browser. This way, the
small objects can arrive at and be rendered in the browser much faster, thereby
reducing user-perceived delay.
TCP congestion control, discussed in detail in Chapter 3, also provides
browsers an unintended incentive to use multiple parallel TCP connections
rather than a single persistent connection. Very roughly speaking, TCP congestion control aims to give each TCP connection sharing a bottleneck link an
equal share of the available bandwidth of that link; so if there are n TCP connections operating over a bottleneck link, then each connection approximately
gets 1 nth of the bandwidth. By opening multiple parallel TCP connections to
transport a single Web page, the browser can “cheat” and grab a larger portion
of the link bandwidth. Many HTTP 1.1 browsers open up to six parallel TCP
connections not only to circumvent HOL blocking but also to obtain more
bandwidth.
One of the primary goals of HTTP 2 is to get rid of (or at least reduce the
number of) parallel TCP connections for transporting a single Web page. This
not only reduces the number of sockets that need to be open and maintained at
servers, but also allows TCP congestion control to operate as intended. But
with only one TCP connection to transport a Web page, HTTP 2 requires carefully designed mechanisms to avoid HOL blocking.

HTTP 2 Framing
The HTTP 2 solution for HOL blocking is to break each message into small
frames, and interleave the request and response messages on the same TCP
connection. To understand this, more thoroughly consider again the example of
a Web page consisting of one large video clip and, say, 8 smaller objects. Thus
the server will receive 9 concurrent requests from any browser wanting to see
this Web page. For each of these requests, the server needs to send 9 competing
HTTP response messages to the browser over the same TCP connection. For
simplicity, suppose all frames are of fixed length, the video clip consists of 1000
frames, and each of the smaller objects consists of two frames. With frame interleaving, after sending one frame from the video clip, the first frame of each of
the small objects are sent. Then after sending the second frame of the video clip,
the last frame of each of the small objects are sent. Thus, all of the smaller objects
are sent after sending a total of 18 frames. If interleaving were not used, the
smaller objects would be sent only after sending 1016 frames. Thus the HTTP 2
framing mechanism can significantly decrease user-perceived delay.
The ability to break down an HTTP message into independent frames,
interleave them, and then reassemble them on the other end is the single most


Application Layer

important enhancement of HTTP 2. The framing is done by the framing sublayer of the HTTP 2 protocol. When a server wants to send an HTTP response,
the response is processed by the framing sub-layer, where it is broken down
into frames. The header field of the response becomes one frame, and the body
of the message is broken down into one or more additional frames. The frames
of the response are then interleaved by the framing sub-layer in the server with
the frames of other responses and sent over the single persistent TCP connection. As the frames arrive at the client, they are first reassembled into the
original response messages at the framing sub-layer and then processed by the
browser as usual. Similarly, a client’s HTTP requests are broken into frames
and interleaved.
In addition to breaking down each HTTP message into independent
frames, the framing sublayer also binary encodes the frames. Binary protocols
are more efficient to parse, lead to slightly smaller frames, and are less
error-prone.

Response Message Prioritization and Server Pushing
Message prioritization allows developers to customize the relative priority of
requests to better optimize application performance. As we just learned, the
framing sub-layer organizes messages into parallel streams of data destined to
the same requestor. When a client sends concurrent requests to a server, it can
prioritize the responses it is requesting by assigning a weight between 1 and
256 to each message. The higher number indicates higher priority. Using these
weights, the server can send first the frames for the responses with the highest
priority. In addition to this, the client also states each message’s dependency
on other messages by specifying the ID of the message on which it depends.
Another feature of HTTP 2 is the ability for a server to send multiple
responses for a single client request. That is, in addition to the response to the
original request, the server can push additional objects to the client, without the
client having to request each one. This is possible since the HTML base page
indicates the objects that will be needed to fully render the Web page. So
instead of waiting for the HTTP requests for these objects, the server can analyze the HTML page, identify the objects that are needed, and send them to the
client before receiving explicit requests for these objects. Server push eliminates the
extra latency due to waiting for the requests.


### 2.2.7 HTTP 3 and QUIC

We just learned about the evolution of the HTTP protocol, from HTTP 1.0 to
HTTP 1.1 to HTTP 2. Although those three protocols have significant differences, one important common characteristic they share is that they all run over
TCP. But that doesn’t mean HTTP will always run over TCP! HTTP 3, standardized in 2022 in RFC 9114, has hit the Internet community by storm. It is
rapidly gaining market share in the Web, including for email, video/audio
streaming, and social media, and has become the default version of HTTP for
many popular Web browsers and smartphone applications. And remarkably,
HTTP 3 does not run over TCP but instead over UTP! How can this be, you



may ask, since UDP is a bare-bones transport protocol without reliable data
transfer, and thus without guarantees for HTTP message delivery? We will
soon get to the bottom of this most intriguing mystery.

The QUIC Transport Protocol
HTTP 3 runs over the Quick UDP Internet Connections (QUIC) transport protocol. So before describing HTTP 3, we need to discuss the QUIC transport
protocol, which was standardized in 2021 in RFC 9000. You may now be thinking, “Well hold on! Haven’t the authors been telling us over and over again
that the Internet has exactly two transport protocols—UDP and TCP? And
now they’re telling us there is a third transport protocol called QUIC? So, does
the Internet have two or three transport protocols?”
Let’s try to clear this up. Strictly speaking, the Internet continues to have
only two transport protocols, TCP and UDP. And in truth, QUIC is not actually
a transport layer protocol, but is instead a sub-layer in the application layer that
uses UDP to send and receive packets over the Internet, as shown in Figure 2.11.
Hence the “UDP” in the name, Quick UDP Internet Connections (QUIC).
However, even though QUIC is not, strictly speaking, a transport-layer
protocol, from the application developer’s perspective it is. Indeed, network
application developers can write applications by creating QUIC sockets similar
to how they create TCP and UDP sockets (discussed in Section 2.6). When the
application establishes a QUIC socket, the QUIC sublayer will then create a
UDP socket, as described in Section 2.6. The application can then send messages into and receive messages from the QUIC socket without concerning
itself with the inner workings of QUIC. In summary, although in actuality
QUIC is a sublayer of the application layer, from the application developer’s
perspective QUIC is a new transport layer protocol.

Why a New “Transport Protocol”?
Although QUIC is a generic protocol that can be employed by many applications, it was primarily designed with the goal of improving the performance of
the Web. Let’s take a look at where there is room for performance improvement.
In the distant past (about up to 2005), most Web transactions ran directly
over TCP without any encryption. But over the years, encryption and authentication became default requirements in most Web transactions, including Web
surfing, Web search, and Web-based email. Such security services were typically provided to Web applications via TLS as described in the “Security in
Focus” sidebar in Section 2.3 and in greater detail in Chapter 8. Thus, most

Figure 2.11

a. traditional secure HTTP
protocol stack; b. secure
QUIC-based HTTP 3
protocol stack


Application Layer

HTTP 1.1 and HTTP 2 Web transactions today employ TLS running on top of
TCP (with TLS running in a sub-layer of the application layer, as described in
the sidebar). But this “TLS on top of TCP” design (commonly known as https)
requires two handshake phases: one phase for setting up the TCP connection
and a subsequent phase for sharing encryption keys between client and server.
This can introduce undesirable delays for interactive HTTP applications,
including Web browsing. One of the most important features of QUIC is that it
gets rid of this double-handshake by absorbing the TLS handshake phase into
the initial connection setup handshake—and hence the word “Quick” in
“Quick Internet UDP Connections”.
More specifically, QUIC integrates a recent version of TLS, called TLS 1.3,
directly into the QUIC protocol, eliminating the need for a separate TLS handshake. In this manner, QUIC performs both the connection setup and
encryption setup in one round trip, reducing latency. Furthermore, on reconnecting, QUIC can use the previously stored session and encryption
parameters, allowing 0-RTT data transmission without waiting for a full handshake, further reducing connection setup time.
In addition to reducing connection set-up time, QUIC also re-examines the
HOL blocking problem, introduced in Section 2.2.6. Recall that HTTP 2
addresses the HOL blocking problem for the situation of when one big Web
object gets in front of other smaller objects, all of which are being sent over a
single TCP connection. HTTP 2 solves this problem by breaking up HTTP
messages into small frames, and multiplexes the frames from different HTTP
messages over the single TCP connection. But, as it turns out, HTTP 2 doesn’t
fully resolve the HOL blocking problem. In HTTP 2, multiple messages are
multiplexed over a single TCP connection. If a packet is lost in this connection,
TCP requires that the lost packet be retransmitted and processed before other
packets can be delivered. This delays all the other messages, even if they don’t
depend on the lost packet. This phenomenon results in another form of HOL
blocking, where one lost packet for one HTTP message blocks the transmission
of the other HTTP messages. This problem is particularly severe in wireless
environments, where packet loss rates can be high.
QUIC solves this by using UDP instead of TCP, and then applying reliable
data-transfer to each message separately within the same QUIC connection.
QUIC uses the terminology “streams” for the different data streams (different
HTTP messages in an HTTP context) sharing the same QUIC connection. Specifically, QUIC not only breaks up streams into small frames and multiplexes
the frames, but also manages each stream independently within a single QUIC
connection, which means if a packet from one stream is lost, only that stream is
affected. The other streams can continue to send and receive data without
waiting for the lost packet to be retransmitted, eliminating the HOL blocking
problem that plagues single-connection TCP. The inner workings of QUIC are
discussed in greater detail in Section 3.7.

QUIC Services
Suppose you want to develop a new networking application. Should you run
your application over UDP, TCP or QUIC? To make this decision, you will



want to know what services each of these protocols would provide to your
application. We have already discussed the services that UDP and TCP provide
in Section 2.1.4. Let’s now summarize QUIC’s services so that you will have all
the facts at your disposal before making this crucial decision.
From the application developer’s perspective, QUIC services are more
similar to those of TCP than to those of UDP.
* Like TCP, QUIC is connection-oriented. Before sending data, a QUIC connection is created between client and server. This connection is established
on top of the bare-bones connectionless protocol UDP.
* Like TCP, QUIC provides reliable data transfer, so that the application
knows that every message one side sends will eventually arrive at the
other side.
* Like TCP, QUIC provides congestion and flow control services.
But QUIC offers additional services that go well beyond the services provided by TCP, services which are highly desirable for applications in the
modern Internet:
* Built-in Encryption: QUIC integrates TLS 1.3 (which we will learn about
in Chapter 8) directly into its protocol, providing encrypted communication by default. This eliminates the need for separate handshakes for TLS
over TCP, making secure connections faster and more efficient.
* Independent Data Streams: QUIC allows multiple streams (for example,
multiple HTTP messages) to be sent simultaneously over a single QUIC
connection. These streams are independent, so packet loss in one stream
doesn’t affect others, unlike in TCP, where losses in one stream can delay
all streams. Further, each stream can be managed individually, allowing
applications to prioritize different types of data, such as video, text, or
control messages, ensuring a smoother user experience.
* 0 -RTT Handshakes: For returning clients, QUIC supports 0-RTT handshakes, allowing data to be sent immediately without waiting for a full
connection handshake. This speeds up reconnecting to services, benefiting
latency-sensitive applications like Web surfing and gaming.
* Connection Migration: QUIC supports connection migration, allowing
connections to remain active if the client’s IP address changes (e.g., switching from Wi-Fi to cellular). This improves reliability for mobile users
where network conditions change frequently.

HTTP 3: Running the Web over QUIC
HTTP 3, the latest version of HTTP, is designed to address several limitations
in previous versions, particularly in terms of performance, security, and reliability over modern networks. Unlike previous versions, HTTP 3 operates
over the QUIC protocol, which provides all the QUIC services just described.
Since its release, HTTP 3 has seen growing adoption. Major browsers like
Chrome, Firefox, Edge, and Safari now support HTTP 3 and have adopted it
as their default HTTP protocol when connecting to HTTP 3-compatible servers. Leading Internet companies such as Google have also implemented


Application Layer

HTTP 3 to improve user experience across many of their services including
search, video distribution, and video conferencing.
HTTP 3 does not change the message formats of early HTTP protocols.
It’s only major change as compared with HTTP 2 is that instead of using a persistent TCP connection between client and server to send the HTTP messages,
it uses a persistent QUIC connection. We will describe in greater detail how
HTTP messages are sent and received over QUIC connections in Section 2.6.3.
In summary, HTTP 3 clients and servers use QUIC’s features—such as
fast connection establishment, encryption, multiplexing independent streams,
prioritization, and connection migration—to efficiently and securely deliver
multiple objects of a Web page in parallel while reducing latency and ensuring
smooth, uninterrupted transmission.


## 2.3 Electronic Mail in the

Internet
Electronic mail has been around since the beginning of the Internet. It was the
most popular application when the Internet was in its infancy [Segaller 1998],
and has become more elaborate and powerful over the years. It remains one of
the Internet’s most important and utilized applications.
In this section, we examine the application-layer protocols that are at the
heart of Internet e-mail. But before we jump into an in-depth discussion of
these protocols, let’s take a high-level view of the Internet mail system and its
key components.
Figure 2.12 presents a high-level view of the Internet mail system. We
see from this diagram that it has three major components: user agents, mail
servers, and the Simple Mail Transfer Protocol (SMTP). We now describe
each of these components in the context of a sender, Alice, sending an e-mail
message to a recipient, Bob. User agents allow users to read, reply to, forward,
save, and compose messages. Examples of user agents for e-mail include
Microsoft Outlook, Apple Mail, Web-based Gmail, the Gmail App running in a
smartphone, and so on. Today, many users send emails to their mail servers
and receive emails from their mail servers via HTTP-based user agents such as
gmail and Yahoo! mail. When Alice is finished composing her message, her
user agent sends the message to her mail server, where the message is placed
in the mail server’s outgoing message queue. When Bob wants to read a message, his user agent retrieves the message from his mailbox in his mail server.
Mail servers form the core of the e-mail infrastructure. Each recipient,
such as Bob, has a mailbox located in one of the mail servers. Bob’s mailbox
manages and maintains the messages that have been sent to him. A typical
message starts its journey in the sender’s user agent, then travels to the sender’s
mail server, and then travels to the recipient’s mail server, where it is deposited
in the recipient’s mailbox. When Bob wants to access the messages in his mailbox, the mail server containing his mailbox authenticates Bob (with his
username and password). Alice’s mail server must also deal with failures in
Bob’s mail server. If Alice’s server cannot deliver mail to Bob’s server, Alice’s




Figure 2.12 A high-level view of the Internet e-mail system

server holds the message in a message queue and attempts to transfer the
­message later. Reattempts are often done every 30 minutes or so; if there is no
success after several days, the server removes the message and notifies
the sender (Alice) with an e-mail message.
SMTP is the principal application-layer protocol for Internet electronic
mail. It uses the reliable data transfer service of TCP to transfer mail from the
sender’s mail server to the recipient’s mail server. As with most applicationlayer protocols, SMTP has two sides: a client side, which executes on the
sender’s mail server, and a server side, which executes on the recipient’s mail
server. Both the client and server sides of SMTP run on every mail server. When
a mail server sends mail to other mail servers, it acts as an SMTP client. When a
mail server receives mail from other mail servers, it acts as an SMTP server.


### 2.3.1 SMTP

SMTP, defined in RFC 5321, is at the heart of Internet electronic mail. As mentioned above, SMTP transfers messages from senders’ mail servers to the
recipients’ mail servers. SMTP is much older than HTTP. (The original SMTP


Application Layer

RFC dates back to 1982, and SMTP was around long before that.) Although
SMTP has numerous wonderful qualities, as evidenced by its ubiquity in the
Internet, it is nevertheless a legacy technology that possesses certain archaic
characteristics. For example, it restricts the body (not just the headers) of all
mail messages to simple 7-bit ASCII. This restriction made sense in the early
1980s when transmission capacity was scarce and no one was e-mailing large
attachments or large image, audio, or video files. But today, in the multimedia
era, the 7-bit ASCII restriction is a bit of a pain—it requires binary multimedia
data to be encoded to ASCII before being sent over SMTP; and it requires the
corresponding ASCII message to be decoded back to binary after SMTP transport. Recall from Section 2.2 that HTTP does not require multimedia data to be
ASCII encoded before transfer.
To illustrate the basic operation of SMTP, let’s walk through a common
scenario. Suppose Alice wants to send Bob a simple ASCII message.
1. Alice invokes her user agent for e-mail, provides Bob’s e-mail address (for
example, bob@someschool.edu), composes a message, and instructs
the user agent to send the message.
2. Alice’s user agent sends the message to her mail server, where it is placed
in a message queue.
3. The client side of SMTP, running on Alice’s mail server, sees the message
in the message queue. It opens a TCP connection to an SMTP server, running on Bob’s mail server.
4. After some initial SMTP handshaking, the SMTP client sends Alice’s message into the TCP connection.
5. At Bob’s mail server, the server side of SMTP receives the message. Bob’s
mail server then places the message in Bob’s mailbox.
6. Bob invokes his user agent to read the message at his convenience.
The scenario is summarized in Figure 2.13.
It is important to observe that SMTP does not normally use intermediate
mail servers for sending mail, even when the two mail servers are located at
opposite ends of the world. If Alice’s server is in Hong Kong and Bob’s server
is in St. Louis, the TCP connection is a direct connection between the Hong

Figure 2.13 Alice sends a message to Bob



Kong and St. Louis servers. In particular, if Bob’s mail server is down, the message remains in Alice’s mail server and waits for a new attempt—the message
does not get placed in some intermediate mail server.
Let’s now take a closer look at how SMTP transfers a message from a
sending mail server to a receiving mail server. We will see that the SMTP
protocol has many similarities with protocols that are used for face-to-face
human interaction. First, the client SMTP (running on the sending mail
server host) has TCP establish a connection to port 25 at the server SMTP
(running on the receiving mail server host). If the server is down, the client
tries again later. Once this connection is established, the server and client
perform some application-layer handshaking—just as humans often introduce themselves before transferring information from one to another, SMTP
clients and servers introduce themselves before transferring information.
During this SMTP handshaking phase, the SMTP client indicates the e-mail
address of the sender (the person who generated the message) and the
e-mail address of the recipient. Once the SMTP client and server have introduced themselves to each other, the client sends the message. SMTP can
count on the reliable data transfer service of TCP to get the message to the
server without errors. The client then repeats this process over the same TCP
connection if it has other messages to send to the server; otherwise, it
instructs TCP to close the connection.
Let’s next take a look at an example transcript of messages exchanged
between an SMTP client (C) and an SMTP server (S). The hostname of the client is crepes.fr and the hostname of the server is hamburger.edu. The
ASCII text lines prefaced with C: are exactly the lines the client sends into its
TCP socket, and the ASCII text lines prefaced with S: are exactly the lines the
server sends into its TCP socket. The following transcript begins as soon as the
TCP connection is established.
S: 220 hamburger.edu
C: HELO crepes.fr
S: 250 Hello crepes.fr, pleased to meet you
C: MAIL FROM: <alice@crepes.fr>
S: 250 alice@crepes.fr ... Sender ok
C: RCPT TO: <bob@hamburger.edu>
S: 250 bob@hamburger.edu ... Recipient ok
C: DATA
S: 354 Enter mail, end with ”.” on a line by itself
C: Do you like ketchup?
C: How about pickles?
C: .
S: 250 Message accepted for delivery
C: QUIT
S: 221 hamburger.edu closing connection
In the example above, the client sends a message (“Do you like
ketchup? How about pickles?”) from mail server crepes.fr to mail
server hamburger.edu. As part of the dialogue, the client issued five commands: HELO (an abbreviation for HELLO), MAIL FROM, RCPT TO, DATA, and
QUIT. These commands are self-explanatory. The client also sends a line consisting of a single period, which indicates the end of the message to the server.


Application Layer

(In ASCII jargon, each message ends with CRLF.CRLF, where CR and LF stand
for carriage return and line feed, respectively.) The server issues replies to each
command, with each reply having a reply code and some (optional) Englishlanguage explanation. We mention here that SMTP uses persistent connections:
If the sending mail server has several messages to send to the same receiving
mail server, it can send all of the messages over the same TCP connection. For
each message, the client begins the process with a new MAIL FROM: crepes.
fr, designates the end of message with an isolated period, and issues QUIT
only after all messages have been sent.
It is highly recommended that you use Telnet to carry out a direct dialogue with an SMTP server. To do this, issue
telnet serverName 25
where serverName is the name of a local mail server. When you do this, you
are simply establishing a TCP connection between your local host and the mail
server. After typing this line, you should immediately receive the 220 reply
from the server. Then issue the SMTP commands HELO, MAIL FROM, RCPT
TO, DATA, CRLF.CRLF, and QUIT at the appropriate times. It is also highly recommended that you do Programming Assignment 3 at the end of this chapter.
In that assignment, you’ll build a simple user agent that implements the client
side of SMTP. It will allow you to send an e-mail message to an arbitrary recipient via a local mail server.


### 2.3.2 Mail Message Formats

When Alice writes an ordinary snail-mail letter to Bob, she may include all kinds
of peripheral header information at the top of the letter, such as Bob’s address,
her own return address, and the date. Similarly, when an e-mail message is sent
from one person to another, a header containing peripheral information precedes the body of the message itself. This peripheral information is contained in
a series of header lines, which are defined in RFC 5322. The header lines and the
body of the message are separated by a blank line (that is, by CRLF). RFC 5322
specifies the exact format for mail header lines as well as their semantic interpretations. As with HTTP, each header line contains readable text, consisting of a
keyword followed by a colon followed by a value. Some of the keywords are
required and others are optional. Every header must have a From: header line
and a To: header line; a header may include a Subject: header line as well as
other optional header lines. It is important to note that these header lines are different from the SMTP commands we studied in Section 2.3.1 (even though they
contain some common words such as “from” and “to”). The commands in that
section were part of the SMTP handshaking protocol; the header lines examined
in this section are part of the mail message itself.
A typical message header looks like this:
From: alice@crepes.fr
To: bob@hamburger.edu
Subject: Searching for the meaning of life.
After the message header, a blank line follows; then the message body (in
ASCII) follows.





### 2.3.3 Mail Access Protocols

Once SMTP delivers the message from Alice’s mail server to Bob’s mail server,
the message is placed in Bob’s mailbox. Given that Bob (the recipient) executes
his user agent on his local host (e.g., smartphone or PC), it is natural to consider placing a mail server on his local host as well. With this approach, Alice’s
mail server would dialogue directly with Bob’s PC. There is a problem with
this approach, however. Recall that a mail server manages mailboxes and runs
the client and server sides of SMTP. If Bob’s mail server were to reside on his
local host, then Bob’s host would have to remain always on, and connected to
the Internet, in order to receive new mail, which can arrive at any time. This is
impractical for many Internet users. Instead, a typical user runs a user agent on
the local host but accesses its mailbox stored on an always-on shared mail
server. This mail server is shared with other users.
Now let’s consider the path an e-mail message takes when it is sent from
Alice to Bob. We just learned that at some point along the path the e-mail
message needs to be deposited in Bob’s mail server. This could be done simply by having Alice’s user agent send the message directly to Bob’s mail
server. However, typically the sender’s user agent does not dialogue directly
with the recipient’s mail server. Instead, as shown in Figure 2.14, Alice’s user
agent uses SMTP or HTTP to deliver the e-mail message into her mail server,
then Alice’s mail server uses SMTP (as an SMTP client) to relay the e-mail
message to Bob’s mail server. Why the two-step procedure? Primarily
because without relaying through Alice’s mail server, Alice’s user agent
doesn’t have any recourse to an unreachable destination mail server. By having Alice first deposit the e-mail in her own mail server, Alice’s mail server
can repeatedly try to send the message to Bob’s mail server, say every
30 ­minutes, until Bob’s mail server becomes operational. (And if Alice’s mail
server is down, then she has the recourse of complaining to her system
administrator!)
But there is still one missing piece to the puzzle! How does a recipient like
Bob, running a user agent on his local host, obtain his messages, which are sitting in a mail server? Note that Bob’s user agent can’t use SMTP to obtain the
messages because obtaining the messages is a pull operation, whereas SMTP is
a push protocol.

Figure 2.14 E-mail protocols and their communicating entities


Application Layer

Today, there are two common ways for Bob to retrieve his e-mail from a
mail server. If Bob is using Web-based e-mail or a smartphone app (such as
Gmail), then the user agent will use HTTP to retrieve Bob’s e-mail. This case
requires Bob’s mail server to have an HTTP interface as well as an SMTP interface (to communicate with Alice’s mail server). The alternative method,
typically used with mail clients such as Microsoft Outlook, is to use the
­Internet Mail Access Protocol (IMAP) defined in RFC 3501. Both the HTTP
and IMAP approaches allow Bob to manage folders, maintained in Bob’s mail
server. Bob can move messages into the folders he creates, delete messages,
mark messages as important, and so on.


## 2.4 DNS—The Internet’s

Directory Service
We human beings can be identified in many ways. For example, we can be
identified by the names that appear on our birth certificates. We can be identified by our social security numbers. We can be identified by our driver ’s
license numbers. Although each can be used to identify people, within a given
context one identifier may be more appropriate than another. For example, the
computers at the IRS (the infamous tax-collecting agency in the United States)
prefer to use fixed-length social security numbers rather than birth certificate
names. On the other hand, ordinary people prefer the more mnemonic birth
certificate names rather than social security numbers. (Indeed, can you imagine saying, “Hi. My name is 132-67-9875. Please meet my husband,
178-87-1146.”)
Just as humans can be identified in many ways, so too can Internet hosts.
One identifier for a host is its hostname. Hostnames—such as www.facebook.com, www.google.com, gaia.cs.umass.edu—are mnemonic and
are therefore appreciated by humans. However, hostnames provide little, if
any, information about the location within the Internet of the host. (A hostname such as www.eurecom.fr, which ends with the country code .fr, tells
us that the host is probably in France, but doesn’t say much more.) Furthermore, because hostnames can consist of variable-length alphanumeric
characters, they would be difficult to process by routers. For these reasons,
hosts are also identified by so-called IP addresses.
We discuss IP addresses in some detail in Chapter 4, but it is useful to say
a few brief words about them now. An IP address consists of four bytes and
has a rigid hierarchical structure. An IP address looks like 121.7.106.83,
where each period separates one of the bytes expressed in decimal notation
from 0 to 255. An IP address is hierarchical because as we scan the address
from left to right, we obtain more and more specific information about where
the host is located in the Internet (that is, within which network, in the network of networks). Similarly, when we scan a postal address from bottom to
top, we obtain more and more specific information about where the addressee
is located.





### 2.4.1 Services Provided by DNS

We have just seen that there are two ways to identify a host—by a hostname
and by an IP address. People prefer the more mnemonic hostname identifier,
while routers prefer fixed-length, hierarchically structured IP addresses. In
order to reconcile these preferences, we need a directory service that translates
hostnames to IP addresses. This is the main task of the Internet’s domain name
system (DNS). The DNS is (1) a distributed database implemented in a hierarchy of DNS servers, and (2) an application-layer protocol that allows hosts to
query the distributed database. The DNS servers are often UNIX machines
running the Berkeley Internet Name Domain (BIND) software [BIND 2025].
The DNS protocol runs over UDP and uses port 53.
DNS is commonly employed by other application-layer protocols, including HTTP and SMTP, to translate user-supplied hostnames to IP addresses. As
an example, consider what happens when a browser (that is, an HTTP client),
running on some user’s host, requests the URL www.someschool.edu/
index.html. In order for the user’s host to be able to send an HTTP request
message to the Web server www.someschool.edu, the user’s host must first
obtain the IP address of www.someschool.edu. This is done as follows.
1. The same user machine runs the client side of the DNS application.
2. The browser extracts the hostname, www.someschool.edu, from the
URL and passes the hostname to the client side of the DNS application.
3. The DNS client sends a query containing the hostname to a DNS server.
4. The DNS client eventually receives a reply, which includes the IP address
for the hostname.
5. Once the browser receives the IP address from DNS, it can initiate a TCP
connection to the HTTP server process located at port 80 at that IP address.
We see from this example that DNS adds an additional delay—sometimes
substantial—to the Internet applications that use it. Fortunately, as we discuss
below, the desired IP address is often cached in a “nearby” DNS server, which
helps to reduce DNS network traffic as well as the average DNS delay.
DNS provides a few other important services in addition to translating
hostnames to IP addresses:
* Host aliasing. A host with a complicated hostname can have one or more
alias names. For example, a hostname such as relay1.west-coast.
enterprise.com could have, say, two aliases such as enterprise.com
and www.enterprise.com. In this case, the hostname relay1.westcoast.enterprise.com is said to be a canonical hostname. Alias hostnames, when present, are typically more mnemonic than canonical
hostnames. DNS can be invoked by an application to obtain the canonical
hostname for a supplied alias hostname as well as the IP address of the host.
* Mail server aliasing. For obvious reasons, it is highly desirable that e-mail
addresses be mnemonic. For example, if Bob has an account with Yahoo
Mail, Bob’s e-mail address might be as simple as bob@yahoo.com. However, the hostname of the Yahoo mail server is more complicated and


Application Layer

much less mnemonic than simply yahoo.com (for example, the canonical
hostname might be something like relay1.west-coast.yahoo.com).
DNS can be invoked by a mail application to obtain the canonical hostname for a supplied alias hostname as well as the IP address of the host. In
fact, the MX record (see below) permits a company’s mail server and Web
server to have identical (aliased) hostnames; for example, a company’s
Web server and mail server can both be called enterprise.com.
* Load distribution. DNS is also used to perform load distribution among
replicated servers, such as replicated Web servers. Busy sites, such as
cnn.com, are replicated over multiple servers, with each server running
on a different end system and each having a different IP address. For replicated Web servers, a set of IP addresses is thus associated with one alias
hostname. The DNS database contains this set of IP addresses. When clients make a DNS query for a name mapped to a set of addresses, the
server responds with the entire set of IP addresses, but rotates the ordering of the addresses within each reply. Because a client typically sends its
HTTP request message to the IP address that is listed first in the set, DNS
rotation distributes the traffic among the replicated servers. DNS rotation
is also used for e-mail so that multiple mail servers can have the same
alias name. Also, content distribution companies such as Akamai have
used DNS in more sophisticated ways [Nygren 2010] to provide Web content distribution (see Section 2.5.3).

Principles in Practice
DNS: Critical Network Functions Via
the Client-Server Paradigm
Like HTTP and SMTP, the DNS protocol is an application-layer protocol since it (1)
runs between communicating end systems using the client-server paradigm and
(2) relies on an underlying end-to-end transport protocol to transfer DNS messages
between communicating end systems. In another sense, however, the role of the
DNS is quite different from Web, file transfer, and e-mail applications. Unlike these
applications, the DNS is not an application with which a user directly interacts.
Instead, the DNS provides a core Internet function—namely, translating hostnames
to their underlying IP addresses, for user applications and other software in the
Internet. We noted in Section 1.2 that much of the complexity in the Internet
architecture is located at the “edges” of the network. The DNS, which implements
the critical name-to-address translation process using clients and servers located at
the edge of the network, is yet another example of that design philosophy.

The DNS is specified in RFC 1034 and RFC 1035, and updated in several
additional RFCs. It is a complex system, and we only touch upon key aspects
of its operation here. The interested reader is referred to these RFCs, the book
[Albitz 1993], and a recent description of Akamai’s DNS service [Schomp
2020]. See also the retrospectives [Mockapetris 1988; Mockapetris 2005] that
also provide a nice description of the what and why of DNS.





### 2.4.2 Overview of How DNS Works

We now present a high-level overview of how DNS works. Our discussion will
focus on the hostname-to-IP-address translation service.
Suppose that some application (such as a Web browser or a mail client)
running in a user’s host needs to translate a hostname to an IP address. The
application will invoke the client side of DNS, specifying the hostname that
needs to be translated. (On many UNIX-based machines, gethostbyname()
is the function call that an application calls in order to perform the translation.)
DNS in the user’s host then takes over, sending a query message into the network. All DNS query and reply messages are sent within UDP datagrams to
port 53. After a delay, ranging from milliseconds to seconds, DNS in the user’s
host receives a DNS reply message that provides the desired mapping. This
mapping is then passed to the invoking application. Thus, from the perspective of the invoking application in the user’s host, DNS is a black box providing
a simple, straightforward translation service. But in fact, the black box that
implements the service is complex, consisting of a large number of DNS servers distributed around the globe, as well as an application-layer protocol that
specifies how the DNS servers and querying hosts communicate.
A simple design for DNS would have one DNS server that contains all the
mappings. In this centralized design, clients simply direct all queries to the single DNS server, and the DNS server responds directly to the querying clients.
Although the simplicity of this design is attractive, it is inappropriate for
today’s Internet, with its vast (and growing) number of hosts. The problems
with a centralized design include:
* A single point of failure. If the DNS server crashes, so does the entire
Internet!
* Traffic volume. A single DNS server would have to handle all DNS queries (for all the HTTP requests and e-mail messages generated from hundreds of millions of hosts).
* Distant centralized database. A single DNS server cannot be “close to” all
the querying clients. If we put the single DNS server in New York City,
then all queries from Australia must travel to the other side of the globe,
perhaps over slow and congested links. This can lead to significant delays.
* Maintenance. The single DNS server would have to keep records for all
Internet hosts. Not only would this centralized database be huge, but it
would have to be updated frequently to account for every new host.
In summary, a centralized database in a single DNS server simply doesn’t
scale. Consequently, the DNS is distributed by design. In fact, the DNS is a
wonderful example of how a distributed database can be implemented in the
Internet.

A Distributed, Hierarchical Database
In order to deal with the issue of scale, the DNS uses a large number of servers,
organized in a hierarchical fashion and distributed around the world.


Application Layer


Figure 2.15 Portion
of the hierarchy of DNS
servers

No single DNS server has all of the mappings for all of the hosts in the Internet.
Instead, the mappings are distributed across the DNS servers. To a first approximation, there are three classes of DNS servers—root DNS servers, top-level
domain (TLD) DNS servers, and authoritative DNS servers—organized in a
hierarchy as shown in Figure 2.15. To understand how these three classes of
servers interact, suppose a DNS client wants to determine the IP address for
the hostname www.amazon.com. To a first approximation, the following
events will take place. The client first contacts one of the root servers, which
returns IP addresses for TLD servers for the top-level domain com. The client
then contacts one of these TLD servers, which returns the IP address of
an authoritative server for amazon.com. Finally, the client contacts one of the
authoritative servers for amazon.com, which returns the IP address for
the hostname www.amazon.com. We’ll soon examine this DNS lookup process in more detail. But let’s first take a closer look at these three classes of
DNS servers:
* Root DNS servers. There are nearly 2000 root servers instances scattered
all over the world, as shown in Figure 2.16, serving tens of billions of DNS
queries per day. These root servers are copies of 13 different root servers,

Figure 2.16 Number of root servers and locations (2024)


managed by 12 different organizations, and coordinated through the
Internet Assigned Numbers Authority [IANA 2025]. The full list of root
name servers, along with the organizations that manage them and their IP
addresses can be found at [Root Servers 2025]. Root name servers provide
the IP addresses of the TLD servers.
* Top-level domain (TLD) servers. For each of the top-level domains—­
top-level domains such as com, org, net, edu, and gov, and all of the country top-level domains such as uk, fr, ca, and jp—there is TLD server (or
server cluster). The company Verisign Global Registry Services maintains
the TLD servers for the com top-level domain, and the company Educause
maintains the TLD servers for the edu top-level domain. The network
infrastructure supporting a TLD can be large and complex; see [Osterweil
2012] for a nice overview of the Verisign network. See [TLD list 2025] for a
list of all top-level domains. TLD servers provide the IP addresses for
authoritative DNS servers.
* Authoritative DNS servers. Every organization with publicly accessible
hosts (such as Web servers and mail servers) on the Internet must provide publicly accessible DNS records that map the names of those hosts
to IP addresses. An organization’s authoritative DNS server houses these
DNS records. An organization can choose to implement its own authoritative DNS server to hold these records; alternatively, the organization
can pay to have these records stored in an authoritative DNS server of
some service provider. Most universities and large companies implement and maintain their own primary and secondary (backup) authoritative DNS server.
The root, TLD, and authoritative DNS servers all belong to the hierarchy
of DNS servers, as shown in Figure 2.15. There is another important type of
DNS server called the local DNS server. A local DNS server does not strictly
belong to the hierarchy of servers but is nevertheless central to the DNS architecture. Each ISP—such as a residential ISP or an institutional ISP—has a local
DNS server (also called a default name server). When a host connects to an ISP,
the ISP provides the host with the IP addresses of one or more of its local DNS
servers (typically through DHCP, which is discussed in Chapter 4). Rather
than using your ISPs or institution’s local DNS server, you can also configure
your device to receive its local DNS service from a commercial provider such
as Google (at IP address 8.8.8.8). You can easily determine the IP address of
your local DNS server by accessing network status windows in Windows or
UNIX. A host’s local DNS server is typically “close to” the host. For an institutional ISP, the local DNS server may be on the same LAN as the host; for a
residential ISP, it is typically separated from the host by no more than a few
routers. When a host makes a DNS query, the query is sent to the local DNS
server, which acts a proxy, forwarding the query into the DNS server hierarchy,
as we’ll discuss in more detail below.
Let’s take a look at a simple example. Suppose the host cse.nyu.edu
desires the IP address of gaia.cs.umass.edu. Also suppose that NYU’s local
DNS server for cse.nyu.edu is called dns.nyu.edu and that an authoritative DNS server for gaia.cs.umass.edu is called dns.umass.edu. As


Application Layer


Figure 2.17 Interaction

of the various DNS servers

shown in Figure 2.17, the host cse.nyu.edu first sends a DNS query message
to its local DNS server, dns.nyu.edu. The query message contains the hostname to be translated, namely, gaia.cs.umass.edu. The local DNS server
forwards the query message to a root DNS server. The root DNS server takes
note of the edu suffix and returns to the local DNS server a list of IP addresses
for TLD servers responsible for edu. The local DNS server then resends the
query message to one of these TLD servers. The TLD server takes note of the
umass.edu suffix and responds with the IP address of the authoritative DNS
server for the University of Massachusetts, namely, dns.umass.edu. Finally,
the local DNS server resends the query message directly to dns.umass.edu,
which responds with the IP address of gaia.cs.umass.edu. Note that in this
example, in order to obtain the mapping for one hostname, eight DNS messages were sent: four query messages and four reply messages! We’ll soon see
how DNS caching reduces this query traffic.
Our previous example assumed that the TLD server knows the authoritative DNS server for the hostname. In general, this is not always true. Instead,
the TLD server may know only of an intermediate DNS server, which in turn
knows the authoritative DNS server for the hostname. For example, suppose
again that the University of Massachusetts has a DNS server for the university,
called dns.umass.edu. Also suppose that each of the departments at the University of Massachusetts has its own DNS server, and that each departmental
DNS server is authoritative for all hosts in the department. In this case, when


the intermediate DNS server, dns.umass.edu, receives a query for a host
with a hostname ending with cs.umass.edu, it returns to dns.nyu.edu the
IP address of dns.cs.umass.edu, which is authoritative for all hostnames
ending with cs.umass.edu. The local DNS server dns.nyu.edu then sends
the query to the authoritative DNS server, which returns the desired mapping
to the local DNS server, which in turn returns the mapping to the requesting
host. In this case, a total of 10 DNS messages are sent!
The example shown in Figure 2.17 makes use of both recursive queries
and iterative queries. The query sent from cse.nyu.edu to dns.nyu.edu is
a recursive query, since the query asks dns.nyu.edu to obtain the mapping
on its behalf. However, the subsequent three queries are iterative since all of
the replies are directly returned to dns.nyu.edu. In theory, any DNS query
can be iterative or recursive. For example, Figure 2.18 shows a DNS query
chain for which all of the queries are recursive. In practice, the queries typically follow the pattern in Figure 2.17: The query from the requesting host to
the local DNS server is recursive, and the remaining queries are iterative.

DNS Caching
Our discussion thus far has ignored DNS caching, a critically important feature of the DNS system. In truth, DNS extensively exploits DNS caching in

Figure 2.18 Recursive

queries in DNS


Application Layer

order to improve the delay performance and to reduce the number of DNS
messages ricocheting around the Internet. The idea behind DNS caching is
very simple. In a query chain, when a DNS server receives a DNS reply (containing, for example, a mapping from a hostname to an IP address), it can
cache the mapping in its local memory. For example, in Figure 2.17, each time
the local DNS server dns.nyu.edu receives a reply from some DNS server, it
can cache any of the information contained in the reply. If a hostname/IP
address pair is cached in a DNS server and another query arrives to the DNS
server for the same hostname, the DNS server can provide the desired IP
address, even if it is not authoritative for the hostname. Because hosts and
mappings between hostnames and IP addresses are by no means permanent,
DNS servers discard cached information after a period of time (often set to
two days).
As an example, suppose that a host a p r i c o t . n y u . e d u queries
dns.nyu.edu for the IP address for the hostname cnn.com. Furthermore,
suppose that a few hours later, another NYU host, say, kiwi.nyu.edu, also
queries dns.nyu.edu with the same hostname. Because of caching, the local
DNS server will be able to immediately return the IP address of cnn.com to
this second requesting host without having to query any other DNS servers. A
local DNS server can also cache the IP addresses of TLD servers, thereby allowing the local DNS server to bypass the root DNS servers in a query chain. In
fact, because of caching, root servers are bypassed for all but a very small fraction of DNS queries.


### 2.4.3 DNS Records and Messages

The DNS servers that together implement the DNS distributed database store
resource records (RRs), including RRs that provide hostname-to-IP address
mappings. Each DNS reply message carries one or more resource records. In
this and the following subsection, we provide a brief overview of DNS resource
records and messages; more details can be found in [Albitz 1993] or in the DNS
RFCs [RFC 1034; RFC 1035].
A resource record is a four-tuple that contains the following fields:
(Name, Value, Type, TTL)
TTL is the time to live of the resource record; it determines when a resource
should be removed from a cache. In the example records given below, we
ignore the TTL field. The meaning of Name and Value depend on Type:
* If Type=A, then Name is a hostname and Value is the IP address for the
hostname. Thus, a Type A record provides the standard hostname-to-IP
address mapping. As an example, ( r e l a y 1 . b a r . f o o . c o m ,
145.37.93.126, A) is a Type A record.
* If Type=NS, then Name is a domain (such as foo.com) and Value is the
hostname of an authoritative DNS server that knows how to obtain the IP
addresses for hosts in the domain. This record is used to route DNS queries further along in the query chain. As an example, ( f o o . c o m,
dns.foo.com, NS) is a Type NS record.



* If Type=CNAME, then Value is a canonical hostname for the alias hostname Name. This record can provide querying hosts the canonical name
for a hostname. As an example, (foo.com, relay1.bar.foo.com,
CNAME) is a CNAME record.
* If Type=MX, then Value is the canonical name of a mail server that has
an alias hostname Name. As an example, (foo.com, mail.bar.foo.
com, MX) is an MX record. MX records allow the hostnames of mail servers to have simple aliases. Note that by using the MX record, a company
can have the same aliased name for its mail server and for one of its
other servers (such as its Web server). To obtain the canonical name for
the mail server, a DNS client would query for an MX record; to obtain
the canonical name for the other server, the DNS client would query for
the CNAME record.
If a DNS server is authoritative for a particular hostname, then the DNS
server will contain a Type A record for the hostname. (Even if the DNS server is
not authoritative, it may contain a Type A record in its cache.) If a server is not
authoritative for a hostname, then the server will contain a Type NS record for
the domain that includes the hostname; it will also contain a Type A record that
provides the IP address of the DNS server in the Value field of the NS record.
As an example, suppose an edu TLD server is not authoritative for the host
gaia.cs.umass.edu. Then this server will contain a record for a domain
that includes the host gaia.cs.umass.edu, for example, (umass.edu,
dns.umass.edu, NS). The edu TLD server would also contain a Type A
record, which maps the DNS server dns.umass.edu to an IP address, for
example, (dns.umass.edu, 128.119.40.111, A).

DNS Messages
Earlier in this section, we referred to DNS query and reply messages. These are
the only two kinds of DNS messages. Furthermore, both query and reply messages have the same format, as shown in Figure 2.19. The semantics of the
various fields in a DNS message are as follows:
* The first 12 bytes is the header section, which has a number of fields. The
first field is a 16-bit number that identifies the query. This identifier is copied into the reply message to a query, allowing the client to match received
replies with sent queries. There are a number of flags in the flag field. A
1-bit query/reply flag indicates whether the message is a query (0) or a
reply (1). A 1-bit authoritative flag is set in a reply message when a DNS
server is an authoritative server for a queried name. A 1-bit recursiondesired flag is set when a client (host or DNS server) desires that the DNS
server perform recursion when it doesn’t have the record. A 1-bit recursionavailable field is set in a reply if the DNS server supports recursion. In the
header, there are also four number-of fields. These fields indicate
the number of occurrences of the four types of data sections that follow
the header.
* The question section contains information about the query that is being
made. This section includes (1) a name field that contains the name that is


Application Layer

Figure 2.19 DNS

message format

being queried, and (2) a type field that indicates the type of question being
asked about the name—for example, a host address associated with a
name (Type A) or the mail server for a name (Type MX).
* In a reply from a DNS server, the answer section contains the resource
records for the name that was originally queried. Recall that in each
resource record there is the Type (for example, A, NS, CNAME, and MX),
the Value, and the TTL. A reply can return multiple RRs in the answer,
since a hostname can have multiple IP addresses (for example, for replicated Web servers, as discussed earlier in this section).
* The authority section contains records of other authoritative servers.
* The additional section contains other helpful records. For example, the
answer field in a reply to an MX query contains a resource record providing the canonical hostname of a mail server. The additional section contains a Type A record providing the IP address for the canonical hostname
of the mail server.
How would you like to send a DNS query message directly from the host
you’re working on to some DNS server? This can easily be done with the
nslookup program, which is available from most Windows and UNIX platforms. For example, from a Windows host, open the Command Prompt and
invoke the nslookup program by simply typing “nslookup.” After invoking
nslookup, you can send a DNS query to any DNS server (root, TLD, or authoritative). After receiving the reply message from the DNS server, nslookup will
display the records included in the reply (in a human-readable format). As an
alternative to running nslookup from your own host, you can visit one of many
Web sites that allow you to remotely employ nslookup. (Just type “nslookup”
into a search engine and you’ll be brought to one of these sites.) The DNS Wireshark lab at the end of this chapter will allow you to explore the DNS in much
more detail.




Inserting Records into the DNS Database
The discussion above focused on how records are retrieved from the DNS
database. You might be wondering how records get into the database in the
first place. Let’s look at how this is done in the context of a specific example.
Suppose you have just created an exciting new startup company called Network Utopia. The first thing you’ll surely want to do is register the domain
name networkutopia.com at a registrar. A registrar is a commercial entity
that verifies the uniqueness of the domain name, enters the domain name into
the DNS database (as discussed below), and collects a small fee from you for
its services. Prior to 1999, a single registrar, Network Solutions, had a monopoly on domain name registration for com, net, and org domains. But now
there are many registrars competing for customers, and the Internet Corporation for Assigned Names and Numbers (ICANN) accredits the various
registrars. A complete list of accredited registrars is available at http://www.
internic.net. In 2024, measurements [Sommese 2024] indicate that approximately 75 thousand new domain names are registered daily.
When you register the domain name networkutopia.com with some
registrar, you also need to provide the registrar with the names and IP
addresses of your primary and secondary authoritative DNS servers. Suppose
the names and IP addresses are dns1.networkutopia.com, dns2.networkutopia.com, 212.2.212.1, and 212.212.212.2. For each of these
two authoritative DNS servers, the registrar would then make sure that a Type
NS and a Type A record are entered into the TLD com servers. Specifically, for
the primary authoritative server for networkutopia.com, the registrar
would insert the following two resource records into the DNS system:
(networkutopia.com, dns1.networkutopia.com, NS)
(dns1.networkutopia.com, 212.212.212.1, A)

Focus on Security
DNS Vulnerabilities
We have seen that DNS is a critical component of the Internet infrastructure,
with many important services—including the Web and e-mail—simply incapable
of functioning without it. We therefore naturally ask, how can DNS be attacked?
Is DNS a sitting duck, waiting to be knocked out of service, while taking most
Internet applications down with it?
The first type of attack that comes to mind is a DDoS bandwidth-flooding
attack (see Section 1.6) against DNS servers. For example, an attacker could
attempt to send to each DNS root server a deluge of packets, so many that
the majority of legitimate DNS queries never get answered. Such a large-scale
DDoS attack against DNS root servers actually took place on October 21, 2002.
In this attack, the attackers leveraged a botnet to send truck loads of ICMP
ping messages to each of the 13 DNS root IP addresses. (ICMP messages
are discussed in Section 5.6. For now, it suffices to know that ICMP packets


Application Layer
are special types of IP datagrams.) Fortunately, this large-scale attack caused
minimal damage, having little or no impact on users’ Internet experience. The
attackers did succeed at directing a deluge of packets at the root servers. But
many of the DNS root servers were protected by packet filters, configured
to always block all ICMP ping messages directed at the root servers. These
protected servers were thus spared and functioned as normal. Furthermore,
most local DNS servers cache the IP addresses of top-level-domain servers,
allowing the query process to often bypass the DNS root servers.
A potentially more effective DDoS attack against DNS is send a deluge
of DNS queries to top-level-domain servers, for example, to top-level-domain
servers that handle the .com domain. It is harder to filter DNS queries directed
to DNS servers; and top-level-domain servers are not as easily bypassed as are
root servers. Such an attack took place against the top-level-domain service
provider Dyn on October 21, 2016. This DDoS attack was accomplished through
a large number of DNS lookup requests from a botnet consisting of about
one hundred thousand IoT devices such as printers, IP cameras, residential
gateways and baby monitors that had been infected with Mirai malware. For
almost a full day, Amazon, Twitter, Netflix, Github and Spotify were disturbed.
DNS could potentially be attacked in other ways. In a man-in-the-middle
attack, the attacker intercepts queries from hosts and returns bogus replies. In
the DNS poisoning attack, the attacker sends bogus replies to a DNS server,
tricking the server into accepting bogus records into its cache. Either of these
attacks could be used, for example, to redirect an unsuspecting Web user to
the attacker’s Web site. The DNS Security Extensions (DNSSEC [Gieben 2004;
RFC 4033] have been designed and deployed to protect against such exploits.
DNSSEC, a secured version of DNS, addresses many of these possible attacks
and is gaining popularity in the Internet.

You’ll also have to make sure that the Type A resource record for your Web
server www.networkutopia.com and the Type MX resource record for your
mail server mail.networkutopia.com are entered into your authoritative
DNS servers. (Until recently, the contents of each DNS server were configured
statically, for example, from a configuration file created by a system manager.
More recently, an UPDATE option has been added to the DNS protocol to
allow data to be dynamically added or deleted from the database via DNS
messages. [RFC 2136] and [RFC 3007] specify DNS dynamic updates.)
Once all of these steps are completed, people will be able to visit your Web
site and send e-mail to the employees at your company. Let’s conclude our discussion of DNS by verifying that this statement is true. This verification also
helps to solidify what we have learned about DNS. Suppose Alice in Australia
wants to view the Web page www.networkutopia.com. As discussed earlier,
her host will first send a DNS query to her local DNS server. The local DNS
server will then contact a TLD com server. (The local DNS server will also have
to contact a root DNS server if the address of a TLD com server is not cached.)
This TLD server contains the Type NS and Type A resource records listed
above, because the registrar had these resource records inserted into all of the
TLD com servers. The TLD com server sends a reply to Alice’s local DNS



server, with the reply containing the two resource records. The local DNS
server then sends a DNS query to 212.212.212.1, asking for the Type A
record corresponding to www.networkutopia.com. This record provides the
IP address of the desired Web server, say, 212.212.71.4, which the local
DNS server passes back to Alice’s host. Alice’s browser can now initiate a TCP
connection to the host 212.212.71.4 and send an HTTP request over the
connection. Whew! There’s a lot more going on than what meets the eye when
one surfs the Web!


## 2.5 Video Streaming and

Content Distribution
Networks
By many estimates, streaming video—including Netflix, YouTube, AppleTV,
Amazon Prime, and so on—account for more than 65% of global Internet traffic [Sandvine 2024] and nearly 75% of mobile network traffic [Ericsson 2024].
This section we will provide an overview of how popular video streaming services are implemented in today’s Internet.


### 2.5.1 Internet Video

In streaming stored video applications, the underlying medium is prerecorded
video, such as a movie, a television show, a prerecorded sporting event, or a
prerecorded user-generated video (such as those commonly seen on YouTube).
These prerecorded videos are placed on servers, and users send requests to the
servers to view the videos on demand. Many Internet companies today provide
streaming video, including, Netflix, YouTube (Google), Amazon, and TikTok.
But before launching into a discussion of video streaming, we should first
get a quick feel for the video medium itself. A video is a sequence of images,
typically being displayed at a constant rate, for example, at 24 or 30 images per
second. An uncompressed, digitally encoded image consists of an array of pixels, with each pixel encoded into a number of bits to represent luminance and
color. An important characteristic of video is that it can be compressed, thereby
trading off video quality with bit rate. Today’s off-the-shelf compression algorithms can compress a video to essentially any bit rate desired. Of course, the
higher the bit rate, the better the image quality and the better the overall user
viewing experience.
From a networking perspective, perhaps the most salient characteristic of
video is its high bit rate. Compressed Internet video typically ranges from
100 kbps for low-quality video to 25 Mbps for ultra high definition video.
This can translate to huge amount of traffic and storage, particularly for highend video. For example, a single 7 Mbps video with a duration of one hour
will consume 3 gigabytes of storage and traffic. By far, the most important performance measure for streaming video is average end-to-end throughput. In
order to provide continuous playout, the network must provide an average


Application Layer

throughput to the streaming application that is at least as large as the bit rate of
the compressed video.
We can also use compression to create multiple versions of the same video,
each at a different quality level. For example, we can use compression to create, say, three versions of the same video, at rates of 300 kbps, 1 Mbps, and
3 Mbps. Users can then decide which version they want to watch as a function
of their current available bandwidth. Users with high-speed Internet connections might choose the 3 Mbps version; users watching the video over 3G with
a smartphone might choose the 300 kbps version.


### 2.5.2 HTTP Streaming and DASH

In HTTP streaming, the video is simply stored at an HTTP server as an ordinary file with a specific URL. When a user wants to see the video, the client
establishes a TCP connection with the server and issues an HTTP GET request
for that URL. The server then sends the video file, within an HTTP response
message, as quickly as the underlying network protocols and traffic conditions
will allow. On the client side, the bytes are collected in a client application buffer. Once the number of bytes in this buffer exceeds a predetermined threshold,
the client application begins playback—specifically, the streaming video application periodically grabs video frames from the client application buffer,
decompresses the frames, and displays them on the user’s screen. Thus, the
video streaming application is displaying video as it is receiving and buffering
frames corresponding to latter parts of the video.
Although HTTP streaming, as described in the previous paragraph, has
been extensively deployed in practice (for example, by YouTube since its inception), it has a major shortcoming: All clients receive the same encoding of the
video, despite the large variations in the amount of bandwidth available to a
client, both across different clients and also over time for the same client. This
has led to the development of a new type of HTTP-based streaming, often
referred to as Dynamic Adaptive Streaming over HTTP (DASH). In DASH,
the video is encoded into several different versions, with each version having a
different bit rate and, correspondingly, a different quality level. The client
dynamically requests chunks of video segments of a few seconds in length.
When the amount of available bandwidth is high, the client naturally selects
chunks from a high-rate version; and when the available bandwidth is low, it
naturally selects from a low-rate version. The client selects different chunks
one at a time with HTTP GET request messages [Akhshabi 2011].
DASH allows clients with different Internet access rates to stream in video at
different encoding rates. Clients with low-speed 3G connections can receive a
low bit-rate (and low-quality) version, and clients with fiber connections can
receive a high-quality version. DASH also allows a client to adapt to the available
bandwidth if the available end-to-end bandwidth changes during the session.
This feature is particularly important for mobile users, who typically see their
bandwidth availability fluctuate as they move with respect to the base stations.
With DASH, each video version is stored in the HTTP server, each with a
different URL. The HTTP server also has a manifest file, which provides a
URL for each version along with its bit rate. The client first requests the



manifest file and learns about the various versions. The client then selects one
chunk at a time by specifying a URL and a byte range in an HTTP GET request
message for each chunk. While downloading chunks, the client also measures
the received bandwidth and runs a rate determination algorithm to select the
chunk to request next. Naturally, if the client has a lot of video buffered and if
the measured receive bandwidth is high, it will choose a chunk from a highbitrate version. And naturally if the client has little video buffered and the
measured received bandwidth is low, it will choose a chunk from a low-bitrate
version. DASH therefore allows the client to freely switch among different
quality levels.


### 2.5.3 Content Distribution Networks

Today, many Internet video companies are distributing on-demand multiMbps streams to millions of users on a daily basis. YouTube, for example, with
a library of hundreds of millions of videos, distributes hundreds of millions of
video streams to users around the world every day. Streaming all this traffic to
locations all over the world while providing continuous playout and high
interactivity is clearly a challenging task.
For an Internet video company, perhaps the most straightforward
approach to providing streaming video service is to build a single massive
data center, store all of its videos in the data center, and stream the videos
directly from the data center to clients worldwide. But there are three major
problems with this approach. First, if the client is far from the data center,
server-to-client packets will cross many communication links and likely pass
through many ISPs, with some of the ISPs possibly located on different continents. If one of these links provides a throughput that is less than the video
consumption rate, the end-to-end throughput will also be below the consumption rate, resulting in annoying freezing delays for the user. (Recall from
throughput at the bottleneck link.) The likelihood of this happening increases
as the number of links in the end-to-end path increases. A second drawback is
that a popular video will likely be sent many times over the same communication links. Not only does this waste network bandwidth, but the Internet video
company itself will be paying its provider ISP (connected to the data center)
for sending the same bytes into the Internet over and over again. A third problem with this solution is that a single data center represents a single point of
failure—if the data center or its links to the Internet goes down, it would not be
able to distribute any video streams.
In order to meet the challenge of distributing massive amounts of video
data to users distributed around the world, almost all major video-streaming
companies make use of Content Distribution Networks (CDNs). A CDN
manages servers in multiple geographically distributed locations, stores copies
of the videos (and other types of Web content, including documents, images,
and audio) in its servers, and attempts to direct each user request to a CDN
location that will provide the best user experience. The CDN may be a private
CDN, that is, owned by the content provider itself; for example, Google’s CDN
distributes YouTube videos and other types of content. The CDN may


Application Layer

alternatively be a third-party CDN that distributes content on behalf of multiple content providers; Akamai, Cloudflare, and Amazon Cloudfront all operate
third-party CDNs. A very readable overview of modern CDNs is [Leighton
2009; Nygren 2010].
CDNs typically adopt one of two different server placement philosophies
[Huang 2008]:
* Enter Deep. One philosophy, pioneered by Akamai, is to enter deep into
the access networks of Internet Service Providers, by deploying server
clusters in access ISPs all over the world. (Access networks are described
in Section 1.3.) Akamai takes this approach with clusters in thousands of
locations. The goal is to get close to end users, thereby improving userperceived delay and throughput by decreasing the number of links and
routers between the end user and the CDN server from which it receives
content. Because of this highly distributed design, the task of maintaining
and managing the clusters becomes challenging.
* Bring Home. A second design philosophy, taken by Limelight and many
other CDN companies, is to bring the ISPs home by building large clusters
at a smaller number (for example, tens) of sites. Instead of getting inside
the access ISPs, these CDNs typically place their clusters in Internet
Exchange Points (IXPs) (see Section 1.3). Compared with the enter-deep
design philosophy, the bring-home design typically results in lower maintenance and management overhead, possibly at the expense of higher
delay and lower throughput to end users.
Once its clusters are in place, the CDN replicates content across its clusters. The CDN may not want to place a copy of every video in each cluster,
since some videos are rarely viewed or are only popular in some countries. In
fact, many CDNs do not push videos to their clusters but instead use a simple
pull strategy: If a client requests a video from a cluster that is not storing the
video, then the cluster retrieves the video (from a central repository or from
another cluster) and stores a copy locally while streaming the video to the client at the same time. When a cluster’s storage becomes full, it removes videos
that are not frequently requested.

CDN Operation
Having identified the two major approaches toward deploying a CDN, let’s
now dive down into the nuts and bolts of how a CDN operates. When a
browser in a user’s host is instructed to retrieve a specific video (identified by a
URL), the CDN must intercept the request so that it can (1) determine a suitable CDN server cluster for that client at that time, and (2) redirect the client’s
request to a server in that cluster. We’ll shortly discuss how a CDN can determine a suitable cluster. But first let’s examine the mechanics behind
intercepting and redirecting a request.
Most CDNs take advantage of DNS to intercept and redirect requests; an
interesting discussion of such a use of the DNS is [Vixie 2009]. Let’s consider a
simple example to illustrate how the DNS is typically involved. Suppose a
content provider, NetCinema, employs the third-party CDN company,




Figure 2.20 DNS
redirects a user’s request
to a CDN server

KingCDN, to distribute its videos to its customers. On the NetCinema Web
pages, each of its videos is assigned a URL that includes the string “video”
and a unique identifier for the video itself; for example, Transformers 7 might
be assigned http://video.netcinema.com/6Y7B23V. Six steps then occur, as
shown in Figure 2.20:
1. The user visits the Web page at NetCinema.
2. When the user clicks on the link http://video.netcinema.com/6Y7B23V,
the user’s host sends a DNS query for video.netcinema.com.
3. The user’s Local DNS Server (LDNS) relays the DNS query to an authoritative DNS server for NetCinema, which observes the string “video” in
the hostname video.netcinema.com. To “hand over” the DNS query to
KingCDN, instead of returning an IP address, the NetCinema authoritative DNS server returns to the LDNS a hostname in the KingCDN’s
domain, for example, a1105.kingcdn.com.
4. From this point on, the DNS query enters into KingCDN’s private DNS
infrastructure. The user’s LDNS then sends a second query, now for a1105.
kingcdn.com, and KingCDN’s DNS system eventually returns the IP
addresses of a KingCDN content server to the LDNS. It is thus here, within
the KingCDN’s DNS system, that the CDN server from which the client
will receive its content is specified.
5. The LDNS forwards the IP address of the content-serving CDN node to
the user’s host.
6. Once the client receives the IP address for a KingCDN content server, it
establishes a direct TCP connection with the server at that IP address and
issues an HTTP GET request for the video. If DASH is used, the server will
first send to the client a manifest file with a list of URLs, one for each version of the video, and the client will dynamically select chunks from the
different versions.


Application Layer

Cluster Selection Strategies
At the core of any CDN deployment is a cluster selection strategy, that is, a
mechanism for dynamically directing clients to a server cluster or a data center
within the CDN. As we just saw, the CDN learns the IP address of the client’s
LDNS server via the client’s DNS lookup. After learning this IP address, the
CDN needs to select an appropriate cluster based on this IP address. CDNs generally employ proprietary cluster selection strategies. We now briefly survey a
few approaches, each of which has its own advantages and disadvantages.
One simple strategy is to assign the client to the cluster that is geographically closest. Using commercial geo-location databases (such as Quova [Quova
2025] and Max-Mind [MaxMind 2025]), each LDNS IP address is mapped to a
geographic location. When a DNS request is received from a particular LDNS,
the CDN chooses the geographically closest cluster, that is, the cluster that is
the fewest kilometers from the LDNS “as the bird flies.” Such a solution can
work reasonably well for a large fraction of the clients [Agarwal 2009]. However, for some clients, the solution may perform poorly, since the geographically
closest cluster may not be the closest cluster in terms of the length or number
of hops of the network path. Furthermore, a problem inherent with all DNSbased approaches is that some end-users are configured to use remotely
located LDNSs [Shaikh 2001; Mao 2002], in which case the LDNS location may
be far from the client’s location. Moreover, this simple strategy ignores the
variation in delay and available bandwidth over time of Internet paths, always
assigning the same cluster to a particular client.
In order to determine the best cluster for a client based on the current traffic conditions, CDNs can instead perform periodic real-time measurements of
delay and loss performance between their clusters and clients. For instance, a
CDN can have each of its clusters periodically send probes (for example, ping
messages or DNS queries) to all of the LDNSs around the world. One drawback of this approach is that many LDNSs are configured to not respond to
such probes.

CDN Caching
A CDN may have servers in hundreds or thousands of different geographical
locations. Putting all of its content in all of these geographical locations may
not only incur high network distribution costs, but may also demand excessive
storage capacity in the various locations. For this reason, a CDN typically
places different subsets of its content in different geographical locations. Since
each location will typically remove, on a regular basis, some of its content to
make room for fresher content or content that is in greater demand, the servers
located at a particular location are collectively referred to as a cache.
A CDN has at its disposal two fundamental strategies for placing video
files (and other content) in its caches: push and pull. In the push strategy, the
CDN forecasts which videos will be in greatest demand at each of its geographical locations. The CDN central servers will then send to each of its
geographical locations the videos that it expects to be in highest demand for
those locations. As described in Section 2.5.4, the video streaming company
Netflix takes this push approach. In the pull strategy, when a user makes a



request for a video, the user first gets redirected to a nearby cache in the CDN.
If that cache has a copy of the video, then the cache streams the video to
the user using, for example, the DASH protocol. However, if there is a cache
miss—that is if the cache doesn’t have a copy of the requested video—the
cache first retrieves the video from one the CDN’s central servers, stores
the video in the local cache, and streams the video to the requesting user. In
order to reduce latency, once the cache has received the beginning of the video
from the central CDN server, it may start the streaming while in parallel receiving the remainder of the video. As described in Section 2.5.4, the video sharing
service YouTube takes this pull approach. Akamai (see sidebar) combines both
a push and a pull approach.

Case Study
Akamai: Living on the Edge
for a Quarter Century
Akamai has been a pioneer of CDN delivery of content since the late 1990’s
[Spinrad 1999, Leighton 2000] and has evolved to also provide general edgebased computing services for companies that want to provide content and
computing “close” to the company’s customers, i.e., at the network’s edge. In
late 2023, Akamai truly operated at “Internet scale,” with more than 360,000
servers in 4,200 edge locations in more than 1,350 networks, and delivering
more than 175 Terabit per second of data to end users [Sitaraman 2023].
At the heart of the Akamai CDN are (i) its content replication/placement
algorithms that scale the number of replicated instances of content, e.g.,
in response to flash crowds, according to demand, and seeks to place that
content “close” to requesting users, and (ii) a redirection service, [Leighton 2000,
Nygren 2010] similar to that shown in Figure 2.20, to direct a user’s request for
content to a nearby copy at an available server. More detailed descriptions of
Akamai’s algorithms and services can be found at the reference above.

Case Study
Google’s Data Center and Network
Infrastructure
To support its vast array of services—including search, Gmail, calendar,
YouTube video, maps, documents, and social networks—Google has deployed
an extensive private network and data center infrastructure. Google’s worldwide
infrastructure has two tiers of data centers, interconnected by an internal private
network and connected to the ISPs at hundreds of peering points:

* Large Scale data centers. Google current has twenty three “mega data
centers” in North and South America, Europe, and Asia [Google data


Application Layer
centers 2024], with each data center having on the order of perhaps
100,000 servers. These large-scale data centers are responsible for serving
dynamic (and often personalized) content, including search results and
Gmail messages.

* Network Edge sites. More than 100 Google Global Cache (GGC) sites and
140 network edge sites [Diot 2022] that allow ISPs to serve relatively static
Google content (e.g., YouTube and Google Play) from within their own networks. Google traffic management systems directs user requests a nearby
Google edge location for service. This near-to-the user (and often withinthe-user’s-ISP) servicing of user requests helps ensure a high-quality user
experiences and frees the ISP from having to carry traffic from outside its
ISP, though the network to the end-user.

* Network connectivity. Google runs its own private global wide-area network, known as B4 [Jain 2013] to connect its data centers. We’ll discuss
the control and management of Googles B4 network in Chapter 5. Google’s
Edge Points of Presence (POPs) connect to ISP and private networks at
more than 200 IXPs (Figure 1.15) and at over 100 interconnection facilities
around the world.

* Google cloud. In addition to the large-scale and edge infrastructure that
provide Google services to users, Google also provides cloud hosting and
application services for third-party Internet services. For example, Spotify
uses Google cloud to run its (Spotify’s) services. In the Fall of 2024, Google
had Cloud data centers in 40 regions around the world [Statista Google
Cloud 2024; Google Cloud 2025].
As noted above, all of these data centers are networked together with
Google’s own private network. When a user makes a search query, often the
query is first sent over the local ISP to a nearby enter-deep cache, from where
the static content can be retrieved; while providing the static content to the
client, the nearby cache also forwards the query over Google’s private network
to one of the mega data centers, from where the personalized search results are
retrieved. For a YouTube video, the video itself may come from one of the bringhome caches, whereas portions of the Web page surrounding the video may
come from the nearby enter-deep cache, and the advertisements surrounding
the video come from the data centers.


### 2.5.4 Case Studies: Netflix and YouTube

We conclude our discussion of streaming stored video by taking a look at two
highly successful large-scale deployments: Netflix and YouTube. We’ll see that
each of these systems take a very different approach, yet employ many of the
underlying principles discussed in this section.

Netflix
As of 2025, Netflix is one of the leading service providers for online movies
and TV series in North America. As we discuss below, Netflix video




Figure 2.21 Netflix
video streaming platform

distribution has two major components: the Amazon cloud and its own private
CDN infrastructure.
Netflix has a Web site that handles numerous functions, including user registration and login, billing, movie catalogue for browsing and searching, and a
movie recommendation system. As shown in Figure 2.21, this Web site (and its
associated backend databases) run entirely on Amazon servers in the Amazon
cloud. Additionally, the Amazon cloud handles the following critical functions:
* Content ingestion. Before Netflix can distribute a movie to its customers,
it must first ingest and process the movie. Netflix receives studio master
versions of movies and uploads them to hosts in the Amazon cloud.
* Content processing. The machines in the Amazon cloud create many different formats for each movie, suitable for a diverse array of client video
players running on desktop computers, smartphones, and game consoles
connected to televisions. A different version is created for each of these
formats and at multiple bit rates, allowing for adaptive streaming over
HTTP using DASH.
* Uploading versions to its CDN. Once all of the versions of a movie have
been created, the hosts in the Amazon cloud upload the versions to its CDN.
When Netflix first rolled out its video streaming service in 2007, it
employed three third-party CDN companies to distribute its video content.
Netflix has since created its own private CDN, called Open Connect, from
which it now streams all of its videos. To create its own CDN, Netflix has
installed server racks both in IXPs and within residential ISPs themselves. Netflix currently has server racks in over 200 IXP locations; see [Bottger 2018]
[Netflix Open Connect 2025] for a current list of IXPs housing Netflix racks.
There are also hundreds of ISP locations housing Netflix racks; also see [Netflix
Open Connect 2025], where Netflix provides to potential ISP partners


Application Layer

instructions about installing a (free) Netflix rack for their networks. Each server
in the rack has several 10 Gbps Ethernet ports and over 100 terabytes of storage. The number of servers in a rack varies: IXP installations often have tens of
servers and contain the entire Netflix streaming video library, including multiple versions of the videos to support DASH. Netflix does not use pull-caching
(Section 2.5.4) to populate its CDN servers in the IXPs and ISPs. Instead, Netflix
distributes by pushing the videos to its CDN servers during off-peak hours. For
those locations that cannot hold the entire library, Netflix pushes only the most
popular videos, which are determined on a day-to-day basis. The Netflix CDN
design is described in some detail in the YouTube videos [Netflix Video 1] and
[Netflix Video 2]; see also [Bottger 2018]. An excellent and accessible overview
of Netflix’s architecture, algorithms, and operation is [Teixeira 2021].
Having described the components of the Netflix architecture, let’s take a
closer look at the interaction between the client and the various servers that are
involved in movie delivery. As indicated earlier, the Web pages for browsing
the Netflix video library are served from servers in the Amazon cloud. When a
user selects a movie to play, the Netflix software, running in the Amazon
cloud, first determines which of its CDN servers have copies of the movie.
Among the servers that have the movie, the software then determines the
“best” server for that client request. If the client is using a residential ISP that
has a Netflix CDN server rack installed in that ISP, and this rack has a copy of
the requested movie, then a server in this rack is typically selected. If not, a
server at a nearby IXP is typically selected.
Once Netflix determines the CDN server that is to deliver the content, it
sends the client the IP address of the specific server as well as a manifest file,
which has the URLs for the different versions of the requested movie. The client and that CDN server then directly interact using a proprietary version of
DASH. Specifically, as described in Section 2.5.2, the client uses the byte-range
header in HTTP GET request messages, to request chunks from the different
versions of the movie. Netflix uses chunks that are approximately four-­seconds
long [Adhikari 2012]. While the chunks are being downloaded, the client measures the received throughput and runs a rate-determination algorithm to
determine the quality of the next chunk to request.
Netflix embodies many of the key principles discussed earlier in this section, including adaptive streaming and CDN distribution. However, because
Netflix uses its own private CDN, which distributes only video (and not Web
pages), Netflix has been able to simplify and tailor its CDN design. In particular, Netflix does not need to employ DNS redirect, as discussed in Section 2.5.3,
to connect a particular client to a CDN server; instead, the Netflix software
(running in the Amazon cloud) directly tells the client to use a particular CDN
server. Furthermore, the Netflix CDN uses push caching rather than pull caching (Section 2.5.4): content is pushed into the servers at scheduled times at
off-peak hours, rather than dynamically during cache misses.

YouTube
With hundreds of hours of video uploaded to YouTube every minute and several billion video views per day, YouTube is indisputably the world’s largest



video-sharing site. YouTube began its service in April 2005 and was acquired
by Google in November 2006. Although the Google/YouTube design and protocols are proprietary, through several independent measurement efforts we
can gain a basic understanding about how YouTube operates [Zink 2009; ­Torres
2011; Adhikari 2011a]. As with Netflix, YouTube makes extensive use of CDN
technology to distribute its videos [Torres 2011]. Similar to Netflix, Google uses
its own private CDN to distribute YouTube videos, and has installed server
clusters in many hundreds of different IXP and ISP locations. From these locations and directly from its huge data centers, Google distributes YouTube
videos [Adhikari 2011a]. Unlike Netflix, however, Google uses pull caching, as
described in Section 2.5.3, and DNS redirect, as also described in Section 2.5.3.
Most of the time, Google’s cluster-selection strategy directs the client to the
cluster for which the RTT between client and cluster is the lowest; however, in
order to balance the load across clusters, sometimes the client is directed (via
DNS) to a more distant cluster [Torres 2011].
Several million videos are uploaded to YouTube every day. Not only are
YouTube videos streamed from server to client over HTTP, but YouTube
uploaders also upload their videos from client to server over HTTP. YouTube
processes each video it receives, converting it to a YouTube video format and
creating multiple versions at different bit rates. This processing takes place
entirely within Google data centers. (See the case study on Google’s network
infrastructure in Section 2.5.3.)


## 2.6 Socket Programming:

Creating Network
Applications
Now that we’ve looked at a number of important network applications, let’s
explore how network application programs are actually created. Recall from
Section 2.1 that a typical network application consists of a pair of programs—a
client program and a server program—residing in two different end systems.
When these two programs are executed, a client process and a server process
are created, and these processes communicate with each other by reading
from, and writing to, sockets. When creating a network application, the developer’s main task is therefore to write the code for both the client and server
programs.
There are two types of network applications. One type is an implementation whose operation is specified in a protocol standard, such as an RFC or
some other standards document; such an application is sometimes referred to
as “open,” since the rules specifying its operation are known to all. For such an
implementation, the client and server programs must conform to the rules dictated by the RFC. For example, the client program could be an implementation
of the client side of the HTTP protocol, described in Section 2.2 and precisely
defined in RFC 2616; similarly, the server program could be an implementation
of the HTTP server protocol, also precisely defined in RFC 2616. If one


Application Layer

developer writes code for the client program and another developer writes
code for the server program, and both developers carefully follow the rules of
the RFC, then the two programs will be able to interoperate. Indeed, many of
today’s network applications involve communication between client and
server programs that have been created by independent developers—for
example, a Google Chrome browser communicating with an Apache Web
server, or a BitTorrent client communicating with BitTorrent tracker.
The other type of network application is a proprietary network application. In this case, the client and server programs employ an application-layer
protocol that has not been openly published in an RFC or elsewhere. A single
developer (or development team) creates both the client and server programs,
and the developer has complete control over what goes in the code. But
because the code does not implement an open protocol, other independent
developers will not be able to develop code that interoperates with the
application.
In this section, we’ll examine the key issues in developing a client-server
application, and we’ll “get our hands dirty” by looking at code that implements a very simple client-server application. During the development phase,
one of the first decisions the developer must make is whether the application
is to run over TCP or over UDP. Recall that TCP is connection oriented and
provides a reliable byte-stream channel through which data flows between
two end systems. UDP is connectionless and sends independent packets of
data from one end system to the other, without any guarantees about delivery.
Recall also that when a client or server program implements a protocol
defined by an RFC, it should use the well-known port number associated with
the protocol; conversely, when developing a proprietary application, the
developer must be careful to avoid using such well-known port numbers.
(Port numbers were briefly discussed in Section 2.1. They are covered in more
detail in Chapter 3.)
We introduce UDP and TCP socket programming by way of a simple UDP
application and a simple TCP application. We present the simple UDP and
TCP applications in Python 3. We could have written the code in Java, C, or
C++, but we chose Python mostly because Python clearly exposes the key
socket concepts. With Python there are fewer lines of code, and each line can be
explained to the novice programmer without difficulty. But there’s no need to
be frightened if you are not familiar with Python. You should be able to easily
follow the code if you have experience programming in Java, C, or C++.
If you are interested in client-server programming with Java, you are
encouraged to see the Companion Website for this textbook; in fact, you can
find there all the examples in this section (and associated labs) in Java. For
readers who are interested in client-server programming in C, there are several
good references available [Donahoo 2001; Stevens 1997; Frost 1994]; our Python
examples below have a similar look and feel to C.


### 2.6.1 Socket Programming with UDP

In this subsection, we’ll write simple client-server programs that use UDP; in
the following section, we’ll write similar programs that use TCP.



Recall from Section 2.1 that processes running on different machines communicate with each other by sending messages into sockets. We said that each
process is analogous to a house and the process’s socket is analogous to a door.
The application resides on one side of the door in the house; the transportlayer protocol resides on the other side of the door in the outside world. The
application developer has control of everything on the application-layer side
of the socket; however, it has little control of the transport-layer side.
Now let’s take a closer look at the interaction between two communicating processes that use UDP sockets. Before the sending process can push a
packet of data out the socket door, when using UDP, it must first attach a destination address to the packet. After the packet passes through the sender’s
socket, the Internet will use this destination address to route the packet
through the Internet to the socket in the receiving process. When
the packet arrives at the receiving socket, the receiving process will retrieve the
packet through the socket, and then inspect the packet’s contents and take
appropriate action.
So you may be now wondering, what goes into the destination address
that is attached to the packet? As you might expect, the destination host’s IP
address is part of the destination address. By including the destination IP
address in the packet, the routers in the Internet will be able to route the packet
through the Internet to the destination host. But because a host may be running
many network application processes, each with one or more sockets, it is also
necessary to identify the particular socket in the destination host. When a socket
is created, an identifier, called a port number, is assigned to it. So, as you might
expect, the packet’s destination address also includes the socket’s port number.
In summary, the sending process attaches to the packet a destination address,
which consists of the destination host’s IP address and the destination socket’s
port number. Moreover, as we shall soon see, the sender’s source address—­
consisting of the IP address of the source host and the port number of the source
socket—are also attached to the packet. However, attaching the source address
to the packet is typically not done by the UDP application code; instead it is
automatically done by the underlying operating system.
We’ll use the following simple client-server application to demonstrate
socket programming for both UDP and TCP:
1. The client reads a line of characters (data) from its keyboard and sends the
data to the server.
2. The server receives the data and converts the characters to uppercase.
3. The server sends the modified data to the client.
4. The client receives the modified data and displays the line on its screen.
Figure 2.22 highlights the main socket-related activity of the client and
server that communicate over the UDP transport service.
Now let’s get our hands dirty and take a look at the client-server program
pair for a UDP implementation of this simple application. We also provide a
detailed, line-by-line analysis after each program. We’ll begin with the UDP
client, which will send a simple application-level message to the server. In
order for the server to be able to receive and reply to the client’s message, it


Application Layer

Figure 2.22 The client-server application using UDP

must be ready and running—that is, it must be running as a process before the
client sends its message.
The client program is called UDPClient.py, and the server program is
called UDPServer.py. In order to emphasize the key issues, we intentionally
provide code that is minimal. “Good code” would certainly have a few more
auxiliary lines, in particular for handling error cases. For this application, we
have arbitrarily chosen 12000 for the server port number.

UDPClient.py
Here is the code for the client side of the application:
from socket import *
serverName = 'hostname'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input('Input lowercase sentence:')
clientSocket.sendto(message.encode(),(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()
Now let’s take a look at the various lines of code in UDPClient.py.
from socket import *



The socket module forms the basis of all network communications in Python.
By including this line, we will be able to create sockets within our program.
serverName = 'hostname'
serverPort = 12000
The first line sets the variable serverName to the string ‘hostname’. Here, we
provide a string containing either the IP address of the server (e.g.,
“128.138.32.126”) or the hostname of the server (e.g., “cis.poly.edu”). If we use
the hostname, then a DNS lookup will automatically be performed to get the
IP address.) The second line sets the integer variable serverPort to 12000.
clientSocket = socket(AF_INET, SOCK_DGRAM)
This line creates the client’s socket, called clientSocket. The first parameter
indicates the address family; in particular, AF_INET indicates that the underlying network is using IPv4. (Do not worry about this now—we will discuss
IPv4 in Chapter 4.) The second parameter indicates that the socket is of type
SOCK_DGRAM, which means it is a UDP socket (rather than a TCP socket).
Note that we are not specifying the port number of the client socket when we
create it; we are instead letting the operating system do this for us. Now that
the client process’s door has been created, we will want to create a message to
send through the door.
message = input('Input lowercase sentence:')
input() is a built-in function in Python. When this command is executed, the
user at the client is prompted with the words “Input lowercase sentence:”
The user then uses her keyboard to input a line, which is put into the variable
message. Now that we have a socket and a message, we will want to send
the message through the socket to the destination host.
clientSocket.sendto(message.encode(), (serverName, serverPort))
In the above line, we first convert the message from string type to byte type, as
we need to send bytes into a socket; this is done with the encode() method.
The method sendto() attaches the destination address (serverName,
serverPort) to the message and sends the resulting packet into the process’s
socket, clientSocket. (As mentioned earlier, the source address is also
attached to the packet, although this is done automatically rather than explicitly by the code.) Sending a client-to-server message via a UDP socket is
that simple! After sending the packet, the client waits to receive data from
the server.
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
With the above line, when a packet arrives from the Internet at the client’s
socket, the packet’s data is put into the variable modifiedMessage and the
packet’s source address is put into the variable serverAddress. The variable
serverAddress contains both the server’s IP address and the server’s port
number. The program UDPClient doesn’t actually need this server address
information, since it already knows the server address from the outset; but this
line of Python provides the server address nevertheless. The method


Application Layer

recvfrom also takes the buffer size 2048 as input. (This buffer size works for
most purposes.)
print(modifiedMessage.decode())
This line prints out modifiedMessage on the user’s display, after converting
the message from bytes to string. It should be the original line that the user
typed, but now capitalized.
clientSocket.close()
This line closes the socket. The process then terminates.

UDPServer.py
Let’s now take a look at the server side of the application:
from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((", serverPort))
print("The server is ready to receive")
while True:
message, clientAddress = serverSocket.recvfrom(2048)
modifiedMessage = message.decode().upper()
serverSocket.sendto(modifiedMessage.encode(),
clientAddress)
Note that the beginning of UDPServer is similar to UDPClient. It also imports
the socket module, also sets the integer variable serverPort to 12000, and
also creates a socket of type SOCK_DGRAM (a UDP socket). The first line of code
that is significantly different from UDPClient is:
serverSocket.bind((", serverPort))
The above line binds (that is, assigns) the port number 12000 to the server’s
socket. Thus, in UDPServer, the code (written by the application developer) is
explicitly assigning a port number to the socket. In this manner, when anyone
sends a packet to port 12000 at the IP address of the server, that packet will be
directed to this socket. UDPServer then enters a while loop; the while loop will
allow UDPServer to receive and process packets from clients indefinitely. In
the while loop, UDPServer waits for a packet to arrive.
message, clientAddress = serverSocket.recvfrom(2048)
This line of code is similar to what we saw in UDPClient. When a packet
arrives at the server’s socket, the packet’s data is put into the variable ­message
and the packet’s source address is put into the variable clientAddress. The
variable clientAddress contains both the client’s IP address and the client’s
port number. Here, UDPServer will make use of this address information, as it
provides a return address, similar to the return address with ordinary postal
mail. With this source address information, the server now knows to where it
should direct its reply.
modifiedMessage = message.decode().upper()



This line is the heart of our simple application. It takes the line sent by the client and, after converting the message to a string, uses the method upper() to
capitalize it.
serverSocket.sendto(modifiedMessage.encode(), clientAddress)
This last line attaches the client’s address (IP address and port number) to the
capitalized message (after converting the string to bytes), and sends the resulting packet into the server’s socket. (As mentioned earlier, the server address is
also attached to the packet, although this is done automatically rather than
explicitly by the code.) The Internet will then deliver the packet to this client
address. After the server sends the packet, it remains in the while loop, waiting
for another UDP packet to arrive (from any client running on any host).
To test the pair of programs, you run UDPClient.py on one host and
UDPServer.py on another host. Be sure to include the proper hostname or IP
address of the server in UDPClient.py. Next, you execute UDPServer.py, the
compiled server program, in the server host. This creates a process in the server
that idles until it is contacted by some client. Then you execute UDPClient.py,
the compiled client program, in the client. This creates a process in the client.
Finally, to use the application at the client, you type a sentence followed by a
carriage return.
To develop your own UDP client-server application, you can begin by
slightly modifying the client or server programs. For example, instead of converting all the letters to uppercase, the server could count the number of times
the letter s appears and return this number. Or you can modify the client so
that after receiving a capitalized sentence, the user can continue to send more
sentences to the server.


### 2.6.2 Socket Programming with TCP

Unlike UDP, TCP is a connection-oriented protocol. This means that before
the client and server can start to send data to each other, they first need to
handshake and establish a TCP connection. One end of the TCP connection
is attached to the client socket and the other end is attached to a server
socket. When creating the TCP connection, we associate with it the client
socket address (IP address and port number) and the server socket address
(IP address and port number). With the TCP connection established, when
one side wants to send data to the other side, it just drops the data into the
TCP connection via its socket. This is different from UDP, for which the
server must attach a destination address to the packet before dropping it
into the socket.
Now let’s take a closer look at the interaction of client and server programs in TCP. The client has the job of initiating contact with the server. In
order for the server to be able to react to the client’s initial contact, the server
has to be ready. This implies two things. First, as in the case of UDP, the TCP
server must be running as a process before the client attempts to initiate contact. Second, the server program must have a special door—more precisely, a
special socket—that welcomes some initial contact from a client process running on an arbitrary host. Using our house/door analogy for a process/socket,


Application Layer


we will sometimes refer to the client’s initial contact as “knocking on the welcoming door.”
With the server process running, the client process can initiate a TCP connection to the server. This is done in the client program by creating a TCP
socket. When the client creates its TCP socket, it specifies the address of the
welcoming socket in the server, namely, the IP address of the server host and
the port number of the socket. After creating its socket, the client initiates a
three-way handshake and establishes a TCP connection with the server. The
three-way handshake, which takes place within the transport layer, is completely invisible to the client and server programs.
During the three-way handshake, the client process knocks on the welcoming door of the server process. When the server “hears” the knocking, it
creates a new door—more precisely, a new socket that is dedicated to that particular client. In our example below, the welcoming door is a TCP socket object
that we call serverSocket; the newly created socket dedicated to the client
making the connection is called connectionSocket. Students who are
encountering TCP sockets for the first time sometimes confuse the welcoming
socket (which is the initial point of contact for all clients wanting to communicate with the server), and each newly created server-side connection socket
that is subsequently created for communicating with each client.
From the application’s perspective, the client’s socket and the server’s
connection socket are directly connected by a pipe. As shown in Figure 2.23,
the client process can send arbitrary bytes into its socket, and TCP guarantees
that the server process will receive (through the connection socket) each byte
in the order sent. TCP thus provides a reliable service between the client and
server processes. Furthermore, just as people can go in and out the same door,
the client process not only sends bytes into but also receives bytes from its
socket; similarly, the server process not only receives bytes from but also sends
bytes into its connection socket.

Figure 2.23 The
TCPServer process has
two sockets



Figure 2.24 The
client-server application
using TCP

We use the same simple client-server application to demonstrate socket
programming with TCP: The client sends one line of data to the server, the
server capitalizes the line and sends it back to the client. Figure 2.24 highlights
the main socket-related activity of the client and server that communicate over
the TCP transport service.

TCPClient.py
Here is the code for the client side of the application:
from socket import *
serverName = 'servername'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
print('From Server: ', modifiedSentence.decode())
clientSocket.close()


Application Layer

Let’s now take a look at the various lines in the code that differ significantly from the UDP implementation. The first such line is the creation of the
client socket.
clientSocket = socket(AF_INET, SOCK_STREAM)
This line creates the client’s socket, called clientSocket. The first parameter
again indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM, which means it is a TCP
socket (rather than a UDP socket). Note that we are again not specifying the
port number of the client socket when we create it; we are instead letting the
operating system do this for us. Now the next line of code is very different
from what we saw in UDPClient:
clientSocket.connect((serverName,serverPort))
Recall that before the client can send data to the server (or vice versa) using a
TCP socket, a TCP connection must first be established between the client and
server. The above line initiates the TCP connection between the client and
server. The parameter of the connect() method is the address of the server
side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client
and server.
sentence = input('Input lowercase sentence:')
As with UDPClient, the above obtains a sentence from the user. The string
sentence continues to gather characters until the user ends the line by typing
a carriage return. The next line of code is also very different from UDPClient:
clientSocket.send(sentence.encode())
The above line sends the sentence through the client’s socket and into the
TCP connection. Note that the program does not explicitly create a packet and
attach the destination address to the packet, as was the case with UDP sockets.
Instead the client program simply drops the bytes in the string sentence into
the TCP connection. The client then waits to receive bytes from the server.
modifiedSentence = clientSocket.recv(2048)
When characters arrive from the server, they get placed into the string
modifiedSentence. Characters continue to accumulate in modifiedSentence until the line ends with a carriage return character. After printing the
capitalized sentence, we close the client’s socket:
clientSocket.close()
This last line closes the socket and, hence, closes the TCP connection between
the client and the server. It causes TCP in the client to send a TCP message to
TCP in the server (see Section 3.5).

TCPServer.py
Now let’s take a look at the server program.



from socket import *
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while True:
connectionSocket, addr = serverSocket.accept()
sentence = connectionSocket.recv(1024).decode()
capitalizedSentence = sentence.upper()
connectionSocket.send(capitalizedSentence.encode())
connectionSocket.close()
Let’s now take a look at the lines that differ significantly from UDPServer
and TCPClient. As with TCPClient, the server creates a TCP socket with:
serverSocket=socket(AF_INET,SOCK_STREAM)
Similar to UDPServer, we associate the server port number, serverPort, with
this socket:
serverSocket.bind((",serverPort))
But with TCP, serverSocket will be our welcoming socket. After establishing this welcoming door, we will wait and listen for some client to knock on
the door:
serverSocket.listen(1)
This line has the server listen for TCP connection requests from the client.
The parameter specifies the maximum number of queued connections (at
least 1).
connectionSocket, addr = serverSocket.accept()
When a client knocks on this door, the program invokes the accept()
method for serverSocket, which creates a new socket in the server, called
­c onnectionSocket, dedicated to this particular client. The client and
server then complete the handshaking, creating a TCP connection between
the client’s clientSocket and the server’s connectionSocket. With the
TCP connection established, the client and server can now send bytes to each
other over the connection. With TCP, all bytes sent from one side are only
guaranteed to arrive at the other side but also guaranteed to arrive in order.
connectionSocket.close()
In this program, after sending the modified sentence to the client, we close
the connection socket. But since serverSocket remains open, another client
can now knock on the door and send the server a sentence to modify.
This completes our discussion of socket programming in TCP. You are
encouraged to run the two programs in two separate hosts, and also to modify
them to achieve slightly different goals. You should compare the UDP program
pair with the TCP program pair and see how they differ. You should also do
many of the socket programming assignments described at the end of


Application Layer

­ hapters 2 and 3. Finally, we hope someday, after mastering these and more
C
advanced socket programs, you will write your own popular network application, become very rich and famous, and remember the authors of this
textbook!


### 2.6.3 Socket Programming with QUIC

We will close this section with a high-level discussion of how an application
developer would use a QUIC API to send messages between a client and
server. Consider what happens when a Web browser uses the HTTP 3 protocol to request a Web page from a server also running HTTP 3. Instead of
initiating a traditional TCP handshake, the client initiates a QUIC handshake on top of UDP. QUIC incorporates the TLS 1.3 handshake into the
QUIC handshake, meaning the connection and encryption setup are done in
parallel, and not serially as when HTTP 2. Even though UDP is connectionless, QUIC is connection-oriented, allowing the client and server to retain
connection information across different HTTP requests for the same or different Web pages.
Let’s now turn our attention to the HTTP 3 server with a connection
already established between the client and the server. After receiving
request(s) over the QUIC connection, the server will need to send HTTP
messages, each encapsulating an object, to the client. The HTTP 3 server
will use the QUIC API to create a separate stream and a corresponding
stream ID for each message it wants to send. For example, the server may
create Stream 1 for the HTML base page, create Stream 2 for a CSS object,
and Stream 3 for an image. It could then send all three of these messages
back-to-back into the QUIC connection. When HTTP 3 wants to send a message, it specifies, to the QUIC API, the QUIC connection ID and the stream
ID. Tasks such as encryption, breaking the streams (i.e., messages) into
smaller frames, and stream multiplexing are all handled by the QUIC sublayer internally. The HTTP 3 server can also indicate to the QUIC API that it
should prioritize streams based on the importance of the resource. For
instance, the HTTP 3 server can tell QUIC to prioritize the HTML content
(as it forms the basic structure of the web page) and send it before other
resources like images or JavaScript.
Importantly, the HTTP 3 code interacts with the QUIC API and not with
the underlying UDP socket API. So from the perspective of the HTTP 3 application developer, HTTP 3 runs over the QUIC transport protocol.


## 2.7 Summary

In this chapter, we’ve studied the conceptual and the implementation aspects
of network applications. We’ve learned about the ubiquitous client-server
architecture adopted by many Internet applications and seen its use in the
HTTP, SMTP, and DNS protocols. We’ve studied these important applicationlevel protocols, and their corresponding associated applications (the Web, file



transfer, e-mail, and DNS) in some detail. We’ve also learned about streaming
video, and how modern video distribution systems leverage CDNs. We’ve
examined how the socket API can be used to build network applications.
We’ve walked through the use of sockets for connection-oriented (TCP) and
connectionless (UDP) end-to-end transport services. The first step in our journey down the layered network architecture is now complete!
At the very beginning of this book, in Section 1.1, we gave a rather vague,
bare-bones definition of a protocol: “the format and the order of messages
exchanged between two or more communicating entities, as well as the actions
taken on the transmission and/or receipt of a message or other event.” The
material in this chapter, and in particular our detailed study of the HTTP,
SMTP, and DNS protocols, has now added considerable substance to this definition. Protocols are a key concept in networking; our study of application
protocols has now given us the opportunity to develop a more intuitive feel for
what protocols are all about.
In Section 2.1, we described the service models that TCP and UDP offer
to applications that invoke them. We took an even closer look at these service
models when we developed simple applications that run over TCP and UDP
in Section 2.6. However, we have said little about how TCP and UDP provide
these service models. For example, we know that TCP provides a reliable
data service, but we haven’t said yet how it does so. In the next chapter, we’ll
take a careful look at not only the what, but also the how and why of transport protocols.
Equipped with knowledge about Internet application structure and application-level protocols, we’re now ready to head further down the protocol
stack and examine the transport layer in Chapter 3.

Homework Problems and Questions
Section 2.1

R5. What information is used by a process running on one host to identify a process running
on another host?

R1. List five nonproprietary Internet applications
and the application-layer protocols that they
use.

R6. Suppose you wanted to do a transaction from
a remote client to a server as fast as possible.
Would you use UDP or TCP? Why?

R2. What is the difference between network architecture and application architecture?

R7. Referring to Figure 2.4, we see that none of the
applications listed in Figure 2.4 requires both
no data loss and timing. Can you conceive of
an application that requires no data loss and
that is also highly time-sensitive?

R3. For a communication session between a pair
of processes, which process is the client and
which is the server?
R4. What is the software interface that a process
sends messages into, and receives messages
from?

R8. List the four broad classes of services that a
transport protocol can provide. For each of
the service classes, indicate if either UDP or
TCP (or both) provides such a service.


Application Layer

R9. Recall that TCP can be enhanced with TLS to
provide process-to-process security services,
including encryption. Does TLS operate at the
transport layer or the application layer? If
the application developer wants TCP to be
enhanced with TLS, what does the developer
have to do?

Sections 2.2–2.4
R10. What is meant by a handshaking protocol?
R11. Why do HTTP, SMTP, and IMAP run on top of
TCP rather than on UDP?
R12. Consider an e-commerce site that wants to
keep a purchase record for each of its customers. Describe how this can be done with
cookies.
R13. How is it that QUIC can be connection-­oriented
even though it runs over UDP?
R14. In HTTP 3 code, are UDP, TCP, or QUIC sockets opened and closed?
R15. List several popular messaging apps. Do they
use the same protocols as SMS?
R16. Alice uses Gmail and Bob uses Yahoo! Mail.
Suppose Alice sends and email message to
Bob. List the series of application protocols that
are used to get the message from Alice to Bob.
R17. Print out the header of an e-mail message you
have recently received. How many Received:
header lines are there? Analyze each of the
header lines in the message.
R18. What is the HOL blocking issue in HTTP 1.1?
How does HTTP 2 attempt to solve it? What
is the HOL issue in HTTP 2 ? How does
HTTP 3 solve it.


R19. Is it possible for an organization’s Web server
and mail server to have exactly the same alias
for a hostname (for example, foo.com)?
What would be the type for the RR that contains the hostname of the mail server?
R20. Look over your received e-mails, and examine
the header of a message sent from a user. Is it
possible to determine from the header the IP
address of the host from which the message
was sent? Do the same for a message sent
from a Gmail account.

Section 2.5
R21. CDNs typically adopt one of two different
server placement philosophies. Name and
briefly describe them.
R22. Besides network-related considerations such
as delay, loss, and bandwidth performance,
there are other important factors that go into
designing a CDN server selection strategy.
What are they?

Section 2.6
R23. In Section 2.6, the UDP server described
needed only one socket, whereas the TCP
server needed two sockets. Why? If the TCP
server were to support n simultaneous connections, each from a different client host, how
many sockets would the TCP server need?
R24. For the client-server application over TCP
described in Section 2.6, why must the server
program be executed before the client program? For the client-server application over
UDP, why may the client program be executed
before the server program?

Problems
P1. True or false?
a. A user requests a Web page that consists of some text and three
images. For this page, the client will send one request message and
receive four response messages.
b. Two distinct Web pages (for example, www.mit.edu/research.
html and www.mit.edu/students.html) can be sent over the
same persistent connection.


c. With nonpersistent connections between browser and origin server,
it is possible for a single TCP segment to carry two distinct HTTP
request messages.
d. The Date: header in the HTTP response message indicates when the
object in the response was last modified.
e. HTTP response messages never have an empty message body.
P2. SMS, iMessage, Wechat, and WhatsApp are all smartphone real-time
messaging systems. After doing some research on the Internet, for each
of these systems write one paragraph about the protocols they use. Then
write a paragraph explaining how they differ.
P3. Consider an HTTP client that wants to retrieve a Web document at a given
URL. The IP address of the HTTP server is initially unknown. What transport and application-layer protocols besides HTTP are needed in this
scenario?
P4. Consider the following string of ASCII characters that were captured by
Wireshark when the browser sent an HTTP GET message (i.e., this is the
actual content of an HTTP GET message). The characters <cr><lf> are carriage return and line-feed characters (that is, the italized character string
<cr> in the text below represents the single carriage-return character that
was contained at that point in the HTTP header). Answer the following
questions, indicating where in the HTTP GET message below you find the
answer.
GET /cs453/index.html HTTP/1.1<cr><lf>Host: gai
a.cs.umass.edu<cr><lf>User-Agent: Mozilla/5.0 (
Windows;U; Windows NT 5.1; en-US; rv:1.7.2) Gec
ko/20040804 Netscape/7.2 (ax) <cr><lf>Accept:ex
t/xml, application/xml, application/xhtml+xml, text
/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5
<cr><lf>Accept-Language: en-us,en;q=0.5<cr><lf>AcceptEncoding: zip,deflate<cr><lf>Accept-Charset: ISO
-8859-1,utf-8;q=0.7,*;q=0.7<cr><lf>Keep-Alive: 300<cr>
<lf>Connection:keep-alive<cr><lf><cr><lf>
a. What is the URL of the document requested by the browser?
b. What version of HTTP is the browser running?
c. Does the browser request a non-persistent or a persistent connection?
d. What is the IP address of the host on which the browser is running?
e. What type of browser initiates this message? Why is the browser type
needed in an HTTP request message?
P5. The text below shows the reply sent from the server in response to the
HTTP GET message in the question above. Answer the following questions, indicating where in the message below you find the answer.
HTTP/1.1 200 OK<cr><lf>Date: Tue, 07 Mar 2008
12:39:45GMT<cr><lf>Server: Apache/2.0.52 (Fedora)
<cr><lf>Last-Modified: Sat, 10 Dec2005 18:27:46
GMT<cr><lf>ETag: “526c3-f22-a88a4c80”<cr><lf>Accept-


Application Layer

Ranges: bytes<cr><lf>Content-Length: 3874<cr><lf>
Keep-Alive: timeout=max=100<cr><lf>Connection:
Keep-Alive<cr><lf>Content-Type: text/html; charset=
ISO-8859-1<cr><lf><cr><lf><!doctype html public {“//w3c//dtd html 4.0transitional//en”><lf><html><lf>
<head><lf> <meta http-equiv=”Content-Type”
content=”text/html; charset=iso-8859-1”><lf> <meta
name=”GENERATOR” content=”Mozilla/4.79 [en] (Windows NT
5.0; U) Netscape]”><lf> <title>CMPSCI 453 / 591 /
NTU-ST550ASpring 2005 homepage</title><lf></head><lf>
<much more document text following here (not shown)>
a. Was the server able to successfully find the document or not? What
time was the document reply provided?
b. When was the document last modified?
c. How many bytes are there in the document being returned?
d. What are the first 5 bytes of the document being returned? Did the
server agree to a persistent connection?
P6. Obtain the HTTP 1.1 specification (RFC 2616). Answer the following
questions:
a. Explain the mechanism used for signaling between the client and
server to indicate that a persistent connection is being closed. Can the
client, the server, or both signal the close of a connection?
b. What encryption services are provided by HTTP?
c. Can a client open three or more simultaneous connections with a
given server?
d. Either a server or a client may close a transport connection between
them if either one detects the connection has been idle for some time.
Is it possible that one side starts closing a connection while the other
side is transmitting data via this connection? Explain.
P7. Suppose within your Web browser you click on a link to obtain a Web
page. The IP address for the associated URL is not cached in your local
host, so a DNS lookup is necessary to obtain the IP address. Suppose that
n DNS servers are visited before your host receives the IP address from
DNS; the successive visits incur an RTT of RTT1 , . . . , RTTn . Further
suppose that the Web page associated with the link contains exactly one
object, consisting of a small amount of HTML text. Let RTT0 denote the
RTT between the local host and the server containing the object. Assuming zero transmission time of the object, how much time elapses from
when the client clicks on the link until the client receives the object?
P8. Referring to Problem P7, suppose the HTML file references eight very
small objects on the same server. Neglecting transmission times, how
much time elapses with
a. Non-persistent HTTP with no parallel TCP connections?
b. Non-persistent HTTP with the browser configured for 6 parallel
connections?
c. Persistent HTTP?



P9. Consider a short, 10-meter link, over which a sender can transmit at a
rate of 150 bits sec in both directions. Suppose that packets containing
data are 100,000 bits long, and packets containing only control (e.g.,
ACK or handshaking) are 200 bits long. Assume that N parallel connections each get 1 N of the link bandwidth. Now consider the HTTP protocol, and suppose that each downloaded object is 100 Kbits long, and that
the initial downloaded object contains 10 referenced objects from the
same sender. Would parallel downloads via parallel instances of nonpersistent HTTP make sense in this case? Now consider persistent HTTP.
Do you expect significant gains over the non-persistent case? Justify and
explain your answer.
P10. Consider the scenario introduced in the previous problem. Now suppose
that the link is shared by Bob with four other users. Bob uses parallel
instances of non-persistent HTTP, and the other four users use non-­
persistent HTTP without parallel downloads.
a. Do Bob’s parallel connections help him get Web pages more quickly?
Why or why not?
b. If all five users open five parallel instances of non-persistent HTTP, then
would Bob’s parallel connections still be beneficial? Why or why not?
P11. Write a simple TCP program for a server that accepts lines of input from
a client and prints the lines onto the server’s standard output. (You can
do this by modifying the TCPServer.py program in the text.) Compile
and execute your program. On any other machine that contains a Web
browser, set the proxy server in the browser to the host that is running
your server program; also configure the port number appropriately. Your
browser should now send its GET request messages to your server, and
your server should display the messages on its standard output. Use this
platform to determine whether your browser generates conditional GET
messages for objects that are locally cached.
P12. Consider sending over HTTP 2 a Web page that consists of one video
clip, and five images. Suppose that the video clip is transported as 2000
frames, and each image has three frames.
a. If all the video frames are sent first without interleaving, how many
“frame times” are needed until all five images are sent?
b. If frames are interleaved, how many frame times are needed until all
five images are sent.
P13. Consider the Web page in problem 12. Now HTTP 2 prioritization is
employed. Suppose all the images are given priority over the video clip,
and that the first image is given priority over the second image, the second image over the third image, and so on. How many frame times will
be needed until the second image is sent?
P14. What is the difference between MAIL FROM: in SMTP and From: in the
mail message itself?
P15. How does SMTP mark the end of a message body? How about HTTP?
Can HTTP use the same method as SMTP to mark the end of a message
body? Explain.


Application Layer

P16. Read RFC 5321 for SMTP. What does MTA stand for? Consider the following received spam e-mail (modified from a real spam e-mail). Assuming only the originator of this spam e-mail is malicious and all other
hosts are honest, identify the malacious host that has generated this
spam e-mail.
From - Fri Nov 07 13:41:30 2008
Return-Path: <tennis5@pp33head.com>
Received: from barmail.cs.umass.edu (barmail.cs.umass.
edu
[128.119.240.3]) by cs.umass.edu (8.13.1/8.12.6) for
<hg@cs.umass.edu>; Fri, 7 Nov 2008 13:27:10 -0500
Received: from asusus-4b96 (localhost [127.0.0.1]) by
barmail.cs.umass.edu (Spam Firewall) for <hg@cs.umass.
edu>; Fri, 7
Nov 2008 13:27:07 -0500 (EST)
Received: from asusus-4b96 ([58.88.21.177]) by barmail.
cs.umass.edu
for <hg@cs.umass.edu>; Fri, 07 Nov 2008 13:27:07 -0500
(EST)
Received: from [58.88.21.177] by inbnd55.exchangeddd.
com; Sat, 8
Nov 2008 01:27:07 +0700
From: ‘’Jonny’’ <tennis5@pp33head.com>
To: <hg@cs.umass.edu>
Subject: How to secure your savings
P17. a. What is a who is database?
b. Use various whois databases on the Internet to obtain the names of
two DNS servers. Indicate which whois databases you used.
c. Use nslookup on your local host to send DNS queries to three DNS
servers: your local DNS server and the two DNS servers you found
in part (b). Try querying for Type A, NS, and MX reports. Summarize
your findings.
d. Use nslookup to find a Web server that has multiple IP addresses.
Does the Web server of your institution (school or company) have
multiple IP addresses?
e. Use the ARIN whois database to determine the IP address range used
by your university.
f. Describe how an attacker can use whois databases and the nslookup
tool to perform reconnaissance on an institution before launching an
attack.
g. Discuss why whois databases should be publicly available.
P18. In this problem, we use the useful dig tool available on Unix and Linux
hosts to explore the hierarchy of DNS servers. Recall that in Figure 2.17,
a DNS server in the DNS hierarchy delegates a DNS query to a DNS
server lower in the hierarchy, by sending back to the DNS client the



name of that lower-level DNS server. First read the man page for dig, and
then answer the following questions.
a. Starting with a root DNS server (from one of the root servers [a-m].
root-servers.net), initiate a sequence of queries for the IP address for
your department’s Web server by using dig. Show the list of the names
of DNS servers in the delegation chain in answering your query.
b. Repeat part (a) for several popular Web sites, such as google.com,
yahoo.com, or amazon.com.
P19. Suppose you can access the caches in the local DNS servers of your
department. Can you propose a way to roughly determine the Web servers (outside your department) that are most popular among the users in
your department? Explain.
P20. Suppose that your department has a local DNS server for all computers
in the department. You are an ordinary user (i.e., not a network/system
administrator). Can you determine if an external Web site was likely
accessed from a computer in your department a couple of seconds ago?
Explain.
P21. Consider a DASH system for which there are N video versions (at N different rates and qualities) and N audio versions (at N different rates and
qualities). Suppose we want to allow the player to choose at any time
any of the N video versions and any of the N audio versions.
a. If we create files so that the audio is mixed in with the video, so server
sends only one media stream at given time, how many files will the
server need to store (each a different URL)?
b. If the server instead sends the audio and video streams separately and
has the client synchronize the streams, how many files will the server
need to store?
P22. Install and compile the Python programs TCPClient and UDPClient on
one host and TCPServer and UDPServer on another host.
a. Suppose you run TCPClient before you run TCPServer. What happens? Why?
b. Suppose you run UDPClient before you run UDPServer. What happens? Why?
c. What happens if you use different port numbers for the client and
server sides?
P23. Suppose that in UDPClient.py, after we create the socket, we add the
line:
clientSocket.bind((", 5432))
Will it become necessary to change UDPServer.py? What are the port
numbers for the sockets in UDPClient and UDPServer? What were they
before making this change?
P24. We have seen that Internet TCP sockets treat the data being sent as a byte
stream but UDP sockets recognize message boundaries. What are


Application Layer


one advantage and one disadvantage of byte-oriented API versus having
the API explicitly recognize and preserve application-defined message
boundaries?
P25. What is the Apache Web server? How much does it cost? What functionality does it currently have?

Socket Programming Assignments
The Companion Website includes six socket programming assignments. The first four assignments
are summarized below. The fifth assignment makes
use of the ICMP protocol and is summarized at the
end of Chapter 5. It is highly recommended that students complete several, if not all, of these assignments. Students can find full details of these
assignments, as well as important snippets of the
Python code, at the Web site www.pearsonhighered.
com/cs-resources.

Assignment 1: Web Server
In this assignment, you will develop a simple Web
server in Python that is capable of processing only
one request. Specifically, your Web server will (i) create a connection socket when contacted by a client
(browser); (ii) receive the HTTP request from this
connection; (iii) parse the request to determine the
specific file being requested; (iv) get the requested
file from the server’s file system; (v) create an HTTP
response message consisting of the requested file
preceded by header lines; and (vi) send the response
over the TCP connection to the requesting browser.
If a browser requests a file that is not present in your
server, your server should return a “404 Not Found”
error message.
In the Companion Website, we provide the
skeleton code for your server. Your job is to complete the code, run your server, and then test your
server by sending requests from browsers running
on different hosts. If you run your server on a host
that already has a Web server running on it, then
you should use a different port than port 80 for your
Web server.

Assignment 2: UDP Pinger
In this programming assignment, you will write a
client ping program in Python. Your client will send
a simple ping message to a server, receive a corresponding pong message back from the server, and
determine the delay between when the client sent
the ping message and received the pong message.
This delay is called the Round Trip Time (RTT). The
functionality provided by the client and server is
similar to the functionality provided by standard
ping program available in modern operating systems. However, standard ping programs use the
Internet Control Message Protocol (ICMP) (which
we will study in Chapter 5). Here we will create a
nonstandard (but simple!) UDP-based ping
program.
Your ping program is to send 10 ping messages
to the target server over UDP. For each message,
your client is to determine and print the RTT when
the corresponding pong message is returned.
Because UDP is an unreliable protocol, a packet sent
by the client or server may be lost. For this reason,
the client cannot wait indefinitely for a reply to a
ping message. You should have the client wait up to
one second for a reply from the server; if no reply is
received, the client should assume that the packet
was lost and print a message accordingly.
In this assignment, you will be given the complete code for the server (available in the Companion Website). Your job is to write the client code,
which will be very similar to the server code. It is
recommended that you first study carefully the
server code. You can then write your client code, liberally cutting and pasting lines from the server code.



Assignment 3: Mail Client

Assignment 4: Web Proxy

The goal of this programming assignment is to create a simple mail client that sends e-mail to any
recipient. Your client will need to establish a TCP
connection with a mail server (e.g., a Google mail
server), dialogue with the mail server using the
SMTP protocol, send an e-mail message to a recipient (e.g., your friend) via the mail server, and finally
close the TCP connection with the mail server.
For this assignment, the Companion Website
provides the skeleton code for your client. Your job
is to complete the code and test your client by sending e-mail to different user accounts. You may also
try sending through different servers (for example,
through a Google mail server and through your university mail server).

In this assignment, you will develop a Web proxy.
When your proxy receives an HTTP request for an
object from a browser, it generates a new HTTP
request for the same object and sends it to the origin
server. When the proxy receives the corresponding
HTTP response with the object from the origin
server, it creates a new HTTP response, including
the object, and sends it to the client.
For this assignment, the Companion Website
provides the skeleton code for the proxy server.
Your job is to complete the code, and then test it by
having different browsers request Web objects via
your proxy.

Wireshark Labs: HTTP, DNS
Having gotten our feet wet with the Wireshark
packet sniffer in Lab 1, we’re now ready to use Wireshark to investigate protocols in operation. In this
lab, we’ll explore several aspects of the HTTP protocol: the basic GET/reply interaction, HTTP message
formats, retrieving large HTML files, retrieving

HTML files with embedded URLs, persistent and
non-persistent connections, and HTTP authentication and security.
As is the case with all Wireshark labs, the full
description of this lab is available at this book’s Web
site, www.pearsonhighered.com/cs-resources.

Wireshark Lab: DNS
In this lab, we take a closer look at the client side of
the DNS, the protocol that translates Internet hostnames to IP addresses. Recall from Section 2.5 that
the client’s role in the DNS is relatively simple—a
client sends a query to its local DNS server and
receives a response back. Much can go on under the
covers, invisible to the DNS clients, as the hierarchical DNS servers communicate with each other to
either recursively or iteratively resolve the client’s

DNS query. From the DNS client’s standpoint, however, the protocol is quite simple—a query is formulated to the local DNS server and a response is
received from that server. We observe DNS in action
in this lab.
As is the case with all Wireshark labs, the full
description of this lab is available at this book’s Web
site, www.pearsonhighered.com/cs-resources.


Application Layer


AN INTERVIEW WITH...
Paul Mockapetris
Paul Mockapetris is best known as the creator of the Domain Name System (DNS),
and wrote the first implementation of SMTP, the Internet’s mail protocol. At present,
he is a board member and Chief Scientist at ThreatSTOP, a realtime threat prevention service using DNS.
Previously he was Chief Scientist and board member of Nominum, CTO at Urban
Media, Siara, Fiberlane, and Software.com and director of engineering at @Home. He
has been IETF chair, program manager at ARPA, and division director at the USC
Information Sciences Institute. He spent 10 years at UC Irvine with the DCS project, and
4 years at MIT with the Architecture Machine Group before it became the Media Lab.
He received his learner's permits in Physics and Electrical Engineering from
the MIT in 1971, and a Ph.D. in Information and Computer Science from UC Irvine.
He is a member of the inaugural Internet Hall of Fame, and is Doctor Honoris Causa
of the Miguel Hernandez and Ramon Llull Universities. He is the recipient of the
ACM Software System Award, IEEE Internet award and the ACM Sigcomm award,
and is a Fellow of the ACM, IEEE and the US National Academy of Engineering.

How did you get interested in computers and
computer networking?
My first interaction with a computer was as a high school student taking a summer
programming course at MIT, one of many offered at the time. Stu Madnick taught
us programming on IBM 1620s, and I managed to get access to a few other machines.
As a Physics major at MIT, I needed income, so I took an entry level
programming job with Nicholas Negroponte as the first employee of the
Architecture Machine Group, which evolved into the Media Lab. Huge timesharing
systems were at the forefront of computing research then, but all we had was a few
donated minicomputers and one expensive hard disk. So we built a cluster that
shared I/O devices and a file system. I coauthored the MagicOS with Steve Gregory.
Little did we know while we were supporting various architects and their projects
that we had built something that was state of the art computing research. I also
worked at the IBM Cambridge Scientific Center on virtual machine technology and
Draper Labs on flight code for rockets. Eventually, my Physics advisor and the head
of the IBM center convinced me that computing was my future, not Physics.
For my PhD, I headed west to UC Irvine and the Distributed Computing
System project led by Dave Farber. This was a cluster of minicomputers tied together
with a ring LAN – cloud computing over 50 years ago! All based on message passing
between named processes. Dave and UC Irvine introduced me to VLSI at Caltech,
dialup ARPAnet, and the USC Information Sciences Institute, or ISI

What was ISI like at the time?
ISI’s home was a high rise across the street from the Pacific ocean, packed with
­computers and ARPA researchers, doing everything from VLSI to AI to networking.
I got a research assistantship, all the computing resources I could use and a connection on the ARPAnet backbone while I worked on my thesis.

Courtesy of Paul Mockapetris



So how did you start on the DNS?
In 1982 I finished my thesis and accepted a fulltime position at ISI. I had been working
on email and TCP performance, but it wasn’t satisfying. My boss, Jon Postel, suggested
that I might think about the problem of naming in the network. There were some ideas
about “domain names” for email, and some thought we needed a new way to manage
the HOST.TXT file. There were even some existing designs that might be used.
The DNS design I created combines my experiences before ISI, ideas borrowed
from other naming systems and input from the community. In particular, DCS and
Magic OS had taught me a lot about how to build distributed systems with loose
coupling. I didn’t repeat mistakes I had made with DCS and Magic OS naming.
The design is purposefully general and extensible; its first application was
organizing its own data and permitting multiple organizations to manage their
own separate names and data while allowing the namespace to appear seamless to
the end user; its second application was the HOSTS.TXT issue; and then email
routing. The system achieves reliability by having redundant servers that can
compensate for both network failures as well as server problems.
The specs for DNS were revised a couple times in response to feedback from
the networking community and then published as RFCs in 1983; they were later
revised and published as RFCs 1034 and 1035 in 1986. Other milestones that year
were the first machines that relied on the DNS and didn’t have HOSTS.TXT as a
backup, as well as others adding to the DNS specs.

Was it really that simple?
Specs are fine, but to get the DCS adopted it had to be implemented and deployed
across the Internet. SRI, which maintained the HOSTS.TXT file was happy to
administer its successor. I wrote the first implementation, Jeeves, which was
deployed across DEC timesharing systems to be the first few generations of root
servers. UC Berkeley wrote bind, the first UNIX implementation, and ARPA funded
the Berkeley UNIX distribution carrying bind around the world. I did many classes
on DNS. Jon Postel created a transition plan for HOSTS.TXT to DNS. The Internet
owes a great debt to all the individuals who bought into the DNS plan and moved it
forward; there were a lot of skeptics. Simple things required rethinking. For example, email systems had to deal with situations where a particular domain wasn’t
resolvable at a given time, and mail had to be queued for later delivery.

Are you happy with the subsequent
evolution of DNS?
By the late 1980s, ARPA and the NSF both decided that DNS wasn’t research anymore and that they should move on. Somewhat paradoxically, that led me to be an
ARPA program manager. I probably should have taken DNS to the venture capitalists of Sand Hill Road, but I didn’t know that world.
NSF enabled the commercial exploitation of DNS buy allowing registries to
charge for names. The Internet scaled up with the DNS. Early DNS was guided by
my utopian idea that eventually everyone would have their own domain, perhaps
analogous to the digital identities or wallets we have today. But the DNS wasn’t just
serving just the network research community, it moved on to the universities in
general, then the commercial world, and then the world in general. Today the large


Application Layer
Internet companies dominate the discussion on DNS in the IETF and governments
want their interests served.
After many years away from the DNS, I came back to working on DNS
protection or DNS for security. This was service sold at a series of startups. The
basic idea is that you want to avoid using domain names that lead you to undesirable
places or content. It’s a n ext remely cost effect ive layer of securit y, but
quite problematic when governments et al use it to censor your Internet. Meanwhile,
the bad actors try to avoid being known. All in all, a Gordian knot of technology
and policy that can perhaps be solved by having everyone control their own name
space. It’s one of the many Internet problems that create a tension between
outsourcing complicated tasks and retaining individual control.

Do you have any advice for students based on
your experiences?
First, always be exploring. For example, I tell all PhD students that their first step
should be to go to the library and examine recent PhD theses to set expectations. If
you want to be a professor, at least learn a bit about how the startup/entrepreneur
world works. Second, opportunities often are best where two different disciplines
intersect. Computing, like mathematics, has most of its utility when applied. Biology and computing are made for each other. Third, hope to see places where conventional wisdom is wrong and you see low-hanging fruit. I had many people tell
me about the impossibility of sending data over cable TV systems because of the
noisy environment, but I believed that Moore’s law and digital signal processing
would make it possible, so took a chance on my first startup.
But above all collect great mentors or people that can inspire you. In my case
(alphabetically): Dave Farber, Bob Kahn, Nicholas Negroponte, Jon Postel, Steve
Squires, and Ed Thorpe, to name a few.




