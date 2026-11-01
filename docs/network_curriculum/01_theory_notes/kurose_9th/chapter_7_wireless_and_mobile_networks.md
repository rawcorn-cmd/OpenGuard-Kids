# Chương 7: Wireless and Mobile Networks
> **Giáo trình:** Computer Networking: A Top-Down Approach (9th Edition, 2026)  
> **Tác giả:** Jim Kurose, Keith Ross — Pearson Education  
> **Số trang bản gốc:** PDF trang 490 – 580 (Độ dài: 91 trang)  

---

> [!NOTE] ỨNG DỤNG TRỰC TIẾP VÀO ĐỒ ÁN OPENGUARD KIDS
> **Mục tiêu học tập & Áp dụng thực tiễn:**  
> Mạng Wi-Fi 802.11 (Wi-Fi 6), mạng di động 4G/5G, quản lý chuyển vùng (Mobility) khi thiết bị laptop của trẻ chuyển giữa các mạng Wi-Fi khác nhau.

---

Wireless and Mobile Networks


The past 15 years have seen a breathtaking increase in the deployment and
use of wireless and mobile networks. In 2008, the number of fixed (wired)
broadband Internet subscribers was approximately the same as the number
of broadband subscribers attached via wireless technologies. While both subscriber bases have grown since then, there are now (in 2025) five times as many
Internet-connected wireless subscribers than wired subscribers. An estimated
60 percent of Web site traffic was directed to mobile versus fixed devices in
2025 [Statista Mobile 2025]. The many advantages of wireless access are evident to all—anywhere, anytime, untethered access to the global Internet via a
highly portable lightweight device. Increasingly, devices such as gaming consoles, home appliances, security systems, watches, eyeglasses, cars, wearable
clothing, and so much more are being wirelessly connected to the Internet.
Indeed, some have posited that a profoundly important, fourth industrial
revolution [Schwab 2016]—enabled by wireless networks and cyber-physical
systems that integrate the physical and digital worlds—is now underway.
The challenges posed by networking wireless and mobile devices are so
different from traditional wired computer networks that an individual chapter


Wireless and Mobile Networks

devoted to the study of wireless and mobile networks (i.e., this chapter) is
appropriate. In this chapter, we’ll cover both the principles and the practice of
wireless and mobile networks. In Section 7.1, we’ll begin by setting the “big
picture” context.
As a reader of this book, you know by now that we’re huge fans of a topdown approach. But so many aspects of wireless networking result from the
complex, time-varying, capacity-limited, and shared nature of the physical wireless channel that an early mastery of radio channels is needed to appreciate
practically any other aspect of wireless networking. Thus, we’ll begin our indepth study of wireless and mobile networks bottom-up, where we’ll first learn
about the properties of wireless radio channels in Section 7.2. In ­Section 7.3, we’ll
then focus on the first-hop radio access network. Here, we’ll learn about techniques for sharing the radio channel, network discovery and device attachment,
frame transmission scheduling, energy conservation, and more. In Section 7.4,
we’ll learn about the wireless network “core” that provides control-plane services
such as identity and mobility management as well as data-plane connectivity to
the larger Internet. Throughout Sections 7.2–7.4, we’ll begin by identifying and
studying fundamental principles that transcend any particular networking technology, and then illustrate these principles in practice in the context of WiFi and
cellular networks. Our goal here is to separate out the “why” and “how,” from the
“what.” There are many books and other documents that describe “what” is done
in a particular wireless network architecture. Indeed, there are (rather dry) standards, many of them thousands of pages long, describing the “what” in great
detail. Sections 7.2–7.4 thus aim to provide a foundation to understand the
“why”—why an architecture is structured a certain way, or why a protocol takes a
particular approach to accomplish a task. This deeper understanding will also
last far beyond the lifetime of any specific wireless technology, helping to futureproof your knowledge of wireless and mobile networks!
Device mobility is such a unique feature of wireless networks that we’ll
devote an entire section (Section 7.5) to this important topic. While we focus
primarily on 5G and WiFi networks throughout this chapter, there are other
widely deployed wireless network architectures as well. In Section 7.6, we’ll
thus briefly cover Bluetooth, satellite, and IoT wireless networks.Section 7.7
concludes this chapter. We’ll defer our discussion of security in wireless networks to the next chapter.


## 7.1 Introduction

Figure 7.1 shows the setting for our discussion of wireless and mobile networks. We’ll begin by keeping our discussion general enough to cover a wide
range of networks, including 5G cellular networks, WiFi local area networks
(WLANs), and ad hoc networks including Bluetooth and IoT networks.
We can identify the following key common elements in a wireless
network:
* Wireless access networks. At the highest level, a wireless network has one or
more wireless access networks. The wireless access network lies at the
outermost “edge” of the entire network, connecting devices into a larger




Figure 7.1 Elements of
a wireless network

network via a wireless radio channel. An access network can be thought of
as a type of local area network, as studied in Chapter 6: it has limited geographic scope, is under the control of a single service provider, and primarily provides a link-layer service. In cellular networks, the wireless
access network is known as the Radio Access Network (RAN). In WiFi
networks, the wireless access network is often referred to as a Wireless
Local Area Network (WLAN).
* Wireless core network. The wireless core network consists of servers, storage, routers, and (typically wired) links that lie between the devices in a
provider’s access network and the external network. The core network
may be geographically distributed, e.g., with some parts collocated with
infrastructure in the access network and other parts located in distant data
centers. The core network implements higher-level control-plane and
management-plane services (e.g., for user and device identity, mobility,
and access-security management) as well as data-plane services that
­forward datagrams from devices in the access network to the larger Internet,
and vice versa. In cellular networks, there is a well-defined core network
operated by the cellular network provider; we’ll study the 4G 5G core
network in Section 7.4. Unlike 4G 5G, there is no corresponding wireless
core network for WiFi. Instead, an enterprise uses the same infrastructure
for WLANs that it uses for its wired LANs. In this sense, an enterprise
views WiFi as just another link-layer technology in its enterprise network.
* Wireless devices. A wireless device might be a smartphone, tablet, or laptop, or
an IoT device such as a sensor or appliance. As in the case of wired networks,
it is these devices that host and run applications. As shown in Figure 7.1,
wireless devices attach to a wireless access network. We note that wireless
devices may or may not be mobile—a topic we’ll return to in Section 7.5.
* Base station. The base station is arguably the most important and most
unique part of a wireless network, as it has no counterpart in a wired network. A base station is responsible for sending and receiving packets to
and from the wireless user devices that are associated with that base station. That is, all wireless devices that send packets into the Internet and


Wireless and Mobile Networks

receive packets from the Internet do so via a base station. A base station
will typically be responsible for multiple associated wireless devices.
When we say a wireless device is “associated” with a base station, we
mean that (1) the device is within the wireless communication distance of
the base station, and (2) the device and base station have executed a protocol that has resulted in the base station serving as a relay of packets
between the device and the larger Internet. The transmission of frames
from the base station to the associated devices is often said to take place
on the downstream or downlink channel, while transmission of frames
from the associated devices to the base station takes place on the upstream
or uplink channel.
* In 5G networks, the base station is known as a gNodeB, abbreviated gNB,
which stands for “Next Generation Node B” in the 5G standards. In 4G
networks, the base station is referred to as an eNodeB, which stands for
“evolved Node B,” abbreviated eNB. These are possibly the least intuitive,
least self-explanatory, and most impenetrable acronyms in all of networking! For that reason, and always preferring to use descriptive language
rather than jargon, we’ll refer to base stations in 4G and 5G networks simply as “base stations.” However, if you’re going to dig into the technical
standards, keep in mind that “eNB” and “gNB” are 3GPP terminology for
“base station” in a 4G or 5G network, respectively. In WiFi networks, a
base station is referred to as an Access Point (AP). Since that terminology
is more descriptive and in common use, we’ll also occasionally refer to
WiFi base stations as APs.
Devices associated with a base station are often referred to as operating in
infrastructure mode, since traditional network services (e.g., address assignment, identity and access privileges, and routing) are provided by the network
infrastructure to which a device is connected via the base station. In ad hoc
networks, wireless devices have no such infrastructure with which to connect.
In the absence of such infrastructure, the devices themselves must self-­organize
and provide for services such as routing, address assignment, DNS-like name
translation, and more. WiFi networks can operate in either infrastructure or
ad hoc mode, but we’ll assume throughout this chapter that WiFi networks
have a base station, i.e., operate in infrastructure mode. Bluetooth networks,
which we’ll study in Section 7.6, are an example of purely ad hoc networks.
[­Mohapatra 2004] provides a detailed study of ad hoc networks.
When a mobile device moves beyond the range of one base station and
into the range of another, it will change its point of attachment into the larger
network, i.e., change the base station with which it is associated—a process
referred to as handoff or handover. Such mobility raises many challenging
questions. If a wireless device can move, how does one find the mobile device’s
current location in the network so that data can be forwarded to that mobile
device? How is addressing performed, given that a device can be in one of
many possible locations? If the device moves during a TCP connection or
voice/video call, how are datagrams forwarded so that the connection continues uninterrupted? We’ll look at the answer to these and many other
mobility-related questions in Section 7.5.



Let’s now dive deeper into our study of wireless networks, bottom-up and
beginning at the network edge, with a study of wireless radio channels.


## 7.2 The Physical Layer in

Wireless Networks
You may have noticed that our study of networking so far has mostly steered
clear of the physical layer. There is only so much material one can cover in a
single book and an understanding of a few simple physical-layer characteristics such as bit transmission rate, bit error rate, and propagation delay has been
sufficient to understand the material we’ve covered in Chapters 2 through 6.
But this is not so in the case of wireless networks! Thus, in this section and the
next, we’ll dive down into the details of the wireless network physical layer.
We’ll adopt more of a computer-science perspective than a traditional EE perspective on the wireless channel, offering more of an intuitive description of
the physical layer rather than a more precise mathematical description.


### 7.2.1 Characteristics of wireless channels

At the most basic level, a time-varying electric current in an antenna at one
location (the transmitter), creates electromagnetic (radio) waves that propagate
through space and create a current in receiving antenna(s) at other location(s).
The transmitter will code information into the electromagnetic signal by
changing (also known as “modulating”) characteristics of the electromagnetic
wave. Given the coding of information in the electromagnetic signal, it’s
important that we understand some of these basic characteristics of electromagnetic waves.

Radio Waves: Amplitude, Frequency, and Phase
Figure 7.2 shows the electric field component of an electromagnetic wave—a
figure you may perhaps recall from an introductory physics course. An electromagnetic wave is characterized by its
* amplitude: the height of a wave at a particular point in space and time;
* wavelength (λ ): the distance between two successive wave peaks in the
wave;
* cycle time: the time between two successive wave peaks;
* frequency: 1 cycle time, measured in Hertz (Hz). A one-megahertz (MHz)
wave, for example, has 1 × 10 6 cycles sec;
* phase: the fraction of a cycle covered up until time t. As shown in Figure 7.2,
phase is measured from a reference point in time, typically, when the
wave’s amplitude is zero and increasing. Phase is also typically expressed
in angular units, i.e., from 0 to 360 degrees. Thus, if the phase were equal to
75 percent of a cycle, this would correspond to a phase of 270 degrees.


Wireless and Mobile Networks

Figure 7.2


Electromagnetic wave:
amplitude, wavelength,
and phase

Electromagnetic waves have a direction and propagate at approximately
the speed of light, 3 × 10 8 m sec.

Radio Transmission: Power, Bandwidth
Informally, we understand from our everyday experience, that radio signals
may be strong or weak, and that they may be clear or filled with static (“noise”).
Let’s next formalize these concepts.
Power is the amount of energy per unit time that a transmitter puts into its
emitted electromagnetic waves. We can think of power informally as the signal’s strength. Power is measured in units of watts, typically milliwatts (mW)
in wireless networks. Electrical engineers sometimes like to measure power in
decibel milliwatts (“dBm”), which is the logarithm of the ratio of the signal’s
power (measured in mW) to one mW. But we’ll use the more common linear
measure of mW here.
The idealized electromagnetic wave in Figure 7.2 has just one frequency.
That is, all of the radiated electromagnetic energy is concentrated at one
­specific frequency. In practice, a transmitter’s power will be spread across
more than one frequency. The power spectral density function, shown in
­Figure 7.3(a), characterizes the amount of power present in the transmitter’s
signal as a function of frequency. A power spectral density function is typically
centered around a so-called carrier frequency, as shown in Figure 7.3(a). The
carrier frequency in the example of Figure 7.3(a) is 1 GHz.
Equipped with the concept of power spectral density, we can now carefully define the notion of a radio signal’s bandwidth—a key physical-layer
concept in wireless networks. A radio signal’s bandwidth, as its name suggests, is the width (measured in Hz) of the range of frequencies occupied by
the signal. The signal in Figure 7.3(b), has a bandwidth of 22 MHz, with its
power spread evenly between 2.427 and 2.429 GHz. We’ll see in Section 7.6
that this particular 22 -MHz-wide “channel”—i.e., a radio channel with a
22 MHz bandwidth—corresponds to channel 6 in a WiFi network.
It’s important to note that this precise notion of signal “bandwidth” in the
wireless physical layer—the width of the frequency band occupied by a radio



Figure 7.3 (a) Signal power spectral density, (b) signal bandwidth (idealized)

signal—is very different from the rather informal use of the term “bandwidth” elsewhere in networking to refer to a link’s bit transmission rate or capacity. Students
are often understandably confused by this. For starters, note that radio signal
bandwidth is measured in Hertz, while a link’s transmission rate is measured in
bits per second (bps). As we’ll see, a radio channel’s bandwidth (in Hertz) is
related to the rate at which bits can be transmitted across a radio link (in bits per
second). In general, the larger the bandwidth, the higher the rate at which bits can
be transmitted. For example, a 20-MHz-wide 802.11n WiFi channel (Section 7.3.2)
supports a maximum transmission rate of 72.2 Mbps, while a 40-MHz-wide
802.11n WiFi channel has a maximum transmission rate of 150 Mbps [Intel 2024].
But as we will see, the relationship between radio channel bandwidth (measured
in Hertz) and link transmission bandwidth (measured in bits per second) is rather
complex. We’ll be careful to use the term “bandwidth” in this chapter to mean the
width of the frequency band occupied by a radio signal.
We know from our everyday experience (e.g., from listening to AM, FM, or
satellite radio) that radio signals can sometimes be clear but at other times be
filled with noise. The top part of Figure 7.4 shows the original “clean” signal
from Figure 7.2, with additional noise signal introduced between the transmitter
and receiver (the middle section of Figure 7.4), and the received signal (the bottom part of Figure 7.4). Looking at the middle section of the noisy received
signal, you can perhaps appreciate the challenge of extracting the original transmitted signal from the received noisy signal. There can be many sources of noise:
* Interfering transmitters. Certain radio frequency bands are reserved for
“unlicensed” use, meaning that many industrial and consumer devices can
transmit radio waves in that band, subject to power restrictions. One of
these bands is the 2.4–2.5 GHz band, where baby monitors, garage door
openers, and many other home devices can all transmit signals. Even
more importantly, many networks—WiFi, Bluetooth and Zigbee
(IEEE 802.15.4) networks, for example—use the unlicensed 2.4–2.5 GHz
band and do so in an uncoordinated manner. Of course, it’s fine when it’s
your WiFi network using this band, but nearby networks owned by others
look just like noise to your network! As the saying goes, “One person’s
network transmission is another person’s noise.”


Wireless and Mobile Networks

Figure 7.4 Original


signal, noise, and noisy
received signal

* EM radiators. Electric motors and microwaves, particularly older models
with less shielding, can emit radio waves.
* Thermal and electronic noise. Natural thermal variations and imperfections
in electronics at a transmitter or receiver can add noise to the signal.

Radio Channel: Noise, Signal-to-Noise (SNR) Ratio,
and Capacity
The ratio of the signal power to noise power is known as the signal-to-noise
ratio (SNR). The SNR is typically measured in decibels (dB):
 received signal power 
SNR ( dB ) = 10 i log 10 



noise power
Note that an SNR value of 0 means that there is an equal amount of signal and
noise. For WiFi networks, a minimum acceptable value of SNR in a received
signal is around 20 dB [Meraki 2023]; the minimum acceptable value for LTE
ranges from –5 to 18 dB, depending on the modulation technique used; see
Section 7.2.2 [Rohde and Schwarz 2013].
With the concepts of power, bandwidth and noise in hand, we’re now ready
to state one of the most important results in communication theory, Shannon’s
capacity theorem. Shannon’s theorem relates communication channel capacity,
C—the maximum possible rate at which data can be transmitted (measured in
bits per second), error-free, over the channel—to the channel’s bandwidth (B),
and received signal and noise powers (both measured linearly, e.g., in mW):

received signal power 
C = B i log 2  1 +



noise power
It’s important to note that Shannon’s capacity theorem gives an upper bound
on channel capacity. It says that no matter how cleverly data is coded and
modulated into the wireless signal, the amount of received data will be less
than or equal to C, for a given channel bandwidth and SNR. There are also several important practical consequences of Shannon’s capacity theorem:
* At a given SNR, maximum channel capacity scales linearly with channel
bandwidth. A wider channel bandwidth means the potential to transmit
more bits per second.


* For the case of a high SNR, there is little additional benefit in expending
more effort to increase the SNR, since the maximum capacity will only
increase logarithmically, i.e., sublinearly with increasing SNR.

Radio channel properties: path loss, multipath, and
hidden terminals
A radio signal can change in important ways as it propagates from transmitter
to receiver. Most fundamentally, a wave loses strength as it propagates. This
weakening of a radio signal as it propagates is referred to as path loss or
­attenuation. In the case of an unobstructed line-of-sight path from transmitter
to receiver, the ratio of the transmitted power to received power decreases
according to an inverse-square law:
Preceived
~
Ptransmitted
( fd )
where Ptransmitted and Preceived are the transmitted and received powers, respectively, f is a signal’s frequency, and d is the distance between the transmitter
and receiver.
The intuition behind this quadratic path loss is illustrated in Figure 7.5.
Since the surface area of a sphere increases as the square of the distance
between the center and surface of the sphere, the energy passing through a
unit of area at distance d from the sender is the same amount of energy that
passes through area four times larger at distance 2 d , and an area nine times
larger at distance 3d. The path loss exponent of 2 is for so-called free-space path
loss in air. A path loss exponent of around 3 is common in an outdoor urban
environment, and a path loss exponent of 4 or higher is common within
­buildings—making path loss an even more important concern.
The quadratic path loss in both distance and frequency has important
ramifications for radio communication: low frequency (e.g., kHz) radio tends
to be used for long-distance, low-data-rate radio applications such as radio
navigation, while high frequencies (e.g., GHz) tend to be used for relatively
shorter distance terrestrial applications including cellular and WiFi networks.
The exponential decrease in received power as a function of distance gives
rise to the hidden terminal problem, a phenomenon that will drive the design

Figure 7.5 Free space
path loss decreases
according to the square
of the distance between
transmitter and receiver


Wireless and Mobile Networks

Figure 7.6 Hidden terminals: A and B can hear each other, B and C can hear each
other, but A and C cannot hear each other

of wireless link-layer multiple access protocols such as WiFi’s CSMA/CA protocol (Section 7.3.1). Figure 7.6(a) illustrates the case where nodes A and B can
“hear” each other, i.e., the received power levels of their signals are above a
detection threshold. Similarly, nodes B and C can hear each other. However,
because of path loss, nodes A and C cannot hear each other because their
received power levels have dropped below the detection threshold. Thus, nodes
A and C are “hidden” from each other. One can already appreciate how hidden
terminals will impact wireless CSMA protocols—if A and C want to transmit to
B they may listen to the channel, not hear each other transmitting (due to path loss),
and yet their transmissions to B will interfere with each other at B. Figure 7.6(b)
illustrates another hidden terminal scenario where A’s and B’s signals are physically blocked from each other. And yet in this case as well, their transmissions
interfere with each other at B. Clearly, communicating over a wireless channel
will be more complicated than communicating over a wired channel!
The inverse square law also states that the received power decreases exponentially not just in distance, but in frequency as well. This exponential
decrease with frequency also has very important consequences in wireless networks. It means, for example, that moving from a fixed-bandwidth channel at
5 GHz to a similar channel at 50 GHz , will result in 100 times less power
received at 50 GHz! Thus, channels at higher frequencies tend to operate at shorter
ranges, while lower frequency channels tend to be used to cover longer distances.
Figure 7.7 illustrates another important characteristic of wireless communication: multipath signals. In this figure, part of the radio signal transmitted by a
sender follows a direct line-of-sight path to the receiver, shown conceptually as
a received green pulse in Figure 7.7(a). However, the transmitted signal also
reflects off of objects (e.g., buildings) in the environment and arrives at the
receiver at slightly later points in time, as the reflected pulses have travelled
longer distances from the transmitter to the receiver. These multipath received
signals are shown as the red and purple pulses in Figure 7.7(b). Because of multipath, the reception of a signal that was transmitted at a given instant of time at
the sender is spread out over time at the receiver. Clearly, multipath will complicate the receiver’s job of reconstructing the originally transmitted signal.
Multipath also places constraints on the maximum rate at which a transmitter can change its transmitted signal, and consequently constrains the rate




Figure 7.7 (a) Line-of-sight (LoS) signal; (b) LoS and reflected signal reception

at which a transmitter can transmit bits. Figure 7.8 shows two transmitted
pulses from the sender. The transmitter must space its signal/pulse transmissions far enough apart so that the LoS signal (the green pulse in Figure 7.8) and
all of its multipath reflections (the red and purple pulses) are received at the
receiver before the next LoS signal/pulse is received. If this isn’t done, the two
pulses and their reflections will be mixed in time at the receiver. This receiverdictated minimum amount of time needed between changes in the sender’s
signal is referred to as the receiver’s coherence time.

Antennas: MIMO
The antennas deployed in most of today’s wireless cellular and WiFi base stations and devices aren’t at all like your grandparent’s (or even your parent’s)
antennas! Beginning in the early 2000s wireless networks began moving from
systems with a single antenna at the transmitter and a single antenna at the
receiver, to multiple-input and multiple-output (MIMO) antennas that use
multiple antennas at both the transmitter and receiver. As we’ll see, these innovative MIMO technologies have allowed radio networks to significantly
increase link throughput (the number of bits per second successfully received)

Figure 7.8 Multipath
reflections determine
coherence time


Wireless and Mobile Networks


between transmitter and receiver. One immediate advantage of having multiple antennas at the receiver should be apparent –N receiver antennas means
(to a first approximation) that the total received signal has N times more
power. But MIMO systems are about much more than that!
MIMO gains its advantages over single-antenna systems by exploiting the
multiple paths between sending and receiving antennas in one of two fundamentally different ways:
* MIMO spatial diversity. MIMO spatial diversity techniques send redundant streams of information from a transmitter to a receiver, exploiting the
fact that radio signals travelling on different physical paths between the
one or more transmitting antennas to the one or more receiving antennas
will experience different degradations (e.g., multipath effects). This technique is essential in combating the adverse effects of multipath fading,
where signal reflections from buildings, trees, and other obstacles cause
variations in signal strength. By receiving multiple copies of the signal
through different paths, MIMO systems can combine these signals in a
way that maximizes signal strength and minimizes error rates. Even
though antennas may be separated by only a few centimeters (e.g., on a
cell phone), signals received on different paths may indeed experience
quite different channel conditions.
* Figure 7.9(a) shows the case of a single transmitting antenna and two
receiving antennas. Spatial diversity can also be exploited with multiple
transmitting antennas, but we’ll focus on the simplest case here; see
[­Halperin 2010] for a readable introduction to the more general case.
* Suppose that the transmitter sends an original signal, x. The upper antenna
receives a signal y 1 = H 1, 1 ( x ), where the H 1, 1 () function represents how
the transmitted signal has been changed (e.g., in amplitude and phase)
between the single transmitter antenna and the upper receiver antenna.
Similarly, the lower antenna receives a different signal y 2 = H 1, 2( x ). But
what should the receiver do with these two different received signals? This
is where physical-layer signal-processing techniques come in. Simply
“adding” the signals together would essentially just recreate the effects of
single-antenna multipath. One might instead choose to select the y i signal
with the largest SNR. Or one might first choose to align the phases of the
received signals (which may have been shifted as a result of transmission)
and then coherently add the signals together, perhaps weighting the contributions of the two signals by their SNRs. These are but two of the many
techniques that can be used to recover the original signal from multiple
received signals [Goldsmith 2005; Tze 2005].

Figure 7.9 Simple

MIMO (a) spatial diversity,
(b) spatial multiplexing


* MIMO spatial multiplexing. In the case of MIMO spatial multiplexing,
multiple different streams of information are sent in parallel along the different paths from transmitter antennas to receiver antennas. This is illustrated in Figure 7.9(b), which shows an example where two different
streams of information, x 1 and x 2 are transmitted by two different transmitting antennas. At the receiver, each antenna receives a signal containing both streams of information, with each component stream having
experienced different degradations. For example, the received signal at
the upper receiver antenna is represented by y 1 = H 1, 1 ( x 1 ) + H 2, 1 ( x 2 ),
where the sum indicates that the signals are combined in the air, that the
original signal x 1 has been transformed according to H 1, 1 () on its way to
the upper receiving antenna, and that x 2 has been transformed by H 2, 1()
on its way to this upper antenna. The signal received at the lower antenna, y 2 ,
has an analogous interpretation.
* The receiver’s task is to determine the original signals x 1, x 2 , given the
received signals, y 1, y 2 . Of course, H 1, 1 () and H 2, 1() are unknown in practice, but they can be estimated if the sender and receiver work together. This,
together with the observation that Figure 7.9(b) has two equations (one for
y 1, one for y 2 ) with two unknowns (x 1 and x 2 ), hints at the type of signal
processing algorithms that might be used at the receiver to compute the
original signals, x 1 and x 2 . In practice, a sender can also perform coding and
modulation that helps the receiver improve its estimates for x 1 and x 2 .
The theory and practice of the MIMO signal-processing techniques are
well beyond the scope of what we can cover here. Our modest goal here has
been to introduce spatial diversity and spatial multiplexing and give a flavor
of the types of signal processing that is at the foundation of MIMO systems.
The reader is referred to [Goldsmith 2005; Tze 2005; Halperin 2010] for more
in-depth treatments.

Beam Forming and Directional Antennas
Beamforming involves directing the transmitted signal towards a specific user
or area instead of radiating the signal in all directions. Beamforming with
directional antennas enhances signal strength at the receiver, reduces interference, and improves overall wireless communication performance.
Beamforming is typically implemented using an array of antennas. By
adjusting the phase and amplitude of the signal at each transmitting antenna,
the system can create constructive interference in the desired direction and
destructive interference in others, forming a “beam” of radio waves. Beamforming can be dynamic, with the system continuously adjusting the beam
direction based on the location of the user. This ensures optimal signal quality
even as users move. Beamforming has the following benefits:
1. Increased signal strength: By focusing the signal in a specific direction,
beamforming increases the signal strength received by the intended user,
leading to higher data rates and more reliable connections.
2. Reduced interference: Beamforming reduces interference with other
users by minimizing signal leakage into undesired directions. This leads
to better performance in dense environments with many devices.


Wireless and Mobile Networks

3. Improved coverage: Directional beams can extend the coverage area of
wireless networks, providing better connectivity at the edges of the coverage zone.
4. Enhanced capacity: By enabling more efficient use of the available spectrum, beamforming can increase the overall capacity of the network, supporting more users simultaneously.
Beamforming is used widely in WiFi, modern cellular networks, and satellite communications.

Multi-user MIMO (MU-MIMO)
Our MIMO discussion above has implicitly focused so far on Single-user
MIMO (SU-MIMO)—using multiple antennas at the transmitter and/or
receiver to transmit to a single device, as shown in Figure 7.10(a). In practice,
the number of antennas in such systems is small, e.g., 2 to 4 antennas in a WiFi
base station.
In cellular networks, MIMO techniques are also used to send from one
sender to many receivers simultaneously. This is known as Multi-user MIMO
(MU-MIMO), or sometimes as Massive MIMO. MU-MIMO uses different subsets of its antennas to transmit to multiple different devices at the same time, as
shown in Figure 7.10(b). Each subset of antennas, in turn, uses MIMO spatial
diversity to transmit multiple signals with the same information to a device. In
addition, MU-MIMO often employs beamforming as just described and shown
in Figure 7.10(b). A modern MU-MIMO antenna for a 5G base station can contain an array of up to 64 beamforming transmitter elements, and an equal or
similar number of receiving antenna elements [Ericsson 2024; Samsung 2021].

Radio Spectrum
The radio spectrum is the range of the electromagnetic spectrum from 3 Hz to
3 THz. The radio spectrum is considered a national asset and thus its use is

Figure 7.10

Beamforming in
MU-MIMO



regulated by individual countries, with some coordination (but no regulation)
provided by a United Nations agency known as the International Telecommunication Union (ITU). Typically, a country assigns specific frequency ranges of the
radio spectrum for specific uses. A popular poster graphic (“popular” at least
among radio geeks!) [NTIA 2016] shows the allocation of the US radio spectrum
for uses that include maritime and aeronautical radio navigation; terrestrial AM,
FM, and television broadcasting; satellite broadcasting; radio location (e.g., GPS);
amateur radio; radio astronomy; weather radar, consumer wireless devices, and
of course, to the wireless networks covered in Sections 7.3 through 7.6.
There are two broad classes of spectrum-use types:
* Licensed spectrum. As the name would suggest, a government-issued
license must be obtained to operate a transmitter in a licensed spectrum
band; this includes the spectrum bands used by commercial cellular network providers (see Table 7.1).
* In many countries, spectrum is allocated to commercial cellular network
providers through spectrum auctions, which have generated tens to hundreds of billions of dollars of licensing fees in India, the UK, and the US.
One consequence of commercial purchase of expensive spectrum rights
(as well as the costs of tower and land access needed to operate a cellular
network) is that cellular commercial services (say unlike WiFi providers)
must price their services so that they can cover all of these costs and make
a profit. Because of the scarcity and cost of licensed spectrum, new
­spectrum-sharing methods are being developed to allow non-incumbent
devices (i.e., devices not associated with the spectrum licensee) to use the

Table 7.1 Most common US spectrum bands used by wireless networks (non-exhaustive; non-US
frequencies differ slightly)
Spectrum band
(informal name)

Network Type

(L)icensed
(U)nlicensed

Comments


## 2.4 GHz ( 2.40 – 2.49 GHz )


WiFi, Bluetooth,
Zigbee

U

WiFi: 802.11 b/g/n/ax . See Section 7.3.2.
Bluetooth: See Section 7.6.1.

5 GHz ( 5.17 – 5.83 GHz )

WiFi

U


## 802.11 a/h/n/ac/ax . See Section 7.3.2.


6 GHz ( 5.9 – 7.12 GHz )

WiFi

U


## 802.11 ax/be. See Section 7.3.2.


< 1 GHz (various cellular “lowband” frequencies)

cellular

L

2G/3G/4G/5G. See Section 7.2.2. Low-band
frequences cover longer distances (10s of miles),
but at lower speeds ( 50 – 250 Mbps ).


## 1.8 GHz, 3.3 – 3.8 GHz, 6 GHz

(various cellular “mid-band”
frequencies)

cellular

L

2G/3G/4G/5G. See Section 7.3.3. Midband
frequencies are the “sweet spot,” balancing
distances ( 5 miles ) and transmission rates
(100 – 900 Mbps ).


## 3.5 GHz Citizens Broadband Radio

Service (CBRS)

cellular

L/U

CBRS also known as “Private 5G”.

26 GHz, 40 GHz, 50 GHz, 66 GHz
(various cellular “high-band”
frequencies)

cellular

L

5G. See Section 7.3.2. High band frequencies, also
known as “millimeter wave” frequencies, cover short
distances (< mile), but at high speeds (< 3 Gbps ).

915 MHz ( 902 – 928 MHz )

LoRa (IoT)

U

See Section 7.6.3


Wireless and Mobile Networks

incumbents’ licensed spectrum under specific rules and conditions. As an
example, in the US, the 3.5GHz CBRS band (see Table 7.1) allows cellular
base stations (non-incumbents) to transmit if there are no naval radars
(incumbents) in the spectrum. Many approaches are being explored,
including cognitive radio schemes that dynamically sense and use spectrum not currently in use. See [Parvini 2023] for a recent survey.
* Unlicensed spectrum. Portions of the spectrum are also available for unlicensed use. This means that institutions and people can purchase and use
devices (e.g., garage door openers, baby monitors, microwave ovens, and
much more) and wireless networks (notably WiFi networks) that operate in
the unlicensed spectrum without obtaining a license. However, these
devices must conform with use rules, e.g., limiting their transmission power
level. Also, since many uncoordinated devices can transmit in unlicensed
spectrum, they can interfere with each other. We’ll see throughout this chapter that wireless networks operating in the unlicensed spectrum take many
different approaches to avoid, mitigate, and respond to this interference.
Table 7.1 presents a non-exhaustive list of the most common spectrum
bands used by wireless networks.
In this section, we’ve already covered a lot of material about the characteristics of the wireless channel, all of which will serve us well in understanding
the higher layers of wireless networks. But before we leave the physical layer,
we need to cover one more foundational physical-layer concept—how bits
from the link layer are transformed into symbols and how symbols are then
transformed into transmitted waveforms.


### 7.2.2 Coding and Modulation: from bits to

symbols to waveforms
In this subsection, we’ll move “up” the stack (while staying in the physical
layer) and discuss how a wireless transmitter groups the bits that are to be
transmitted into “symbols,” which are then encoded into waveforms that are
then transmitted over the wireless channel. At the receiver, symbols are then
extracted from the received waveform and translated back into bits.
Figure 7.11 shows the major steps in physical-layer transmission and
reception. Data bits are presented to the physical layer at the transmitter from
the link layer above. These bits are then processed into electromagnetic waveforms that propagate over the channel to the receiver, where they are

Figure 7.11 Major steps in physical-layer transmission and reception



transformed back into bits that are then passed from the physical layer to the
link layer. Ideally, these bits also pass through this processing and transmission pipeline as fast as possible.

Physical-layer coding
In the first step (“coding”) the original data bits from the link layer may be
expanded, e.g., in the simplest case, redundant copies of the original bits can
be added to the original set of bits to protect against the corruption of some of
the transmitted bits by channel noise. It is important to note that bits added
here in the physical layer are in addition to checksum or CRC bits that have
been added at the link layer, and that we studied in Chapter 6. If a link-layer
frame contains checksum or CRC bits, these bits are treated in the physical
layer exactly the same as any other bits in the link-layer frame, and so may
themselves be protected by added physical-layer bits!
The transmitted bits might also be reordered, e.g., spreading redundant
bits among the transmitted bits, so that a burst of noise does not cause all copies of a bit to be affected. The receiver then reverses the encoding steps to
recover the original bitstream. For example, eight original data bits
d 1 d 2 d 3 d 4 d 5 d 6 d7 d 8
might be expanded (where d i ’ denotes a copy of the ith bit) to 16 bits:
d1 d1 ’ d 2 d 2 ’ d 3 d 3 ’ d 4 d 4 ’ d 5 d5 ’ d6 d 6 ’ d7 d7 ’ d8 d8 ’
and then shuffled to produce:
d1 d 5 ’ d 2 d 6 ’ d 3 d7 ’ d 4 d8 ’ d5 d1 ’ d6 d 2 ’ d7 d 3 ’ d 8 d 4 ’
If, for example, three bits in a row experience a burst of interference when
transmitted (where x denotes a bit that the receiver is not able to extract from
the received signal):
d1 d 5 ’ d 2 d 6 ’ d 3 d7 ’ x x x d1 ’ d 6 d 2 ’ d7 d 3 ’ d 8 d 4 ’
then after the receiver unshuffles the received bits to obtain:
d1 d1 ’ d 2 d 2 ’ d 3 d 3 ’ x d 4 ’ x d 5 ’ d6 d 6 ’ d7 d7 ’ d8 x
there are still enough received bits for the receiver to recover the original eight
data bits, even in the presence of a burst error. There are much more sophisticated coding techniques that offer more efficient techniques than the simple
redundancy code illustrated above, and indeed entire courses are taught on
this topic; see [Goldsmith 2005].
Lastly, we note that the dashed arrows at the top of Figure 7.11 from the
receiver to the transmitter represent receiver feedback that is used by the transmitter to choose a modulation technique that is best suited to the current (yet
changing) wireless channel conditions—a topic we’ll consider shortly at the
end of this section.

Modulation: amplitude, frequency, and phase
Modulation lies at the heart of the wireless transmitter’s physical layer. Modulation takes coded bits from the coding module shown in Figure 7.11 and
creates waveforms that encode these bits.


Wireless and Mobile Networks

Figure 7.12


Amplitude, frequency, and
phase modulation

As shown in Figure 7.12, there are three common approaches for encoding
information into a radio signal, sometimes referred to as a carrier signal. Each
approach encodes information by changing or “modulating” one of the three
fundamental radio-wave characteristics discussed in Section 7.2.1: the signal’s
amplitude, frequency, or phase.
* Amplitude Modulation. In amplitude modulation, also known as amplitude
shift keying (ASK), bit values are encoded into the carrier signal by changing
the signal’s amplitude among several discrete values. The “amplitude modulation” timeline in Figure 7.12 shows how the 0- and 1-bit values at the top
of the figure that are to be transmitted during different intervals of time are
encoded by setting the carrier signal’s amplitude to 0 or 1, respectively.
* Frequency Modulation. In frequency modulation, also known as frequency shift keying (FSK), bit values are encoded into the carrier signal by
changing the carrier signal’s frequency during different time intervals. The
“frequency modulation” timeline in Figure 7.12 shows how the signal’s
frequency is set to one of two frequencies to encode a 0- or a 1-bit value.
* Phase Modulation. In phase modulation, also known as phase shift keying (PSK), bit values are encoded into the carrier signal by changing the
phase of the carrier signal during different time intervals. In the “phase
modulation” timeline in Figure 7.12, the red signal has a zero-and-increasing
value at the start of a time interval; this phase encodes a 0-bit value in this
example. The blue curve is 180 degrees out of phase from the red curve; it
has a zero-and-decreasing value at the start of a time interval and encodes
a 1-bit value.
In these examples, we see that the receiver can determine whether a bit
value of 0 or 1 is encoded into the transmitter’s analog radio signal simply by
measuring the amplitude, frequency, or phase of the radio signal. Note the
ability to detect frequency and phase shifts implies that the clocks at the sender
and receiver have been carefully synchronized.

Quadrature Phase Shift Keying (QPSK)
Our example in Figure 7.12 shows two values of amplitude, frequency or
phase being used to encode a single bit value. But why stop at two values?


Why not use more than two values of amplitude, phase, or frequency to encode
more than just two values? And why not modulate the amplitude, phase or frequency values at the same time to encode even more information? The answers
to these questions lie at the heart of modern, physical-layer modulation techniques standardized for 4G 5G, WiFi, Bluetooth, and other wireless networks.
Thus, let’s next consider grouping the serial bits exiting the coding module in Figure 7.11 pairwise, two bits at a time: if the two serial bits values are a 0
followed by another 0 they will be grouped together and become the single
symbol “00”; if two serial bits values are a 0 followed by a 1, they will be
grouped together and become a different symbol, “01”; if two serial bits values
are a 1 followed by a 0, they will be grouped together and become the symbol,
“10”; and two serial bits values of a 1 followed by a 1, they will be grouped
together and become the symbol, “11”. The transmitter’s job of transmitting a
stream of bits is now transformed into the job of transmitting symbols. Since
there are four symbol values ( “00”, “01”, “10”, “11” ) that can be transmitted,
four different values of phase shift will do nicely to represent these four symbol values. This approach of using four phase values to encode four different
symbols (which represent four different pairs of two-bit values) is known as
Quadrature Phase Shift Keying (QPSK), illustrated in Figure 7.13.
Notice that in QPSK, all signals have the same amplitude but have phase
values separated by 90 degrees: of 45° (red), 135° (green), 225° (blue), and 315°
(purple). The receiver need only measure the signal’s phase to determine
which of the four symbols is being transmitted. Note also that the rate at which
symbols are processed is only half of the bit rate, leaving more time for symbol
signal processing than bit-by-bit signal-processing. A fun interactive Web site
where you can learn about and play with QPSK signals is https://www.geogebra.
org/m/enkymjtg
The four symbols in QPSK can be succinctly characterized in a diagram
known as a constellation diagram. A point in a constellation diagram depicts
the symbol’s phase (measured in degrees counterclockwise from the east, i.e.,
3:00, position) and amplitude (measured in distance from the origin). The four
QPSK symbols are represented as red dots in Figure 7.14. For example, the
symbol in the northeast quadrant has a phase of 45 degrees. As we’d expect,
the four QPSK symbols shown in Figure 7.14 have the same phases of 45°,
135°, 225°, and 315° and all have the same amplitude.

Figure 7.13

Quadrature Phase Shift
Keying (QPSK)


Wireless and Mobile Networks


Figure 7.14 QPSK
constellation diagram—
four symbols represented
by four signal waveforms
that have four different
phases and identical
amplitudes

Quadrature Amplitude Modulation (QAM)
In QPSK, only the signal’s phase is modulated. In quadrature amplitude modulation (QAM), a signal’s phase and its amplitude are both modulated. QAM
is nicely illustrated using constellation diagrams. Figure 7.15 shows the constellation diagrams for 4-QAM, 16-QAM and 64-QAM. The number preceding
“-QAM” refers to the number of symbols in this version of QAM. 4-QAM is
essentially the same as QPSK and has 4 symbols. Figure 7.15 also shows the bit
values encoded by a symbol—2 bits for 4-QAM, 4 bits for 16-QAM, and

Figure 7.15 Bit encodings for 4-QAM, 16-QAM, 64-QAM, constellations (for WiFi)



Figure 7.16

Transmitted versus
received 16-QAMmodulated signals

6 bits for 64-QAM. 16-QAM, 64-QAM and 256-QAM are used in 4 5G and
WiFi networks, with higher order QAMs ( 1024, 4096 ) appearing in the WiFi-6
and WiFi-7 standards.
A constellation diagram can also provide us with additional insight about
how noise gives rise to bit (or more accurately, symbol) errors. Consider the
16-QAM constellation in Figure 7.16 and suppose a sender transmits the
“1111” symbol shown in solid red. As a result of changing electromagnetic and
measurement noise at the receiver, a “1111” signal’s amplitude and phase will
be received differently each time that signal is transmitted. The yellow-shaded
dots in Figure 7.16 represent possible instances of measured amplitude and
phase at the receiver. Most of the yellow-shaded dots, corresponding to measured amplitude and phase values, are closer to the amplitude and phase of
the “1111” symbol than any other constellation symbol. In these cases, the
receiver would correctly infer that the originally transmitted symbol was
“1111”. However, note that there is one received signal that is closer to the
“1011” symbol than the “1111” symbol; in this case, the receiver would incorrectly infer that the “1011” symbol had been sent, when in fact the “1111”
symbol was transmitted, resulting in an incorrect symbol reception.

Adaptive Modulation
Figures 7.15 and 7.16 also suggest that as the constellation diagram becomes
more densely packed at higher order QAMs, the effects of noise and receiver
measurement error will become more pronounced. This results in higher symbol-error rates, and hence bit-error rates. While higher transmission rates
might seem to always be desirable and thus using a higher-order QAM might
also always seem like a good idea, this won’t be true if the error rate is too
high! This observation offers a valuable insight for physical-layer wireless
­communication—that it will be important for the transmitter and receiver to choose a
modulation technique that is matched to the channel conditions.
Figure 7.17 illustrates this insight. Suppose the goal is to keep the bit error
rate (BER) below 10 −4. At the same time, of course, we’d like to achieve the
highest bit rate possible subject to this constraint. Figure 7.17 indicates that if
the signal-to-noise ratio (SNR, measured in dB) is less than 13, then 4-QAM
should be used. On the other hand, if the SNR is between 13 and 17, then
16-QAM can be used, with a correspondingly higher bit rate. And if the SNR is


Wireless and Mobile Networks


Figure 7.17 SNR
versus BER for 4-QAM,
16-QAM, and 64-QAM

higher than 17, then 64-QAM can be used. As the SNR varies over time, the
modulation technique used by the transmitter and receiver can be changed
dynamically to realize the highest throughput possible at a given time, given
the BER constraint. Of course, this will require that the sender and receiver
coordinate to measure and report BER and SNR, and to coordinate changes in
modulation technique. We’ll see how this is done when we study the 4G/5G
wireless networks.
This concludes our discussion of the wireless physical layer. We’ve covered a lot of ground! Indeed, as we noted at the outset of this section, wireless
networking is an example where the functions of the lower layers cannot be
easily abstracted away with a few easy-to-understand concepts. If you’re a
computer scientist, the wireless physical layer may be quite new ground for
you. Nonetheless, the physical-layer concepts we have learned in this section
will provide a great foundation for a deeper and broader understanding of
wireless networks.


## 7.3 The Wireless Access

Network
In this section, we’ll cover the principles and practice underlying wireless
access networks, including the 802.11 WiFi WLAN and the 4 5G RAN. The
radio channel and modulation and coding topics we just studied are physicallayer topics; the access network principles and practices that we’ll study in this
section are link-layer topics, building on top of this physical-layer foundation.
We’ll begin in Section 7.3.1 by studying how the radio channel is shared
among the many devices and the base station in an access network. Since
we’ve already studied the multiple access problem in Section 6.3, we’ll focus
here on how the basic techniques we learned about there (FDM, TDM and random access) are specialized for a wireless channel. With this common


foundation, along with the foundations from Section 7.2, we’ll then study the
two major wireless access networks: 802.11 WiFi WLAN and the 4 5G RAN in
Sections 7.3.2 and 7.3.3, respectively. We’ll then turn to more specialized topics
related to the wireless access network. In Section 7.3.4, we’ll learn how a wireless device discovers the existence of a wireless access network and the initial
steps taken to join such a network. In Section 7.3.5, we’ll dive deeper into channel sharing, studying bandwidth allocation and the scheduling of frame
transmissions onto upstream and downstream channels. Section 7.3.6 covers
energy use in wireless network devices.


### 7.3.1 Sharing the wireless channel

In Section 6.3, we learned about the various approaches used to share a multiple access channel:
* channel partitioning techniques, including time-division multiplexing
(TDM) and frequency-division multiplexing (FDM);
* random access protocols, including Aloha and Carrier Sense Multiple Access
(CSMA) protocols; and
* taking-turns protocols, including polling.
We’ll assume Section 6.3 as background here, so you may want to refer
back to that section to refresh your understanding. We’ll see that all of these
techniques are used in the wireless network architectures we’ll study! In some
cases, their use is quite straightforward. But in other cases, these basic
approaches are combined or extended specifically for use in wireless networks.
In this subsection, we’ll cover two specific approaches for sharing the wireless
channel: (i) Orthogonal Frequency Division Multiple Access (OFDMA), used
in 4G, 5G and WiFi-6 7 networks; and (ii) carrier sense multiple access with
collision avoidance (CSMA/CA), used in all generations of WiFi networks.
We’ll also learn how the physical radio channel is partitioned into upstream
and downstream channels for link-layer data frame transmission, channel
measurement, network discovery and more.

FDM, OFDM: channels and subchannels
Figure 7.18 shows the starting point of our OFDM discussion. Figure 7.18(a)
shows an idealized single wideband channel, where the power spectrum (see
Section 7.2) is distributed evenly across the frequency spectrum used. Because
a single wideband channel can be difficult to implement in practice (e.g., due
to different impairments being present at different frequencies), and because
devices will not need the full bandwidth of a wideband channel, a frequency
band is thus often divided into multiple narrowband channels, each with
smaller bandwidth, as shown in Figure 7.18(b). Each narrowband channel in
Figure 7.18(b) is shown in a different color. This figure also shows guard bands
between the narrowband channels—a small frequency range where no signal
is transmitted in this frequency range, preventing one subchannel’s transmissions from interfering with a neighboring subchannel’s transmissions.


Wireless and Mobile Networks

Figure 7.18 Power spectrum of (a) an idealized single wideband channel; (b) frequency
division multiplexing (FDM) with 12 subchannels; (c) orthogonal FDM (OFDM) with 12 subchannels

Orthogonal frequency division multiplexing (OFDM) is a technique for
modulating the FDM subchannel carrier signals so that overlapping signals on
different channels cancel each other out, as shown in Figure 7.18(c). OFDM
doesn’t need guard bands, thus making fuller use of the available channel
spectrum. Note that there is more area under the power spectral density curves
in Figure 7.18(c) than under the curves in Figure 7.18(b). That is, OFDM has
higher spectral efficiency than FDM with guard bands. With spectrum a scarce
and costly commodity (see Section 7.2.1), spectral efficiency is important!
In Section 7.4, we’ll see how 4G 5G and WiFi networks specifically define
the bandwidths of their various channels and subchannels.

Orthogonal Frequency Division Multiple
Access (OFDMA)
Orthogonal Frequency Division Multiplexing Access (OFDMA) combines
both frequency-division multiplexing and time-division multiplexing.
­Figure 7.19 illustrates how each OFDM frequency subchannel is divided into
time minislots. An OFDMA Resource Element (RE) is a single time minislot at
a subchannel frequency. As in Figure 7.18(c), each subchannel frequency in
­Figure 7.19 is shown in a different color, with the 12 subchannel colors in
­Figures 7.19 matching the 12 subchannel colors in Figure 7.18. The RE is the
smallest unit of the OFDMA channel resource—a transmitter can send exactly
one symbol (see Section 7.2.2), shown as a black dot in Figure 7.19, in an RE. In
4G 5G networks, an RE occupies a subchannel bandwidth of 15 kHz and is

## 66.6 µsec in duration. In WiFi networks supporting OFDMA, an RE occupies a

subchannel bandwidth of 78 kHz and is 12.8 µsec in duration.
Although the RE is the smallest unit of an OFDMA channel resource, REs
themselves are not used individually. Instead, adjacent REs (in both frequency
and time) are grouped together, with all symbols transmitted using the same
modulation technique and at the same power. In 4G 5G networks a group of REs
is referred to as a resource block (RB); in WiFi OFDM networks, a group of REs is
referred to as a Resource Unit (RU). A base station or wireless device transmits its




Figure 7.19

Orthogonal Frequency
Division Multiple Access
(OFDMA): combining
frequency division and
time division multiplexing

data as symbols in one or more RBs or RUs, as discussed in Section 7.3.5. In 4G
networks, an RB consists of 84 symbols, contained in 7 time minislots, each

## 66.6 µsecs long, and 12 frequency subchannels, each 15 kHz wide, as shown in

Figure 7.19. Different RB/RU sizes are defined for 5G and WiFi networks.

Random access: Aloha and CSMA/CA
In Section 6.3.2, we learned that random access protocols are simple (e.g., there
is no centralized assignment of frame transmission times to transmitting
nodes) and ideal when the channel load is low. We learned that in Aloha, a
node simply transmits whenever it has data to send, using the full channel
bandwidth. If two or more transmitters send messages at the same time, the
overlapping transmissions “collide,” and neither is received successfully at
their destination(s). It is important to note that collisions are manifested in
overlapping, interfering signals received at the destination (i.e., the receiver)
rather than at the sender or intermediate locations. A higher-level retransmission mechanism is then used to recover from such collisions. Aloha protocols
were first developed more than 50 years ago for wireless satellite networks
[Abramson 1972; Schwartz 2009]. As we will see, they are still in use today in
satellite and IoT networks, and are implemented in selected control-plane
functions in 4G 5G networks.

Carrier Sense Multiple Access with Collision
Avoidance (CSMA/CA)
Carrier Sense Multiple Access with Collision Avoidance (CSMA/CA) was the
original (and for many years the only) channel access method used in WiFi networks. As discussed later in Section 7.3.2, the most recent WiFi standards
(WiFi-6 onwards) offer both CSMA/CA and OFDMA as channel access
techniques.
CSMA/CA is a carrier sense multiple access (CSMA) protocol that has the
same listen-before-transmit behavior that we learned about in Section 6.3.2.


Wireless and Mobile Networks


However, CSMA/CA has other features that address two challenges specific to
a wireless setting:
* Hidden terminal problem. Due to the hidden terminal problem, a first transmitter may not even hear a transmission from a “hidden” second transmitter that is also sending to the first transmitter’s intended destination.
* No collision detection. The ability to detect collisions requires the ability to
send (the transmitter’s own signal) and receive (to determine whether
another station is also transmitting) at the same time. Because the strength
of the received wireless signal is typically very small compared to the
strength of the sender’s transmitted signal, it is difficult for a wireless
transmitter to detect a collision with its own ongoing transmission (even
at its own radio), obviating the use of CSMA/CD’s collision detection
technique. Because CSMA/CA does not use collision detection, once a
­station begins transmitting a frame, it transmits the frame in its entirety;
that is, once a station gets started, there is no turning back. As one might
expect, transmitting entire frames (particularly long frames) when collisions are prevalent can significantly degrade a multiple access protocol’s
performance.
Because of these two challenges, collisions at a destination are typically
more prevalent in wireless networks than in wired networks. Thus, CSMA/CA
­ igure 7.20,
has an explicit link-layer acknowledgment mechanism. As shown in F
when the destination station correctly receives a frame (e.g., a received frame
that has passed the CRC bit-error check) it waits a short period of time known
as the Short Inter-frame Spacing (SIFS) and then sends back an acknowledgment frame. If the transmitting station does not receive an acknowledgment

Figure 7.20 CSMA/
CA uses link-layer
acknowledgments


within a given amount of time, it assumes that an error has occurred and
retransmits the frame, using the CSMA/CA protocol to access the channel. If
an acknowledgment is not received after some fixed number of retransmissions, the transmitting station gives up and discards the frame.
Having discussed how CSMA/CA uses link-layer acknowledgments,
we’re now in a position to describe the CSMA/CA protocol more fully. Suppose that a station (wireless device or an AP) has a frame to transmit.
1. If initially the station senses the channel idle, it transmits its frame after a
short period of time known as the Distributed Inter-Frame Space (DIFS);
see Figure 7.20.
2. Otherwise, the station chooses a random backoff value using binary exponential backoff (as we encountered in Section 6.3.2) and counts down this
value after DIFS when the channel is sensed idle. While the channel is
sensed busy, the counter value remains frozen.
3. When the counter reaches zero (which can only occur while the channel is
sensed idle), the station transmits the entire frame and then waits for an
acknowledgment.
4. If an acknowledgment is received, the transmitting station knows that its
frame has been correctly received at the destination station. If the station
has another frame to send, it begins the CSMA/CA protocol anew at
step 2. If the acknowledgment isn’t received, the transmitting station
­re-enters the backoff phase in step 2, with the random value chosen from a
larger interval.
Recall that under Ethernet’s CSMA/CD multiple access protocol
(­Section 6.3.2), a station begins transmitting as soon as the channel is sensed
idle. With CSMA/CA, however, the station refrains from transmitting while
counting down, even when it senses the channel is idle. Why do CSMA/CD
and CSMA/CA take different approaches here?
To answer this question, let’s consider a scenario in which two stations
each have a data frame to transmit, but neither station transmits immediately
because each senses that a third station is already transmitting. With Ethernet’s
CSMA/CD, the two stations would each transmit as soon as they detect that
the third station has finished transmitting. This would cause a collision, which
isn’t a serious issue in CSMA/CD, since both stations would abort their transmissions and thus avoid the useless transmission of the remainders of their
frames. In a WiFi network, however, the situation is quite different. Because
WiFi transmitters do not detect and abort a collision, a frame suffering a collision is transmitted in its entirety. The goal in WiFi is thus to avoid collisions
whenever possible. In WiFi, if the two stations sense the channel busy, they
both immediately enter random backoff, hopefully choosing different backoff
values. If these values are indeed different, one of the two stations will eventually begin transmitting before the other, and (if the two stations are not hidden
from each other) the “losing station” will hear the “winning station’s” transmission, freeze its counter, and refrain from transmitting until the winning
station has completed its transmission. In this manner, a costly collision is
avoided. Of course, collisions can still occur with 802.11 in this scenario: the two


Wireless and Mobile Networks

stations could be hidden from each other, or the two stations could choose random backoff values that are close enough that the transmission from the station
starting first has yet to reach the second station. Recall that we encountered
this problem earlier in our discussion of random-access algorithms in the context of Figure 6.12.

Dealing with Hidden Terminals: RTS and CTS
WiFi’s CSMA/CA protocol also has a nifty (but optional) reservation scheme
that helps avoid collisions even in the presence of hidden terminals. Recall
from Figure 7.6 that in the hidden terminal problem, stations A and B can hear
each other, stations B and C can hear each other, but stations A and C cannot
hear each other. Suppose A is transmitting a frame to B, and halfway through
A’s transmission, C wants to send a frame to B. Station C, not hearing the transmission from A, will first wait a DIFS interval and then transmit the frame,
resulting in a collision at B. The channel will therefore be wasted during the
entire period of both A’s and C’s transmissions.
In order to avoid this problem, the CSMA/CA protocol has an optional,
short Request to Send (RTS) control frame and a short Clear to Send (CTS)
control frame to (implicitly) reserve access to the channel. Let’s describe this in
the common context of a station wanting to transmit a frame to an access point
(AP). When a sender wants to send a DATA frame, it first sends an RTS frame
to the AP, indicating the total time required to transmit the DATA frame and
the acknowledgment (ACK) frame. When the destination receives the RTS
frame, it responds by broadcasting a CTS frame. This CTS frame serves two
purposes: it gives the sender explicit permission to send and also instructs the
other stations within hearing range of the destination not to send for the
reserved duration.
Figure 7.21 shows that before transmitting a DATA frame, the source first
broadcasts an RTS frame, which is heard by all stations within hearing range,
including the AP. Note that the stations to the right of the AP are not within
hearing distance of the sender and do not receive this RTS. However, the AP
then responds with a CTS frame, which is heard by all stations within its range,
including the sender and the other stations to the right of the AP. These other
stations, having heard the CTS, refrain from transmitting for the time duration
specified in the CTS frame. The RTS, CTS, DATA, and ACK frames are shown
in Figure 7.21.
The use of RTS/CTS improves performance in two important ways:
* The hidden station problem is mitigated, since a long DATA frame is
transmitted only after the channel has been reserved.
* Because RTS and CTS frames are short, a collision involving an RTS or
CTS frame will last only for the duration of the short RTS or CTS frame.
Once the RTS and CTS frames are correctly transmitted, the following
DATA and ACK frames are usually transmitted collision-free. You should
convince yourself, however, that the RTS/CTS mechanism will not always
successfully reserve the channel for a DATA message, since an RTS/CTS
message may itself be lost due to channel fading or noise. You’re




Figure 7.21 Collision
avoidance using RTS/CTS

encouraged to check out the CSMA/CA animation in the textbook’s Web
site. This interactive animation illustrates the CSMA/CA protocol, including the RTS/CTS exchange sequence.
Although the RTS/CTS exchange can help reduce collisions, it also introduces delay and consumes channel resources. For this reason, the RTS/CTS
exchange is only used (if at all) to reserve the channel for the transmission of a
long DATA frame.


### 7.3.2 WiFi: the 802.11 Wireless LAN

Pervasive in the workplace, home, educational institutions, cafés, airports, stadiums, and street corners, wireless LANs are now one of the Internet’s most
important access network technologies. Although many wireless LANs were
developed in the 1990s, one particular network technology has clearly emerged
as the winner: the IEEE 802.11 wireless LAN, aka WiFi. Just as Ethernet has
come to rule the wired LAN, so too has WiFi come to rule the wireless LAN.
The 802.11 standards for wireless LANs are created by the IEEE 802.11


Wireless and Mobile Networks


standards committee [IEEE 802.11 Standards 2024]. Since 2000, a number of
the 802.11 standards (but not all) have also been branded as “WiFi” by the WiFi
Alliance, with numbered generations of WiFi conceptually matching the similar notion of numbered “generations” of cellular network standards. Although
there are a number of 802.11 standards that are not part of the WiFi “branding”
(and for example operate at higher or lower frequency ranges than shown in
Table 7.3), we’ll nonetheless use the terms “WiFi” and “802.11” interchangeably, as each of the major commercial 802.11 standards corresponds to a WiFi
generation, as shown in Table 7.2.

Overview of 802.11* Wireless LANs
We’ve already covered many of the foundational aspects of WiFi in
­Section 7.3.1, including CSMA/CA, OFDM, and OFDMA. So we’ve already
gotten a great start in understanding WiFi! In this section we’ll provide an
overview of WiFi networks, and discuss its channel structure, frame formats,
and internetworking with wired Ethernet LANs. Later in this chapter, we’ll
also cover how a device discovers and attaches to a WiFi network (­Section 7.3.4),
the scheduling of WiFi frame transmissions (Section 7.3.5) and how a device
conserves energy in a WiFi network through sleep/wake cycles in Section 7.3.6.
We’ll also cover how a wireless network (including WiFi) supports device
mobility in Section 7.4.2.
Table 7.2 shows the evolution of the IEEE 802.11 standard. One takeaway
from Table 7.2 is that WiFi has provided a relentless increase in the maximum
throughput seen by a WiFi user—after all, more is always better! While this
was true particularly in WiFi’s early days, WiFi networks are not always (or
even often) deployed with the aim of providing maximum sustained throughput for a single user. Indeed, the most recent use case driving many WiFi
developments is dense deployment of WiFi networks in large enterprises, airports, stadiums, and public spaces, where a large number of users want to
send and receive data at the same time. In dense deployments, the focus is on
efficiently supporting many simultaneous users, rather than delivering maximum throughput to a single user.

Table 7.2 Evolution of major 802.11 standards
IEEE 802.11
standard

Year

Max data rate
(theoretical)

Frequency
(GHz)

Bandwidth

PHY

802.11b


11 Mbps

2.4


Direct-sequence spread
spectrum

802.11g


54 Mbps

2.4


OFDM

WiFi gen

802.11n

WiFi 4


600 Mbps

2.4, 5

20, 40

OFDM

802.11ac

WiFi 5



## 6.9 Gbps



20, 40, 80, 160

OFDM, MIMO

802.11ax

WiFi 6



## 9.5 Gbps


2.4, 5

20, 40, 80, 160

OFDM, OFDMA, MIMO

802.11be

WiFi 7


30 + Gbps

2.4, 5, 6

20, 40, 80, 160, 320

OFDM, OFDMA, MIMO


So, let’s look beyond the gains in maximum throughput and make the following observations about WiFi evolution:
* Frequency. Most WiFi networks operate in unlicensed frequency bands
(One exception to this is the 802.11p for vehicle to vehicle communication
that operates in a licensed spectrum band). The bands used by WiFi have
expanded from just the 2.4 GHz band (which we recall is crowded with
many consumer-electronic devices that are potential sources of interference for WiFi networks) to the 5 GHz band and now the 6 GHz band as
well. Some 802.11 standards (e.g., 802.11 ah) use sub-1GHz bands, while
others (801.11ad, 802.11ay) use the so-called millimeter wave band at
60 GHz and higher.
* Bandwidth. The bandwidth used by WiFi networks is divided into channels of different channel bandwidths, with each successive WiFi generation boasting of an increase in the maximum channel bandwidth. The
minimum channel bandwidth is 20 MHz, with higher channel bandwidths achieved by “bonding” multiple adjacent 20 MHz channels
together; see Figure 7.43. An individual WiFi network will operate on just
one of these channels.
* The Physical Layer. The 802.11 physical layer has evolved from a spreadspectrum form of modulation related to that used in 3G cellular networks
to OFDM to OFDMA, the same modulation technique used in 4G and 5G
networks that support dense deployment scenarios. Given that an AP
must support a range of legacy devices, e.g., from ancient 802.11g devices
to modern WiFi6-capable devices, an AP must support OFDM, OFDMA,
and CSMA/CA at the same time. We’ll soon see how this technical challenge is solved.
Figure 7.22 illustrates the principal components of the 802.11 wireless
LAN architecture. The fundamental building block is known as the basic
­service set (BSS). A BSS contains two or more wireless nodes, with one of those
nodes typically being a central base station, known as an access point (AP)

Figure 7.22 Elements
of 802.11 Wireless LAN


Wireless and Mobile Networks

in 802.11 parlance. Figure 7.22 shows the AP in each of two BSSs connecting to
an interconnection device (such as a switch or router), which in turn leads to
the Internet. In a typical home network, there is one AP, one layer 2 switch and
one layer 3 router (typically all integrated together in one physical “box”) that
connects the BSS to the Internet. In our discussion below, we’ll occasionally
play a little fast-and-loose with 802.11 parlance and refer to the combination of
an AP together with a switch and possibly a router simply as an “AP”. But
according to the 802.11 standard, the AP is a layer-2-only device. Network
devices can only transmit/receive to/from the AP; direct device-to-device
communication cannot happen.

WiFi channel structures
Figure 7.23 shows how WiFi divides its use of the 2.4 and 5 GHz spectrum
bands into channels, with each channel having a unique channel number. In the

## 2.4 GHz band, 802.11 defines 11 partially overlapping channels, each with a bandwidth of 20 MHz. Here, two channels are non-overlapping if and only if they are

separated by four or more channels. In particular, the set of channels 1, 6, and 11
is the only set of three non-overlapping channels. This means that if three APs all
operate in the same physical space using channels 1, 6, and 11, then the transmissions on these three networks will not interfere with each other. However, if
two of the networks operate in overlapping channels, then the devices on these
two networks can interfere with each other. This can be particularly problematic,
of course, when multiple WiFi networks in the physical space are operated independently, e.g., your home WiFi network, and all of the other home WiFi
networks in all apartments within 30 meters of your apartment.

Figure 7.23 WiFi channels in the 2.4 and 5 GHz bands




Putting it all together: CSMA/CA, OFDM,
and OFDMA in WiFi 6
As noted in Table 7.2, all 802.11 standards from the past 20 years support
orthogonal frequency division multiplexing (OFDM), which is used to create
the multiple separate WiFi channels in Figure 7.23. A WiFi AP can be configured to operate using just one of these fixed-bandwidth channels, with all
devices in the AP’s WLAN communicating with the AP over this single channel. Alternatively, an AP can be assigned a primary channel and then
dynamically increase the available bandwidth by bonding one or more adjacent secondary channels with the primary channel. With OFDM, a device or
AP uses the full channel bandwidth when transmitting. We’ve also learned
that WiFi 6 (and onwards) also supports OFDMA, which is different from pure
OFDM and particularly useful in dense deployment scenarios. We learned in
Section 7.3.1 that OFDMA divides a channel into multiple subchannels and
allows transmission to/from multiple devices simultaneously, with each
device using a different set of subchannels and timeslots. And we learned in
Section 7.3.1 that WiFi also uses CSMA/CA random access to share the WiFi
channel. But how can all three of these channel-sharing approaches—OFDM,
OFDMA, and CSMA/CA—be used in the same WiFi network? How is that
even possible?
The answer to this question lies in the clever extension of WiFi’s basic
RTS/CTS mechanism—initially developed to help solve the hidden terminal
problem—to also solve the problem OFDM, OFDMA, and CSMA/CA co-existence.
WiFi 6 introduced a new type of RTS message, known as a multi-user RTS
message (MU-RTS). In the downlink direction, the AP sends an MU-RTS when
it wants to initiate OFDMA transmissions to multiple devices. The MU-RTS
contains a list of OFDMA resource unit (RU) allocations, indicating which RUs
the AP will use to send data to which devices simultaneously, and the length of
time that the channel will be used. The MU-RTS is transmitted using OFDM to
all devices, whether OFDMA capable or not, as part of the CSMA/CA protocol. Thus, all devices will receive the MU-RTS message. An OFDM-only device
will respond to the RTS with a CTS as discussed earlier and as shown in
­Figure 7.20. An OFDMA-capable device responds to the RTS with a CTS that is
transmitted in just the frequencies being assigned to that device. As with regular RTS/CTS messages, an RTS message may not be successful. However, if
this MU-RTS/CTS exchange is successful, the AP has now reserved the ­channel
and can then send RUs to the multiple devices using OFDMA. In the uplink
direction, transmissions from the devices to the AP are also coordinated by the
AP, again using MU-RTS messages; see [Meraki WiFi6 2020] for details.
The interaction of CSMA/CA, OFDM, and OFDMA is illustrated in
­Figure 7.24. In this example, there are two legacy 802.11g (pre-WiFi 4!) devices,
a and b, and five 802.11ax (WiFi 6) devices. In this example, devices a and b
gain use of the full OFDM channel following t 0 and t 1 respectively, using the
CSMA/CA protocol. At t 2 , the AP uses CSMA/CA with the MU-RTS mechanism (during the time and at frequencies shown in the shaded gray box
beginning at t 2) to successfully reserve the channel for simultaneous OFDMA
RU transmissions to devices 1, 2, 4, and 5 in the RUs shown. At t 3, device b


Wireless and Mobile Networks

Figure 7.24 Intervals of CSMA/CA, OFDM, and OFDMA

again uses CSMA/CA to gain access to the channel and transmits another
frame using OFDM. At t 4, the AP uses the MU-RTS mechanism to successfully
reserve the channel for OFDMA RU transmissions to devices 1, 2, and 3 in the
RUs shown.


### 7.3.2 802.11 MAC: the WiFi wireless link layer

Figure 7.25 expands on Figure 7.22, showing the IEEE 802.11 medium access
control (MAC) as the wireless link layer in a WiFi network. Note that the
MACs in all devices in Figure 7.25 have data-plane and control-plane components. The job of the MAC data plane is to transport link-layer frames to and
from end user applications. The job of the MAC control plane is to implement
control functions such as RTS/CTS, ACKs and NAKs, beaconing (Section 7.3.4)
and power control (Section 7.3.6). Since MAC control plane modules in the
device and the AP exchange control messages in link-layer frames, a logical
connection with dashed lines is shown between the control modules on both
sides of the wireless link. MAC data and control frames are both scheduled for
transmission across the wireless medium by the MAC scheduler (Section 7.3.5).

Figure 7.25 WiFi: the wireless link layer




Figure 7.26 802.11
frame format (numbers
indicate field length in
bytes) and frame control
field (numbers indicate
subfield length in bits)

Note that the wireless user device in Figure 7.25 implements all five layers
of the Internet protocol stack. The AP, however, is a layer-2-only device. On
one side of the AP, the AP’s link layer uses WiFi to communicate with the user
device; on the other side, the AP’s link layer connects to an Ethernet link layer
to communicate with the layer-3 router. In practice, the AP, Ethernet, and
layer-3 router functions are often packaged together in the same “box” for
small-scale (e.g., residential) deployments, technically making the box a layer-3
device.
The 802.11 frame is shown in Figure 7.26. Although it shares many similarities with an Ethernet frame, it also contains a number of fields that are
specific to its use in wireless LANs. The numbers above each of the fields in
the frame show the lengths of the fields in bytes; the numbers above each of
the subfields in the frame control field give the subfield lengths in bits. In
­Figure 7.26, not all fields shown are always used, and there are additional
optional fields that are not shown. Let’s now examine the fields in the frame as
well as some of the more important subfields in the frame control field.

Payload and CRC Fields
At the heart of the frame is the payload, which typically consists of an IP datagram, a MAC control frame, or an ARP packet. Although the field is permitted
to be as long as 2,312 bytes, it is typically less than 1,500 bytes . As with an
Ethernet frame, an 802.11 frame includes a 32-bit cyclic redundancy check
(CRC) so that the receiver can detect bit errors in the received frame. As we’ve
seen, bit errors are much more common in wireless LANs than in wired LANs,
so the CRC is even more useful here.

Address Fields
Perhaps the most striking difference between the 802.11 and Ethernet frames is
that the 802.11 frame has four address fields, each of which can hold a 6-byte
MAC address. But why four address fields? Doesn’t a source MAC field and
destination MAC field suffice, as they do for Ethernet? It turns out that three
address fields are needed for internetworking purposes—specifically, for moving the network-layer datagram from a wireless station through an AP to a
router interface. The fourth address field is used when devices forward frames
to each other in ad hoc mode, without an AP. Since we are only considering


Wireless and Mobile Networks


infrastructure networks here, let’s focus our attention on the first three address
fields. The 802.11 standard defines these fields as follows:
* Address 2 is the MAC address of the device that transmits the 802.11
frame. Thus, if a (non-AP) wireless device transmits the frame, its MAC
address is inserted in the Address 2 field. Similarly, if an AP transmits the
frame, the AP’s MAC address is inserted in the Address 2 field.
* Address 1 is the MAC address of the wireless device that is to receive the
frame. Thus, if a (non-AP) wireless device transmits the frame, Address 1
contains the MAC address of the destination AP. Similarly, if an AP transmits the frame, Address 1 contains the MAC address of the destination
wireless device.
* To understand Address 3, recall that the BSS (consisting of the AP and
wireless devices) is part of a subnet, and that this subnet connects to other
subnets via some router interface. Address 3 contains the MAC address of
this router interface.
To gain further insight into the purpose of Address 3, let’s walk through
the example in Figure 7.27. In this figure, there are two APs, each of which is
responsible for a number of wireless devices. Each of the APs has an Ethernet
connection to a router, which in turn connects to the global Internet. We should
keep in mind that an AP is a link-layer device, and thus neither “speaks” IP
nor understands IP addresses. Consider now moving a datagram from the
router interface R1 to the wireless device H1. The router is not aware that there
is an AP between it and H1; from the router’s perspective, H1 is just a device in
one of the subnets to which it (the router) is connected.
* The router, which knows the IP address of H1 (from the destination
address of the datagram), uses ARP to determine the MAC address of H1,
just as in an ordinary Ethernet LAN. After obtaining H1’s MAC address,
the router interface R1 encapsulates the datagram within an Ethernet
frame. The source address field of this frame contains R1’s MAC address,
and the destination address field contains H1’s MAC address.

Figure 7.27 Use of
address fields in 802.11
frames: sending frames
between H1 and R1


* When the Ethernet frame arrives at the AP, the AP converts the 802.3
­Ethernet frame to an 802.11 frame before transmitting the frame into the
wireless channel. The AP fills in Addresses 1 and 2 with H1’s MAC
address and its own MAC address, respectively, as described above. For
Address 3, the AP inserts the MAC address of R1. In this manner, H1 can
determine (from Address 3) the MAC address of the router interface that
sent the datagram into the subnet.
Now consider what happens when the wireless device H1 responds by transmitting a datagram from H1 to R1.
* H1 creates an 802.11 frame, filling the fields for Addresses 1 and 2 with
the AP’s MAC address and H1’s MAC address, respectively, as described
above. For Address 3, H1 inserts R1’s MAC address.
* When the AP receives the 802.11 frame, it converts the frame to an Ethernet frame. The source address field for this frame is H1’s MAC address,
and the destination address field is R1’s MAC address. Thus, Address 3
allows the AP to determine the appropriate destination MAC address
when constructing the Ethernet frame.
In summary, Address 3 plays a crucial role for internetworking the BSS
with a wired LAN.

Sequence Number, Duration, and Frame
Control Fields
Recall that in 802.11, whenever a station correctly receives a frame from
another station, it sends back an acknowledgment. Because acknowledgments
can get lost, the sending station may send multiple copies of a given frame. As
we saw in our discussion of the rdt2.1 protocol (Section 3.4.1), sequence numbers allow the receiver to distinguish between a newly transmitted frame and
the retransmission of a previous frame. The sequence number field in the

## 802.11 frame serves exactly the same purpose here at the link layer as it did in

the transport layer in Chapter 3.
Recall that the 802.11 protocol allows a transmitting station to reserve the
channel for a period of time that includes the time to transmit its data frame
and the time to transmit an acknowledgment. This amount of time (in microseconds) is included in the frame’s duration field, both for data frames and for
the RTS and CTS frames.
As shown in Figure 7.26, the frame control field includes many subfields.
We’ll say just a few words about some of the more important subfields; for a
more complete discussion, see [Wikipedia 802.11_frame_types 2024]. The type
and subtype fields are used to identify 802.11 control and data frames. Among
the control messages are the RTS, CTS, and ACK messages that we encountered in Figure 7.21. Several types of control frames are used when a device
joins a network, as discussed in Section 7.3.4. The power management bit is
used (as the name would suggest) when a device sleeps to preserve battery
power, as discussed in Section 7.3.6.


Wireless and Mobile Networks


### 7.3.3 The 5G Radio Access Network

In this subsection, we’ll cover key aspects of the Radio Access Network (RAN)
in 4G and 5G cellular networks. We’ll rely heavily on the foundational material from the earlier sections of this chapter on wireless channels and OFDMA
in particular. We’ll focus here primarily on 5G, but will address 4G LTE cellular networks where appropriate.

Architectural components of 5G networks:
the big picture
Before diving into the 5G RAN itself, let’s situate the RAN in the context of the
larger 5G cellular network. As shown in Figure 7.28, a 5G (and 3G and 4G) cellular network has two principal components—the edge and the core.
* Radio Access Network (RAN). The RAN is at the edge of the 5G network.
A RAN consists of (i) the end-user wireless devices (referred to as user
equipment (UE) in cellular parlance) that are attached over (ii) the local
5G wireless radio channel known as New Radio (NR), presumably to distinguish it from the “old” 4G radio channel to (iii) a base station, known
as a Next Generation Node (gNB). As discussed in Section 7.1, since the
UE, NR, gNB nomenclature is opaque and non-intuitive, we’ll use the
more intuitive and descriptive nomenclature here of “base station” rather
than “gNB”, “user device” rather than “UE”, and “wireless channel” or
“radio channel” rather than “NR.” The RAN is the cellular equivalent of a
WiFi wireless LAN—it contains the first-hop wireless link between the
user and the larger network, the wireless user devices, and a 5G base station that is similar to, but considerably more multi-functional, complex
and sophisticated than, a WiFi access point (AP) in a wireless LAN.
* The 5G Core. The 5G Core consists of the links, routers, servers, and Core
Network Functions that lie between a RAN and a gateway from the cellular provider’s network into the larger Internet, including other cellular
provider networks. A typical cellular network will have a single core, with
multiple attached edge networks The links and routers in the cellular core
are typically wired, use the same Internet protocols and technology that
we studied in Chapters 4, 5, and 6. The distinction between the networklayer data and control planes that we made earlier in Chapters 4 and 5,
respectively, is also very much present in 5G, except that the data plane is
known as the user plane in 5G terminology. Indeed, the logical separation
of control and user planes is so foundational in 5G architecture that (of
course!) it even has its own acronym in the 5G standards: CUPS, which
stands for Control Plane and User Plane Separation!
* What is unique in the 5G Core is the set of control and management
­functions, known as 5G Core Network Functions, that provide 5G
­services such as RAN access and authorization, and support for user-device
mobility. We’ll study these services, shown in blue boxes in Figure 7.28,




Figure 7.28 Major elements of a 5G network

in Section 7.4. The locations where these Core services are implemented will
differ from one 5G network to another. For example, the servers implementing Core services might be co-located at the base station in the case of a small
private 5G network, or might be implemented in a physically separate small
data center (often referred to as an edge-cloud) in the Core but near
the RAN, or may be implemented in a large, physically-distant data center.
The only absolute requirement is that these services be reachable via IP.
User application code may also run on servers at the base station or in the
5G Core, communicating with wireless devices in the RAN to implement an
application’s service. This is referred to as local breakout, as the user’s
application client-server traffic never leaves the cellular network.

4G, 5G RAN: the physical radio channel
4G and 5G RANs implement OFDMA channel sharing, which we studied in
Section 7.3.1. In 4G networks, the smallest subchannel bandwidth is 15 kHz,
where the transmission time for a single symbol in a single minislot is 66 µsec .
In 5G networks, larger subchannel bandwidths (30, 60, 120, 240, 480, and
960 kHz) with proportionally shorter minislot lengths are also defined.
Recall from Section 7.3.1 that a resource element (RE) is a single time minislot on a single OFDMA subcarrier frequency. Both 4G and 5G networks
bundle neighboring REs (in frequency and time) into a Resource Block (RB).


Wireless and Mobile Networks


Figure 7.29 4G
Resource Blocks

A resource block is the smallest unit of channel resource that is used by a transmitting device or base station in 4G and 5G networks. In 4G networks, an RB
bundles together 84 symbols (on 12 neighboring subcarriers, and in 7 consecutive time minislots), as shown in Figure 7.29. This is the only bundling of REs
into an RB in 4G networks. In 5G networks, there are a number of different
ways to bundle REs into an RB.
Figure 7.29 also illustrates the relationship between a channel and an RB,
showing a 10 MHz wide channel that consists of 50 time-parallel RBs, each
using one of the 50 different frequency subchannels. Standard channel bandwidths for 4G networks are 1.4, 3, 5, 10, 15, and 20 MHz. 5G incorporates all
of the earlier 4G channel definitions and additionally defines channels up to
100 MHz wide.
There is even one last higher level of bandwidth aggregation in 4G 5G
networks! A band is an aggregation of one or more channels, with each channel consisting of a number of different subcarriers(subchannels), as shown in
Figure 7.30. Various 5G bands are defined by the 3GPP [3GPP TS 38.101-1
2024]. Recall from Section 7.2.1, that the allocation of licensed spectrum within
these bands to cellular network providers is made by national governments,
typically via auctions. The amount of spectrum made available nationally to
carriers in these bands varies from country to country. Once a network operator has been allocated a frequency band, it’s up to that operator to decide how
to divide the band into channels, and the channels into subcarriers.

Figure 7.30 Bands,
channels, and subcarriers



4G, 5G RAN Radio: physical and logical control
and data channels
Our discussion above has focused on the physical radio channel resources—
the radio frequencies, time minislots, and RB structure. Each RB also has a
direction. The downlink direction is from the base station to the user device.
The uplink direction is from the user device to the base station. As we saw in
wired (e.g., cable) edge networks in Chapter 6, there is typically significantly
more downstream traffic than uplink traffic, with a ratio of approximately 10:1
[Sauter 2021; Mitra 2024] between downlink and uplink traffic in 4G 5G networks. Each network operator can set the ratio of downlink to uplink channel
resources by determining the fraction of OFDMA time slots assigned in each
direction, a process known as Time Division Duplexing (TDD). It is also possible to group resources by frequency, with a range of channel frequencies
assigned exclusively for uplink or downlink transmission—a process known
the Frequency Division Duplexing (FDD).
Given the frequency and time slot assignments for the uplink and downlink RBs in the RAN, RBs are then partitioned into three groups in the downlink
direction and three groups in the uplink direction. These groups are known as
downlink physical channels and uplink physical channels. The RBs in each
physical channel are used for the same purpose. Three of these channels are in
the downlink direction:
* Physical Downlink Shared Channel (PDSCH). This channel carries all
downstream user-plane data, as well as control plane messages from the
base station to the user device for all user devices.
* Physical Downlink Control Channel (PDCCH). This channel is used to
inform user devices about the RBs in which they will be receiving data in
the downlink direction and which they can use to transmit data in the
uplink direction.
* Physical Broadcast Channel (PBCH). This channel carries information
broadcast by the base station that is needed for a user device to discover
and then join the cellular network, as discussed in Section 7.3.4.
and three of these channels are in the uplink direction:
* Physical Uplink Shared Channel (PUSCH). This channel is the upstream
equivalent of the PDSCH. It carries all upstream user-plane data, as well
as control plane messages from user devices to the base station.
* Physical Random-Access Channel (PRACH). This channel is used by
user devices to request a connection to the base station, when a device first
joins the network. As the name would suggest, devices access this channel
using a random-access scheme.
* Physical Uplink Control Channel (PUCCH). A device uses this channel
to request that the base station allocate it RBs in the PUSCH that it can use
in the future to transmit data to the base station. The PUCCH also carries
measurement data, and link-layer ACK/NAKs used for reliable data
transfer.


Wireless and Mobile Networks


There are also multiple logical channels defined in the uplink and downlink directions, which are then mapped onto the physical uplink and downlink
channels. All information flowing on the same logical channel is semantically
related. See [Sauter 2021; electronicsnotes 2024] for details. Given these definitions of 5G logical and physical uplink and downlink channels, the notion of
frequency bands and channels in Figure 7.30, and our discussion of the characteristics of radio channels in Section 7.2, it’s clear that the word “channel” takes
on very different meanings in different contexts and is one of the most used (or
perhaps overused) words in wireless networking!

5G RAN: the wireless link layer
Having earlier studied the WiFi link-layer protocol stack, let’s now take a look
at the link-layer protocol stack in the 5G RAN.
Figure 7.31 shows the 5G RAN protocol stack, with an expanded view of
the various sublayers in the 5G link layer. Note that as in the case of WiFi, the
link layers in both the device and the base station have a user plane and a control plane. The job of the user plane is to move link-layer frames from the
device’s applications to the base station and vice versa. The job of the control
plane is to control and configure the RAN’s radio resources, provide control
functions for user-plane frame transfer (e.g., ARQ and quality of service) and
additional services such as device mobility (Section 7.4.2), attachment to the
network (Section 7.3.4), and power control (Section 7.3.6). Since link-layer control plane actions usually involve message exchange between control functions
in the device and the base station, a logical connection with dashed lines is
shown between control modules in the sublayers on both sides of the wireless
link in Figure 7.31. Control messages sent between the base station and user
device are carried in link-layer frames over one of the appropriate 5G physical
control channels.
Figure 7.31 shows that the 5G RAN link layer is divided into a number of
sublayers:
* The Radio Resource Control (RRC) is the control-plane function responsible for (i) establishing, maintaining and releasing link-layer logical ­channels,
(ii) managing the per-device link-layer connection state (­Sections 7.3.4
and 7.3.6), (iii) managing aspects of device mobility (Section 7.4), and

Figure 7.31 5G RAN
protocol stacks at the user
device and base station


(iv) performing channel quality measurement and reporting (­Section 7.3.5).
The RRC accomplishes its work by configuring local link- and physicallayer state, using the RRC protocol [3GPP TS 38.331 2024] to send control
messages between the base station and a user device.
* The Service Data Adaptation Protocol (SDAP) is the highest sublayer in
the link-layer user plane. When Quality of Service guarantees are to be
provided to packet flows, SDAP assigns QoS Flow IDs and maps the flows
onto underlying radio resources.
* The Packet Data Convergence Protocol (PDCP) is responsible for IP
header compression and (optionally) encryption and cryptographic message integrity checks.
* The Radio Link Control (RLC) is responsible for segmentation/reassembly and reliable frame transfer using a simple ARQ (Automatic Repeat
Request) protocol with sequence numbers, cyclic redundancy checks, and
ACK/NACK messages, as we studied in Chapter 3.
* The Medium Access Control (MAC) sublayer is responsible for scheduling the transmission of link-layer user- and control-plane frames between
the base station and user devices. As we learned earlier in this section, the
data in these frames is segmented into smaller chunks that are then
mapped onto OFDMA Resource Blocks for transmission. We’ll cover MAC
scheduling in Section 7.3.5.
While the WiFi link-layer frame in Figure 7.26 is relatively simple, the 5G
RAN frame is considerably more complex, due in great part to the multiple
link sublayers. A 5G link-layer frame includes an IP datagram or an RRC control-plane message with added SDAP, PDCP, RLC, and MAC header fields.
Each sublayer adds its own header fields, typically including a user/control
message bit, a sequence number or identifier, a payload field, and other fields
needed to accomplish the sublayers functions. Rather than laboriously detail
these fields, we’ll instead simply refer the interested reader to Section 6 in each
of the 3GPP link—sublayer protocol documents [3GPP RRC TS 38.331 2024;
3GPP SDAP TS 38.300 2024; 3GPP PDCP TS 38.323 2024; 3GPP RLC TS 38.322
2024; 3GPP MAC TS 38.321 2024].
Figure 7.32 shows a view of the 5G base station’s link-layer control and
packet-processing pipeline, once again emphasizing control- and user-plane
separation. We also note the central, controlling role of the RRC.
In earlier 2G, 3G, and 4G networks, a RAN cellular base station was
implemented as a monolithic unit—essentially a specialized, single vendor
“box” implementing that generation’s standardized functions. Beginning with
5G, there has been a move to “disaggregate” RAN functions into multiple
functional units that interoperate with each other through standardized interfaces. This disaggregated architecture allows multiple vendors to offer
competing implementations of pieces of the 5G base station, lowering the barrier to entry, and increasing competition and innovation—similar to a key
motivation we found behind the development of SDN in Chapter 5.
Figure 7.33 shows the functional split of a 5G base station into a Radio
Unit (RU), a Distributed Unit (DU), and a Central Unit (CU), as well as the


Wireless and Mobile Networks

Figure 7.32 5G base station RAN control and packet-processing pipeline

RAN functions performed within each unit. Where such functional units are
situated in the RAN—in the base station, in an edge cloud, or in a central
cloud—is an implementation decision, often driven by communication delays
and real-time communication requirements. While the RU, DU, and CU are
part of the 3GPP 5G specification [3GPP TS 38.300; 3GPP TS 38.401], the
O-RAN Alliance takes this disaggregation one step further by specifying interfaces among these units [O-RAN Architecture 2024; Polese 2023].

Implementing the 5G RAN control plane
The disaggregation of the 5G base station into RU, DU, and CU functional
units is but one of two disaggregations in 5G. A second form of disaggregation
arises in the 5G control plane. In particular, since the RRC control plane is

Figure 7.33 Disaggregation: functional split of a 5G base station into three “units”




Figure 7.34 SD-RAN: a software-defined RAN control plane

separate from the user plane (in much the same way that the Internet control
plane and data plane are separate), it’s possible to implement the standardized
RRC functions in a modern SDN-like manner.
Figure 7.34 shows an SDN-like implementation of the RAN control plane.
It’s instructive to compare the monolithic RRC implementation suggested in
Figure 7.33 with the SDN RRC implementation of Figure 7.34. In particular, as
long as the re-factored implementation in Figure 7.34 implements all of the
functional interfaces to the mobile core and to the user plane as in Figure 7.33,
one implementation is indistinguishable from the other as far as the other components of the 5G network are concerned.
An SD-RAN controller will typically have the following main components
shown in Figure 7.34:
* A control-plane proxy that implements a 3GPP-compliant interface
between the RAN and 5G Core’s control plane. Specifically, the RAN’s
control plane proxy must implement the well-defined service-based interface to each of the Core Network Functions shown in Figure 7.28 and discussed later in Section 7.4.
* A real-time intelligent controller (RIC) that serves a similar function here
as the SDN controller in Figure 5.14. The RIC itself has three major
components:
* A lower layer communication layer that communicates commands to
the data-plane RAN components.
* A RAN-wide state-management layer. The RIC’s control decisions will
require up-to-date information about channel state, connection state
and identity information for each user device, for the QoS requirements, and for much more. This information is stored in the local RAN
Node Information Base (R-NIB).
* An interface to a set of application-layer control processes.


Wireless and Mobile Networks

* The RIC control processes that make RAN control decisions regarding
load balancing, device handover, QoS provisioning, and more. These processes, known as xApps in the OpenRAN parlance, can access information in the R-NIB and are implemented as separate software processes
executing outside of the RIC itself, as shown in Figure 7.34. A set of opensource xApps can be found at [O-RAN xApp 2024]. OpenRAN [O-RAN
Architecture 2024] is one of the most prominent examples of an SD-RAN.
OpenRAN is open in the sense that there are well-defined, standardized
interfaces between the different components of the SD-RAN, allowing
multi-vendor implementations of different components of the SD-RAN to
interoperate.
For a thoughtful discussion of the softwareization of the 5G RAN, see
[Peterson 2024].


### 7.3.4 Discovery: attaching to a wireless

network
Having discussed both cellular RANs and WiFi LANs in detail, let’s now turn
our attention to a capability needed in any edge network, regardless of whether
it is a wired Ethernet LAN, a 5G RAN, or WiFi WLAN—the ability for a device
to detect the existence of network infrastructure and to “attach” to that network. This process is known as network association.

Beaconing
A base station, whether in a 5G network or a WiFi network, will periodically
transmit beacon messages, that announce the existence of the access network
and information about its characteristics such as its name, its transmission
capabilities (e.g., transmission rates), and physical-layer parameters about its
radio channels. A device wishing to attach to a network will passively scan the
various possible wireless channels, looking for such beacon messages.
Wireless network standards don’t specify the algorithm a device uses to
select which of the advertised networks to associate with—that choice is left up
to you (the device or user) or the designers of the firmware and software in
your wireless device. Typically, a device may choose to associate with the network with which it was most recently associated, may choose from an ordered
list, or may choose to join the network whose signal strength is best. In public
5G networks, a device will almost always preferably associate with a 5G network operated by the provider that issued the device’s SIM card, and with
which the device has a paid service plan.

Attaching to a WiFi network
After scanning for available networks and selecting the AP with which to associate, a WiFi device sends an 802.11 association request frame to the AP. The
AP responds with an association response frame, as shown in Figure 7.35. As
discussed in Section 8.8, but not shown in Figure 7.35, a device will




Figure 7.35

Associating with a WiFi
network

authenticate itself to the network using WPA (WiFi Protected Access) security
after receiving a beacon, and either before or after association.
Once associated with a WiFi AP, the device will want to join the subnet (in
the IP addressing sense of Section 4.3.3) to which the AP belongs. The device
will thus typically send a DHCP discovery message (see Figure 4.21) into the
subnet via the AP in order to obtain an IP address on the subnet. Once the
address is obtained, the rest of the world then views that device simply as
another device with an IP address in that subnet.

Attaching to a 5G network
The process by which a device attaches to a 5G network to get its own collision-free control and data channels is a bit more complicated than attaching to
a WiFi network. In particular, rather than looking for just a single beacon message that contains all of the information needed to join an access network, a 5G
device goes through a multistep process to obtain the needed information.
­Figure 7.36 illustrates the process:
1. Each base station broadcasts multiple pieces of information needed by a
device to decide whether or not to join a network. A network’s primary
synchronization signal (PSS) is first located by a device and used to synchronize its clock with that of the base station. The secondary synchronization signal (SSS), which provides an initial network identifier, is then
located. The PSS and SSS are broadcast every 5 msec on the center 127
subcarriers of every 5G channel by every 5G base station. Next, the device
obtains the Master Information Block (MIB) for that channel, which
includes information about subcarrier spacing, and whether or not the cell
is even open for association. The PSS, SSS, and MIB together form the
System Signal Block (SSB). With this information, the device can then
locate and receive up to 20 System Information Blocks (SIBs) that characterize the 5G network and its operation. The most important of these is
SIB1, which is transmitted every 80 ms and contains:
* The mobile country code (MCC) and mobile network code (MNC) for
the carrier operating this channel,


Wireless and Mobile Networks

Figure 7.36

Associating with a 5G
network

* the base station identifier, and
* the minimum reception level (channel quality) acceptable.
2. Now suppose that the device decides that it wants to associate with this
5G network. However, the base station is not yet even aware of the
device’s existence, and the device has yet to be allocated any uplink RBs
that can be used to communicate with the base station. Thus, the device
uses the cell’s upstream random-access channel to send a Radio Resource
Control (RRC) connection setup request (similar in spirit to the 802.11
association request frame) to the base station.
3. In step 3, the base station responds to the device’s connection setup
request message with an RRC connection setup response message (similar in spirit to the 802.11 association response frame).
At this point, the user device and base station are able to exchange control
messages with each other in the RAN. But the device still has not yet joined the
5G network (!) as it hasn’t yet identified or authenticated itself to the network,
nor does it have an IP address. We’ll see how the device completes the process
of joining a 5G network when we cover the 5G Core (Section 7.4) and authentication (Section 8.8).


### 7.3.5 Scheduling transmissions over the

RAN/WLAN
One of the most important functions of the MAC layer is to schedule the order in
which data is transmitted in the downlink direction from a base station to user
devices, and on the uplink reverse direction. This is the role of the MAC scheduler,
which is particularly important in dense deployment scenarios (i.e., in 4 5G
­networks and WiFi 6 7 OFDMA deployments), where there may be tens or
­hundreds of users with data to transmit at a given time. Thus, we’ll focus here
on the scenario in which there is a central MAC scheduler at the base station.



Distributed scheduling of transmissions is also a topic of interest in pure
­random-access environments (see, e.g., [Liang 2010]), but will not be covered here.
Recall that we previously studied link-layer scheduling in a wired setting
in Section 4.2.5. We saw there that the overall performance at the link layer
(e.g., measured in throughput and aggregated over all traffic flowing across
the link) was essentially independent of the order in which frames were transmitted, since a fixed number of frames were transmitted per second regardless
of the specific selection of frames to be transmitted. In a wireless setting, however, this is decidedly not the case! As we learned in Section 7.2, a base station
is able to transmit at higher rates (by using a higher-bitrate modulation
scheme) to a device that is physically close and has clear line-of-sight, than to a
device that is far away and suffers from multipath effects. Thus, WLAN and
RAN throughput depends on which devices are scheduled as transmitters and
receivers. MIMO spatial multiplexing and spatial diversity offer additional
degrees of freedom to transmit single or multiple streams to a given receiver.
Beamforming offers yet a different opportunity—to send to different sets of
receivers simultaneously. And, of course, channel characteristics are constantly
changing over time. Consequently, overall aggregate wireless link-layer performance
will very much depend on MAC scheduling choices!
Since neither the 3GPP nor the WiFi standards mandate (or even describe)
MAC scheduling algorithms, the choice of scheduling algorithms is completely
in the hands of the network operator. Scheduling is thus part of the “secret
sauce” that can distinguish one network provider from another. Indeed, many
wireless hardware/software vendors and wireless network providers tout that
their sophisticated approach to MAC scheduling sets them apart from their
competition.
There are four key considerations in MAC scheduling:
* Channel quality awareness. Does the scheduler consider estimates/measurements of the quality of the radio channel between the base station and
device when making a scheduling decision? Since a device with highquality radio channel between itself and a base station can send/receive
data at higher rates, a network can achieve a higher aggregate throughput
by preferentially sending to devices with high quality radio channels to/
from the base station.
* Fairness among devices. Does the scheduler provide a degree of fairness
(e.g., approximately equal throughput) among devices? If so, what is
meant by “fairness”? For example, a scheduling policy that transmits only
to devices with the highest quality channel may achieve high throughput
but does not provide throughput fairness among devices. If fairness is to
be provided, the “price” to be paid may be some reduction in aggregate
throughput (with respect to the maximum throughput achievable in the
absence of fairness considerations).
* Prioritization among classes of traffic. Does the scheduler distinguish
between control-plane traffic versus user-plane traffic, e.g., by prioritizing
the former over the latter, or by providing for a fixed minimum amount of
channel resources for one or both of these classes? Does the scheduler distinguish between traffic with real-time constraints (such as control


Wireless and Mobile Networks


applications, and interactive voice and video) and non-real-time traffic
(e.g., web browsing). Our earlier discussion of priority scheduling in Section 4.2.5 is applicable here.
* Quality of Service (QoS) awareness. Does the scheduler make scheduling
decisions so that quality-of-service (performance) guarantees are provided to devices in the network?
Thousands of research papers have been written, and nearly as many
MAC scheduling algorithms have been proposed, over the years. Here, we’ll
describe just a few representative algorithms, adopting notation from [Capozzi
2012]. Surveys of MAC scheduling algorithms can be found in [Capozzi 2012;
Haque 2023].
Figure 7.37 illustrates four different MAC scheduling algorithms, showing
the data (i.e., link-layer frames) queued at the base station for transmission to
six downstream devices. We’ll focus here on scheduling the downstream transmissions from the base station to its associated devices. Our discussion,
however, is applicable to the upstream channel as well, since the base station
also schedules the upstream channel and informs devices of the upstream
channel resources that the devices can use, and when. With an OFDMA downstream channel, the scheduler’s decision determines which device’s queued
frames will be transmitted in which resource blocks (RBs) between the current
scheduling instant and the next. In 4G 5G systems, scheduling decisions are
made every 1 ms. In WiFi 6, the time between scheduling decisions can be
even shorter [Qualcomm 2021].

Round Robin (RR) Scheduling
Recall our discussion of RR scheduling in a wired setting in Section 4.2.5. In a
wireless setting, RR allocates an equal number of RBs to each device for the

Figure 7.37 Four MAC
scheduling algorithms,
measurements used


next transmission round. RR is channel-unaware and QoS-unaware. RR is fair
by turns, since each device is allocated an equal number of RBs, but not necessarily throughput-fair since different devices may experience different channel
conditions, and thus realize different throughputs.

Maximum Throughput (MT) scheduling
In MT scheduling, shown in Figure 7.37(b), the base station assigns RBs to the
user devices that have the highest measured channel quality for that RB and
that have data to send. Channel quality can be determined in many different
ways. In 5G networks, a base station periodically broadcasts reference signal
symbols in known positions in resource blocks. A device periodically sends a
4-bit Channel Quality Indication (CQI) based on its measured reception of
these reference signals.
In MT scheduling, at each scheduling instant, t, the base station
computes:
d i k ( t ): the expected throughput for device i using kth RB at time t. d i k ( t )
is computed using device-reported CQIs from each device, i, which in turn
will determine the modulation technique to be used (see, e.g., Table 5.2.2.1
in [3GPP 38.214 2024]), which in turn will determine the number of bits per
transmitted symbol in resource block k .
The MT scheduler then finds the device, i, with highest reported quality
channel over all RBs, k :
max i , k { d i k ( t )} ,
and assigns RB k to device i. The process repeats until all RBs have been assigned.
Note that MT scheduling is channel-aware, but unfair. Indeed, in the most unfair
case, the single device with the highest channel quality among all devices may
be assigned all of the available RBs, if there is enough data to send to the device!

Blind Equal Throughput (BET)
The BET scheduling algorithm, shown in Figure 7.37(c), explicitly aims to be
fair by providing equal average throughput to all user devices. In BET, the
scheduler maintains an estimate of a device’s average throughput. Let r i ( t ) be
the measured throughput achieved by device i during time period t. An exponentially weighted moving average (EWMA) of device i’s throughput at time t,
R i ( t ), is then:
R i ( t ) = ( 1 − β ) i r i ( t ) + β i R i ( t − 1) ,
where the parameter β ( 0 < β < 1) determines the relative importance of
more recent values of R i () in computing the average throughput; a higher
value of b gives higher importance to recent values. You might recall that we
encountered this EWMA formula when we learned about how TCP estimates
round-trip times in Section 3.5.3. BET simply assigns an RB to the device with
the smallest throughput that has queued data awaiting transmission in the
base station. The process repeats until all RBs have been assigned. BET scheduling is explicitly throughput-fair, QoS-unaware, and arguably somewhat


Wireless and Mobile Networks

channel-aware, in that it uses the realized per-device throughput (which
depends on the channel quality).

Proportional Fairness (PF) scheduling
PF scheduling seeks to strike a balance between maximizing performance
(throughput) and providing fairness among devices. Let d i k ( t ) and R i ( t ) be
defined as above. At each scheduling time, t, the PF scheduler finds the device
i and resource block, k , that achieves
max i , k { d i k ( t ) R i ( t − 1)}
and then assigns RB k to device i. The intuition behind PF is clear—since d i k ( t )
is in the numerator in the expression to be maximized, higher values of
throughput will raise the value of the expression being maximized. Similarly,
since R i ( t − 1) is in the denominator, a user device with a low average
throughput will also raise the value of the expression being maximized, favoring devices that have experienced low throughput. The process repeats until
all RBs have been assigned. Note that PF scheduling is channel-aware and
aims to provide a measure of fairness.
Our discussion above has just begun to scratch the surface of WLAN and
RAN scheduling. Additional scheduling disciplines, the provision of qualityof-service guarantees through the hard or soft reservation of resources [Prasad
2023], priority scheduling, scheduling for real-time traffic, and virtualized
scheduling [Peterson 2024] are all additionally important topics in this area.


### 7.3.6 Energy considerations: wake/sleep

Energy is a precious resource in wireless mobile devices, and thus many wireless networks provide explicit power-management capabilities that allow
devices to minimize the amount of time that their sense, transmit, and receive
functions and other circuitry need to be “on.” To accomplish this, a device will
typically alternate between sleep and wake states (not unlike a sleepy student
in a classroom!)—waking when there is work to do and sleeping when there is
no work to be done. Measurements have shown that an LTE radio can consume
between 1,000 and 3, 500 mW of energy while transmitting or receiving (or
waiting to receive), but less than 15 mW when powered off—approximately
one percent of on-state energy use [Huang 2012]. Measurements have also
shown that between 20% to more than 50% of energy use in 4G and 5G devices
running popular applications is expended on communication [Xu 2020]. Thus,
communication-related energy use plays a central role in overall mobile device
energy management.
We can identify two main approaches towards energy management via
radio sleep/wake cycles:
* In coordinated sleep/wake approaches, a protocol between the device
and the base station serves to coordinate the device’s sleep/wake cycles,
with both sides being aware of the device’s sleep/wake state, and the time
at which the device is scheduled to awaken next. With this knowledge, the



base station can queue arriving datagrams that are destined for the sleeping device, and then transmit these datagrams to the device when it awakens. Both WiFi and 5G networks adopt a coordinated sleep/wake
approach.
* In uncoordinated, wake-and-send approaches, a device awakes only
when it has data to send. This might happen for example in an IoT device,
where an occasional sensor reading is to be transmitted to a logging server
via a base station. After waking and transmitting, the device may then
wait for messages transmitted to it by the base station in reply, and then
return to sleep until the next sensor reading needs to be transmitted. Bluetooth (Section 7.5.1), LoRaWAN (see Section 7.5.3), and 4G LTE Narrowband IoT (NB-IoT) networks adopt an uncoordinated, wake-and-send
approach.

Coordinated sleep/wake in IEEE 802.11 networks

## 802.11 networks have featured power-management capabilities since their

inception. A WiFi device indicates to the access point that it will be going to
sleep by setting the power-management bit in the header of an 802.11 frame
(see Figure 7.26) to 1. Since the AP knows from the set power-transmission bit
that the device is going to sleep, the AP will buffer any arriving frames that are
destined for the sleeping device until that device awakens. When the WiFi
device wakes up, it will scan for a beacon frame from the AP that contains a
Traffic Indication Map (TIM), indicating those devices that have frames that
are buffered at the AP and awaiting transmission to that sleeping device. If
there are no buffered frames for the device, it can go back to sleep. Otherwise,
the device will send polling request messages to the AP, to ask the AP to transmit the buffered frames.
A number of more recent power-management capabilities have also been
added to 802.11. WiFi 6 introduced a Target Wake Time (TWT) that allows a
device to negotiate the length of its sleep period with the AP. This is valuable
in IoT settings where devices may only occasionally report sensor values. The
maximum TWT value is 4 years, 5 months, 16 days, 13 hours, 37 minutes, and

## 39.49 seconds—a very long sleep! The IEEE 802.11ah standard, designed specifically for IoT applications (see Section 7.5.3), inherited IEEE 802.11’s

power-saving capabilities and added other enhancements, such as reduced
header sizes, to save additional energy. A thorough and readable overview of
WiFi’s modern energy-saving mechanisms is [Guerin 2023].

Coordinated sleep/wake in 5G networks
As in the case of WiFi, when a user device has nothing to send or receive, there
is no reason for its radio to be continuously “on.” Thus, user devices in 5G networks, like their WiFi counterparts, can also go through sleep/wake cycles.
There are two different forms of 5G device sleep/wake cycles, roughly corresponding to a light sleep (perhaps akin to a short “nap”), and a deeper sleep.
Figure 7.38 shows the structure of the light sleep cycle, known as Discontinuous Reception (DRX) in the Connected State. Here, there are two phases


Wireless and Mobile Networks

Figure 7.38 A user device’s light sleep cycle, with short and long DRX cycles

of this light sleep: short DRX cycles and long DRX cycles. The two phases differ, as their names would suggest, only on the length of the sleep period,
trading latency (delay until the device receives datagrams that have arrived at
the base station destined for the device) with the energy expenditures associated with powering up the radio, checking for pending downlink
transmissions, and powering down the radio.
In the example in Figure 7.38, a user device receives a transmission from
the base station at t 0 and starts an activity timer. At t 1, with the device having
neither received any transmissions since t 0 nor having any transmissions to
send, the activity timer expires, and the device enters a short DRX sleep cycle.
At the end of each short DRX cycle, the device awakens and checks whether
the base station is advertising pending transmissions to it, or whether it has
transmissions of its own to send. In this example, since there is no activity for
this device over several short sleep cycles, the device then enters a long DRX
sleep cycle at t 2 . The device again wakes up at the end of each longer sleep
cycle to check for incoming or outgoing transmissions. At t 3, a packet arrives at
the base station for transmission to this device and is buffered, since the device
is sleeping. At the end of the long sleep cycle ending at t 4, the device awakens,
finds that the base station is advertising a transmission for the device, enters
the active state, eventually receives a transmission from the base station at t 5,
and restarts its inactivity timer. In this example, the increase in latency experienced by the arriving packet due to device sleep is equal to t 5–t 3.
There are additional user device sleep states that are even longer and
deeper than the DRX cycles shown in Figure 7.38. After even longer periods of
inactivity, a device can enter the Idle state or Inactive state, where it must take
additional steps to re-establish its active presence in the RAN before it can
send or receive user data. See [Hailu 2019; Developedia 2021; Sauter 2021] for
more details.

Uncoordinated, wake-and-send in LoRaWAN
LoRa (see Section 7.5.3) [Sematech 2019a, 2019b; Sinha 2017] is a low-power,
low-bitrate, wireless networking technology for relatively simple IoT devices




Figure 7.39 LoRa wake-and-send

whose typical task is to report sensor measurement data to a nearby gateway,
typically within a few kilometers of the device. The simplest type of LoRa
device, known as a Class A device, uses its radio in an uncoordinated, wakeand-send approach to do so. A device with data to send simply wakes up,
transmits its data without any coordination with a gateway node (or even
knowing that a gateway node is present), optionally waits for downlink data
from the gateway node, and then goes back to sleep. Here, device-energy conservation is a first-class consideration, with the device’s usual sleep state only
occasionally disturbed by device-initiated wake-up for data transmission.
Figure 7.39 shows LoRa’s wake-and-send behavior. At t 0, the LoRa IoT
device awakes and sends a LoRa frame (e.g., containing a sensor measurement) to the LoRa gateway. The device then looks for messages from the
gateway, and receiving none, returns to sleep at t 1. At t 2 , the gateway has a
message to send to the IoT device but must wait until the next device contact
(following t 3) before sending the message. The gateway’s message is received
at t 4 and the device returns to sleep at t 5.
Like LoRa Class A, Bluetooth Low Energy (BLE) and 4G LTE Narrowband
IoT (NB-IoT) networks also support device-initiated wake-and-send transmission by the IoT device. However, in these cases, the device must first contact
the controller node or base station upon waking to first be allocated channel
transmission slots in which to send its data. See [Sauter 2021] for details.


## 7.4 The Wireless Core Network

Having learned about wireless access networks in Section 7.3, we’ll now move
from the wireless edge and into the wireless core. The 5G Core provides
higher-level control-plane and management-plane services (e.g., for managing
user-device identity, access security, mobility, and more) as well as the dataplane services to forward datagrams between devices in the 5G RAN and the
larger Internet.


Wireless and Mobile Networks

In this section we’ll focus entirely on 5G networks rather than covering
both 5G and WiFi networks. Indeed, there is no reason to discuss core control
and management for WiFi networks here, since traditional IP networks use the
same management and control-plane mechanisms for both wired Ethernet and
WiFi. An enterprise views WiFi, or any wireless edge network, as just another
link-layer technology in its network.
One might wonder why the core network is such a central architectural
component in mobile cellular networks, but not in traditional IP networks. The
answer undoubtedly lies in 5G’s roots in mobile cellular telephony. 1G and 2G
cellular networks were essentially telephone-only networks; 3G networks
were still primarily telephone networks, with packet data grafted on as an
additional service. These early cellular networks supported services for managing user identity (e.g., via SIM cards); device mobility within a provider’s
network; roaming among different provider networks; and accounting, billing,
payment and settlement for services. There was no support for such services in
the deployed Internet at the time. 4G and 5G networks have now become “all IP”
networks and have adopted many of the services pioneered in traditional
IP networks. Nonetheless, native support for services such as identity, mobility, roaming and service billing—services implemented primarily in the 5G
Core—is not implemented in traditional Internet ISPs, and remains a significant difference between 4G 5G networks and traditional IP networks today.
In this section, we’ll provide an overview of the 5G Core and its services
in Section 7.4.1. We’ll focus on the User Plane network function and the extensive use of tunneling in Section 7.4.2 and then cover user identity and its role in
registration and session establishment in Section 7.4.3. Mobility is such an
important topic that we’ll give this a separate treatment in Section 7.5.


### 7.4.1 The 5G Core and Network Functions

Figure 7.40, adapted from [3GPP 23.501 2024], shows a number of the key
5G Core components. The 5G Core adopts a Service-Based Architecture (SBA),
with architectural elements in the Core defined in terms of Network Functions
(NFs) and the services they provide. Although the 5G specifications do not
specify how these functions are to be implemented, a service-based description
would naturally map (as suggested by various figures in this chapter) onto
microservices implemented in a logically centralized data center. This approach
differs significantly from 4G and earlier cellular network architectures that
defined traditional network “entities” that interacted via protocols and were
typically implemented by standalone single-function equipment (“boxes”).
Perhaps reflecting this break from 4G, 5G service elements have completely
new names and abbreviations than their 4G counterparts, causing occasional
headaches for students learning about cellular networks who can be overwhelmed by names and acronyms in the cellular network world.
Many of the innovations in the 5G Core—in particular the evolution from
“boxes” to “services,” the opportunity for SDN-based implementation of services,
and the clear separation between the control plane and user plane—mirror the
earlier evolution of the Internet control plane that we learned about in Chapter 5.




Figure 7.40 5G Core: key network functions

5G Network Functions
If one were to identify the “top three” most centrally important Network Functions in the 5G Core, these three functions would be leading candidates:
* The User Plane Function (UPF) is responsible for the data-plane forwarding of traffic between the RAN and the larger Internet. As the only
5G network function in the data plane, it clearly plays a central role. As
we’ll see in Section 7.4.2, the User Plane Function is structured as a tunneled relay that forwards user IP datagrams between the base station
and the larger Internet. Every datagram transmitted by a device to the
larger Internet and vice versa will pass through the device’s User Plane
Function.
* The Access, Mobility Management Function (AMF) plays the key role in
authorizing and establishing device access to a 5G network’s services
and in managing device mobility (discussed in Section 7.5). The AMF is
arguably the central Network Function in the 5G control plane. As we
will see, the AMF works with many other network functions to implement
its services. For example, the AMF interacts with the Authentication
Server Function (AUSF) to authenticate a device that wants to join a 5G
network. The AMF is also the only control-plane network function that
exchanges control messages directly with a device, via the N1 interface
shown in Figure 7.40, and is one of only two network functions that directly
exchange control messages with a base station (via the N2 interface). A
numbered interface such as N1 is known as a reference point in 3GPP
parlance and defines the interaction between a 5G core function and
another Core function (or device or base station). [3GPP 23.501 2024]
standardizes more than 60 such reference points.


Wireless and Mobile Networks

* The Session Management Function (SMF) manages each device session,
including IP address allocation and assignment (e.g., NAT and DHCP-like
services) and the installation of per-device state for functions such as
­policy-based access control, charging, and establishing device data-plane
forwarding via the UPF.
Network, user, and application data and state information also figure
prominently in the set of network functions. Device profile, service and
authentication information is managed by the Unified Data Management
(UDM) Network Function. The UDM may store its data internally within its
function implementation or externally in the Unified Data Repository
(UDR). When a Network Function chooses to store data externally in the
Unified Data Repository and accesses and updates this information
remotely, stateless transactions (similar in spirit to the stateless client/server
interaction in HTTP) are possible, naturally leading to scalable and resilient
network function implementations in a cloud environment. Other network
functions and third-party applications can also store and retrieve data to
and from the Unified Data Repository and the Unstructured Data Storage
Function (UDSF).
In Section 7.3.3, we learned that user application code can run on servers
in the 5G Core or at the base station and communicate with devices to implement an application’s service, a capability known as local breakout. The
Network Exposure Function (NEF) and Application Function (AF) expose
select network data and Network Function services to these local-breakout
applications, and vice versa.
Sometimes a Network Function running in one operator’s 5G network
will need to interact with a counterpart in another operator’s 5G network. For
example, when your smartphone wants to join a network not operated by the
network provider with whom you have a paid subscription plan (known as
your “home” network), the Authentication Server Function (AUSF) in the network that you want to join will interact with its peer AUSF in your home
network to perform authentication and to determine the set of services available to you. The authentication functions in these two networks will securely
communicate with each other via their local Security Edge Protection Proxy
(SEPP) Network Function.
Finally, capabilities are needed for network functions to register their
services and discover the potentially large number of other network functions. The Network Repository Function (NRF) provides these automatic
registration and discovery services, obviating the need for complex manual
configuration. The Policy Control Function (PCF) provides control, management, and centralized repository services for control policy rules used for
mobility management, per-device quality of service, and roaming. One important new concept introduced in 5G is network slicing, which involves the
virtualization of RAN and Core resources, and the ability to define multiple
logical networks that share the network’s underlying physical resources, in
much the same way that we learned (in Section 6.5) that multiple virtual private
networks (VPNs) can operate over the same set of physical network resources
in traditional IP networks. The Network Slice Selection Function (NSSF)



is the network function that plays the central role in network slicing, a topic
beyond the scope of this book.
As we will see, a network function will typically interact with other network functions to implement its service. Network functions can communicate
with each other using several different styles of interaction, and the standards
do not mandate or recommend one approach over another. NF services may be
accessed using the traditional request/response client-server model that we
studied in Chapter 2, which in turn can be implemented via a protocol such as
HTTP, or by remote procedure calls in a data center setting. Another form of
client-server interaction is the subscribe/notify model (aka the publish/­
subscribe model in the distributed systems literature) in which a client
registers its interest in a service, and the server notifies the client when results
from the service are available (i.e., “pushes” results to subscribed clients).
Recall that we learned in Chapter 5 that the publish/subscribe model is the
central organizing principle in Google’s Orion SDN platform.


### 7.4.2 User Plane Function

We learned above that the User Plane Function is responsible for controlling the data-plane forwarding of traffic between the RAN and the larger
Internet. Since the 5G data plane is an all-IP network, in many ways it functions exactly as we’ve already seen in Chapters 4 and 5. However, the 5G
control plane configures the data plane to support two key services not
always found in traditional IP networks: quality of service (QoS) support
and tunneling. 5G QoS support is an advanced topic beyond the scope of
this book; see [Sauter 2021] for a discussion. In this subsection, we’ll consider tunneling together with the protocol stacks in the 5G data plane that
implement tunneling.
Recall from Chapters 4 and 6 that tunneling provides the abstraction of a
virtual link between two IP devices. In a 5G setting, a tunnel is established for
each device between its base station and its instance of the User Plane Function,
as shown in Figure 7.41. With tunneling, the entire sea of routers and links in
the backhaul network between the base station and the User Plane Function is
abstracted as a single virtual link for that device.
Having studied the RAN protocol stacks in detail in Section 7.3, let’s now
focus on the data-plane protocol stacks at the base station and the User Plane
Function in the 5G Core. As discussed in Section 7.4.3, the Session Management Function will establish a tunnel between the base station and the device’s
User Plane Function when a device joins the network. When a User Plane
Function receives a datagram from the external Internet that is destined for a
device in its data plane, the User Plane Function encapsulates that datagram
within a UDP segment using the GPRS Tunneling Protocol (GTP) [3GPP TS

## 29.281 2022]. The UDP datagram then becomes the payload in a new IP datagram, which is forwarded from the User Plane Function through the backhaul

network to the base station, just like any other IP datagram addressed to the
base station. On the receiving side, the base station decapsulates the tunneled
UDP datagram from the User Plane Function, extracts the encapsulated IP


Wireless and Mobile Networks

Figure 7.41 5G protocol stacks, with tunneling

datagram destined for the device, and forwards that IP datagram over the
RAN to the device. As with the use of tunneling in mixed IPv4 v6 networks
(Section 4.3), you should carefully examine the addresses in the datagramwithin-a-datagram in Figure 7.41.
The protocol details of the tunneling protocol are fairly straightforward
and can be found in [3GPP TS 29.281 2022]. So rather than diving into those
details here, let’s instead consider the more fundamental question of why tunneling is used in the first place. In Chapter 4, we learned that tunneling allowed
IPv4 and IPv6 networks to interoperate. But what are the advantages to wrapping a datagram inside a datagram while operating in a pure 5G network? The
answer lies in device mobility, i.e., a device changing the base station to which
it is attached (Section 7.4) as it moves through the cellular provider’s network.
Consider again the example in Figure 7.41. Without tunneling, all of the
routers in the backhaul network would need to maintain up-to-date information about a device’s location (i.e., the base station to which the device is
currently attached) in order to forward a datagram to that device. Indeed, the
routers would need to maintain that information for all devices in the provider’s
network! With tunneling, only the tunnel endpoint (i.e., the User Plane Function) needs to know the identity of the base station to which the device is
attached; the backhaul routers need only know how to forward and route datagrams to and from the base stations. The UPF thus serves as an anchor point for
forwarding datagrams from a device to the larger Internet, and vice versa, for the



duration of a device’s attachment to the 5G network, regardless of the particular base station to which the device happens to be attached at a given time.


### 7.4.3 User identity, registration, and

session establishment
In Section 7.3.4, we learned how a device discovers the existence of a 5G network and how it initially attaches to a base station. Recall that following this
initial attachment, although the device and base station are able to exchange
control messages, the device still has not yet really joined the 5G network—it
hasn’t yet exchanged control messages with the 5G Core and so can’t yet, for
example, send or receive data-plane datagrams via a User Plane Function.
Let’s begin our discussion of how a device fully joins a 5G network by first
considering how the device identifies itself to the network.

Identity: SIM Cards
As most cell phone owners know, a 4G 5G device needs a physical SIM (Subscriber Identity Module) card, or more recently a software-only eSIM, to attach
to a 4G 5G network. Your SIM uniquely identifies you and your “home” network to all cellular network providers globally. In the cellular network world,
your SIM is your global network identity!
The information included in a SIM can differ from one provider to another,
but will generally include the following information:
* IMSI: International Mobile Subscriber Identity. An IMSI has three parts:
a 3-digit (base 10) mobile country code (MCC), a 2- or 3-digit mobile network code (MNC) and a mobile subscription identification number
(MSIN). The MCC and MNC together define the SIM’s home network, i.e.,
the cellular provider that provided the SIM card to you and with whom
you have a subscription plan. The MSIN uniquely identifies the SIM within
the home network. Your SIM also has your cellular phone number and an
associated set of cellular services that you’re able to access when attached
to your home network. When you’re in an area not served by your home
network, you may attach to another provider’s network, in which case you
are said to be roaming on a visited network. You may have a different set
of services available to you on visited networks, depending on your subscription plan with your home network and the charging/settlement
mechanisms between your home network and the visited network. There
may be networks that, with great frustration, you simply cannot join.
* Cryptographic keys and PINs are also stored on a SIM. The cryptographic
key is used for authenticating the device when it joins the 5G network, as
discussed below and in Chapter 8.
* Local Area Identity information lists current and recently visited networks. Local identity is used to identify networks that a device may try
first when seeking cellular network service.
* Contact lists and text messages may also be stored on a SIM card.


Wireless and Mobile Networks

Joining a 5G network: registration and session
establishment
When a device wants to join a 5G network, there are two important sets of
actions that are undertaken. The first is registration, when the device identifies
and then authenticates itself to the network, and vice versa. The second is PDU
Session establishment, which allocates an IP address for the device and creates a data-plane path between the device and a User Plane Function. “PDU” is
an acronym for “Protocol Data Unit”—3GPP jargon for a “packet.” After these
steps, the device is fully attached to the network, and ready to go (communicate while being mobile)!
Both registration and session establishment are performed by network
functions in the 5G Core, with Access and Mobility Management Function
(AMF) playing a central role in this process. The AMF is the only Network
Function that communicates directly with the base station and the device. It
orchestrates authentication (with the AUSF) and session establishment (with
the SMF) within the 5G Core.
Let’s now briefly consider the steps involved in registration and session
establishment, as shown in Figure 7.42.

Figure 7.42 Device registration and session establishment: interaction among device, base
station and Core Network Functions



* Registration. Earlier in Section 7.3.4, we learned that the device and base
station exchange connection setup request/response messages to establish
a RAN signaling channel between themselves. After this exchange, the
base station then selects an instance of the AMF for the device and sends a
registration request to that AMF for that device. The AMF then contacts
the device and requests and receives device identity information. As shown
in Figure 7.42, that information is then passed to the Authentication
­Function which performs mutual authentication with the device; we’ll postpone our discussion of 5G authentication until Chapter 8, where we’ll cover
this topic in detail. Note that if the network being joined by the device is not
its home network, the local Authentication Function in the visited network
will serve as a proxy to the Authentication Function in the device’s home
network, which will actually perform the authentication. Following a
­successful authentication, the AMF then registers the device’s identity and
subscribed service information in the local UDM, and returns a registration
acceptance message to the device.
* Session establishment. The device initiates the process that will establish
its data plane by sending a PDU session establishment request to the AMF,
which in turn selects an SMF that will be responsible for establishing and
managing the device’s data plane, while the device is attached to the network. After verifying via the User Data Management Function that the
device’s requested session parameters are permissible, the SMF selects an
instance of the User Plane Function and establishes the device’s tunnel
between its base station and that User Plane Function. The SMF then
returns the tunnel, IPv4 address information, and additional session information to the device via the AMF and the base station. The final step is for
the base station and the device to interact to configure the device’s RAN
data plane. Once this is done, the device is then ready to send datagrams
into the Internet!
In the above, we’ve illustrated only the most important interactions
among the device, base station, and various network functions in registration
and session establishment. We note that the Policy Control Function and the
Charging Function are also involved in session establishment and that additional steps are needed to configure IPv6, if desired. For a full discussion of the
process, see [3GPP TS 23.502 2024], and the discussion (34 rather dense pages!)
surrounding Figures 4.2.2.2.2-1 and 4.3.2.2.1.


## 7.5 Mobility

Having covered the characteristics of wireless links and the physical layer of
wireless networks in Section 7.2, wireless access networks in Section 7.3 and
wireless core networks in Section 7.4, let’s now turn our attention to one of the
most unique and interesting aspects of wireless networks—the need to support device mobility. Indeed, this topic is so important that we are devoting an
entire section to the topic! We’ll begin in Section 7.5.1 by discussing the challenges introduced by the need to support mobile devices and the principles


Wireless and Mobile Networks

and broad approaches towards doing so. While WiFi naturally supports mobility in the vicinity of an access point, we’ll see that WiFi (Section 7.5.2) only
provides limited support for mobility among nearby WiFi WLANs. By contrast, cellular networks have had mobility “baked in” as a first-class,
“must-have” service since their earliest days due to their roots in the mobile
telephony world. We’ll cover the extensive support for mobility in 5G networks in Section 7.5.3. In Section 7.5.4, we’ll wrap our discussion of mobility
with observations about past IETF efforts for supporting network-layer mobility within and among non-cellular IP networks, and possibly why such mobile
Internet service has not been deployed to date.


### 7.5.1 Mobility Principles

What is “mobility”?
Let’s begin our discussion of device mobility by carefully considering what we
mean by “mobility” in the first place. Suppose a device is “on” and communicating as it moves, and let’s consider how “far” such a device can move while
communicating without interruption (e.g., maintaining ongoing TCP connections
and not needing to explicitly join any new networks). Drawing on the distinction made between inter-domain and intra-domain routing, we can identify
three distinct mobility scenarios, depending on whether or not a device is able
to move without interrupting ongoing communication within and among
access networks (e.g., 802.11 WLANs or 5G RANs) with a single provider’s
network, and within and among the multiple provider networks.
* Mobility only within a single access network. At one end of the spectrum, scenario (a) in Figure 7.43, a mobile device maintains its communication connectivity only while attached to a given access network. In this scenario, a
device must disconnect from the base station in one access network, and
then connect to a new base station in another access network, as it moves
between access networks. For example, a student might disconnect from a
wireless classroom network and power down their laptop or smartphone,
head to the dining commons and connect to the wireless access network
there while eating, and then disconnect and power down from the dining
commons network, walk to the library, and connect to the library’s wireless network while studying. In this case, the device serially associates
with (joins), and later disassociates from (leaves), each wireless access network encountered. This case of limited device mobility can be completely
handled using the networking mechanisms we’ve already studied in
­Sections 7.3 and 7.4.
* Mobility among access networks within a single provider network. Our interest
in device mobility really starts with case (b), where a device moves
among multiple access networks within a provider’s network while continuing to send and receive IP datagrams, and while maintaining higherlevel (e.g., TCP) connections. Here, the network will need to provide
handover—a transfer of responsibility for forwarding datagrams to/
from one base station to another as the device moves among WLANs or




Figure 7.43 Various degrees of mobility, as a device maintains connectivity

RANs. When handover occurs within access networks belonging to a single network provider, that single provider’s network orchestrates handover on its own.
* Mobility among multiple network providers. When a mobile device roams
between multiple provider networks, as in scenario (c) in Figure 7.43, the
providers must coordinate handover to ensure uninterrupted ongoing
communication. This inter-provider handoff significantly complicates the
process.
As scenario (c) is more complex and occurs less often as cellular network
providers increase their geographical footprints, we’ll focus our attention here
on case (b). See Chapter 7 in earlier editions of this book, available on our publisher’s and authors’ Web sites, for a discussion of scenario (c).

Mobility: challenges and approaches
Any approach toward supporting device mobility among access networks
within a single provider network (case (b) in Figure 7.43) must consider three
fundamental questions:
* Is device mobility supported only at the link layer, or is the network layer involved
as well? If mobility is supported only at the link layer, a device may be able
to move among wireless access (link-layer) networks, but this may restrict
a device’s mobility range while communicating without interruption to be
within its current subnet (in the addressing sense of Section 4.3). This is
because, with only link-layer mobility support, incoming datagrams from
the larger Internet that are destined to the device will always be forwarded
to this subnet for delivery to the device. As we will see in Section 7.5.3, this
is the approach taken in enterprise WiFi networks.
* On the other hand, if device mobility is supported across the provider’s
entire network, network-layer (and/or higher-layer) support will be
needed. For example, the core network will need to know the particular
access network to which the mobile device is currently attached, so that
incoming datagrams from the larger Internet can be forwarded to that
subnet for delivery to the device. As we will see in Section 7.5.3, this is the
approach taken in 5G (and 3G and 4G) cellular networks.


Wireless and Mobile Networks

* Why is handover initiated, and who initiates handover? When a device changes
its point of attachment to the network from one base station to another,
why is that change made in the first place? As we saw in Section 7.2, as a
device moves, the quality of the radio signal between itself and the base
station (and hence packet throughput and latency) can change. A device
might thus change access networks to improve its performance. However,
the network itself may choose to move the device from one access network to another in order to load-balance devices among its access networks. The WiFi and 5G standards do not specify specific algorithms to be
used by a base station to determine whether or not to perform handover,
or which target base station to choose. That decision is left up to network
operators and remains an active area of research [Haghrah 2023].
* A wireless device will also typically measure the signal quality of all base
stations within range and report that information back to the base station
to which it is currently attached. We learned in Section 7.3.5 that in 5G
networks, a base station periodically broadcasts reference signal symbols
and that a device periodically reports a 4-bit channel quality indication
(CQI) to the base station based on its measured reception of these reference signals. WiFi devices measure the strength of the signal received
from various APs and return a Received Signal Strength Indicator for
each of these APs. These measured and reported values can then be used
to decide whether a device should be handed over to a different base station. A device or network could also predict future device mobility and
radio signal strength (e.g., using machine learning) and proactively perform handover, rather than relying just on current measurements. The
decision to perform a handover may be initiated and controlled primarily
by the device, or by the control plane in the network’s base stations.
* How is handoff accomplished? When a device that is associated with one
base station is handed off to another base station, two important tasks
must be accomplished. First, device state (e.g., the authenticated status of
the device, the device’s allowed services) within the WLAN or RAN control plane in one base station must be transferred to the neighboring base
station. Without this transfer, a device would have to disassociate from the
old base station, and associate with the new base station. Secondly, to
ensure the uninterrupted bi-directional flow of datagrams to and from the
mobile device, forwarding tables in routers and switches must be modified to redirect datagrams to and from the device when there is a new
point of attachment to the network.
In the following two subsections, we’ll study how these mobility considerations are addressed in institutional WiFi networks (Section 7.5.3) and 5G
cellular networks (Section 7.5.4).


### 7.5.2 Mobility in a WiFi network

The IEEE 802.11 WiFi standard adopts a decidedly link-layer-only approach
towards mobility, perhaps not surprising because 802.11 is a link-layer




Figure 7.44 WiFi:
handover within the ESS

standard. Consequently, WiFi mobility is supported only among access points
that are within the same subnet (in the addressing sense of Section 4.3).
We learned in Section 7.3.2 (Figure 7.22) that the traditional WiFi network,
known as the Basic Service Set (BSS), contains a single AP and one or more
attached wireless devices. Figure 7.44 shows the concept of an Extended Service Set (ESS), which consists of multiple BSSs (e.g., BSS 2 and BSS 3 ) and their
set of access points (e.g., AP2 and AP3 in Figure 7.44). Assuming that each AP
in the ESS uses the same SSID, an ESS appears logically to be just a single WLAN
from both the device point of view and from the network-layer point of view,
since the devices and APs in the ESS are in the same layer-3 subnet. Indeed, a
device that moves between BSS 2 and BSS 3 in Figure 7.44 is not even mobile
from a network-layer point of view, since it never leaves its subnet! The
IEEE 802.11 standard introduced Fast Basic Service Set Transition (FT) to
­accelerate the 802.1X authentication when a device moves between APs in an
ESS, and to allow APs to suggest alternative APs to which a device may wish
to attach within the ESS.
In addition to these 802.11 standard capabilities, large WiFi equipment
vendors provide proprietary solutions that provide support for mobility, e.g.,
to manage device handover between two APs in an ESS [Cisco 802.11r 2016].


### 7.5.3 Mobility in a 5G network

While 802.11 mobility occurs exclusively at the link layer, mobility in a cellular
5G network is a network-wide undertaking, involving both RANs and the 5G
Core network. 5G’s extensive support for device mobility undoubtedly reflects
its roots in the mobile cellular telephony world. The earliest generations of cellular networks provided call handover with uninterrupted voice service as a
user ranged from cell to cell across a provider’s network, as well as from one
provider’s network to another. With mobility “baked in” to the earliest cellular
network architectures, the addition of mobile data services followed quite naturally in later generation cellular networks.


Wireless and Mobile Networks

In this subsection, we’ll focus on the handover process in 5G networks. As
we’ll see, handover is carefully orchestrated within the RAN and 5G Core control planes, and also involves the reconfiguration of the device’s RAN and 5G
Core data planes, making it a truly network-wide activity.

5G Handover
Let’s consider an active 5G device that is currently associated with a base station in one RAN (the “source” base station for the handover) that will be
handed over to a second base station (the “target” base station) in another
RAN. Let’s suppose that the device is “active” in the sense that it has an ongoing TCP connection with a remote host in the larger Internet and an active
data-plane connection via a tunnel to/from its User Plane Function in the Core
(see Section 7.4.2). After handover, the device will be associated with the target
base station, the source base station will have released the device state it had
been maintaining, the data-plane tunnel to and from the device will now end
in the second RAN (assuming for simplicity that the other tunnel endpoint
remains at the same User Plane Function), and all device states in the 5G Core
will reflect the fact that the device is now located in the newly-joined base station. So many changes that will need to be made!
Figure 7.45, adapted from Figures 4.9.1.2.2-1 in [3GPP TS 23.502 2024] and
9.2.3.2.1-1 in [3GPP TS 38.300 2024], illustrates the handover process. 5G
handover begins in the RANs, and then completes in the Core. Most of the
handover interactions shown in Figure 7.45 are in the control plane, but the
data-plane tunnel between the User Plane Function and the base station to
which the user is associated will also change during the process. We can identify three distinct phases in 5G handover:
* Making the handover decision. Handover begins in the RAN, with the device
measuring the quality of the radio channels of the base stations that it can
hear, and then reporting these measurements to the source base station. If a
handover is deemed desirable by the source base station, it sends a handover
request message to the target base station, which then decides whether or
not to accept the handover and returns its decision (in the case of the example in Figure 7.45, a positive acknowledgment) to the source base station.
* Transferring the device between base stations. The source base station, target
base station and the device then work together to transfer the device’s
RAN connection from the source base station to the target base station.
This process begins with the source base station sending two messages: a
reconfiguration message to the device and a transfer status message to the
target base station that transfers device state to the target base station. The
device and the target base station can then set up a new RAN connection.
The process completes when the device sends a reconfiguration complete
message to the target base station and the target and source base stations
perform a final handshake. Note that the endpoint of the tunnel between
the base station and the User Plane Function remains unchanged during
this process. However, rather than delivering datagrams to the device
over the source RAN, the source base station instead begins forwarding
datagrams addressed to the device to the target base station. The target




Figure 7.45 Device handover: RAN and Core actions

base station will buffer these datagrams for later delivery to the device,
ensuring that no incoming datagrams destined for the device are lost in
the handover process.
* Updating device state and UPF tunnel in the Core. Handover activity now
shifts to the Core. The target base station, which is now fully in charge of
the device’s RAN connection, signals to the Session Management Function (SMF) via the AMF that it is the new base station for the device
being handed over. The SMF then signals to the User Plane Function to
change the device’s tunnel to be terminated at the target base station.
The User Plane Function then sends a data-end marker to the source
base station, which then knows that the device tunnel endpoint has been
switched and informs the target base station. At this point, the target
base station can deliver to the device any buffered datagrams forwarded
to it from the source base station during handover. Additionally, datagrams will now flow directly from the device’s User Plane Function to
the target base station. Following some cleanup handshaking, the handover process is now complete!


Wireless and Mobile Networks

While our description above might seem rather complicated, it actually
only considers the simplest of handover scenarios! One common scenario not
covered above is the case in which a device has powered off its radio to conserve power. Recall from Section 7.3 that after periods of inactivity, there are
sleep periods that are even longer than the DRX sleep cycles we encountered in
Figure 7.38. During these periods of long sleep, a device will first enter the Idle
state and then the Inactive state. In the Idle state, a device must take additional
steps to re-establish its active presence in the RAN before it can send or receive
user data. In the Inactive state, additional handover steps must be taken in both
the RAN and in the Core. In particular, if a device moves among base stations
while Idle or Inactive, the 5G Core may not even know the RAN in which the
device is located. Tracking area update procedures can be used so that the Core
knows the general area where the device is located. Paging procedures can then
be used by the Core to pinpoint the device’s RAN. These topics are beyond the
scope of our discussion here; see [Alsaeedy 2019] for a discussion.
A more complex handover also occurs when a device is handed over from
the RAN in one provider’s mobile cellular network to the RAN in another provider ’s network. In this case, the cellular provider to which the device is
attached changes and inter-provider signaling is needed; see [3GPP TS 138.300
2024] for details.


### 7.5.4 Internet Mobility

Today’s traditional (non-cellular) Internet does not have any widely deployed
infrastructure that provides the type of services for “on the go” mobile users
that we encountered for 5G cellular networks. This, however, is not due to the
lack of technical solutions for providing such services! Indeed, a Mobile IP
architecture and protocols [RFC 5944] were standardized in Internet RFCs
more than 25 years ago. Interested readers can consult earlier editions of our
book and [Perkins 1998] for an in-depth treatment of Mobile IP. And research
has continued on new, more secure and more generalized Internet mobility
solutions [Venkataramani 2014].
Given Mobile IP’s technical solutions, it has perhaps been the lack of motivating business and use cases [Arkko 2012] and the timely, first-mover
development and deployment of alternative mobility solutions in cellular networks that blunted the deployment of Mobile IP. Recall that 25 years ago, 3G
cellular networks had already provided a solution for mobile voice services
(the “killer app” for mobile users) as well as the beginnings of global mobile
data services. Behind these services was a paid subscription model with a
home network provider, and inter-provider business agreements and payments that allowed users to roam from their home networks to visited
networks. The traditional Internet lacks such a business infrastructure in support of roaming.
Today, mobile Internet connectivity is provided via a dual technology
solution—mobile services via cellular networks when we are truly mobile and
“on the go” (i.e., the center and rightmost side of the mobility spectrum in
­Figure 7.44) and Internet services via 802.11 networks or wireline networks
when we are stationary or moving locally (i.e., the center and leftmost side of



the mobility spectrum in Figure 7.44). Perhaps this dual-technology solution
that we’ve now had in place for 25 years will continue to persist into the future.
The one indisputable fact however, is that 15 years ago there were approximately equal numbers of subscribers attached to the Internet via fixed (wired)
broadband technologies and via wireless technologies. While both subscriber
bases have grown since then, there are now five times as many Internet-­
connected wireless subscribers than wired subscribers. There’s a saying that
customers “vote with their feet.” That may be a particularly apt description of
the choices that highly mobile Internet users have made.


## 7.6 Bluetooth, Satellite and IoT

Wireless Networks
In the past three sections, we’ve focused primarily on WiFi and 5G networks.
But these are not the only types of widely deployed wireless networks! In this
section, we’ll thus briefly cover three additional types of wireless networks—
Bluetooth, satellite, and IoT wireless networks. As we’ll see, because these
networks provide more specialized services than WiFi and 5G networks, they
have interestingly different architectures and protocols.


### 7.6.1 Bluetooth networks

Bluetooth networks have quickly become part of everyday life. You may have
used a Bluetooth network as a cable-replacement technology to interconnect a
computer with a wireless keyboard, mouse, or other peripheral device. Or perhaps you’ve used a Bluetooth network to connect wireless earbuds, speaker,
watch, or health monitoring band to a smartphone or to connect a smartphone
to a car’s audio system. In all of these cases, Bluetooth operates over short
ranges (tens of meters or less), at low power, and at low cost. For this reason,
Bluetooth networks are sometimes referred to as wireless personal area
­networks (WPANs) or, because of their limited range, piconets.
Although Bluetooth networks are small and relatively simple by design,
they’re packed with many of the link-level networking techniques that we’ve
studied earlier, including time division and frequency division multiplexing
(Section 6.3.1), randomized backoff (Section 6.3.2), polling (Section 6.3.3), error
detection and correction (Section 6.2), and reliable data transfer and flow control (Chapter 3). And that’s just considering Bluetooth’s link layer!
Bluetooth networks operate in the unlicensed 2.4 GHz Industrial, Scientific, and Medical (ISM) radio band along with other home appliances such as
microwaves, garage door openers, and cordless phones. As a result, Bluetooth
networks are designed explicitly with noise and interference in mind. The
Bluetooth wireless channel is operated in a combined TDM and FDM manner,
with 79 frequency channels and 625 microsecond time slots on each channel.
During each time slot, a sender transmits on one of the 79 channels. The sender
then changes the channel (frequency) used in a pre-determined manner from
one slot to the next, as shown in Figure 7.46.


Wireless and Mobile Networks


Figure 7.46 Bluetooth
frequency hopping over
time

This form of channel hopping, known as frequency-hopping spread spectrum (FHSS), is used so that interference from another device operating at a
given frequency in the ISM band will only interfere with Bluetooth communications in a small number of slots. Additionally, slots with significant
interference, as manifested in a low signal-to-noise ratio, can be adaptively
removed from the hopping pattern. Multiple Bluetooth networks can co-exist
in the same physical space as long as they use different frequency hopping patterns. Bluetooth data rates can reach up to 2 to 3 Mbps.
Bluetooth networks are ad hoc networks, as no network infrastructure
(i.e., base station) is needed. In most usage cases, Bluetooth communication is
between only two devices, e.g., between wireless earphones and a smartphone.
But the Bluetooth standard also allows for devices to organize themselves into
networks, and so a multiple access protocol is required. Bluetooth devices
organize themselves into a piconet of up to eight active devices, as shown in
Figure 7.47. One of these devices is designated as the centralized controller,
with the remaining devices acting as clients in a “peripheral” role. The centralized controller node truly rules the piconet—its clock determines time in the

Figure 7.47 A
Bluetooth piconet


piconet (e.g., determines TDM slot boundaries), it determines the slot-to-slot
frequency hopping sequence, it controls entry of client devices into the piconet,
it controls the power (100 mW, 2.5 mW, or 1 mW) at which peripheral devices
transmit, and (using polling) it grants transmission privileges to a peripheral
device once it has been admitted to the network. In Bluetooth, communication
occurs only between the central and peripheral nodes; there is no direct peripheral-to-peripheral communication.
Because Bluetooth ad hoc networks must be self-organizing, it’s worth
looking into how they bootstrap their network structure. When a centralized
controller node wants to form a Bluetooth network, it must first determine
which other Bluetooth devices are within range; this is the neighbor-discovery
problem. The centralized controller does this by broadcasting a series of
32 inquiry messages, each on a different frequency channel, and repeats the
transmission sequence up to 128 times. A client device listens on its chosen
­frequency, hoping to hear one of the centralized controller’s inquiry messages on
this frequency. When it hears an inquiry message, it backs off a random amount
of time between 0 and 0.3 seconds (to avoid collisions with other responding
nodes, reminiscent of WiFi’s and Ethernet’s binary backoff) and then responds
to the centralized controller with a message containing its device ID.
As the Bluetooth centralized controller discovers potential clients within
range, it can then invite those clients that it wishes to join its piconet. This second phase is known as Bluetooth paging (not to be confused with paging in 5G
networks) and is reminiscent of 802.11 clients associating with a base station.
The centralized controller begins the paging process by again sending 32 identical paging invitation messages, each now addressed to a specific client, but
again using different frequencies, since a client doesn’t yet know the frequency-hopping pattern. Once the client replies with an ACK message to the
paging invitation message, the centralized controller sends frequency-hopping
information, clock synchronization information, and an active member address
to the client. It then finally polls the client, now using the frequency-hopping
pattern, to ensure that the client is connected into the network.
Because Bluetooth was designed for a specific, limited set of services
(unlike the Internet and 5G networks), it’s instructive to take a quick look at its
protocol stack, shown in Figure 7.48. Perhaps most strikingly, the Bluetooth
protocol stack lacks both a network layer and a traditional transport layer! The
lack of a network layer is perhaps not surprising, given that Bluetooth networks are generally single-hop with only controller-to-peripheral, or
peripheral-to-controller transmissions, and so multi-hop forwarding and routing are not of concern. Multi-hop extensions of the basic Bluetooth mechanisms
do exist in the Bluetooth Scatternet and more recently, the Low Energy Mesh
specifications, but these have seen extremely limited deployment [Todtenberg
2019]. Many of the Internet’s end-to-end transport-layer services—including
reliable data transfer, flow control, segmentation, connection-oriented and connection-less services and an API for upper-layer applications—are provided in
Bluetooth’s Logical Link Control and Adaptation Protocol (L2CAP) layer.
L2CAP also provides a service that reserves periodic slots for a connection’s
transmissions; this is useful for multimedia applications with known bandwidth requirements and fixed timings.


Wireless and Mobile Networks

Figure 7.48 Bluetooth protocol stack

In our discussion above, we have only touched on Bluetooth wireless
­ etworking. More recent versions of Bluetooth have emphasized low-energy
n
and security considerations. For more information about Bluetooth, the interested reader should consult [Colbach 2017; Todtenberg 2019; Sauter 2021;
Bluetooth 2025].

Location Discovery
GPS and Wifi Positioning
Many of the most useful and important smartphone apps today are location-based
mobile apps, including Foursquare, Yelp, Uber, Pokémon Go, and Waze. These
software apps all make use of an API that allows them to extract their current
geographical position directly from the smartphone. Have you ever wondered how
your smartphone obtains its geographical position? Today, it is done by combining
two systems: the Global Positioning System (GPS) and the WiFi Positioning
System (WPS).
The GPS, with a constellation of 30 + satellites, broadcasts satellite location
and timing information, which in turn is used by each GPS receiver to estimate its
geolocation. The United States government created the system, maintains it, and
makes it freely accessible to anyone with a GPS receiver. The satellites have very
stable atomic clocks that are synchronized with one another and with ground
clocks. The satellites also know their locations with great precision. Each GPS
satellite continuously broadcasts a radio signal containing its current time and
position. If a GPS receiver obtains this information from at least four satellites, it can
solve trilateration equations to estimate its position.
GPS, however, cannot always provide accurate geolocations if it does not have
line-of-sight with at least four GPS satellites or when there is interference from



other high-frequency communication systems. This is particularly true in urban
environments, where tall buildings frequently block GPS signals. This is where
WiFi positioning systems come to the rescue. WiFi positioning systems make use
of databases of WiFi access points, which are independently maintained by various
Internet companies, including Google, Apple, and Microsoft. Each database contains
information about millions of WiFi access points, including each access point’s SSID
and an estimate of its geographic location. To understand how a WiFi positioning
system makes use of such a database, consider an Android smartphone along
with the Google location service. From each nearby access point, the smartphone
receives and measures the signal strength of beacon signals (see Section 7.3.4),
which contain the access point’s SSID. The smartphone can therefore continually
send messages to the Google location service (in the cloud) that include the SSIDs
of nearby access points and the corresponding signal strengths. It will also send
its GPS position (obtained via the satellite broadcast signals, as described above)
when available. Using the signal-strength information, Google will estimate the
distance between the smartphone and each of the WiFi access points. Leveraging
these estimated distances, it can then solve trilateration equations to estimate the
smartphone’s geolocation. Finally, this WiFi-based estimate is combined with the
GPS satellite-based estimate to form an aggregate estimate, which is then sent back
to the smartphone and used by the location-based mobile apps.
But you may still be wondering how Google (and Apple, Microsoft, and so
on) obtain and maintain the database of access points, and in particular, the access
point’s geographic location? Recall that for a given access point, every nearby
Android smartphone will send to the Google location service the strength of the
signal received from the access point as well as the smartphone’s estimated location.
Given that thousands of smartphones may be passing by the access point during
any single day, Google’s location service will have lots of data at its disposal to use
in estimating the access point’s position, again by solving trilateration equations.
Thus, the access points help the smartphones determine their locations, and in turn
the smartphones help the access points determine their locations!


### 7.6.2 Satellite Networks

The world of satellite communications has evolved dramatically in the last
10 years. Until 10 years ago, deployed satellite applications primarily used satellites in geostationary orbit (GEO). A geostationary satellite is located roughly
35,000 km above the earth’s equator and rotates with the Earth so that it
remains in the same position in the sky relative to observers on Earth. Geostationary satellites have been in use for more than 60 years, for applications
including broadcast TV, sensing (e.g., of the weather, atmospheric or surface
sensing), and Internet connectivity in areas not served by the terrestrial Internet [Hughes 2025].
The past 10 years, however, have seen a tremendous increase in interest in
a different class of satellite networks, known as low earth orbit (LEO) satellites. While the applications remain the same (in particular sensing and Internet
connectivity), LEO satellites (LEOs) are generally smaller, less expensive, and
positioned much closer to the earth than their GEO counterparts. Located
between 500 and 1,200 Km above the surface, LEO satellites thus have much
shorter RTTs ( ~30 msec ) than GEO satellites ( ~800 msec ). As of November


Wireless and Mobile Networks

2022, only 6,800 active satellites had been launched in all of history. But in just
five years (2019–2024) Starlink alone has launched an equivalent number
( 6,281) of LEO satellites [space.com 2024]. Today, well over 90% of all satellites launched are LEO satellites. Clearly, there is tremendous recent interest in
LEO satellite networks!

LEO satellite network architecture
Figure 7.49 shows the principal components of a LEO satellite network:
* LEO satellites. At the top of Figure 7.49, we see the network of orbiting
LEO satellites, often referred to as a “constellation” of satellites. Starlink
reports more than 6,750 satellites in its constellation; in early 2025 there
are approximately 650 LEO satellites in the Oneweb constellation.
Because of their relatively low altitude, LEO satellites are not geostationary but instead are in constant motion with respect to the earth below,
travelling at 27,000 km/hr with respect to the ground [Bhattacherjee
2019]. As we’ll see below, these highly mobile network elements take the
whole topic of “network mobility” in a whole new direction!
* Satellite links. The coverage area of a satellite’s wireless transmitter/receiver
on the earth below is known as its footprint. In the downlink direction, a
satellite’s transmissions are broadcast in nature, as they are received by all
stations within the footprint. In the uplink direction, transmissions from the
various ground stations within the satellite’s footprint are unicast to the
satellite—a classical multiple access channel! The footprint of a typical LEO
satellite is 15 miles in diameter. A ground station will remain in the footprint of a satellite link’s beam for only 10 minutes or so, until the satellite’s
motion takes it out of view of the ground station. You can view the current
and changing Starlink and Oneweb constellation footprints (including
details for where you are on earth) at https://satellitemap.space/. Satellites
may also be directly connected to each other using optical inter-satellite

Figure 7.49

Components of a LEO
satellite network



links (ISLs), although this type of infrastructure link is not yet widely used
in practice.
* Ground stations. On or near the Earth’s surface are the ground stations that
transmit and receive datagrams over the satellite link. These ground stations
may be connected only to the satellite or may be connected both to the satellite and to the terrestrial Internet, in which case the ground station serves as a
gateway between the satellite network and the terrestrial Internet. LEO
ground stations often have small dish or flat panel antennas for satellite communication. However, a low-bandwidth SOS emergency texting service via
satellite is currently available for some (Apple) cellphones, and the provision
of additional 5G-like data services via LEO satellites are under study.

Mobility
With LEO satellites whizzing through the air at 27,000 km/hr and with
ground stations that may themselves be mobile on trucks, boats or airplanes,
LEOS constellations are wireless networks with extreme mobility! In contrast to
WiFi and 5G networks, however, it is the LEO network infrastructure (satellites), not the user device, that is the primary source of “mobility.” Since a
ground station remains attached to a satellite for only 10 minutes or so,
ground-station handover between orbiting satellites is a common and important occurrence, as one satellite moves out-of-range of the ground station,
while other satellites remain in-range. Recent measurements suggest that satellite handover is much less well-developed than 5G handover, with suspected
packet loss occurring during handovers [Kassem 2022]. Also, unlike 5G networks, there is no LEO satellite network standardization body that is similar in
spirit to the 3GPP in the cellular network world. As a result, satellite network
implementations remain proprietary.

A link in the air or a network in the air?
Figure 7.50 shows two possible approaches towards building satellite networks. The “bent pipe” architecture (Figure 7.50(a)) treats each satellite as a
link, with ground stations at each end of each link. An end-to-end path thus

Figure 7.50 Links in the sky or a network in the sky?


Wireless and Mobile Networks

consists of a series of single-hop satellite links, with a packet returning to
ground from the sky after each hop. Figure 7.50(b) shows the network-in-thesky approach, where inter-satellite links (ISLs) directly connect satellites, and a
packet may cross multiple hops among satellites before returning to ground.
Note that because satellites are non-stationary with respect to the ground and
with respect to each other, the ISL links in the network-in-the-sky are dynamically changing, making routing in LEOS networks a challenging problem. For
a recent introduction and overview of LEOS networks, see [Bhattacherjee 2019;
Al Homssi 2022; Kassem 2022].


### 7.6.3 Internet of Things (IoT) networks

The Internet of Things (IoT) [Manyika 2013] is about connecting devices, which
are often small and energy-constrained, with computation to sense, monitor,
report, and control phenomena in the physical world. Myriad IoT applications
in multiple areas abound, including but not limited to (i) manufacturing,
where physical characteristics such as pressure, vibration, temperature,
humidity, switch settings, and gauge levels are monitored, often with actions
then taken; (ii) logistics and supply chains, where asset and transport conditions are monitored and tracked; (iii) agriculture and the environment, where
rainfall, temperature, wind, humidity, animal tracking/health, and soil conditions are monitored and resources deployed as a result; (iv) smart cities, where
the sound, air, water, weather, lighting, traffic, and crowds, are measured and
transportation systems and services are monitored, with services activated and
deactivated in response; and (v) personal health monitoring and care. Some
have characterized IoT’s impact as being so pervasive and so profound as to
constitute a fourth industrial revolution, or “Industry 4.0” [Schwab 2016]. With
more than three times as many connected IoT devices deployed than PCs, laptops, tablets, and cellphones combined by the end of this decade [Statista IoT
2025], IoT is on pace to soon become a $300 billion market [Schwab 2016].
With so many different applications with so many different requirements,
and such a large potential market, it’s not surprising that there are many different competing technologies angling to provide networked services for IoT. Our
modest goal here is to provide an overview of these IoT wireless network technologies, several of which we have already learned about earlier in this chapter,
and to provide pointers for additional reading.
Figure 7.51, adapted from [Ahmad 2019], provides a three-faceted characterization of IoT networking technologies, illustrating the extent to which a
particular technology emphasizes area coverage, energy consumption, and/or
high data rates. Each of the technologies shown in Figure 7.51 emphasizes two
of these three characteristics, but none emphasize all three. This suggests that
rather than a winner-take-all outcome in IoT networking, we’re likely to see
different solutions adopted in practice, depending on the context.
* Emphasizing low energy and low data rate. IEEE 802.11ah, Bluetooth Low
Energy (BLE) and Zigbee are three wireless IoT technologies designed for
short-range coverage. IEEE 802.11ah is a “flavor” of WiFi, inheriting much
of WiFi’s architecture, including the BSS structure, the notion of channels,




Figure 7.51

IoT communication
technologies and their
emphases

and a stripped-down 802.11 frame format. IEEE 802.11ah provides data
rates of 100’s kbps to ~5 – 10 Mbps. Operating in the 900 MHz unlicensed band and with relays, these networks can span up to a kilometer in
practice. Bluetooth Low Energy (BLE) [Sauter 2021] is a significant expansion of the original Bluetooth standard to support IoT devices. We learned
about Bluetooth networks earlier in Section 7.6.1 and in Section 7.3.6 we
learned that BLE (like LoRa Class A, and 4G LTE Narrowband IoT) supports device-initiated wake-and-send transmission by the IoT device.
Introduced in the late 1990s, Zigbee [Gomez 2010] is one of the earliest IoT
networking technologies. It is built on the physical and MAC layers of the
IEEE 802.15.4 standard for low-rate wireless personal area networks.
* Emphasizing low energy and wider area coverage. LoRaWAN [Jouhari 2023]
(Long Range Wide Area Network) is standardized by International
­Telecommunication Union (ITU). We covered LoRaWAN’s energy saving
mechanisms for Class A devices [Semtech 2019a] in Section 7.3.6; Class B
device operation is covered in [Semtech 2019b]. LoRaWAN is a networkwide (as opposed to a link-layer) standard, with servers, gateways, and
IoT devices operating with data rate ranging from 0.3 kbit/s to 50 kbit/s
per channel in the 902 − 928 MHz unlicensed band. LoRaWAN networks span wide areas using a star-of-star network topology, with a
LoRaWAN gateway serving as a coordinating central node in each edgestar network. 4G Narrowband Internet of Things (NB-IoT) [Vaezi 2022] is
a 3GPP 4G standard that naturally contains many of the architectural features of the 4G RAN, including base stations, user devices, downlink
OFDM and uplink single-carrier FDMA—all of which we studied earlier
in ­S ection 7.3. NB-IoT also supports device-initiated wake-and-send
transmission by the IoT device that we encountered in Section 7.6.1. With
200 kHz channel bandwidths, LTE NB-IoT data rates are limited to
approximately 250 Kbps.
* Emphasizing wider area coverage and higher data rates. Long Term Evolution for
Machines (LTE-M) is a second, more fully functional 3GPP LTE standard
aimed at IoT applications. It supports device mobility among base stations
and has channel bandwidths that are 5 times larger than LTE NB-IoT. The
International Telecommunication Union (ITU), which works with the 3GPP
to set the vision for mobile cellular network standards, notes that for 5G,


Wireless and Mobile Networks

while “initial standards and launches have mostly focused on enhanced
Mobile Broadband, 5G is expected to increasingly enable new business
models and countless new use cases, in particular those of massive Machine
Type Communications and Ultra-reliable and Low Latency Communications.” These two latter broad categories of communication applications
include IoT. Thus, while 5G standards and deployments have focused primarily on Mobile Broadband to date, work on supporting IoT within the 5G
standard is well underway [Vaezi 2022; 3GPP TS 38.300 2024].


## 7.7 Summary

Wireless mobile networks first revolutionized telephony and are having an
increasingly profound impact in the world of computer networks as well.
With already more than five times as many Internet-connected wireless subscribers as wired subscribers, and with their anytime, anywhere, untethered
access into the global network infrastructure, wireless networks are providing
nearly ubiquitous wireless Internet connectivity and have enabled an exciting
new set of mobile, location-dependent services. Given the importance of wireless and mobile networks, we’ve devoted an entire chapter (this chapter) to
this topic.
We began this chapter with an introduction to wireless and mobile networks and then embarked on a bottom-up study of their principles and practice.
In spite of our strong preference for a top-down pedagogical approach, we felt
that an early mastery of the underlying radio channel was needed to understand just about every other aspect of wireless networking. Thus, we began
our in-depth study of wireless and mobile networks in Section 7.2 with a study
of the unique characteristics of a radio channel, and then learned how bits are
coded into symbols and then waveforms that are modulated, transmitted, and
received over that channel. In Section 7.3 we then turned our attention to wireless access networks, covering techniques for sharing the radio channel,
network discovery and device attachment, frame transmission scheduling, and
energy conservation. Throughout Section 7.3, we used WiFi and 5G networks to
illustrate how the principles we’ve learned are put into practice. In Section 7.4
we then covered the mobile Core network, a key architectural component of
cellular networks that provides support for global identity, mobility, and service subscription—services not typically found in the traditional wired
Internet. Mobility is such a unique feature of wireless networks, that we
devoted an entire section (7.5) to the topic. While we have focused primarily
on 5G and WiFi networks throughout this chapter, we briefly covered three
other important wireless network architectures—Bluetooth, satellite and IoT
wireless networks—in Section 7.6.
Although we’ve devoted an entire chapter to the study of wireless and
mobile networks, an entire book (or more!) would be required to fully explore
this exciting and rapidly expanding field. A full course could be taught on this
topic alone—and such a course is indeed taught by one of the co-authors
[Kurose 2025]. We encourage you to delve more deeply into this field by consulting the many resources noted in this chapter.




Homework Problems and Questions
Section 7.1
R1. Answer the following review questions
about the wireless access network versus the
wireless core network. Which of these two
contains the user ’s device? Which one of
these two is attached to the larger Internet?
Which of these contains the radio link(s) that
connect the user devices into the wireless
network?
R2. What does it mean for a wireless network to
be operating in “infrastructure mode”? If the
network is not in infrastructure mode, what
mode of operation is it in, and what is the difference between that mode of operation and
infrastructure mode?

Section 7.2
R3. Describe what is meant by an electromagnetic
wave’s amplitude, frequency, and phase.
Which of these three characteristics would
you use to determine the wavelength?
R4. Is a radio signal’s bandwidth the same as the
number of bits per second that are transmitted over the radio channel?
R5. List two contributors to noise in a radio channel between a sender and receiver.
R6. What are the differences between path loss
and multipath effects in radio signal transmission and reception?
R7. What are two causes of the “hidden terminal”
problem?
R8. What is the “coherence time” for a transmitted signal that is received at a receiver?
R9. What are the differences between MIMO spatial diversity and MIMO spatial multiplexing?
R10. What is meant by “beamforming”?
R11. What is the difference between the licensed
and unlicensed spectrum? Does 5G operate
primarily in the licensed or unlicensed spectrum? What about WiFi?

R12. What is the difference between coding and
modulation in the physical layer?
R13. What are three characteristics of a radio signal
that can be modulated to code information
into the radio signal? (Hint: see question R3.)
R14. What characteristics of a radio signal are
modulated in Quadrature Amplitude Modulation (QAM)?
R15. As a mobile node gets farther and farther
away from a base station, what are two
actions that a base station could take to ensure
that the loss probability of a transmitted frame
does not increase?

Section 7.3
R16. What are the commonalities and differences
between FDM, OFDM, and OFDMA?
R17. In CSMA/CA, does a station wanting to
transmit a frame perform carrier sensing?
Does it perform collision detection?
R18. What are the roles/purposes of the Request to
Send (RTS) and Clear to Send (CTS) messages
in CSMA/CA?
R19. Suppose the IEEE 802.11 RTS and CTS frames
were as long as the standard DATA and ACK
frames. Would there be any advantage to using
the CTS and RTS frames? Why or why not?
R20. Why are acknowledgments used in 802.11 but
not in wired Ethernet?
R21. What is meant by a “dense deployment” WiFi
network? How does it differ from say a WiFi
deployment in an Internet café?
R22. What is the relationship between a Resource
Element and a Resource Block in the 5G RAN?
R23. Order the following in 5G structures in terms
of their bandwidth (from widest to narrowest): channel, band, and subchannel.
R24. Briefly (in a sentence each), describe the role
of the Radio Resource Control (RRC), Service
Data Adaptation Protocol (SDAP), Packet
Data Convergence Protocol (PDCP), and
Radio Link Control (RLC) in a 5G RAN.


Wireless and Mobile Networks


R25. What is meant by the term “disaggregation”
in the context of a 5G RAN?

R34. What is the role of the User Plane Function in
the 5G Core?

R26. Describe the role of a “beacon” message in
network discovery.

R35. What are the two key functions performed by
the Access, Mobility Management Function
(AMF) in the 5G Core?

R27. What is the difference between active and
passive scanning for beacons?
R28. What is the purpose of the 802.11 association
request frame?
R29. Which of the following MAC frame scheduling disciplines consider transmitter-toreceiver channel characteristics into account
when making a scheduling decision: Round
Robin (RR), Maximum Throughput (MT),
Blind Equal Throughput (BET), and Proportional Fairness (PF)?
R30. Which of the following MAC frame scheduling disciplines take fairness among users into
account when making a scheduling decision:
Round Robin (RR), Maximum Throughput
(MT), Blind Equal Throughput (BET), and
Proportional Fairness (PF)?
R31. In coordinated sleep/wake approaches to
device energy conservation, what are the network elements whose actions are being
coordinated?

Section 7.4
R32. Control plane vs data plane. Which of the following statements best describes the difference
between the control plane and the data plane?
a. The control plane and data plane perform
the same functions but in different network
layers.
b. The control plane generates data, while the
data plane routes data.
c. The data plane is responsible for the forwarding of packets containing user data,
while the control plane is responsible for
managing (configuring, monitoring) the
network infrastructure that performs this
forwarding.
d. The control plane is hardware-based,
whereas the data plane is software-based.
R33. What is meant when we say that the 5G Core
adopts a “service-based architecture”?

R36. Why are tunnels used in the user plane in the
5G Core?
R37. What are five pieces of information stored on
a cellular SIM card?
R38. True or false: the decision of whether to admit
an arriving device to a 5G network is always
made exclusively within the network that the
arriving device is joining.
R39. Softwarization. What is the primary goal of
network softwarization?
a. To reduce the physical size of network
hardware
b. To increase network flexibility and programmability through software solutions
c. To replace all network hardware with
software
d. To enhance the physical security of network devices

Section 7.5
R40. What are two reasons that a mobile user
device may be handed over from one base station to another?
R41. True or false: While 5G performs handover
from one base station to another, WiFi does
not have such a capability for performing
handover from one base station to another.
R42. In 5G, is device handover initiated by the user
device, the source base station, or the target
base station?
R43. True or false: During 5G handover, user-plane
datagrams destined for a device will always
pass through exactly one base station.
R44. True or false: During and after 5G handover,
the endpoints of the device’s tunnel between
the RAN and Core do not change.

Section 7.6
R45. Why do you think the designers of Bluetooth
chose to use frequency-hopping from one


time slot to the next, rather than fixed frequency channels (e.g., as done in WiFi).

relative position of the satellite and ground
station change?

R46. What is the role of the Logical Link Control
and Adaptation (L2CAP) layer in Bluetooth?

R49. What is meant by a “bent-pipe” end-to-end
path through a LEO satellite network?

R47. True or false: In Bluetooth, communication
occurs only between the central and peripheral nodes; there is no direct peripheral-toperipheral communication.

R50. Consider the three broad classes of IoT network:
short-range low power (WiFi, Bluetooth Low
Energy), wide-area low power (LoRaWAN),
and traditional cellular (LTE-M). Which of these
three classes tends to have the lowest data rates?
Which of these tends to have the smallest geographical footprint? Which of these tends to
have the highest energy consumption?

R48. Consider GEO versus LEO satellite networks.
What is the difference in ground-satelliteground round trip times in these two networks? In which of these networks does the

Problems
P1. Wireless technology speeds. Consider the following four wireless technologies that we studied in this chapter: WiFi, 5G, Bluetooth, and LEO
satellites. Rank order each of these technologies in terms of the link
speed that an individual user is able to achieve using this wireless technology. In the case that there are multiple speeds achievable within a
technology family, use the highest speed possible.
P2. Wireless technology distances. Consider the following four wireless
technologies that we studied in this chapter: WiFi, 5G, Bluetooth, and
LEO satellites. Rank order each of these technologies in terms of the
physical distance over which communication is possible using this wireless technology. In the case that there are multiple distances possible
within a technology family, use the longest distance possible.
P3. Multipath delays. In this question, we’ll consider the idealized multipath scenario shown below, and the line-of-sight (LOS) path and a single reflective path.

Consider the following parameters:
* h = 10 m
* d = 5000 m


Wireless and Mobile Networks

* c = 3 × 10 m/sec (speed of light)
* f = 5 GHz (rate at which pulses are being transmitted)
Compute the delay between when a pulse is sent from the antenna on
the left to when it is received at the device on the right (assuming speed
of light propagation delays), along the line-of-sight path, and along the
single reflective path.
a. What is the time from when a pulse is sent from the tower on the
reflective path, until it is received at the device?
b. Will pulse i on the reflective path arrive before or after pulse i + 1 on
the LOS path? Explain.
P4. Path loss: who can “hear” who? In this question, we’ll consider which
nodes can “hear” other nodes that are transmitting, as a function of distance and frequency. Consider the 4-node network below, where the
nodes are separated by the following distances:

* d AB = d BA = d BC = d CB = 1
* d AC = d CA = 1.41
* d AD = d DA = d CD = d DC = 2.5
* d BD = d DB = 3.5
* f = 1 GHz
Recall that the path loss of a radio signal between two nodes varies (in
free space) as ~( fd ) 2 Suppose that the transmitting power (the same at
all nodes) is such that at frequency f , there is enough received power for
a receiver to “hear” a transmitter as long as the distance d between the
transmitter and the receiver is less than 3 units of distance. For this configuration, which nodes can “hear” the transmissions of which other
nodes?
P5. CSMA/CA. In step 4 of the CSMA/CA protocol, a station that successfully transmits a frame begins the CSMA/CA protocol for a second
frame at step 2, rather than at step 3. What rationale might the designers
of CSMA/CA have had in mind by having such a station not transmit
the second frame immediately (if the channel is sensed idle)?
P6. RTS/CTS in WiFi. Suppose an 802.11b station is configured to always
reserve the channel with the RTS/CTS sequence. Suppose this station
suddenly wants to transmit a 1,500 bytes of data, and all other stations



are idle at this time. As a function of SIFS and DIFS, and ignoring propagation delay and assuming no bit errors, calculate the time required to
transmit the frame and receive the acknowledgment.
P7. Use of ACKs in WiFi. Why are link-layer ACKs used in WiFi (802.11)
networks?
a. Hearing a receiver ACK, all other stations will stop transmitting. This
reduces collisions.
b. Because of the hidden terminal problem, a node that is transmitting
and hears no collisions still doesn’t know if there was a collision at
the receiver.
c. Wireless links are noisier than wired links, and so bit level errors are
more likely to occur, making link-layer error recovery more valuable
than in less-noisy wired links.
d. The sender can use the differences in the signal strength in an ACK
to infer whether the receiver is moving towards, or away from, the
sender.
P8. Multi-hop end-end wireless transmissions. Consider the scenario
shown in the figure below, in which there are four wireless nodes, A, B, C,
and D. The radio coverage of the four nodes is shown via the shaded
ovals; all nodes share the same frequency. When A transmits, it can only
be heard/received by B; when B transmits, both A and C can hear/
receive from B; when C transmits, both B and D can hear/receive from C;
when D transmits, only C can hear/receive from D.

Suppose now that each node has an infinite supply of messages that it
wants to send to each of the other nodes. If a message’s destination is not
an immediate neighbor, then the message must be relayed. For example,
if A wants to send to D, a message from A must first be sent to B, which
then sends the message to C, which then sends the message to D. Time is
slotted, with a message transmission time taking exactly one time slot,
e.g., as in slotted Aloha. During a slot, a node can do one of the following:
(i) send a message, (ii) receive a message (if exactly one message is being
sent to it), and (iii) remain silent. As always, if a node hears two or more
simultaneous transmissions, a collision occurs and none of the transmitted messages are received successfully. You can assume here that there
are no bit-level errors, and thus if exactly one message is sent, it will be
received correctly by those within the transmission radius of the sender.
a. Suppose now that an omniscient controller (i.e., a controller that
knows the state of every node in the network) can command each


Wireless and Mobile Networks

node to do whatever it (the omniscient controller) wishes, that is, to
send a message, to receive a message, or to remain silent. Given this
omniscient controller, what is the maximum rate at which a data message can be transferred from C to A, given that there are no other messages between any other source/destination pairs?
b. Suppose now that A sends messages to B, and D sends messages to C.
What is the combined maximum rate at which data messages can flow
from A to B and from D to C?
c. Suppose now that A sends messages to B, and C sends messages to D.
What is the combined maximum rate at which data messages can flow
from A to B and from C to D?
d. Suppose now that the wireless links are replaced by wired links.
Repeat questions (a) through (c) again in this wired scenario.
e. Now suppose we are again in the wireless scenario, and that for
every data message sent from source to destination, the destination
will send and ACK message back to the source (e.g., as in TCP). Also
suppose that each ACK message takes up one slot. Repeat questions
(a)–(c) for this scenario.
P9. Bluetooth. Describe the format of the Bluetooth frame. You will have to
do some reading outside of the text to find this information. Is there anything in the frame format that inherently limits the number of nodes in a
network to eight active nodes? Explain.
P10. Power savings in WiFi. Recall that in order to implement power savings
(PS) in WiFi, WiFi beacons contain power saving information in a traffic
indication map (TIM). Which of the following statements are true of
power savings in WiFi.
a. Powers savings in WiFi is controlled by the AP, which instructs the
client to sleep when there are no messages to be sent from the AP to
the device.
b. Power savings in WiFi is controlled primarily by the device, which
decides when to go into doze (i.e., sleep) state.
c. Power savings in WiFi is controlled exclusively by the device, and there
is no signaling/control message related to power control exchanged
between the device and the AP.
d. The WiFi AP lets the device know when it has buffered datagrams to
send to the device through the use of a TIM (Traffic Indication Map)
field in AP beacon frames.
e. Similar to 4G 5G, the AP will take down the device-specific tunnel
between itself and the router when the device goes to sleep.
f. The client device sends a PS poll frame to the AP to ask the AP to
send a frame that the AP may have buffered that is destined to the
device.
g. The AP sends a PS poll frame to the client device to ask the device if it
has a frame to send.



P11. Connecting at the 4G 5G Edge. Indicate the order in which each of the
following steps is taken by a user device to connect to the base station in
a 4G 5G network.
a. Locate the reference signals that are embedded in every 7th slot on
every third subcarrier in the OFDM subcarrier-frequency x time space.
b. Locate the channel’s primary synchronization signal (PSS) and secondary synchronization signal (SSS), which are transmitted every 5 ms
in pre-defined symbol locations in the OFDM subcarrier-frequency
x time space.
c. Locate/receive the Master Information Block (MIB), which is broadcast every 40 ms by the base station, and gives (among other pieces of
information) the channel’s bandwidth.
d. Locate/receive a System Information Block 1 (SIB1) message, which
is broadcast every 80 ms by the base station and gives (among other
pieces of information) the mobile country code (MCC), the mobile network code (MNC) for the carrier operating this channel, and whether
the cell is open/closed for a device to join.
e. Locate/receive the cell identifier signal, which provides the cell’s
name, the mobile country code (MCC), the mobile network code
(MNC) for the carrier operating this cell, and the cryptographic keys
needed to perform user device authentication.
P12. RAN Scheduling. In this question, we’ll consider the problem of RAN
scheduling in a 4G 5G base station, as illustrated in the figure below.
Suppose that there are 4 user devices ( UE 1 , . . . , UE 4 ), each with a
queue of bits to be sent from the base station to that device, as shown in
the top part of the figure below. In this problem, we’ll consider bits to be
sent to the device rather than link-layer frames. Suppose that at this
scheduling instant there are more than enough bits in each device queue
to fill all 8 resource blocks to be scheduled at this scheduling time t
(i.e., there is no shortage of bits to be sent!).
The table below shows the Channel Quality Indicator (CQI) values
reported back from the devices, the number of bits encoded in a symbol
at that CQI level, and the average throughput received per device up
until time t. As in 4G OFDMA, each Resource Block (RB) contains 84 symbols; all symbols in an RB must be destined for the same device, but different RBs may be allocated to (destined to) different devices.

Device

Reported
CQI

# bits / transmitted
symbol at this CQI

Past average throughput
achieved by device until
time t-1

UE 1, UE 2



4,800 bits/scheduling time unit

UE 3



4,100 bits/scheduling time unit

UE 4



6,000 bits/scheduling time unit


Wireless and Mobile Networks

a. Under Round Robin (RR) scheduling, how many RBs will be assigned
to UE 1 at this scheduling instant, t?
b. Under RR scheduling, how many RBs will be assigned to UE 3 at this
scheduling instant, t?
c. How many bits will be transmitted to UE 1 in a single RB under RR
scheduling at this time instant, t? (Hint: Recall that each RB contains
84 symbols, but that the number of bits associated with each symbol
will depend on the reported CQI.)
d. Under Maximum Throughput (MT) scheduling, how many RBs will
be assigned to UE 3 at this scheduling instant, t?
e. Under MT scheduling, how many RBs will be assigned to UE 4 at this
scheduling instant, t?
f. How many bits will be transmitted to UE 4 in a single RB under MT
scheduling at this time instant, t?
g. Under Blind Equal Throughput (BET) scheduling, how many RBs will
be assigned to UE 1 at this scheduling instant, t?
h. Under Blind Equal Throughput (BET) scheduling, how many RBs will
be assigned to UE 3 at this scheduling instant, t?
i. Under Blind Equal Throughput (BET) scheduling, how many RBs will
be assigned to UE 4 at this scheduling instant, t?
j. Under Proportional Fairness (PF) scheduling, how many RBs will be
assigned to UE 1 at this scheduling instant, t?
k. Under PF scheduling, how many RBs will be assigned to UE 3 at this
scheduling instant, t?
l. Under Proportional Fairness (PF) scheduling, how many RBs will be
assigned to UE 4 at this scheduling instant, t?
P13. Mobility duality: 4G 5G and LEOS satellite constellations. Let’s consider the similarities and differences between mobility in 4G 5G



networks and mobility in LEOS satellite constellations, recalling that (i)
in 4 5G, the base station is fixed, but users are mobile (ii) in LEOS networks, the infrastructure (LEO satellites) is mobile, but users are (relatively) fixed.
Which of the following statements are TRUE about these similarities/
differences:
a. Mobility (e.g., time of association, next point of association) is more
predictable in 4G 5G networks than in LEOS networks.
b. The radio channel is more variable over time (e.g., there is more multipath) in 4G 5G.
c. In both 4G 5G networks and LEOS networks, the infrastructure controls use of the transmission slots in both downstream (infrastructureto-user) and upstream (user-to-infrastructure) directions.
d. In 4G 5G networks, even though there is mobility, a user’s point of
attachment with the network may not change over the period of an hour.
e. In LEOS networks, even though there is mobility, a user’s point of
attachment with the network may not change over the period of an hour.

Programming Assignment: Implementing a 4G/5G
RAN scheduler
In this lab, you’ll program a downlink RAN scheduler that will implement the Maximum Throughput
(MT), Blind Equal Throughput (BET), and Proportional Fairness (PF) scheduling. You’ll program this
in a simulated environment that will, at each scheduling instant, provide your scheduler with per-UE
CQI information, and the per-UE number of newly
arriving bits for transmission. You will be provided

with an already implemented Round Robin scheduler for this environment, so you’ll have an example that you can generalize from. The full lab
assignment, as well as code you will need to compile with your own code, are available at this book’s
publisher’s Web site: www.pearsonhighered.com/­
cs-resource and mirrored on the instructors’ Web
site: http://gaia.cs.umass.edu/kurose_ross.

Wireshark Labs: WiFi and 4G/5G
At the Web site for this textbook, www.pearsonhighered.com/cs-resources, also mirrored on the
instructors’ Web site, http://gaia.cs.umass.edu/
kurose_ross, you’ll find a Wireshark lab for this
chapter that captures and studies the 802.11 frames

exchanged between a wireless laptop and an access
point. There is also a new Wireshark Lab that studies the interaction between the user device and the
base station in a 4G 5G network and a second 5G
Wireshark lab that studies mobility.


Wireless and Mobile Networks

AN INTERVIEW WITH...
Deborah Estrin
Deborah Estrin is a Professor of Computer Science and Associate Dean for Impact
at Cornell Tech in New York City and a Professor of Population Health at Weill
Cornell Medical College. She received her Ph.D. (1985) in Computer Science from
M.I.T. and her B.S. (1980) from UC Berkeley. Estrin’s early research focused on the
design of network protocols, including multicast and inter-domain routing. In 2002
Estrin founded the NSF-funded Science and Technology Center at UCLA, Center
for Embedded Networked Sensing (CENS http://cens.ucla.edu.). CENS launched
new areas of multi-disciplinary computer systems research from sensor networks for environmental monitoring, to participatory sensing and mobile health.
As described in her 2013 TEDMED talk, she explores how individuals can benefit
from the pervasive data byproducts of digital and IoT interactions for health management. Professor Estrin is an elected member of the American Academy of Arts
and Sciences (2007), the National Academy of Engineering (2009), and the National
Academy of Medicine (2019). She is a Fellow of the IEEE, ACM, and AAAS. She was
awarded the first ACM-W Athena Lecturer (2006), the Anita Borg Institute’s Women
of Vision Award for Innovation (2007), The IEEE Internet Award (2017), a MacArthur
Fellowship (2018), and IEEE John von Neumann Medal (2022). She received honorary doctorates from EPFL (2008), Uppsala (2011), and Concordia (2023) Universities.

Please describe a few of the most exciting
projects you have worked on during your
career. What were the biggest challenges?
In the mid-90s at USC and ISI, I had the great fortune to work with the likes of Steve
Deering, Mark Handley, and Van Jacobson on the design of multicast routing protocols (in particular, PIM). I tried to carry many of the architectural design lessons
from multicast into the design of ecological monitoring arrays, where for the first
time I really began to take applications and multidisciplinary research seriously.
The need for jointly innovating in the social and technological space is what interests me so much about my latest area of research, mobile health. The challenges in
multicast routing, environmental sensing and mobile health are as diverse as the
problem domains, but what they have in common is the need to keep our eyes open
to whether we have the problem definition right as we iterate between design and
deployment, prototype and pilot. None of these are problems that could be solved
solely analytically, or with simulation or even in constructed laboratory experiments. They challenged our ability to retain clean architectures in the presence of
messy problems and contexts, and they required extensive collaboration.

What changes and innovations do you see
happening in wireless networks and
mobility in the future?
In a prior edition of this interview I said that I have never put much faith into predicting the future, but I did go on to speculate that we might see the end of feature

Courtesy of Deborah Estrin



phones (i.e., those that are not programmable and are used only for voice and text
messaging) as smart phones become more and more powerful and the primary
point of Internet access for many—and now not so many years later that is clearly
the case. I also predicted that we would see the continued proliferation of embedded SIMs by which all sorts of devices have the ability to communicate via the cellular network at low data rates. While that has occurred, we see many devices and
“Internet of Things” that use embedded WiFi and other lower power, shorter range,
forms of connectivity to local hubs. I did not anticipate at that time the emergence
of a large consumer wearables market or interactive voice agents like Siri and Alexa,
let alone LLM-based agents. By the time the next edition is published I expect broad
proliferation of personal health applications in the form of digital therapeutics,
powered by multimodal agents.

Where do you see the future of networking
and the Internet?
Data, ML, and Generative AI have all emerged as the dominant forces in Computer
Systems and Network design generally. Low latency needs of real time applications
continue to motivate powerful edge devices. In addition, managing energy consumption and data privacy motivate novel architectures that will not necessarily
emerge from commercial market forces alone. At the same time, information ecosystem has become far more monolithic than in earlier decades. This is a challenge
for networking, the Internet, and frankly our society.

What people inspired you professionally?
There are three people who come to mind. First, Dave Clark, the secret sauce and
under- sung hero of the Internet community. I was lucky to be around in the early
days to see him act as the “organizing principle” of the IAB and Internet governance; the priest of rough consensus and running code. Second, Scott Shenker, for
his intellectual brilliance, integrity, and persistence. I strive for, but rarely attain,
his clarity in defining problems and solutions. He is always the first person I email
for advice on matters large and small. Third, my sister Judy Estrin, who had the
creativity and commitment to spend the first half of her career bringing ideas and
concepts to market; and now has the courage to study, write, and advise on how to
rebuild it to support a healthier democracy.

What are your recommendations for
students who want careers in computer
science and networking?
First, build a strong foundation in your academic work, balanced with any and
every real- world work experience you can get. As you look for a working environment, seek opportunities in problem areas you really care about and with smart
teams that you can learn from and work with to build things that matter.



