# Chương 5: The Network Layer - Control Plane
> **Giáo trình:** Computer Networking: A Top-Down Approach (9th Edition, 2026)  
> **Tác giả:** Jim Kurose, Keith Ross — Pearson Education  
> **Số trang bản gốc:** PDF trang 353 – 412 (Độ dài: 60 trang)  

---

> [!NOTE] ỨNG DỤNG TRỰC TIẾP VÀO ĐỒ ÁN OPENGUARD KIDS
> **Mục tiêu học tập & Áp dụng thực tiễn:**  
> Mặt phẳng điều khiển mạng, SDN (Software-Defined Networking), giao thức ICMP (Ping chẩn đoán mạng), và cấu hình SNMP/YANG.

---

The Network Layer:
Control plane

In this chapter, we’ll complete our journey through the network layer by covering the control-plane of the network layer—the network-wide logic that controls
not only how a datagram is routed along an end-to-end path from the source
host to the destination host, but also how network-layer components and
services are configured and managed. In Section 5.2, we’ll cover traditional
routing algorithms for computing least cost paths in a graph; these algorithms
are the basis for two widely deployed Internet routing protocols: OSPF and
BGP, that we’ll cover in Sections 5.3 and 5.4, respectively. As we’ll see, OSPF is
a routing protocol that operates within a single ISP’s network. BGP is a routing protocol that serves to interconnect all of the networks in the Internet; BGP
is thus often referred to as the “glue” that holds the Internet together. Traditionally, control-plane routing protocols have been implemented together
with data-plane forwarding functions, monolithically, within a router. As we
learned in the introduction to Chapter 4, software-defined networking (SDN)



makes a clear separation between the data and control planes, implementing
control-plane functions in a separate “controller” service that is distinct, and
remote, from the forwarding components of the routers it controls. We’ll cover
SDN controllers in Section 5.5.
In Sections 5.6 and 5.7, we’ll cover some of the nuts and bolts of managing
an IP network: ICMP (the Internet Control Message Protocol) and SNMP (the
Simple Network Management Protocol).


## 5.1 Introduction

Let’s quickly set the context for our study of the network control plane by
recalling Figures 4.2 and 4.3. There, we saw that the forwarding table (in the
case of destination-based forwarding) and the flow table (in the case of generalized forwarding) were the principal elements that linked the network layer’s
data and control planes. We learned that these tables specify the local dataplane forwarding behavior of a router. We saw that in the case of generalized
forwarding, the actions taken could include not only forwarding a packet to a
router’s output port, but also dropping a packet, replicating a packet, and/or
rewriting layer 2, 3 or 4 packet-header fields.
In this chapter, we’ll study how those forwarding and flow tables are computed, maintained and installed. In our introduction to the network layer in
Section 4.1, we learned that there are two possible approaches for doing so.
* Per-router control. Figure 5.1 illustrates the case where a routing algorithm
runs in each and every router; both a forwarding and a routing function
are contained within each router. Each router has a routing component
that communicates with the routing components in other routers to compute the values for its forwarding table. This per-router control approach
has been used in the Internet for decades. The OSPF and BGP protocols

Figure 5.1 Per-router

control: Individual routing
algorithm components
interact in the control
plane


The Network Layer: Control plane


that we’ll study in Sections 5.3 and 5.4 are based on this per-router
approach to control.
* Logically centralized control. Figure 5.2 illustrates the case in which a logically centralized controller computes and distributes the forwarding
tables to be used by each and every router. As we saw in Sections 4.4
and 4.5, the generalized match-plus-action abstraction allows the router to
perform traditional IP forwarding as well as a rich set of other functions
(load sharing, firewalling, and NAT) that had been previously implemented in separate middleboxes.
The controller interacts with a control agent (CA) in each of the routers via
a well-defined protocol to configure and manage that router’s flow table. Typically, the CA has minimum functionality; its job is to communicate with the
controller, and to do as the controller commands. Unlike the routing algorithms in Figure 5.1, the CAs do not directly interact with each other nor do
they actively take part in computing the forwarding table. This is a key distinction between per-router control and logically centralized control.
By “logically centralized” control [Levin 2012] we mean that the routing
control service is accessed as if it were a single central service point, even
though the service is likely to be implemented via multiple servers for faulttolerance, and performance scalability reasons. As we will see in Section 5.5,
SDN adopts this notion of a logically centralized controller—an approach that
is finding increased use in production deployments. [Cisco Trends 2020] noted
that SDN has seen wide adoption across data centers (64%), WANs (58%), and
access networks (40%) in 2020. In Section 5.5, we’ll study Google’s ORION

Figure 5.2 Logically

centralized control: A
distinct, typically remote,
controller interacts with
local control agents (CAs)


SDN [Ferguson 2021], which Google uses to control the networks within its
data centers as well as the global WAN that interconnects these data centers.


## 5.2 Routing Algorithms

In this section, we’ll study routing algorithms, whose goal is to determine
good paths (equivalently, routes), from senders to receivers, through the network of routers. Typically, a “good” path is one that has the least cost. We’ll see
that in practice, however, real-world concerns such as policy issues (for example, a rule such as “router x, belonging to organization Y, should not forward
any packets originating from the network owned by organization Z ”) also
come into play. We note that whether the network control plane adopts a perrouter control approach or a logically centralized approach, there must always
be a well-defined sequence of routers that a packet will cross in traveling from
sending to receiving host. Thus, the routing algorithms that compute these
paths are of fundamental importance, and another candidate for our top-10 list
of fundamentally important networking concepts.
A graph is used to formulate routing problems. Recall that a graph
G = ( N , E ) is a set N of nodes and a collection E of edges, where each edge is a
pair of nodes from N . In the context of network-layer routing, the nodes in the
graph represent routers—the points at which packet-forwarding decisions are
made—and the edges connecting these nodes represent the physical links
between these routers. Such a graph abstraction of a computer network is
shown in Figure 5.3. When we study the BGP inter-domain routing protocol,
we’ll see that nodes represent networks, and the edge connecting two such
nodes represents direction connectivity (know as peering) between the two networks. To view some graphs representing real network maps, see CAIDA 2025;
NetworkingChannel Diot 2021]; for a discussion of how well different graphbased models model the Internet, see [Zegura 1997, Faloutsos 1999, Li 2004].
As shown in Figure 5.3, an edge also has a value representing its cost. Typically, an edge’s cost may reflect the physical length of the corresponding link
(for example, a transoceanic link might have a higher cost than a short-haul
terrestrial link), the link speed, or the monetary cost associated with a link. For
our purposes, we’ll simply take the edge costs as a given and won’t worry
about how they are determined. For any edge ( x , y ) in E, we denote c ( x , y ) as
the cost of the edge between nodes x and y. If the pair ( x , y ) does not belong

Figure 5.3 Abstract
graph model of a
computer network


The Network Layer: Control plane

to E, we set c ( x , y ) = ∞. Also, we’ll only consider undirected graphs
(i.e., graphs whose edges do not have a direction) in our discussion here, so
that edge ( x , y ) is the same as edge ( y , x ) and that c ( x , y ) = c ( y , x ); however, the algorithms we’ll study can be easily extended to the case of directed
links with a different cost in each direction. Also, a node y is said to be a neighbor of node x if ( x , y ) belongs to E.
Given that costs are assigned to the various edges in the graph abstraction,
a natural goal of a routing algorithm is to identify the least costly paths
between sources and destinations. To make this problem more precise, recall
that a path in a graph G = ( N , E ) is a sequence of nodes ( x 1 , x 2 , . . . , x p )
such that each of the pairs ( x 1 , x 2 ), ( x 2 , x 3 ) , . . . , ( x p −1 , x p ) are edges in E.
The cost of a path ( x 1 , x 2 , . . . , x p ) is simply the sum of all the edge costs
along the path, that is, c ( x 1 , x 2 ) + c ( x 2 , x 3 ) + ⋅ ⋅ ⋅ + c ( x p −1 , x p ). Given any
two nodes x and y, there are typically many paths between the two nodes,
with each path having a cost. One or more of these paths is a least-cost path.
The least-cost problem is therefore clear: Find a path between the source and
destination that has least cost. In Figure 5.3, for example, the least-cost path
between source node u and destination node w is ( u, x , y , w ) with a path cost
of 3. Note that if all edges in the graph have the same cost, the least-cost path is
also the shortest path (that is, the path with the smallest number of links
between the source and the destination).
As a simple exercise, try finding the least-cost path from node u to z in
­Figure 5.3 and reflect for a moment on how you calculated that path. If you are
like most people, you found the path from u to z by examining Figure 5.3, tracing a few routes from u to z, and somehow convincing yourself that the path
you had chosen had the least cost among all possible paths. (Did you check all
of the 17 possible paths between u and z? Probably not!) Such a calculation is
an example of a centralized routing algorithm —the routing algorithm was run
in one location, your brain, with complete information about the network.
Broadly, one way in which we can classify routing algorithms is according to
whether they are centralized or decentralized.
* A centralized routing algorithm computes the least-cost path between a
source and destination using complete, global knowledge about the network. That is, the algorithm takes the connectivity between all nodes and
all link costs as inputs. This then requires that the algorithm somehow
obtain this information before actually performing the calculation. The
calculation itself can be run at one site (e.g., a logically centralized controller as in Figure 5.2) or could be replicated in the routing component of
each and every router (e.g., as in Figure 5.1). The key distinguishing feature here, however, is that the algorithm has complete information about
connectivity and link costs. Algorithms with global state information are
often referred to as link-state (LS) algorithms, since the algorithm must
be aware of the cost of each link in the network. We’ll study LS algorithms
in Section 5.2.1.
* In a decentralized routing algorithm, the calculation of the least-cost path
is carried out in an iterative, distributed manner by the routers. No node
has complete information about the costs of all network links. Instead,



each node begins with only the knowledge of the costs of its own directly
attached links. Then, through an iterative process of calculation and
exchange of information with its neighboring nodes, a node gradually calculates the least-cost path to a destination or set of destinations. The
decentralized routing algorithm we’ll study below in Section 5.2.2 is called
a distance-vector (DV) algorithm, because each node maintains a vector of
estimates of the costs (distances) to all other nodes in the network. Such
decentralized algorithms, with interactive message exchange between
neighboring routers is perhaps more naturally suited to control planes
where the routers interact directly with each other, as in Figure 5.1.
A second broad way to classify routing algorithms is according to whether
they are static or dynamic. In static routing algorithms, routes change very
slowly over time, often as a result of human intervention (for example, a
human manually editing a link costs). Dynamic routing algorithms change
the routing paths as the network traffic loads or topology change. A dynamic
algorithm can be run either periodically or in direct response to topology or
link cost changes. While dynamic algorithms are more responsive to network
changes, they are also more susceptible to problems such as routing loops and
route oscillation.
A third way to classify routing algorithms is according to whether they are
load-sensitive or load-insensitive. In a load-sensitive algorithm, link costs vary
dynamically to reflect the current level of congestion in the underlying link. If a
high cost is associated with a link that is currently congested, a routing algorithm will tend to choose routes around such a congested link. While early
ARPAnet routing algorithms were load-sensitive [McQuillan 1980], a number
of difficulties were encountered [Huitema 1998]. Today’s Internet routing algorithms (such as RIP, OSPF, and BGP) are load-insensitive, as a link’s cost does
not explicitly reflect its current (or recent past) level of congestion.


### 5.2.1 The Link-State (LS) Routing

Algorithm
Recall that in a link-state algorithm, the network topology and all link costs are
known, that is, available as input to the LS algorithm. In practice, this is accomplished by having each node broadcast link-state packets to all other nodes in
the network, with each link-state packet containing the identities and costs of
its attached links. In practice (for example, with the Internet’s OSPF routing
protocol, discussed in Section 5.3), this is often accomplished by a link-state
broadcast algorithm [Perlman 1999]. The result of the nodes’ broadcast is that
all nodes have an identical and complete view of the network. Each node can
then run the LS algorithm and compute the same set of least-cost paths as
every other node.
The link-state routing algorithm we present below is known as Dijkstra’s
algorithm, named after its inventor. A closely related algorithm is Prim’s algorithm; see [Cormen 2001] for a general discussion of graph algorithms.
Dijkstra’s algorithm computes the least-cost path from one node (the source,
which we will refer to as u) to all other nodes in the network. Dijkstra’s


The Network Layer: Control plane

algorithm is iterative and has the property that after the kth iteration of the
algorithm, the least-cost paths are known to k destination nodes, and among
the least-cost paths to all destination nodes, these k paths will have the k smallest costs. Let us define the following notation:
* D ( v ): cost of the least-cost path from the source node to destination v as of
this iteration of the algorithm.
* p ( v ): previous node (neighbor of v) along the current least-cost path from
the source to v.
* N ′: subset of nodes; v is in N ′ if the least-cost path from the source to v is
definitively known.
The centralized routing algorithm consists of an initialization step followed by a loop. The number of times the loop is executed is equal to the
number of nodes in the network. Upon termination, the algorithm will have
calculated the shortest paths from the source node u to every other node in the
network.

Link-State (LS) Algorithm for Source Node u
1 Initialization:
2 N’ = {u}
3 for all nodes v
if v is a neighbor of u
then D(v) = c(u,v)
else D(v) = ∞
8 Loop
9 find w not in N’ such that D(w) is a minimum
10 add w to N’
11 update D(v) for each neighbor v of w and not in N’:
D(v) = min(D(v), D(w)+ c(w,v) )
/* new cost to v is either old cost to v or known
least path cost to w plus cost from w to v */
15 until N’= N
As an example, let’s consider the network in Figure 5.3 and compute the leastcost paths from u to all possible destinations. A tabular summary of the
algorithm’s computation is shown in Table 5.1, where each line in the table
gives the values of the algorithm’s variables at the end of the iteration. Let’s
consider the few first steps in detail.
* In the initialization step, the currently known least-cost paths from u to its
directly attached neighbors, v, x, and w , are initialized to 2, 1, and 5,
respectively. Note in particular that the cost to w is set to 5 (even though
we will soon see that a lesser-cost path does indeed exist) since this is the
cost of the direct (one hop) link from u to w. The costs to y and z are set to
infinity because they are not directly connected to u.
* In the first iteration, we look among those nodes not yet added to the set
N ′ and find that node with the least cost as of the end of the previous iteration. That node is x, with a cost of 1, and thus x is added to the set N ′.




Table 5.1 Running the link-state algorithm on the network in Figure 5.3
step

N′

D( v ), p( v )

D( w ), p( w ) D( x ), p( x ) D( y ), p( y ) D( z ), p( z )


u

2, u

5, u


ux

2, u

4, x


uxy

2, u

3, y

4, y


uxyv

3, y

4, y


uxyvw


uxyvwz

1, u

∞

∞

2, x

∞

Line 12 of the LS algorithm is then performed to update D ( v ) for all nodes v,
yielding the results shown in the second line (Step 1) in Table 5.1. The
cost of the path to v is unchanged. The cost of the path to w (which was 5
at the end of the initialization) through node x is found to have a cost of 4.
Hence this lower-cost path is selected and w’s predecessor along the shortest path from u is set to x. Similarly, the cost to y (through x) is computed
to be 2, and the table is updated accordingly.
* In the second iteration, nodes v and y are found to have the least-cost
paths (2), and we break the tie arbitrarily and add y to the set N ′ so that N ′
now contains u, x , and y. The cost to the remaining nodes not yet in N ′,
that is, nodes v , w , and z, are updated via line 12 of the LS algorithm,
yielding the results shown in the third row in Table 5.1.
* And so on . . .
When the LS algorithm terminates, we have, for each node, its predecessor along the least-cost path from the source node. For each predecessor, we
also have its predecessor, and so in this manner we can construct the entire
path from the source to all destinations. The forwarding table in a node, say
node u, can then be constructed from this information by storing, for each destination, the next-hop node on the least-cost path from u to the destination.
Figure 5.4 shows the resulting least-cost paths and forwarding table in u for the
network in Figure 5.3.
What is the computational complexity of this algorithm? That is, given n
nodes (not counting the source), how much computation must be done in the
worst case to find the least-cost paths from the source to all destinations? In the
first iteration, we need to search through all n nodes to determine the node, w,
not in N ′ that has the minimum cost. In the second iteration, we need to

Figure 5.4 Least cost

path and forwarding table
for node u


The Network Layer: Control plane


check n − 1 nodes to determine the minimum cost; in the third iteration n − 2
nodes, and so on. Overall, the total number of nodes we need to search through
over all the iterations is n ( n + 1) 2, and thus we say that the preceding implementation of the LS algorithm has worst-case complexity of order n
squared: O ( n 2 ). (A more sophisticated implementation of this algorithm, using
a data structure known as a heap, can find the minimum in line 9 in logarithmic rather than linear time, thus reducing the complexity.)
Before completing our discussion of the LS algorithm, let us consider a
pathology that can arise. Figure 5.5 shows a simple network topology where
link costs are equal to the load carried on the link, for example, reflecting the
delay that would be experienced. In this example, link costs are not symmetric;
that is, c ( u, v ) equals c ( v , u ) only if the load carried on both directions on the
link ( u, v ) is the same. In this example, node z originates a unit of traffic destined for w, node x also originates a unit of traffic destined for w, and node y
injects an amount of traffic equal to e, also destined for w. The initial routing is
shown in Figure 5.5(a) with the link costs corresponding to the amount of traffic carried.
When the LS algorithm is next run, node y determines (based on the link
costs shown in Figure 5.5(a)) that the clockwise path to w has a cost of 1, while
the counterclockwise path to w (which it had been using) has a cost of 1 + e.
Hence y’s least-cost path to w is now clockwise. Similarly, x determines that its
new least-cost path to w is also clockwise, resulting in costs shown in
­Figure 5.5(b). When the LS algorithm is run next, nodes x, y, and z all detect a
zero-cost path to w in the counterclockwise direction, and all route their traffic

Figure 5.5 Oscillations
with congestion-sensitive
routing


to the counterclockwise routes. The next time the LS algorithm is run, x , y , and
z all then route their traffic to the clockwise routes.
What can be done to prevent such oscillations (which can occur in any
algorithm, not just an LS algorithm, that uses a congestion or delay-based link
metric)? One solution would be to mandate that link costs not depend on the
amount of traffic carried—an unacceptable solution since one goal of routing is
to avoid highly congested (for example, high-delay) links. Another solution is
to ensure that not all routers run the LS algorithm at the same time. This seems
a more reasonable solution, since we would hope that even if routers ran the
LS algorithm with the same periodicity, the execution instance of the algorithm
would not be the same at each node. Interestingly, researchers have found that
routers in the Internet can self-synchronize among themselves [Floyd Synchronization 1994]. That is, even though they initially execute the algorithm with
the same period but at different instants of time, the algorithm execution
instance can eventually become, and remain, synchronized at the routers. One
way to avoid such self-synchronization is for each router to randomize the
time it sends out a link advertisement.
Having studied the LS algorithm, let’s consider the other major routing
algorithm that is used in practice today—the distance-vector routing algorithm.


### 5.2.2 The Distance-Vector (DV) Routing

Algorithm
Whereas the LS algorithm is an algorithm using global information, the
­distance-vector (DV) algorithm is iterative, asynchronous, and distributed. It
is distributed in that each node receives some information from one or more of
its directly attached neighbors, performs a calculation, and then distributes the
results of its calculation back to its neighbors. It is iterative in that this process
continues on until no more information is exchanged between neighbors.
(Interestingly, the algorithm is also self-terminating—there is no signal that the
computation should stop; it just stops.) The algorithm is asynchronous in that it
does not require all of the nodes to operate in lockstep with each other. We’ll
see that an asynchronous, iterative, self-terminating, distributed algorithm is
much more interesting and fun than a centralized algorithm!
Before we present the DV algorithm, it will prove beneficial to discuss an
important relationship that exists among the costs of the least-cost paths. Let
d x ( y ) be the cost of the least-cost path from node x to node y. Then the least
costs are related by the celebrated Bellman-Ford equation, namely,
d x ( y ) = min v { c ( x , v ) + d v ( y )} ,

(5.1)

where the min v in the equation is taken over all of x’s neighbors. The BellmanFord equation is rather intuitive. Indeed, after traveling from x to v, if we then
take the least-cost path from v to y, the path cost will be c ( x , v ) + d v ( y ). Since
we must begin by traveling to some neighbor v, the least cost from x to y is the
minimum of c ( x , v ) + d v ( y ) taken over all neighbors v.
But for those who might be skeptical about the validity of the equation,
let’s check it for source node u and destination node z in Figure 5.3. The source


The Network Layer: Control plane

node u has three neighbors: nodes v, x, and w. By walking along various paths
in the graph, it is easy to see that d v ( z ) = 5, d x ( z ) = 3, and d w ( z ) = 3 . Plugging these values into Equation 5.1, along with the costs c ( u, v ) = 2 ,
c ( u, x ) = 1, and c ( u, w ) = 5 , gives d u ( z ) = min { 2 + 5, 5 + 3, 1 + 3 } = 4,
which is obviously true and which is exactly what the Dijskstra algorithm gave
us for the same network. This quick verification should help relieve any skepticism you may have.
The Bellman-Ford equation is not just an intellectual curiosity. It actually
has significant practical importance: the solution to the Bellman-Ford equation
provides the entries in node x’s forwarding table. To see this, let v* be any
neighboring node that achieves the minimum in Equation 5.1. Then, if node x
wants to send a packet to node y along a least-cost path, it should first forward
the packet to node v*. Thus, node x’s forwarding table would specify node v*
as the next-hop router for the ultimate destination y. Another important practical contribution of the Bellman-Ford equation is that it suggests the form of the
neighbor-to-neighbor communication that will take place in the DV algorithm.
The basic idea is as follows. Each node x begins with D x ( y ), an estimate of
the cost of the least-cost path from itself to node y, for all nodes, y, in N . Let
D x = [ D x ( y ): y in N ] be node x’s distance vector, which is the vector of cost
estimates from x to all other nodes, y, in N . With the DV algorithm, each node
x maintains the following routing information:
* For each neighbor v, the cost c ( x , v ) from x to directly attached neighbor, v
* Node x’s distance vector, that is, D x = [ D x ( y ): y in N ], containing x’s
estimate of its cost to all destinations, y, in N
* The distance vectors of each of its neighbors, that is, D v = [ D v ( y ): y in N ]
for each neighbor v of x
In the distributed, asynchronous algorithm, from time to time, each node
sends a copy of its distance vector to each of its neighbors. When a node x
receives a new distance vector from any of its neighbors w, it saves w’s distance vector, and then uses the Bellman-Ford equation to update its own
distance vector as follows:
D x ( y ) = min v { c ( x , v ) + D v ( y )}

for each node y in N

If node x’s distance vector has changed as a result of this update step,
node x will then send its updated distance vector to each of its neighbors,
which can in turn update their own distance vectors. Miraculously enough, as
long as all the nodes continue to exchange their distance vectors in an asynchronous fashion, each cost estimate D x ( y ) converges to d x ( y ), the actual cost
of the least-cost path from node x to node y [Bertsekas 1991]!

Distance-Vector (DV) Algorithm
At each node, x:

Initialization:
for all destinations y in N:

Dx(y)= c(x,y)/* if y is not a neighbor then c(x,y)= ∞ */
for each neighbor w



Dw(y) = ? for all destinations y in N
for each neighbor w
send distance vector Dx = [Dx(y): y in N] to w
9 loop
wait 
(until I see a link cost change to some neighbor w or

until I receive a distance vector from some neighbor w)
for each y in N:
Dx(y) = minv{c(x,v) + Dv(y)}
16 if Dx(y) changed for any destination y

send distance vector Dx = [Dx(y): y in N] to all neighbors
19 forever
In the DV algorithm, a node x updates its distance-vector estimate when it
either sees a cost change in one of its directly attached links or receives a distance-vector update from some neighbor. But to update its own forwarding
table for a given destination y, what node x really needs to know is not the
shortest-path distance to y but instead the neighboring node v* (y) that is the
next-hop router along the shortest path to y. As you might expect, the next-hop
router v* ( y ) is the neighbor v that achieves the minimum in Line 14 of the DV
algorithm. (If there are multiple neighbors v that achieve the minimum, then
v*(y) can be any of the minimizing neighbors.) Thus, in Lines 13–14, for each
destination y, node x also determines v* ( y ) and updates its forwarding table
for destination y.
Recall that the LS algorithm is a centralized algorithm in the sense that it
requires each node to first obtain a complete map of the network before running the Dijkstra algorithm. The DV algorithm is decentralized and does not use
such global information. Indeed, the only information a node will have is the
costs of the links to its directly attached neighbors and information it receives
from these neighbors. Each node waits for an update from any neighbor
(Lines 10–11), calculates its new distance vector when receiving an update
(Line 14), and distributes its new distance vector to its neighbors (Lines 16–17).
DV-like algorithms are used in many routing protocols in practice, including
the Internet’s RIP and BGP, ISO IDRP, Novell IPX, and the original ARPAnet.
Figure 5.6 illustrates the operation of the DV algorithm for the simple
three-node network shown at the top of the figure. The operation of the algorithm is illustrated in a synchronous manner, where all nodes simultaneously
receive distance vectors from their neighbors, compute their new distance vectors, and inform their neighbors if their distance vectors have changed. After
studying this example, you should convince yourself that the algorithm operates correctly in an asynchronous manner as well, with node computations
and update generation/reception occurring at any time.
The leftmost column of the figure displays three initial routing tables for
each of the three nodes. For example, the table in the upper-left corner is node
x’s initial routing table. Within a specific routing table, each row is a distance
vector—specifically, each node’s routing table includes its own distance vector


The Network Layer: Control plane


Figure 5.6 Distancevector (DV) algorithm in
operation

and that of each of its neighbors. Thus, the first row in node x’s initial routing
table is D x = [ D x ( x ) , D x ( y ) , D x ( z ) ] = [ 0, 2, 7 ]. The second and third rows
in this table are the most recently received distance vectors from nodes y and z,
respectively. Because at initialization node x has not received anything from
node y or z, the entries in the second and third rows are initialized to infinity.
After initialization, each node sends its distance vector to each of its two
neighbors. This is illustrated in Figure 5.6 by the arrows from the first column
of tables to the second column of tables. For example, node x sends its distance
vector D x = [ 0, 2, 7 ] to both nodes y and z. After receiving the updates, each
node recomputes its own distance vector. For example, node x computes
Dx ( x) = 0
D x ( y ) = min { c ( x , y ) + D y ( y ) , c ( x , z ) + D z ( y )} = min { 2 + 0, 7 + 1} = 2
D x ( z ) = min { c ( x , y ) + D y ( z ) , c ( x , z ) + D z ( z )} = min { 2 + 1, 7 + 0 } = 3
The second column therefore displays, for each node, the node’s new distance vector along with distance vectors just received from its neighbors. Note,
for example, that node x’s estimate for the least cost to node z, D x ( z ), has
changed from 7 to 3. Also note that for node x, neighboring node y achieves
the minimum in line 14 of the DV algorithm; thus, at this stage of the algorithm, we have at node x that v* ( y ) = y and v* ( z ) = y.


After the nodes recompute their distance vectors, they again send their
updated distance vectors to their neighbors (if there has been a change). This is
illustrated in Figure 5.6 by the arrows from the second column of tables to the
third column of tables. Note that only nodes x and z send updates: node y’s
distance vector didn’t change so node y doesn’t send an update. After receiving the updates, the nodes then recompute their distance vectors and update
their routing tables, which are shown in the third column.
The process of receiving updated distance vectors from neighbors,
recomputing routing table entries, and informing neighbors of changed costs
of the least-cost path to a destination continues until no update messages are
sent. At this point, since no update messages are sent, no further routing
table calculations will occur and the algorithm will enter a quiescent state;
that is, all nodes will be performing the wait in Lines 10–11 of the DV algorithm. The algorithm remains in the quiescent state until a link cost changes,
as discussed next.

Distance-Vector Algorithm: Link-Cost Changes
and Link Failure
When a node running the DV algorithm detects a change in the link cost from
itself to a neighbor (Lines 10–11), it updates its distance vector (Lines 13–14)
and, if there’s a change in the cost of the least-cost path, informs its neighbors
(Lines 16–17) of its new distance vector. Figure 5.7(a) illustrates a scenario
where the link cost from y to x changes from 4 to 1. We focus here only on y’
and z’s distance table entries to destination x. The DV algorithm causes the following sequence of events to occur:
* At time t 0, y detects the link-cost change (the cost has changed from 4 to 1),
updates its distance vector, and informs its neighbors of this change since
its distance vector has changed.
* At time t 1, z receives the update from y and updates its table. It computes
a new least cost to x (it has decreased from a cost of 5 to a cost of 2) and
sends its new distance vector to its neighbors.
* At time t 2 , y receives z’s update and updates its distance table. y’s least
costs do not change and hence y does not send any message to z. The algorithm comes to a quiescent state.
Thus, only two iterations are required for the DV algorithm to reach a quiescent state. The good news about the decreased cost between x and y has
propagated quickly through the network.

Figure 5.7 Changes in
link cost


The Network Layer: Control plane

Let’s now consider what can happen when a link cost increases. Suppose
that the link cost between x and y increases from 4 to 60, as shown in
Figure 5.7(b).
1. Before the link cost changes, D y ( x ) = 4, D y ( z ) = 1, D z ( y ) = 1, and
D z ( x ) = 5 . At time t 0, y detects the link-cost change (the cost has changed
from 4 to 60). y computes its new minimum-cost path to x to have a cost of
D y ( x ) = min { c ( y , x ) + D x ( x ) , c ( y , z ) + D z ( x )} = min { 60 + 0, 1 + 5 } = 6
Of course, with our global view of the network, we can see that this new
cost via z is wrong. But the only information node y has is that its direct cost
to x is 60 and that z has last told y that z could get to x with a cost of 5. So in
order to get to x, y would now route through z, fully expecting that z will
be able to get to x with a cost of 5. As of t 1 we have a routing loop—in order
to get to x, y routes through z, and z routes through y. A routing loop is like
a black hole—a packet destined for x arriving at y or z as of t 1 will bounce
back and forth between these two nodes forever (or until the forwarding
tables are changed).
2. Since node y has computed a new minimum cost to x, it informs z of its
new distance vector at time t 1.
3. Sometime after t 1, z receives y’s new distance vector, which indicates that
y’s minimum cost to x is 6. z knows it can get to y with a cost of 1 and
hence computes a new least cost to x of D z ( x ) = min { 50 + 0, 1 + 6 } = 7.
Since z’s least cost to x has increased, it then informs y of its new distance
vector at t 2 .
4. In a similar manner, after receiving z’s new distance vector, y determines
D y ( x ) = 8 and sends z its distance vector. z then determines D z ( x ) = 9
and sends z its distance vector, and so on.
How long will the process continue? You should convince yourself that
the loop will persist for 44 iterations (message exchanges between y and z)—
until z eventually computes the cost of its path via y to be greater than 50. At
this point, z will (finally!) determine that its least-cost path to x is via its direct
connection to x. y will then route to x via z. The result of the bad news about
the increase in link cost has indeed traveled slowly! What would have happened if the link cost c(y, x) had changed from 4 to 10,000 and the cost c(z, x)
had been 9,999? Because of such scenarios, the problem we have seen is sometimes referred to as the count-to-infinity problem.

Distance-Vector Algorithm: Adding Poisoned Reverse
The specific looping scenario just described can be avoided using a technique
known as poisoned reverse. The idea is simple—if z routes through y to get to
destination x, then z will advertise to y that its distance to x is infinity, that is, z
will advertise to y that D z ( x ) = ∞ (even though z knows D z ( x ) = 5 in truth).
z will continue telling this little white lie to y as long as it routes to x via y.
Since y believes that z has no path to x, y will never attempt to route to x via z,
as long as z continues to route to x via y (and lies about doing so).



Let’s now see how poisoned reverse solves the particular looping problem
we encountered before in Figure 5.5(b). As a result of the poisoned reverse, y’s
distance table indicates D z ( x ) = ∞. When the cost of the (x, y) link changes
from 4 to 60 at time t 0, y updates its table and continues to route directly to x,
albeit at a higher cost of 60, and informs z of its new cost to x, that is,
D y ( x ) = 60. After receiving the update at t 1, z immediately shifts its route to x
to be via the direct (z, x) link at a cost of 50. Since this is a new least-cost path to x,
and since the path no longer passes through y, z now informs y that
D z ( x ) = 50 at t 2 . After receiving the update from z, y updates its distance
table with D y ( x ) = 51. Also, since z is now on y’s least-cost path to x, y poisons the reverse path from z to x by informing z at time t 3 that D y ( x ) = ∞
(even though y knows that D y ( x ) = 51 in truth).
Does poisoned reverse solve the general count-to-infinity problem? It
does not. You should convince yourself that loops involving three or more
nodes (rather than simply two immediately neighboring nodes) will not be
detected by the poisoned reverse technique.

A Comparison of LS and DV Routing Algorithms
The DV and LS algorithms take complementary approaches toward computing routing. In the DV algorithm, each node talks to only its directly connected
neighbors, but it provides its neighbors with least-cost estimates from itself to
all the nodes (that it knows about) in the network. The LS algorithm requires
global information. Consequently, when implemented in each and every
router, for example, as in Figures 4.2 and 5.1, each node would need to communicate with all other nodes (via broadcast), but it tells them only the costs of
its directly connected links. Let’s conclude our study of LS and DV algorithms
with a quick comparison of some of their attributes. Recall that N is the set of
nodes (routers) and E is the set of edges (links).
* Message complexity. We have seen that LS requires each node to know the
cost of each link in the network. This requires O ( N E ) messages to be
sent. Also, whenever a link cost changes, the new link cost must be sent to
all nodes. The DV algorithm requires message exchanges between directly
connected neighbors at each iteration. We have seen that the time needed
for the algorithm to converge can depend on many factors. When link
costs change, the DV algorithm will propagate the results of the changed
link cost only if the new link cost results in a changed least-cost path for
one of the nodes attached to that link.
* Speed of convergence. We have seen that our implementation of LS is an
O ( N 2 ) algorithm requiring O(|N| |E|)) messages. The DV algorithm
can converge slowly and can have routing loops while the algorithm is
converging. DV also suffers from the count-to-infinity problem.
* Robustness. What can happen if a router fails, misbehaves, or is sabotaged?
Under LS, a router could broadcast an incorrect cost for one of its attached
links (but no others). A node could also corrupt or drop any packets it
received as part of an LS broadcast. But an LS node is computing only its
own forwarding tables; other nodes are performing similar calculations


The Network Layer: Control plane

for themselves. This means route calculations are somewhat separated
under LS, providing a degree of robustness. Under DV, a node can advertise incorrect least-cost paths to any or all destinations. (Indeed, in 1997,
a malfunctioning router in a small ISP provided national backbone routers
with erroneous routing information. This caused other routers to flood the
malfunctioning router with traffic and caused large portions of the Internet to become disconnected for up to several hours [Neumann 1997].)
More generally, we note that, at each iteration, a node’s calculation in DV
is passed on to its neighbor and then indirectly to its neighbor’s neighbor
on the next iteration. In this sense, an incorrect node calculation can be diffused through the entire network under DV.
In the end, neither algorithm is an obvious winner over the other; indeed,
both algorithms are used in the Internet.


## 5.3 Intra-AS Routing in the

Internet: OSPF
In our study of routing algorithms so far, we’ve viewed the network simply as
a collection of interconnected routers. One router was indistinguishable from
another in the sense that all routers executed the same routing algorithm to
compute routing paths through the entire network. In practice, this model and
its view of a homogenous set of routers all executing the same routing algorithm is simplistic for two important reasons:
* Scale. As the number of routers becomes large, the overhead involved in
communicating, computing, and storing routing information becomes
prohibitive. Today’s Internet consists of hundreds of millions of routers.
Storing routing information for possible destinations at each of these routers would clearly require enormous amounts of memory. The overhead
required to broadcast connectivity and link cost updates among all of the
routers would be huge! A distance-vector algorithm that iterated among
such a large number of routers would surely never converge. Clearly,
something must be done to reduce the complexity of route computation in
a network as large as the Internet.
* Administrative autonomy. As described in Section 1.3, the Internet is a network of ISPs, with each ISP consisting of its own network of routers. An
ISP generally desires to operate its network as it pleases (for example, to
run whatever routing algorithm it chooses within its network) or to hide
aspects of its network’s internal organization from the outside. Ideally, an
organization should be able to operate and administer its network as it
wishes, while still being able to connect its network to other outside
networks.
Both of these problems can be solved by organizing routers into autonomous
systems (ASs), with each AS consisting of a group of routers that are under the
same administrative control. Often the routers in an ISP, and the links that



interconnect them, constitute a single AS. Some ISPs, however, partition their
network into multiple ASs. In particular, some tier-1 ISPs use one gigantic AS
for their entire network, whereas others break up their ISP into tens of interconnected ASs. An autonomous system is identified by its globally unique
autonomous system number (ASN) [RFC 1930]. AS numbers, like IP addresses,
are assigned by ICANN regional registries [ICANN 2025].
Routers within the same AS all run the same routing algorithm and have
information about each other. The routing algorithm running within an autonomous system is called an intra-autonomous system routing protocol.

Open Shortest Path First (OSPF)
OSPF routing and its closely related cousin, IS-IS, are widely used for intra-AS
routing in the Internet. The Open in OSPF indicates that the routing protocol
specification is publicly available (for example, as opposed to Cisco’s EIGRP
protocol, which was only recently became open [Savage 2015], after roughly
20 years as a Cisco-proprietary protocol). The most recent version of OSPF,
­version 2, is defined in [RFC 2328], a public document.
OSPF is a link-state protocol that uses flooding of link-state information
and a Dijkstra’s least-cost path algorithm. With OSPF, each router constructs a
complete topological map (that is, a graph) of the entire autonomous system.
Each router then locally runs Dijkstra’s shortest-path algorithm to determine a
shortest-path tree to all subnets, with itself as the root node. Individual link
costs are configured by the network administrator (see sidebar, Principles and
Practice: Setting OSPF Weights). The administrator might choose to set all link
costs to 1, thus achieving minimum-hop routing, or might choose to set the
link weights to be inversely proportional to link capacity in order to discourage traffic from using low-bandwidth links. OSPF does not mandate a policy
for how link weights are set (that is the job of the network administrator), but
instead provides the mechanisms (protocol) for determining least-cost path
routing for the given set of link weights.

Principles in Practice
Setting OSPF Link Weights
Our discussion of link-state routing has implicitly assumed that link weights are set,
a routing algorithm such as OSPF is run, and traffic flows according to the routing
tables computed by the LS algorithm. In terms of cause and effect, the link weights
are given (i.e., they come first) and result (via Dijkstra’s algorithm) in routing paths
that minimize overall cost. In this viewpoint, link weights reflect the cost of using
a link (for example, if link weights are inversely proportional to capacity, then the
use of high-capacity links would have smaller weight and thus be more attractive
from a routing standpoint) and Dijsktra’s algorithm serves to minimize overall cost.
In practice, the cause and effect relationship between link weights and routing
paths may be reversed, with network operators configuring link weights in order
to obtain routing paths that achieve certain traffic engineering goals [Fortz 2000,
Fortz 2002]. For example, suppose a network operator has an estimate of traffic


The Network Layer: Control plane
flow entering the network at each ingress point and destined for each egress point.
The operator may then want to put in place a specific routing of ingress-to-egress
flows that minimizes the maximum utilization over all of the network’s links. But
with a routing algorithm such as OSPF, the operator’s main “knobs” for tuning the
routing of flows through the network are the link weights. Thus, in order to achieve
the goal of minimizing the maximum link utilization, the operator must find the
set of link weights that achieves this goal. This is a reversal of the cause and effect
relationship—the desired routing of flows is known, and the OSPF link weights
must be found such that the OSPF routing algorithm results in this desired routing
of flows.

With OSPF, a router broadcasts routing information to all other routers in
the autonomous system, not just to its neighboring routers. A router broadcasts
link-state information whenever there is a change in a link’s state (for example,
a change in cost or a change in up/down status). It also broadcasts a link’s
state periodically (at least once every 30 minutes), even if the link’s state has
not changed. RFC 2328 notes that “this periodic updating of link state advertisements adds robustness to the link state algorithm.” OSPF advertisements
are contained in OSPF messages that are carried directly by IP, with an upperlayer protocol of 89 for OSPF. Thus, the OSPF protocol must itself implement
functionality such as reliable message transfer and link-state broadcast. The
OSPF protocol also checks that links are operational (via a HELLO message
that is sent to an attached neighbor) and allows an OSPF router to obtain a
neighboring router’s database of network-wide link state.
Some of the advances embodied in OSPF include the following:

* Security. Exchanges between OSPF routers (for example, link-state updates)
can be authenticated. With authentication, only trusted routers can participate in the OSPF protocol within an AS, thus preventing malicious intruders (or networking students taking their newfound knowledge out for a
joyride) from injecting incorrect information into router tables. By default,
OSPF packets between routers are not authenticated and could be forged.
Two types of authentication can be configured—simple and MD5 (see
simple authentication, the same password is configured on each router.
When a router sends an OSPF packet, it includes the password in plaintext.
Clearly, simple authentication is not very secure. MD5 authentication is
based on shared secret keys that are configured in all the routers. For each
OSPF packet that it sends, the router computes the MD5 hash of the content
of the OSPF packet appended with the secret key. (See the discussion of
message authentication codes in Chapter 8.) Then the router includes the
resulting hash value in the OSPF packet. The receiving router, using the
preconfigured secret key, will compute an MD5 hash of the packet and
compare it with the hash value that the packet carries, thus verifying the
packet’s authenticity. Sequence numbers are also used with MD5 authentication to protect against replay attacks.
* Multiple same-cost paths. When multiple paths to a destination have the same
cost, OSPF allows multiple paths to be used (that is, a single path need not
be chosen for carrying all traffic when multiple equal-cost paths exist).



* Integrated support for unicast and multicast routing. Multicast OSPF (MOSPF)
[RFC 1584] provides simple extensions to OSPF to provide for multicast
routing. MOSPF uses the existing OSPF link database and adds a new
type of link-state advertisement to the existing OSPF link-state broadcast
mechanism.
* Support for hierarchy within a single AS. An OSPF autonomous system can be
configured hierarchically into areas. Each area runs its own OSPF link-state
routing algorithm, with each router in an area broadcasting its link state to
all other routers in that area. Within each area, one or more area border
routers are responsible for routing packets outside the area. Lastly, exactly
one OSPF area in the AS is configured to be the backbone area. The primary role of the backbone area is to route traffic between the other areas in
the AS. The backbone always contains all area border routers in the AS and
may contain non-border routers as well. Inter-area routing within the AS
requires that the packet be first routed to an area border router (intra-area
routing), then routed through the backbone to the area border router that is
in the destination area, and then routed to the final destination.
OSPF is a relatively complex protocol, and our coverage here has been necessarily brief; [Huitema 1998; Moy 1998; RFC 2328] provide additional details.


## 5.4 Routing Among the ISPs:

BGP
We just learned that OSPF is an example of an intra-AS routing protocol. When
routing a packet between a source and destination within the same AS, the
route the packet follows is entirely determined by the intra-AS routing protocol.
However, to route a packet across multiple ASs, say from a smartphone in
­Timbuktu to a server in a datacenter in Silicon Valley, we need an inter-­
autonomous system routing protocol. Since an inter-AS routing protocol
involves coordination among multiple ASs, communicating ASs must run the
same inter-AS routing protocol. In fact, in the Internet, all ASs run the same
inter-AS routing protocol, called the Border Gateway Protocol, more commonly known as BGP [RFC 4271; Stewart 1999].
BGP is arguably the most important of all the Internet protocols (the only
other contender would be the IP protocol that we studied in Section 4.3), as it is
the protocol that glues the thousands of ISPs in the Internet together. As we
will soon see, BGP is a decentralized and asynchronous protocol in the vein of
distance-vector routing described in Section 5.2.2. Although BGP is a complex
and challenging protocol, to understand the Internet on a deep level, we need
to become familiar with its underpinnings and operation. The time we devote
to learning BGP will be well worth the effort.


### 5.4.1 The Role of BGP

To understand the responsibilities of BGP, consider an AS and an arbitrary
router in that AS. Recall that every router has a forwarding table, which plays


The Network Layer: Control plane

the central role in the process of forwarding arriving packets to outbound
router links. As we have learned, for destinations that are within the same AS,
the entries in the router’s forwarding table are determined by the AS’s intraAS routing protocol. But what about destinations that are outside of the AS?
This is precisely where BGP comes to the rescue.
In BGP, packets are not routed to a specific destination address, but instead
to CIDRized prefixes, with each prefix representing a subnet or a collection of
subnets. In the world of BGP, a destination may take the form 138.16.68 22,
which for this example includes 1,024 IP addresses. Thus, a router’s forwarding table will have entries of the form ( x , I ), where x is a prefix (such as

### 138.16.68 22) and I is an interface number for one of the router’s interfaces.

As an inter-AS routing protocol, BGP provides each router a means to:
1. Obtain prefix reachability information from neighboring ASs. In particular,
BGP allows each subnet to advertise its existence to the rest of the Internet.
A subnet screams, “I exist and I am here,” and BGP makes sure that all the
routers in the Internet know about this subnet. If it weren’t for BGP, each
subnet would be an isolated island—alone, unknown and unreachable by
the rest of the Internet.
2. Determine the “best” routes to the prefixes. A router may learn about two or
more different routes to a specific prefix. To determine the best route, the
router will locally run a BGP route-selection procedure (using the prefix
reachability information it obtained via neighboring routers). The best
route will be determined based on policy as well as the reachability information.
Let’s now delve into how BGP carries out these two tasks.


### 5.4.2 Advertising BGP Route Information

Consider the network shown in Figure 5.8. As we can see, this simple network
has three autonomous systems: AS1, AS2, and AS3. As shown, AS3 includes a
subnet with prefix x. For each AS, each router is either a gateway router or an
internal router. A gateway router is a router on the edge of an AS that directly
connects to one or more routers in other ASs. An internal router connects only
to hosts and routers within its own AS. In AS1, for example, router 1c is a gateway router; routers 1a, 1b, and 1d are internal routers.
Let’s consider the task of advertising reachability information for prefix x
to all of the routers shown in Figure 5.8. At a high level, this is straightforward.
First, AS3 sends a BGP message to AS2, saying that x exists and is in AS3; let’s
denote this message as “AS3 x”. Then AS2 sends a BGP message to AS1, saying that x exists and that you can get to x by first passing through AS2 and
then going to AS3; let’s denote that message as “AS2 AS3 x”. In this manner,
each of the autonomous systems will not only learn about the existence of x,
but also learn about a path of autonomous systems that leads to x.
Although the discussion in the above paragraph about advertising BGP
reachability information should get the general idea across, it is not precise in
the sense that autonomous systems do not actually send messages to each
other, but instead routers do. To understand this, let’s now re-examine the




Figure 5.8 Network

with three autonomous
systems. AS3 includes a
subnet with prefix x

example in Figure 5.8. In BGP, pairs of routers exchange routing information
over semi-permanent TCP connections using port 179. Each such TCP connection, along with all the BGP messages sent over the connection, is called a BGP
connection. Furthermore, a BGP connection that spans two ASs is called an
external BGP (eBGP) connection, and a BGP session between routers in the
same AS is called an internal BGP (iBGP) connection. Examples of BGP connections for the network in Figure 5.8 are shown in Figure 5.9. There is typically
one eBGP connection for each link that directly connects gateway routers in
different ASs; thus, in Figure 5.9, there is an eBGP connection between gateway
routers 1c and 2a and an eBGP connection between gateway routers 2c and 3a.
There are also iBGP connections between routers within each of the ASs.
In particular, Figure 5.9 displays a common configuration of one BGP connection for each pair of routers internal to an AS, creating a mesh of TCP
connections within each AS. In Figure 5.9, the eBGP connections are shown
with the long dashes; the iBGP connections are shown with the short dashes.
Note that iBGP connections do not always correspond to physical links.
In order to propagate the reachability information, both iBGP and eBGP
sessions are used. Consider again advertising the reachability information for
prefix x to all routers in AS1 and AS2. In this process, gateway router 3a first
sends an eBGP message “AS3 x” to gateway router 2c. Gateway router 2c then
sends the iBGP message “AS3 x” to all of the other routers in AS2, including to
gateway router 2a . Gateway router 2a then sends the eBGP message
“AS2 AS3 x” to gateway router 1c. Finally, gateway router 1c uses iBGP to

Figure 5.9 eBGP and
iBGP connections


The Network Layer: Control plane


send the message “AS2 AS3 x” to all the routers in AS1. After this process is
complete, each router in AS1 and AS2 is aware of the existence of x and is also
aware of an AS path that leads to x.
Of course, in a real network, from a given router there may be many different paths to a given destination, each through a different sequence of ASs.
For example, consider the network in Figure 5.10, which is the original network in Figure 5.8, with an additional physical link from router 1d to router 3d.
In this case, there are two paths from AS1 to x: the path “AS2 AS3 x” via
router 1c; and the new path “AS3 x” via the router 1d.


### 5.4.3 Determining the Best Routes

As we have just learned, there may be many paths from a given router to a destination subnet. In fact, in the Internet, routers often receive reachability
information about dozens of different possible paths. How does a router
choose among these paths (and then configure its forwarding table
accordingly)?
Before addressing this critical question, we need to introduce a little more
BGP terminology. When a router advertises a prefix across a BGP connection, it
includes with the prefix several BGP attributes. In BGP jargon, a prefix along
with its attributes is called a route. Two of the more important attributes are
AS-PATH and NEXT-HOP. The AS-PATH attribute contains the list of ASs
through which the advertisement has passed, as we’ve seen in our examples
above. To generate the AS-PATH value, when a prefix is passed to an AS, the AS
adds its ASN to the existing list in the AS-PATH. For example, in Figure 5.10,
there are two routes from AS1 to subnet x: one which uses the AS-PATH
“AS2 AS3”; and another that uses the AS-PATH “A3”. BGP routers also use
the AS-PATH attribute to detect and prevent looping advertisements; specifically, if a router sees that its own AS is contained in the path list, it will reject
the advertisement.
Providing the critical link between the inter-AS and intra-AS routing protocols, the NEXT-HOP attribute has a subtle but important use. The NEXT-HOP
is the IP address of the router interface that begins the AS-PATH. To gain insight
into this attribute, let’s again refer to Figure 5.10. As indicated in Figure 5.10,
the NEXT-HOP attribute for the route “AS2 AS3 x” from AS1 to x that
passes through AS2 is the IP address of the left interface on router 2a .

Figure 5.10 Network
augmented with peering
link between AS1 and AS3


The NEXT-HOP attribute for the route “AS3 x” from AS1 to x that bypasses
AS2 is the IP address of the leftmost interface of router 3d. In summary, in this
toy example, each router in AS1 becomes aware of two BGP routes to prefix x:
IP address of leftmost interface for router 2a; AS2 AS3; x
IP address of leftmost interface of router 3d; AS3; x
Here, each BGP route is written as a list with three components: NEXTHOP; AS-PATH; destination prefix. In practice, a BGP route includes additional
attributes, which we will ignore for the time being. Note that the NEXT-HOP
attribute is an IP address of a router that does not belong to AS1; however, the
subnet that contains this IP address directly attaches to AS1.

Hot Potato Routing
We are now finally in position to talk about BGP routing algorithms in a precise
manner. We will begin with one of the simplest routing algorithms, namely,
hot potato routing.
Consider router 1b in the network in Figure 5.10. As just described, this
router will learn about two possible BGP routes to prefix x. In hot potato routing, the route chosen (from among all possible routes) is that route with the
least cost to the NEXT-HOP router beginning that route. In this example, router
1b will consult its intra-AS routing information to find the least-cost intra-AS
path to NEXT-HOP router 2a and the least-cost intra-AS path to NEXT-HOP
router 3d, and then select the route with the smallest of these least-cost paths.
For example, suppose that cost is defined as the number of links traversed.
Then the least cost from router 1b to router 2a is 2, the least cost from router 1b
to router 2d is 3, and router 2a would therefore be selected. Router 1b would
then consult its forwarding table (configured by its intra-AS algorithm) and
find the interface I that is on the least-cost path to router 2a. It then adds ( x , I )
to its forwarding table.
The steps for adding an outside-AS prefix in a router ’s forwarding
table for hot potato routing are summarized in Figure 5.11. It is important to
note that when adding an outside-AS prefix into a forwarding table, both the
inter-AS routing protocol (BGP) and the intra-AS routing protocol (e.g., OSPF)
are used.
The idea behind hot-potato routing is for router 1b to get packets out of its
AS as quickly as possible (more specifically, with the least cost possible) without worrying about the cost of the remaining portions of the path outside of its
AS to the destination. In the name “hot potato routing,” a packet is analogous

Figure 5.11 Steps in adding outside-AS destination in a router’s forwarding table


The Network Layer: Control plane

to a hot potato that is burning in your hands. Because it is burning hot, you
want to pass it off to another person (another AS) as quickly as possible. Hot
potato routing is thus a selfish algorithm—it tries to reduce the cost in its own
AS while ignoring the other components of the end-to-end costs outside its AS.
Note that with hot potato routing, two routers in the same AS may choose two
different AS paths to the same prefix. For example, we just saw that router 1b
would send packets through AS2 to reach x. However, router 1d would bypass
AS2 and send packets directly to AS3 to reach x.

Route-Selection Algorithm
In practice, BGP uses an algorithm that is more complicated than hot potato
routing, but nevertheless incorporates hot potato routing. For any given destination prefix, the input into BGP’s route-selection algorithm is the set of all
routes to that prefix that have been learned and accepted by the router. If there
is only one such route, then BGP obviously selects that route. If there are two
or more routes to the same prefix, then BGP sequentially invokes the following
elimination rules until one route remains:
1. A route is assigned a local preference value as one of its attributes
(in addition to the AS-PATH and NEXT-HOP attributes). The local preference of a route could have been set by the router or could have been
learned from another router in the same AS. The value of the local preference attribute is a policy decision that is left entirely up to the AS’s network administrator. (We will shortly discuss BGP policy issues in some
detail.) The routes with the highest local preference values are selected.
2. From the remaining routes (all with the same highest local preference
value), the route with the shortest AS-PATH is selected. If this rule were
the only rule for route selection, then BGP would be using a DV algorithm
for path determination, where the distance metric uses the number of AS
hops rather than the number of router hops.
3. From the remaining routes (all with the same highest local preference
value and the same AS-PATH length), hot potato routing is used, that is,
the route with the closest NEXT-HOP router is selected.
4. If more than one route still remains, the router uses BGP identifiers to
select the route; see [Stewart 1999].
As an example, let’s again consider router 1b in Figure 5.10. Recall that
there are exactly two BGP routes to prefix x, one that passes through AS2 and
one that bypasses AS2. Also recall that if hot potato routing on its own were
used, then BGP would route packets through AS2 to prefix x. But in the above
route-selection algorithm, rule 2 is applied before rule 3, causing BGP to select
the route that bypasses AS2, since that route has a shorter AS PATH. So we see
that with the above route-selection algorithm, BGP is no longer a selfish
­algorithm—it first looks for routes with short AS paths (thereby likely reducing end-to-end delay).
As noted above, BGP is the de facto standard for inter-AS routing for the
Internet. To see the contents of various BGP routing tables (large!) extracted



from routers in tier-1 ISPs, see http://www.routeviews.org. BGP routing tables
often contain over half a million routes (that is, prefixes and corresponding
attributes). Statistics about the size and characteristics of BGP routing tables
are presented in [Huston 2019b].


### 5.4.4 IP-Anycast

In addition to being the Internet’s inter-AS routing protocol, BGP is often used
to implement the IP-anycast service [RFC 1546, RFC 7094], which is commonly
used in DNS. To motivate IP-anycast, consider that in many applications, we
are interested in (1) replicating the same content on different servers in many
different dispersed geographical locations, and (2) having each user access the
content from the server that is closest. For example, a CDN may replicate videos and other objects on servers in different countries. Similarly, the DNS
system can replicate DNS records on DNS servers throughout the world. When
a user wants to access this replicated content, it is desirable to point the user to
the “nearest” server with the replicated content. BGP’s route-selection algorithm provides an easy and natural mechanism for doing so.
To make our discussion concrete, let’s describe how a CDN might use
IP-anycast. As shown in Figure 5.12, during the IP-anycast configuration stage,
the CDN company assigns the same IP address to each of its servers, and uses
standard BGP to advertise this IP address from each of the servers. When a
BGP router receives multiple route advertisements for this IP address, it treats
these advertisements as providing different paths to the same physical location
(when, in fact, the advertisements are for different paths to different physical
locations). When configuring its routing table, each router will locally use the
BGP route-selection algorithm to pick the “best” (for example, closest, as

Figure 5.12 Using
IP-anycast to bring users
to the closest CDN server


The Network Layer: Control plane


determined by AS-hop counts) route to that IP address. For example, if one
BGP route (corresponding to one location) is only one AS hop away from the
router, and all other BGP routes (corresponding to other locations) are two or
more AS hops away, then the BGP router would choose to route packets to the
location that is one hop away. After this initial BGP address-advertisement
phase, the CDN can do its main job of distributing content. When a client
requests the video, the CDN returns to the client the common IP address used
by the geographically dispersed servers, no matter where the client is located.
When the client sends a request to that IP address, Internet routers then forward the request packet to the “closest” server, as defined by the BGP
route-selection algorithm.
Although the above CDN example nicely illustrates how IP-anycast can
be used, in practice, CDNs generally choose not to use IP-anycast because BGP
routing changes can result in different packets of the same TCP connection
arriving at different instances of the Web server. But IP-anycast is extensively
used by the DNS system to direct DNS queries to the closest root DNS server.
Recall from Section 2.4, there are currently 13 IP addresses for root DNS servers. But corresponding to each of these addresses, there are multiple DNS root
servers, with some of these addresses having over 100 DNS root servers scattered over all corners of the world. When a DNS query is sent to one of these 13
IP addresses, IP anycast is used to route the query to the nearest of the DNS
root servers that is responsible for that address. [Li 2018; Zhou 2023] present
recent measurements illustrating Internet anycast, use, performance, and
challenges.


### 5.4.5 Routing Policy

When a router selects a route to a destination, the AS routing policy can trump
all other considerations, such as shortest AS path or hot potato routing. Indeed,
in the route-selection algorithm, routes are first selected according to the localpreference attribute, whose value is fixed by the policy of the local AS.
Let’s illustrate some of the basic concepts of BGP routing policy with a
simple example. Figure 5.13 shows six interconnected autonomous systems:
A, B, C, W, X, and Y. It is important to note that A, B, C, W, X, and Y are
ASs, not routers. Let’s assume that autonomous systems W, X, and Y are
access ISPs and that A, B, and C are backbone provider networks. We’ll also
assume that A, B, and C, directly send traffic to each other, and provide full
BGP information to their customer networks. All traffic entering an ISP access
network must be destined for that network, and all traffic leaving an ISP
access network must have originated in that network. W and Y are clearly

Figure 5.13 A simple
BGP policy scenario


access ISPs. X is a multi-homed access ISP, since it is connected to the rest of
the network via two different providers (a scenario that is becoming increasingly common in practice). However, like W and Y, X itself must be the
source/destination of all traffic leaving/entering X. But how will this stub
network behavior be implemented and enforced? How will X be prevented
from forwarding traffic between B and C? This can easily be accomplished by
controlling the manner in which BGP routes are advertised. In particular, X
will function as an access ISP network if it advertises (to its neighbors B and C)
that it has no paths to any other destinations except itself. That is, even though
X may know of a path, say XCY, that reaches network Y, it will not advertise
this path to B. Since B is unaware that X has a path to Y, B would never forward traffic destined to Y (or C) via X. This simple example illustrates how a
selective route advertisement policy can be used to implement
customer/provider routing relationships.
Let’s next focus on a provider network, say AS B . Suppose that B has
learned (from A) that A has a path AW to W. B can thus install the route AW
into its routing information base. Clearly, B also wants to advertise the path
BAW to its customer, X, so that X knows that it can route to W via B . But
should B advertise the path BAW to C? If it does so, then C could route traffic
to W via BAW. If A, B, and C are all backbone providers, than B might rightly
feel that it should not have to shoulder the burden (and cost!) of carrying transit traffic between A and C. B might rightly feel that it is A’s and C’s job (and
cost!) to make sure that C can route to/from A’s customers via a direct connection between A and C. There are currently no official standards that govern
how backbone ISPs route among themselves. However, a rule of thumb followed by commercial ISPs is that any traffic flowing across an ISP’s backbone
network must have either a source or a destination (or both) in a network that
is a customer of that ISP; otherwise the traffic would be getting a free ride on
the ISP’s network. Individual peering agreements (that would govern questions such as those raised above) are typically negotiated between pairs of
ISPs and are often confidential; [Huston 1999a; Huston 2012] provide an interesting discussion of peering agreements. For a detailed description of how
routing policy reflects commercial relationships among ISPs, see [Gao 2001;
Dmitiropoulos 2007]. For a discussion of BGP routing polices from an ISP
standpoint, see [Caesar 2005b].

Principles in Practice
Why Are There Different Inter-AS and
Intra-AS Routing Protocols?
Having now studied the details of specific inter-AS and intra-AS routing
protocols deployed in today’s Internet, let’s conclude by considering perhaps the
most fundamental question we could ask about these protocols in the first place
(hopefully, you have been wondering this all along, and have not lost the forest for
the trees!): Why are different inter-AS and intra-AS routing protocols used?


The Network Layer: Control plane
The answer to this question gets at the heart of the differences between the
goals of routing within an AS and among ASs:

•

Policy. Among ASs, policy issues dominate. It may well be important that
traffic originating in a given AS not be able to pass through another specific
AS. Similarly, a given AS may well want to control what transit traffic it carries between other ASs. We have seen that BGP carries path attributes and
provides for controlled distribution of routing information so that such
policy-based routing decisions can be made. Within an AS, everything is
nominally under the same administrative control, and thus policy issues
play a much less important role in choosing routes within the AS.

•

Scale. The ability of a routing algorithm and its data structures to scale to
handle routing to/among large numbers of networks is a critical issue in
inter-AS routing. Within an AS, scalability is less of a concern. For one thing,
if a single ISP becomes too large, it is always possible to divide it into two
ASs and perform inter-AS routing between the two new ASs. (Recall that
OSPF allows such a hierarchy to be built by splitting an AS into areas.)

•

Performance. Because inter-AS routing is so policy oriented, the quality (for
example, performance) of the routes used is often of secondary concern (that
is, a longer or more costly route that satisfies certain policy criteria may well
be taken over a route that is shorter but does not meet that criteria). Indeed,
we saw that among ASs, there is not even the notion of cost (other than AS
hop count) associated with routes. Within a single AS, however, such policy
concerns are of less importance, allowing routing to focus more on the level
of performance realized on a route.

This completes our brief introduction to BGP. Understanding BGP is
important because it plays a central role in the Internet. We encourage you to
consult the BGP references in this section (in particular [Stewart 1999; Huston
2019a]) and the outstanding online BGP resources available at [NSRC 2025].


### 5.4.6 Putting the Pieces Together:

Obtaining Internet Presence
Although this subsection is not about BGP per se, it brings together many of
the protocols and concepts we’ve seen thus far, including IP addressing, DNS,
and BGP.
Suppose you have just created a small company that has a number of servers, including a public Web server that describes your company’s products and
services, a mail server from which your employees obtain their e-mail messages, and a DNS server. Naturally, you would like the entire world to be able
to visit your Web site in order to learn about your exciting products and services. Moreover, you would like your employees to be able to send and receive
e-mail to potential customers throughout the world.
To meet these goals, you first need to obtain Internet connectivity, which is
done by contracting with, and connecting to, a local ISP. Your company will
have a gateway router, which will be connected to a router in your local ISP.
This connection might be a DSL connection through the existing telephone



infrastructure, a leased line to the ISP’s router, or one of the many other access
solutions described in Chapter 1. In the simplest case, your local ISP will also
provide you with an IP address range, for example, a /24 address range consisting of 256 addresses. Once you have your physical connectivity and your IP
address range, you will assign one of the IP addresses (in your address range)
to your Web server, one to your mail server, one to your DNS server, one to
your gateway router, and other IP addresses to other servers and networking
devices in your company’s network. (In the case that your ISP is using NAT,
described in Section 4.3.3, your server addressing setup would be a bit more
complicated.)
In addition to contracting with an ISP, you will also need to contract with
an Internet registrar to obtain a domain name for your company, as described
in Chapter 2. For example, if your company’s name is, say, Xanadu Inc., you
will naturally try to obtain the domain name xanadu.com. Your company must
also obtain presence in the DNS system. Specifically, because outsiders will
want to contact your DNS server to obtain the IP addresses of your servers,
you will also need to provide your registrar with the IP address of your DNS
server. Your registrar will then put an entry for your DNS server (domain
name and corresponding IP address) in the .com top-level-domain servers, as
described in Chapter 2. After this step is completed, any user who knows your
domain name (e.g., xanadu.com) will be able to obtain the IP address of your
DNS server via the DNS system.
So that people can discover the IP addresses of your Web server, in your
DNS server you will need to include entries that map the host name of your
Web server (e.g., www.xanadu.com) to its IP address. You will want to have
similar entries for other publicly available servers in your company, including
your mail server. In this manner, if Alice wants to browse your Web server, the
DNS system will contact your DNS server, find the IP address of your Web
server, and give it to Alice. Alice can then establish a TCP connection directly
with your Web server.
However, there still remains one other necessary and crucial step to allow
outsiders from around the world to access your Web server. Consider what
happens when Alice, who knows the IP address of your Web server, sends an
IP datagram (e.g., a TCP SYN segment) to that IP address. This datagram will
be routed through the Internet, visiting a series of routers in many different
ASs, and eventually reach your Web server. When any one of the routers
receives the datagram, it is going to look for an entry in its forwarding table to
determine on which outgoing port it should forward the datagram. Therefore,
each of the routers needs to know about the existence of your company’s /24
prefix (or some aggregate entry). How does a router become aware of your
company’s prefix? As we have just seen, it becomes aware of it from BGP!
Specifically, when your company contracts with a local ISP and gets assigned
a prefix (i.e., an address range), your local ISP will use BGP to advertise your
prefix to the ISPs to which it connects. Those ISPs will then, in turn, use BGP
to propagate the advertisement. Eventually, all Internet routers will know
about your prefix (or about some aggregate that includes your prefix) and
thus be able to appropriately forward datagrams destined to your Web and
mail servers.


The Network Layer: Control plane


## 5.5 The SDN Control Plane

In this section, we’ll dive into the SDN control plane—the network-wide logic
that controls packet forwarding among a network’s SDN-enabled devices, as
well as the configuration and management of these devices and their services.
Our study here builds on our earlier discussion of generalized SDN forwarding in Section 4.4, so you might want to first review that section, as well as
Section 5.1 of this chapter, before continuing on. As in Section 4.4, we’ll again
adopt the terminology used in the SDN literature and refer to the network’s
forwarding devices as “packet switches” (or just switches, with “packet” being
understood), since forwarding decisions can be made on the basis of networklayer source/destination addresses, link-layer source/destination addresses,
as well as many other values in transport, network, and link-layer packetheader fields. Our discussion here will also be a good foundation for our
discussion of the control plane in 5G cellular networks, which adopts an SDNlike approach.
Four key characteristics of an SDN architecture can be identified
[Kreutz 2015]:
* Flow-based forwarding. Packet forwarding by SDN-controlled switches can
be based on any number of header field values in the transport-layer,
­n etwork-layer, or link-layer header. We saw in Section 4.4 that the
­OpenFlow 1.0 abstraction allows forwarding based on eleven different
header field values. This contrasts sharply with the traditional approach
to router-based forwarding that we studied in Sections 5.2–5.4, where forwarding of IP datagrams was based solely on a datagram’s destination IP
address. Recall from Figure 5.2 that packet forwarding rules are specified
in a switch’s flow table; it is the job of the SDN control plane to compute,
manage and install flow table entries in all of the network’s switches.
* Separation of data plane and control plane. This separation is shown clearly in
Figures 5.2 and 5.14. The data plane consists of the network’s switches—
relatively simple (but fast) devices that execute the “match plus action”
rules in their flow tables. The control plane consists of servers and software that determine and manage the switches’ flow tables.
* Network control functions: external to data-plane switches. Given that the “S”
in SDN is for “software,” it’s perhaps not surprising that the SDN control
plane is implemented in software. Unlike traditional routers, however,
this software executes on servers that are both distinct and remote from
the network’s switches. As shown in Figure 5.14, the control plane itself
consists of two components—an SDN controller (or network operating
system [Gude 2008]) and a set of network-control applications. The controller maintains accurate network state information (e.g., the state of
remote links, switches, and hosts); provides this information to the
­network-control applications running in the control plane; and provides the
means through which these applications can monitor, program, and control the underlying network devices. Although the controller in Figure 5.14
is shown as a single central server, in practice the controller is only




Figure 5.14

Components of the
SDN architecture:
SDN-controlled switches,
the SDN controller,
network-control
applications

logically centralized; it is typically implemented on several servers that
provide coordinated, scalable performance and high availability.
* A programmable network control plane. The network control plane is programmable through the network-control applications running in the control plane. These applications represent the “brains” of the SDN control
plane, using the APIs provided by the SDN controller to specify and control the data plane in the network devices. For example, a routing network-control application might determine the end-end paths between
sources and destinations (for example, by executing Dijkstra’s algorithm
using the node-state and link-state information maintained by the SDN
controller). Another network application might perform access control,
that is, determine which packets are to be blocked at a switch, as in our
third example in Section 4.4.3. Yet another application might have switches
forward packets in a manner that performs server load balancing (the second example we considered in Section 4.4.3).
From this discussion, we can see that SDN represents a significant “unbundling” of network functionality—data plane switches, SDN controllers, and
network-control applications are separate entities that may each be provided
by different vendors and organizations. This contrasts with the pre-SDN model
in which a switch/router (together with its embedded control plane software
and protocol implementations) was monolithic, vertically integrated, and sold
by a single vendor. This unbundling of network functionality in SDN has been
likened to the earlier evolution from mainframe computers (where hardware,
system software, and applications were provided by a single vendor) to personal computers (with their separate hardware, operating systems, and
applications). The unbundling of computing hardware, system software, and
applications has led to a rich, open ecosystem driven by innovation in all three


The Network Layer: Control plane

of these areas; one hope for SDN is that it will continue to drive and enable
such rich innovation.
Given our understanding of the SDN architecture of Figure 5.14, many
questions naturally arise. How and where are the flow tables actually computed?
How are these tables updated in response to events at SDN-controlled devices
(e.g., an attached link going up/down)? And how are the flow table entries at
multiple switches coordinated in such a way as to result in orchestrated and consistent network-wide functionality (e.g., end-to-end paths for forwarding
packets from sources to destinations, or coordinated distributed firewalls)? It is
the role of the SDN control plane to provide these, and many other, capabilities.


### 5.5.1 The SDN Control Plane: SDN

Controller and SDN Network-control
Applications
Let’s begin our discussion of the SDN control plane in the abstract, by considering the generic capabilities that the control plane must provide. As we’ll see,
this abstract, “first principles” approach will lead us to an overall architecture
that reflects how SDN control planes have been implemented in practice.
As noted above, the SDN control plane divides broadly into two
­components—the SDN controller and the SDN network-control applications.
Let’s explore the controller first. Although many different SDN controllers
have been developed [Kreutz 2015] since the earliest SDN controller [Gude
2008], their structure can be broadly organized into three layers. Let’s consider
these layers in an uncharacteristically bottom-up fashion:
* A communication layer: communicating between the SDN controller and controlled network devices. Clearly, if an SDN controller is going to control the
operation of a remote SDN-enabled switch, host, or other device, a protocol is needed to transfer information between the controller and that
device. In addition, a device must be able to communicate locallyobserved events to the controller (for example, a message indicating that
an attached link has gone up or down, that a device has just joined the
network, or a heartbeat indicating that a device is up and operational).
These events provide the SDN controller with an up-to-date view of the
network’s state. This protocol constitutes the lowest layer of the controller
architecture, as shown in Figure 5.15. The communication between the
controller and the controlled devices cross what has come to be known as
the controller ’s “southbound” interface. In Section 5.5.2, we’ll study
OpenFlow—a specific protocol that provides this communication functionality. OpenFlow is implemented in most, if not all, SDN controllers.
* A network-wide state-management layer. The ultimate control decisions made
by the SDN control plane—for example, configuring flow tables in all
switches to achieve the desired end-end forwarding, to implement load
balancing, or to implement a particular firewalling capability—will require
that the controller have up-to-date information about state of the networks’
hosts, links, switches, and other SDN-controlled devices. A switch’s flow




Figure 5.15

Components of an SDN
controller

table contains counters whose values might also be profitably used by
­network-control applications; these values should thus be available to the
applications. Since the ultimate aim of the control plane is to determine
flow tables for the various controlled devices, a controller might also maintain a copy of these tables. These pieces of information all constitute examples of the network-wide “state” maintained by the SDN controller.
* The interface to the network-control application layer. The controller interacts
with network-control applications through its “northbound” interface.
This API allows network-control applications to read/write network state
and flow tables within the state-management layer. Applications can register to be notified when state-change events occur, so that they can take
actions in response to network event notifications sent from SDN-­
controlled devices. Different types of APIs may be provided; we’ll see that
two popular SDN controllers communicate with their applications using a
REST [Fielding 2000] request-response interface.
We have noted several times that an SDN controller can be considered to
be “logically centralized,” that is, that the controller may be viewed externally
(for example, from the point of view of SDN-controlled devices and external
network-control applications) as a single, monolithic service. However, these
services and the databases used to hold state information are implemented in
practice by a distributed set of servers for fault tolerance, high availability, or for
performance reasons. With controller functions being implemented by a set of
servers, the semantics of the controller’s internal operations (e.g., maintaining


The Network Layer: Control plane

logical time ordering of events, consistency, consensus, and more) must be
considered [Panda 2013; Ferguson 2021]. Such concerns are common across
many different distributed systems; see [Lamport 1989, Lampson 1996] for elegant solutions to these challenges. Modern controllers such as ONOS [ONOS
2025] and ORION [Ferguson 2021] (see sidebar) have placed considerable
emphasis on architecting a logically centralized but physically distributed controller platform that provides scalable services and high availability to the
controlled devices and network-control applications alike.
The architecture depicted in Figure 5.15 closely resembles the architecture
of the originally proposed NOX controller in 2008 [Gude 2008], as well as that
of today’s controllers (see sidebar). We’ll cover an example of controller operation in Section 5.5.3. First, however, let’s examine the OpenFlow protocol, the
earliest and now one of several protocols that can be used for communication
between an SDN controller and a controlled device, which lies in the controller’s communication layer.


### 5.5.2 OpenFlow Protocol

The OpenFlow protocol [OpenFlow 2025] operates between an SDN controller
and an SDN-controlled switch or other device implementing the OpenFlow
API that we studied earlier in Section 4.4. The OpenFlow protocol operates
over TCP, with a default port number of 6653.
Among the important messages flowing from the controller to the controlled switch are the following:
* Configuration. This message allows the controller to query and set a
switch’s configuration parameters.
* Modify-State. This message is used by a controller to add/delete or modify
entries in the switch’s flow table, and to set switch port properties.
* Read-State. This message is used by a controller to collect statistics and
counter values from the switch’s flow table and ports.
* Send-Packet. This message is used by the controller to send a specific
packet out of a specified port at the controlled switch. The message itself
contains the packet to be sent in its payload.
Among the messages flowing from the SDN-controlled switch to the controller are the following:
* Flow-Removed. This message informs the controller that a flow table entry
has been removed, for example by a timeout or as the result of a received
modify-state message.
* Port-status. This message is used by a switch to inform the controller of a
change in port status.
* Packet-in. Recall from Section 4.4 that a packet arriving at a switch port
and not matching any flow table entry is sent to the controller for additional processing. Matched packets may also be sent to the controller, as
an action to be taken on a match. The packet-in message is used to send
such packets to the controller.





### 5.5.3 Data and Control Plane Interaction:

An Example
In order to solidify our understanding of the interaction between SDN-controlled switches and the SDN controller, let’s consider the example shown in
Figure 5.16, in which Dijkstra’s algorithm (which we studied in Section 5.2) is
used to determine shortest path routes. The SDN scenario in Figure 5.16 has
two important differences from the earlier per-router-control scenario of Sections 5.2.1 and 5.3, where Dijkstra’s algorithm was implemented in each and
every router and link-state updates were flooded among all network routers:
* Dijkstra’s algorithm is executed as a separate application, outside of the
packet switches.
* Packet switches send link updates to the SDN controller and not to each
other.
In this example, let’s assume that the link between switch s1 and s2 goes
down; that shortest path routing is implemented, and consequently and that
incoming and outgoing flow forwarding rules at s1, s3, and s4 are affected, but
that s2’s operation is unchanged. Let’s also assume that OpenFlow is used as
the communication layer protocol, and that the control plane performs no
other function other than link-state routing.
1. Switch s1, experiencing a link failure between itself and s2, notifies the
SDN controller of the link-state change using the OpenFlow port-status
message.

Figure 5.16 SDN
controller scenario:
Link-state change


The Network Layer: Control plane

2. The SDN controller receives the OpenFlow message indicating the linkstate change, and notifies the link-state manager, which updates a linkstate database.
3. The network-control application that implements Dijkstra’s link-state
routing has previously registered to be notified when link state changes.
That application receives the notification of the link-state change.
4. The link-state routing application interacts with the link-state manager to
get updated link state; it might also consult other components in the statemanagement layer. It then computes the new least-cost paths.
5. The link-state routing application then interacts with the flow table manager, which determines the flow tables to be updated.
6. The flow table manager then uses the OpenFlow protocol to update flow
table entries at affected switches—s1 (which will now route packets destined to s2 via s4), s2 (which will now begin receiving packets from s1 via
intermediate switch s4), and s4 (which must now forward packets from s1
destined to s2).
This example is simple but illustrates how the SDN control plane provides
control-plane services (in this case, network-layer routing) that had been previously implemented with per-router control exercised in each and every network
router. One can now easily appreciate how an SDN-enabled ISP could easily
switch from least-cost path routing to a more hand-tailored approach to routing.
Indeed, since the controller can tailor the flow tables as it pleases, it can implement any form of forwarding that it pleases—simply by changing its
application-control software. This ease of change should be contrasted to the case
of a traditional per-router control plane, where software in all routers (which
might be provided to the ISP by multiple independent vendors) must be changed.

Principles in Practice
SDN Controller Case Studies:
The ONOS and Orion Controllers
In the earliest days of SDN, there was a single SDN protocol (OpenFlow [McKeown
2008; OpenFlow 2025]) and a single SDN controller (NOX [Gude 2008]). Since then,
the number of SDN controllers in particular has grown significantly [Kreutz 2015].
Some SDN controllers are company-specific and proprietary, particularly when
used to control internal proprietary networks (e.g., within or among a company’s
data centers). In this sidebar we describe two SDN controllers that demonstrate how
the principle of a logically centralized is implemented in practice.

The ONOS Controller
Open Network Operating System (ONOS ®) [ONOS 2025] is an open-source SDN
controller created, distributed, and supported by the Open Networking Foundation
[OpenNetworking 2025].




Figure 5.17 ONOS controller architecture

Figure 5.17 presents a simplified view of the ONOS controller Similar to the canonical
controller in Figure 5.15, three layers can be identified in the ONOS controller:

•

Northbound abstractions and protocols. A unique feature of ONOS is its intent
framework, which allows an application to request a high-level service (e.g., to
setup a connection between host A and Host B, or conversely to not allow Host
A and host B to communicate) without having to know the details of how this
service is performed. State information is provided to network-­control applications across the northbound API either synchronously (via query) or asynchronously (via listener callbacks, e.g., when network state changes).

•

Distributed core. The state of the network’s links, hosts, and devices is maintained in ONOS’s distributed core. ONOS is deployed as a service on a set of
interconnected servers, with each server running an identical copy of the ONOS
software; an increased number of servers offers an increased service capacity.
The ONOS core provides the mechanisms for service replication and coordination among instances, providing the applications above and the network devices
below with the abstraction of logically centralized core services.

•

Southbound abstractions and protocols. The southbound abstractions mask the heterogeneity of the underlying hosts, links, switches, and protocols, allowing the
distributed core to be both device and protocol agnostic. Because of this abstraction, the southbound interface below the distributed core is logically higher
than in our canonical controller in Figure 5.14.

Orion
Orion [Ferguson 2021] is the second-generation SDN platform used to control
Google’s Jupiter datacenter networks [Singh 2015] as well as the internal B4


The Network Layer: Control plane


wide-area network [Jain 2013] that globally connects these data centers. Figure 5.18
presents of high-level view of Orion. Orion’s overall structure and context are
remarkably similar to that of ONOS, shown in Figure 5.17. Indeed, the Orion creators
note [Ferguson 2021] how the “architecture of Orion . . . maps to the textbook ONF
view” [ONF 2013]. We see the Orion SDN core at the center of Figure 7.18, with a
northbound interface to the Orion apps, and a southbound interface to the Orioncontrolled routers and switches. But we can find many important differences from
ONOS beneath this common high-level view.
Each Google network is divided into one or more domains, with an Orion SDN
controller instance being responsible for managing and controlling the devices within
its domain. The use of domains purposefully limits the scope and impact of any
failures, as well as the amount of work that must be performed by an Orion controller.
At the heart of the Orion core is the Network Information Base (NIB). The
NIB is a logically centralized data store, coupled with a data-driven publication/
subscribe (pub/sub) system for that allows Orion apps and core components to
read/write NIB data, as well as receive notifications when NIB data changes. A
logically centralized data store also has the advantage of globally ordering network
events, which significantly helps with debugging and trouble-shooting problems.
[Ferguson 2021] notes “Based on years of experience, the NIB has been one of our
most successful design elements.” An Orion MIB can process roughly a million
read/write events per second.
The following components, implemented as microservices, are found in the
Orion core:

•

The Topology Manager maintains the state of the links, routers and switches in
the Orion controller’s domain. It also queries and receives runtime port statistics.

•

The Config Manager configures components in the Orion controller’s domain
by setting configuration parameter properties in the MIB table. The Config
­Manager can also check and validate configurations for correctness.

•

The Flow Manager ensures that the intended network state and behavior registered by apps in the NIB matches with the collective state reported by the controlled devices, and performs flow state reconciliation, as needed.

Figure 5.18 Google’s

Orion SDN


The Orion apps sit above the Orion core and interact with each other and
with other Orion components via the NIB. The Routing Engine is the intra-domain
routing app, and provides the abstracted topology and reachability information
needed by interdomain routing apps, e.g., Raven, and datacenter spline routing
apps, e.g., IBR-C. The TE app shown in Figure 7.18 performs traffic engineering and
the Path Exporter app exports data-plane state to services outside of Orion.
Orion enables an approach to network management and control known as
intent-based networking. [Ferguson 2021] notes that “Intent-based networks
specify management or design changes by describing the new intended end-state
of the network (the “what”) rather than prescribing the sequence of modification to
bring the network to that end-state (the “how”). For example, the intended network
topology is specified in terms of an abstract model [Mogul 2020]. This is high-level
intent and is authoritative in that it then requires that lower-level network apps (e.g.,
link activation, routing apps) to monitor, set and change their configurations so that
this high-level intent is met. Intent thus propagates top-down and remains stable
of longer time scales; network state, and the changes needed to reconcile network
state with high-level intent occur bottom up and change more rapidly as network
conditions change. Intent, configuration settings, and monitored device state are all
stored in NIB, and the NIB’s pub/sub mechanism is used to notify apps when they
need to take actions in response to a changed NIB value. For a discussion of Orion’s
intent-based networking, see [Ferguson 2021].


### 5.5.4 SDN: Past and Future

Although the intense interest in SDN is a relatively recent phenomenon, a number of SDN’s technical roots—the separation of the data and control planes in
particular—go back considerably further. The ARPAnet, the ancestor of today’s
Internet, purposefully emphasized a decentralized protocol-based approach to
network control. However, two other data networks from the early 1970’s fully
embraced centralized control and a clear separation of data and control planes.
TYMNET I [Tymes 1981] was a virtual-circuit data network that had a centralized controller with a physically separate tree-based control network connecting
the control portions of TYMNET nodes to the centralized controller at the root
of the tree. The data-plane of TYMNET I nodes, however, could be connected in
an arbitrary mesh topology. AT&T’s Spider network [Fraser 1993] also had a
clear data/control-plane separation, with a dedicated virtual circuit reserved
for sending control message to/from a node and the centralized controller.
In the 1990s and into the 2000s, data/control plane separation again came
to the forefront. [van der Merwe 1998] describes a control framework for ATM
networks [Black 1995] with multiple controllers, each controlling a number of
ATM switches. In 2004, [Feamster 2004; Lakshman 2004; RFC 3746] all argued
for the separation of the network’s data and control planes. In addition to logically- centralized control and data/control plane separation, other attributes
often associated with SDN include network virtualization, softwareization,
and programmability. [Feamster 2014; Anenousis 2021] both delve into the
­history of the concepts underlying SDN.
The Ethane project [Casado 2007] pioneered the notion of a network of
simple flow-based Ethernet switches with match-plus-action flow tables, a
centralized controller that managed flow admission and routing, and the forwarding of unmatched packets from the switch to the controller. A network of


The Network Layer: Control plane

more than 300 Ethane switches was operational in 2007. Ethane quickly
evolved into the OpenFlow project, and the rest (as the saying goes) is history!
Numerous research efforts are aimed at developing future SDN architectures and capabilities. As we have seen, the SDN revolution is leading to the
disruptive replacement of dedicated monolithic switches and routers (with both
data and control planes) by simple commodity switching hardware and a
sophisticated software control plane. A generalization of SDN known as network functions virtualization (NFV) (which we discussed earlier in Section 4.5)
similarly aims at disruptive replacement of sophisticated middleboxes (such as
middleboxes with dedicated hardware and proprietary software for media
­caching/service) with simple commodity servers, switching, and storage.
Another important challenge is to structure SDN controllers to be robust with
respect to failures (e.g., router or computer crashes, loss of connectivity) and to
be able to recover rapidly when failures do occur [Ferguson 2021; Krentsel 2024].


## 5.6 ICMP: The Internet Control

Message Protocol
The Internet Control Message Protocol (ICMP), specified in [RFC 792], is used
by hosts and routers to communicate network-layer information to each other.
The most typical use of ICMP is for error reporting. For example, when running an HTTP session, you may have encountered an error message such as
“Destination network unreachable.” This message had its origins in ICMP. At
some point, an IP router was unable to find a path to the host specified in your
HTTP request. That router created and sent an ICMP message to your host
indicating the error.
ICMP is often considered part of IP, but architecturally it lies just above IP,
as ICMP messages are carried inside IP datagrams. That is, ICMP messages are
carried as IP payload, just as TCP or UDP segments are carried as IP payload.
Similarly, when a host receives an IP datagram with ICMP specified as the
upper-layer protocol (an upper-layer protocol number of 1), it demultiplexes
the datagram’s contents to ICMP, just as it would demultiplex a datagram’s
content to TCP or UDP.
ICMP messages have a type and a code field, and contain the header and
the first 8 bytes of the IP datagram that caused the ICMP message to be generated in the first place (so that the sender can determine the datagram that
caused the error). Selected ICMP message types are shown in Figure 5.19. Note
that ICMP messages are used not only for signaling error conditions.
The well-known ping program sends an ICMP type 8 code 0 message to
the specified host. The destination host, seeing the echo request, sends back a
type 0 code 0 ICMP echo reply. Most TCP/IP implementations support the
ping server directly in the operating system; that is, the server is not a process.
system to generate an ICMP message of type 8 code 0.
In Chapter 1, we introduced the Traceroute program, which allows us to
trace a route from a host to any other host in the world. Interestingly,




Figure 5.19 ICMP

message types

Traceroute is implemented with ICMP messages. To determine the names and
addresses of the routers between source and destination, Traceroute in the source
sends a series of ordinary IP datagrams to the destination. Each of these datagrams
carries a UDP segment with an unlikely UDP port number. The first of these datagrams has a TTL of 1, the second of 2, the third of 3, and so on. The source also
starts timers for each of the datagrams. When the nth datagram arrives at the nth
router, the nth router observes that the TTL of the datagram has just expired.
According to the rules of the IP protocol, a router must discard a datagram when
the datagram’s TTL has expired. In addition, the router typically sends an ICMP
warning message to the source (type 11 code 0). This warning message includes
the name of the router and its IP address. When this ICMP message arrives back at
the source, the source obtains the round-trip time from the timer and the name
and IP address of the nth router from the ICMP message.
How does a Traceroute source know when to stop sending UDP segments?
Recall that the source increments the TTL field for each datagram it sends. Thus,
one of the datagrams will eventually make it all the way to the destination host.
Because this datagram contains a UDP segment with an unlikely port number,
the destination host sends a port unreachable ICMP message (type 3 code 3)
back to the source. When the source host receives this particular ICMP message,
it knows it does not need to send additional probe packets. (The standard
­Traceroute program actually sends sets of three packets with the same TTL;
thus, the Traceroute output provides three results for each TTL.)
In this manner, the source host learns the number and the identities of
routers that lie between it and the destination host and the round-trip time
between the two hosts. Note that the Traceroute client program must be able to
instruct the operating system to generate UDP datagrams with specific TTL
values and must also be able to be notified by its operating system when ICMP
messages arrive. Now that you understand how Traceroute works, you may
want to go back and play with it some more.


The Network Layer: Control plane

A new version of ICMP has been defined for IPv6 in RFC 4443. In addition
to reorganizing the existing ICMP type and code definitions, ICMPv6
also added new types and codes required by the new IPv6 functionality. These
include the “Packet Too Big” type and an “unrecognized IPv6 options”
error code.


## 5.7 Network Management and

SNMP, NETCONF/YANG
Having now made our way to the end of our study of the network layer, with
only the link-layer before us, we’re well aware that a network consists of many
complex, interacting pieces of hardware and software—from the links,
switches, routers, hosts, and other devices that comprise the physical components of the network to the many protocols that control and coordinate these
devices. When hundreds or thousands of such components are brought
together by an organization to form a network, the job of the network administrator to keep the network “up and running” is surely a challenge. We saw in
Section 5.5 that the logically centralized controller can help with this process in
an SDN context. But the challenge of network management has been around
long before SDN, with a rich set of network management tools and approaches
that help the network administrator monitor, manage, and control the network. We’ll study these tools and techniques in this section, as well as new
tools and techniques that have co-evolved along with SDN.
An often-asked question is “What is network management?” A wellconceived, single-sentence (albeit a rather long run-on sentence) definition
of network management from [Saydam 1996] is:

Network management includes the deployment, integration,
and coordination of the hardware, software, and human elements to monitor, test, poll, configure, analyze, evaluate, and
control the network and element resources to meet the real-time,
operational performance, and Quality of Service requirements
at a reasonable cost.
Given this broad definition, we’ll cover only the rudiments of network
management in this section—the architecture, protocols, and data used by a
network administrator in performing their task. We’ll not cover the administrator’s decision-making processes, where topics such as fault identification
[Labovitz 1997; Steinder 2002; Feamster 2005; Wu 2005; Teixeira 2006], anomaly detection [Lakhina 2005; Barford 2009], network design/engineering to
meet contracted Service Level Agreements (SLA’s) [Huston 1999a], and more
come into consideration. Our focus is thus purposefully narrow; the interested
reader should consult these references, the excellent overviews in [Subramanian 2000; Schonwalder 2010; Claise 2019], and the more detailed treatment of
network management available on the Web site for this text.





### 5.7.1 The Network Management

Framework
Figure 5.20 shows the key components of network management:
* Managing server. The managing server is an application, typically with
­network managers (humans) in the loop, running in a centralized n
­ etwork
management station in the network operations center (NOC). The managing server is the locus of activity for network management: it controls the
collection, processing, analysis, and dispatching of network management
information and commands. It is here that actions are initiated to configure, monitor, and control the network’s managed devices. In practice, a
network may have several such managing servers.
* Managed device. A managed device is a piece of network equipment
(including its software) that resides on a managed network. A managed
device might be a host, router, switch, middlebox, modem, thermometer,
or other network-connected device. The device itself will have many manageable components (e.g., a network interface is but one component of a
host or router), and configuration parameters for these hardware and software components (e.g., an intra-AS routing protocol, such as OSPF).
* Data. Each managed device will have data, also known as “state,” associated with it. There are several different types of data. Configuration data
is device information explicitly configured by the network manager, for
example, a manager-assigned/configured IP address or interface speed
for a device interface. Operational data is information that the device
acquires as it operates, for example, the list of immediate neighbors in
OSPF protocol. Device statistics are status indicators and counts that are
updated as the device operators (e.g., the number of dropped packets on
an interface, or the device’s cooling fan speed). The network manager can
query remote device data, and in some cases, control the remote device by
writing device data values, as discussed below. As shown in Figure 5.20,
the managing server also maintains its own copy of configuration, operational and statistics data from its managed devices as well as networkwide data (e.g., the network’s topology).
* Network management agent. The network management agent is a software
process running in the managed device that communicates with the managing server, taking local actions at the managed device under the command and control of the managing server. The network management
agent is similar to the routing agent that we saw in Figure 5.2.
* Network management protocol. The final component of a network management framework is the network management protocol. This protocol runs
between the managing server and the managed devices, allowing the
managing server to query the status of managed devices and take actions
at these devices via its agents. Agents can use the network management
protocol to inform the managing server of exceptional events (e.g., component failures or violation of performance thresholds). It’s important to
note that the network management protocol does not itself manage the
network. Instead, it provides capabilities that network managers can use


The Network Layer: Control plane


Figure 5.20 Elements
of network management

to manage (“monitor, test, poll, configure, analyze, evaluate, and control”)
the network. This is a subtle, but important, distinction.
In practice, there are three commonly used ways in a network operator
can manage the network, using the components described above:
* CLI. A network operator may issue direct Command Line Interface (CLI)
commands to the device. These commands can be typed directly on a managed device’s console (if the operator is physically present at the device), or
over a Telnet or secure shell (SSH) connection, possibly via scripting,
between the managing server/controller and the managed device. CLI
commands are vendor- and device-specific and can be rather arcane. While
seasoned network wizards may be able to use CLI to flawlessly configure
network devices, CLI use is prone to errors, and it is difficult to automate
or efficiently scale for large networks. Consumer-oriented network devices,
such as your wireless home router, may export a management menu that
you (the network manager!) can access via HTTP to configure that device.
While this approach may work well for single, simple devices and is less
error-prone than CLI, it also doesn’t scale to larger-sized networks.
* SNMP/MIB. In this approach, the network operator can query/set the
data contained in a device’s Management Information Base (MIB) objects
using the Simple Network Management Protocol (SNMP). Some MIBs
are device- and vendor-specific, while other MIBs (e.g., the number of IP
datagrams discarded at a router due to errors in an IP datagram header, or
the number of UDP segments received at a host) are device-agnostic, providing abstraction and generality. A network operator would most typically use this approach to query and monitor operational state and device
statistics, and then use CLI to actively control/configure the device. We
note, importantly, that both approaches manage devices individually. We’ll


cover the SNMP and MIBs, which have been in use since the late 1980s, in
Section 5.7.2 below. A network-management workshop convened by the
Internet Architecture Board in 2002 [RFC 3535] noted not only the value of
the SNMP/MIB approach for device monitoring but also noted its shortcomings, particularly for device configuration and network management
at scale. This gave rise to the most recent approach for network management, using NETCONF and YANG.
* NETCONF/YANG. The NETCONF/YANG approach takes a more abstract,
network-wide, and holistic view toward network management, with a
much stronger emphasis on configuration management, including specifying correctness constraints and providing atomic management operations over multiple controlled devices. YANG [RFC 6020] is a data
modeling language used to model configuration and operational data.
The NETCONF protocol [RFC 6241] is used to communicate YANG-­
compatible actions and data to/from/among remote devices.


### 5.7.2 The Simple Network Management

Protocol (SNMP) and the
Management Information Base (MIB)
The Simple Network Management Protocol version 3 (SNMPv3) [RFC 3410]
is an application-layer protocol used to convey network-management control
and information messages between a managing server and an agent executing
on behalf of that managing server. The most common usage of SNMP is in a
request-response mode in which an SNMP managing server sends a request to
an SNMP agent, who receives the request, performs some action, and sends a
reply to the request. Typically, a request will be used to query (retrieve) or
modify (set) MIB object values associated with a managed device. A second
common usage of SNMP is for an agent to send an unsolicited message, known
as a trap message, to a managing server. Trap messages are used to notify a
managing server of an exceptional situation (e.g., a link interface going up or
down) that has resulted in changes to MIB object values.
MIB objects are specified in a data description language known as SMI
(Structure of Management Information) [RFC 2578; RFC 2579; RFC 2580], a
rather oddly named component of the network management framework
whose name gives no hint of its functionality. A formal definition language is
used to ensure that the syntax and semantics of the network management data
are well defined and unambiguous. Related MIB objects are gathered into MIB
modules. As of late 2024, there are more than 400 MIB-related RFCs and a
much larger number of vendor-specific (private) MIB modules.
SNMPv3 defines seven types of messages, known generically as protocol
data units—PDUs—as shown in Table 5.2 and described below.
* The GetRequest, GetNextRequest, and GetBulkRequest PDUs are
all sent from a managing server to an agent to request the value of one or
more MIB objects at the agent’s managed device. The MIB objects whose
values are being requested are specified in the variable binding portion of
the PDU. GetRequest, GetNextRequest, and GetBulkRequest differ


The Network Layer: Control plane

Table 5.2 SNMPv3 PDU types
SNMPv3 PDU Type

Sender-receiver

Description

GetRequest

manager-to-agent

get value of one or more MIB object instances

GetNextRequest

manager-to-agent

get value of next MIB object instance in list or table

GetBulkRequest

manager-to-agent

get values in large block of data, for example, values in a large table

InformRequest

manager-to-manager

inform remote managing entity of MIB values remote to its access

SetRequest

manager-to-agent

set value of one or more MIB object instances

Response

agent-to-manager or

generated in response to

manager-to-manager

GetRequest,
GetNextRequest,
GetBulkRequest,
SetRequest PDU, or
InformRequest

SNMPv2-Trap

agent-to-manager

inform manager of an exceptional event #

in the granularity of their data requests. GetRequest can request an arbitrary set of MIB values; multiple GetNextRequests can be used to
sequence through a list or table of MIB objects; GetBulkRequest allows
a large block of data to be returned, avoiding the overhead incurred if
multiple GetRequest or GetNextRequest messages were to be sent. In
all three cases, the agent responds with a Response PDU containing the
object identifiers and their associated values.
* The SetRequest PDU is used by a managing server to set the value of
one or more MIB objects in a managed device. An agent replies with a
Response PDU with the “noError” error status to confirm that the value
has indeed been set.
* The InformRequest PDU is used by a managing server to notify another
managing server of MIB information that is remote to the receiving server.
* The Response PDU is typically sent from a managed device to the managing server in response to a request message from that server, returning the
requested information.
* The final type of SNMPv3 PDU is the trap message. Trap messages are
generated asynchronously; that is, they are not generated in response to a
received request but rather in response to an event for which the managing server requires notification. RFC 3418 defines well-known trap types
that include a cold or warm start by a device, a link going up or down, the
loss of a neighbor, or an authentication failure event. A received trap
request has no required response from a managing server.
Given the request-response nature of SNMP, it is worth noting here that
although SNMP PDUs can be carried via many different transport protocols,
the SNMP PDU is typically carried in the payload of a UDP datagram. Indeed,
RFC 3417 states that UDP is “the preferred transport mapping.” However,
since UDP is an unreliable transport protocol, there is no guarantee that a
request, or its response, will be received at the intended destination. Interestingly, SNMP standard does not mandate any particular procedure for



retransmission, or even if retransmission is to be done in the first place. It only
requires that the managing server “needs to act responsibly in respect to the
frequency and duration of retransmissions.” This, of course, leads one to wonder how a “responsible” protocol should act!
SNMP has evolved through three versions. The designers of SNMPv3
have said that “SNMPv3 can be thought of as SNMPv2 with additional security and administration capabilities” [RFC 3410]. Certainly, there are changes
in SNMPv3 over SNMPv2, but nowhere are those changes more evident than
in the area of administration and security. The central role of security in
SNMPv3 was particularly important, since the lack of adequate security
resulted in SNMP being used primarily for monitoring rather than control (for
example, SetRequest is rarely used in SNMPv1). Once again, we see that
security—a topic we’ll cover in detail in Chapter 8 — is of critical concern, but
once again a concern whose importance had been realized perhaps a bit late
and only then “added on.”

The Management Information Base (MIB)
We learned earlier that a managed device’s operational state data (and to some
extent its configuration data) in the SNMP/MIB approach to network management are represented as objects that are gathered together into an MIB for that
device. An MIB object might be a counter, such as the number of IP datagrams
discarded at a router due to errors in an IP datagram header; or the number of
carrier sense errors in an Ethernet interface card; descriptive information such
as the version of the software running on a DNS server; status information such
as whether a particular device is functioning correctly; or protocol-specific
information such as a routing path to a destination. Related MIB objects are
gathered into MIB modules. There are over 400 MIB modules defined in various IETC RFC’s; there are many more device- and vendor-specific MIBs. [RFC
4293] specifies the MIB module that defines managed objects (including ipSystemStatsInDelivers) for managing implementations of the Internet Protocol (IP)
and its associated Internet Control Message Protocol (ICMP). [RFC 4022] specifies the MIB module for TCP, and [RFC 4113] specifies the MIB module for UDP.
While MIB-related RFCs make for rather tedious and dry reading, it is
nonetheless instructive (i.e., like eating vegetables, it is “good for you”) to consider an example of a MIB object, The ipSystem-StatsInDelivers
object-type definition from [RFC 4293] defines a 32-bit read-only counter that
keeps track of the number of IP datagrams that were received at the managed
device and were successfully delivered to an upper-layer protocol. In the
example below, Counter32 is one of the basic data types defined in the SMI.
ipSystemStatsInDelivers OBJECT-TYPE
SYNTAX Counter32
MAX-ACCESS read-only
STATUS current
DESCRIPTION
“The total number of datagrams successfully delivered to IPuser-protocols (including ICMP).
...
::= { ipSystemStatsEntry 18 }


The Network Layer: Control plane



### 5.7.3 The Network Configuration Protocol

(NETCONF) and YANG
The NETCONF protocol operates between the managing server and the managed network devices, providing messaging to (i) retrieve, set, and modify
configuration data at managed devices; (ii) to query operational data and statistics at managed devices; and (iii) to subscribe to notifications generated by
managed devices. The managing server actively controls a managed device by
sending it configurations, which are specified in a structured XML document,
and activating a configuration at the managed device. NETCONF uses a
remote procedure call (RPC) paradigm, where protocol messages are also
encoded in XML and exchanged between the managing server and a managed
device over a secure, connection-oriented session such as the TLS (Transport
Layer Security) protocol (discussed in Chapter 8) over TCP.
Figure 5.21 shows an example NETCONF session. First, the managing
server establishes a secure connection to the managed device. (In NETCONF
parlance, the managing server is actually referred to as the “client” and the
managed device as the “server,” since the managing server establishes the connection to the managed device. But we’ll ignore that here for consistency with
the longer-standing network-management server/client terminology shown in
Figure 5.20.) Once a secure connection has been established, the managing
server and the managed device exchange <hello> messages, declaring their
“capabilities”—NETCONF functionality that supplements the base NETCONF
specification in [RFC 6241]. Interactions between the managing server and
managed device take the form of a remote procedure call, using the <rpc>
and <rpc-response> messages. These messages are used to retrieve, set, query
and modify device configurations, operational data and statistics, and to

Figure 5.21 NETCONF
session between
managing server/controller
and managed device



Table 5.3 Selected NETCONF operations
NETCONF Operation

Description

<get-config>

Retrieve all or part of a given configuration. A device may have multiple configurations. There is always
a running/configuration that describes the devices current (running) configuration.

<get>

Retrieve all or part of both configuration state and operational state data.

<edit-config>

Change all or part of a specified configuration at the managed device. If the running/configuration is
specified, then the device’s current (running) configuration will be changed. If the managed device was
able to satisfy the request, an <rpc-reply> is sent containing an <ok> element; otherwise <rpc-error>
response is returned. On error, the device’s configuration state can be roll-ed-back to its previous state.

<lock>, <unlock>

The <lock> (<unlock>) operation allows the managing server to lock (unlock) the entire configuration
datastore system of a managed device. Locks are intended to be short-lived and allow a client to make a
change without fear of interaction with other NETCONF, SNMP, or CLIs commands from other sources.

<createsubscription>,
<notification>

This operation initiates an event notification subscription that will send asynchronous event
<notification> for specified events of interest from the managed device to the managing server, until the
subscription is terminated.

subscribe to device notifications. Device notifications themselves are proactively sent from managed device to the managing server using NETCONF
<notification> messages. A session is closed with the <session-close message>.
Table 5.3 shows a number of the important NETCONF operations that a
managing server can perform at a managed device. As in the case of SNMP, we
see operations for retrieving operational state data (<get>), and for event notification. However, the <get-config>, <edit-config>, <lock> and <unlock>
operation demonstrate NETCONF’s particular emphasis on device configuration. Using the basic operations shown in Table 5.3, it is also possible to create a
set of more sophisticated network management transactions that either complete atomically (i.e., as a group) and successfully on a set of devices, or are
fully reversed and leave the devices in their pre-transaction state. Such multidevice transactions—“enabl[ing] operators to concentrate on the configuration
of the network as a whole rather than individual devices” was an important
operator requirement put forth in [RFC 3535].
A full description of NETCONF is beyond our scope here; [RFC 6241,
RFC 5277, Claise 2019; Schonwalder 2010] provide more in-depth coverage.

YANG
YANG is the data modeling language used to precisely specify the structure,
syntax, and semantics of network management data used by NETCONF, in
much the same way that the SMI is used to specify MIBs in SNMP. All YANG
definitions are contained in modules, and an XML document describing a
device and its capabilities can be generated from a YANG module.
YANG features a small set of built-in data types (as in the case of SMI) and
also allows data modelers to express constraints that must be satisfied by a
valid NETCONF configuration—a powerful aid in helping ensure that NETCONF configurations satisfy specified correctness and consistency constraints.
YANG is also used to specify NETCONF notifications.
A fuller discussion of YANG is beyond our scope here. For more information, we refer the interested reader to the excellent book [Claise 2019].


The Network Layer: Control plane



## 5.8 Summary

We have now completed our two-chapter journey into the network core—a
journey that began with our study of the network layer’s data plane in Chapter
4 and finished here with our study of the network layer’s control plane. We
learned that the control plane is the network-wide logic that controls not only
how a datagram is forwarded among routers along an end-to-end path from
the source host to the destination host, but also how network-layer components and services are configured and managed.
We learned that there are two broad approaches towards building a control plane: traditional per-router control (where a routing algorithm runs in each
and every router and the routing component in the router communicates with
the routing components in other routers) and software-defined networking (SDN)
control (where a logically centralized controller computes and distributes the
forwarding tables to be used by each and every router). We studied two fundamental routing algorithms for computing least cost paths in a graph—link-state
routing and distance-vector routing—in Section 5.2; these algorithms find
application in both per-router control and in SDN control. These algorithms
are the basis for two widely deployed Internet routing protocols, OSPF and
BGP, that we covered in Sections 5.3 and 5.4. We covered the SDN approach to
the network-layer control plane in Section 5.5, investigating SDN networkcontrol applications, the SDN controller, and the OpenFlow protocol for
communicating between the controller and SDN-controlled devices. In Sections 5.6 and 5.7, we covered some of the nuts and bolts of managing an IP
network: ICMP (the Internet Control Message Protocol) and network management using SNMP and NETCONF/YANG.
Having completed our study of the network layer, our journey now takes us
one step further down the protocol stack, namely, to the link layer. Like the network layer, the link layer is part of each and every network-connected device.
But we will see in the next chapter that the link layer has the much more localized task of moving packets between nodes on the same link or LAN. Although
this task may appear on the surface to be rather simple compared with that of
the network layer’s tasks, we will see that the link layer involves a number of
important and fascinating issues that can keep us busy for a long time.

Homework Problems and Questions
Section 5.1
R1. What is meant by a control plane that is based on
per-router control? In such cases, when we say
the network control and data planes are implemented “monolithically,” what do we mean?
R2. What is meant by a control plane that is based
on logically centralized control? In such cases,

are the data plane and the control plane
implemented within the same device or in
separate devices? Explain.

Section 5.2
R3. Compare and contrast the properties of a centralized and a distributed routing algorithm.
Give an example of a routing protocol that takes
a centralized and a decentralized approach.


R4. Compare and contrast link-state and distancevector routing algorithms.

layer, and the network-control application
layer in an SDN controller.

R5. What is the “count to infinity” problem in distance vector routing?

R15. Suppose you wanted to implement a new
routing protocol in the SDN control plane. At
which layer would you implement that protocol? Explain.

R6. Is it necessary that every autonomous system
use the same intra-AS routing algorithm?
Why or why not?

Sections 5.3–5.4
R7. Why are different inter-AS and intra-AS protocols used in the Internet?
R8. True or false: When an OSPF route sends its
link state information, it is sent only to those
nodes directly attached neighbors. Explain.
R9. What is meant by an area in an OSPF autonomous system? Why was the concept of an area
introduced?
R10. Define and contrast the following terms:
­subnet, prefix, and BGP route.
R11. How does BGP use the NEXT-HOP attribute?
How does it use the AS-PATH attribute?
R12. Describe how a network administrator of an
upper-tier ISP can implement policy when
configuring BGP.
R13. True or false: When a BGP router receives an
advertised path from its neighbor, it must add
its own identity to the received path and then
send that new path on to all of its neighbors.
Explain.

Section 5.5
R14. Describe the main role of the communication
layer, the network-wide state-management

R16. What types of messages flow across an SDN
controller ’s northbound and southbound
APIs? Who is the recipient of these messages
sent from the controller across the southbound
interface, and who sends messages to the controller across the northbound interface?
R17. Describe the purpose of two types of OpenFlow messages (of your choosing) that are sent
from a controlled device to the controller.
Describe the purpose of two types of Openflow messages (of your choosing) that are send
from the controller to a controlled device.
R18. What is the purpose of the service abstraction
layer in the OpenDaylight SDN controller?

Sections 5.6–5.7
R19. Names four different types of ICMP messages
R20. What two types of ICMP messages are
received at the sending host executing the
­Traceroute program?
R21. Define the following terms in the context of
SNMP: managing server, managed device, network management agent and MIB.
R22. What are the purposes of the SNMP ­GetRequest
and SetRequest messages?
R23. What is the purpose of the SNMP trap message?

Problems
P1. Looking at Figure 5.3, enumerate the paths from y to u that do not contain any loops.
P2. Repeat Problem P1 for paths from x to z, z to u, and z to w.
P3. Consider the following network. With the indicated link costs, use Dijkstra’s shortest-path algorithm to compute the shortest path from x to all
network nodes. Show how the algorithm works by computing a table
similar to Table 5.1.


The Network Layer: Control plane

P4. Consider the network shown in Problem P3. Using Dijkstra’s algorithm,
and showing your work using a table similar to Table 5.1, do the
following:
a. Compute the shortest path from t to all network nodes.
b. Compute the shortest path from u to all network nodes.
c. Compute the shortest path from v to all network nodes.
d. Compute the shortest path from w to all network nodes.
e. Compute the shortest path from y to all network nodes.
f. Compute the shortest path from z to all network nodes.
P5. Consider the network shown below, and assume that each node initially
knows the costs to each of its neighbors. Consider the distance-vector
algorithm and show the distance table entries at node z.

P6. Consider a general topology (that is, not the specific network shown
above) and a synchronous version of the distance-vector algorithm. Suppose that at each iteration, a node exchanges its distance vectors with its
neighbors and receives their distance vectors. Assuming that the algorithm begins with each node knowing only the costs to its immediate
neighbors, what is the maximum number of iterations required before
the distributed algorithm converges? Justify your answer.
P7. Consider the network fragment shown below. x has only two attached
neighbors, w and y. w has a minimum-cost path to destination u (not
shown) of 5, and y has a minimum-cost path to u of 6. The complete
paths from w and y to u (and between w and y) are not shown. All link
costs in the network have strictly positive integer values.



a. Give x’s distance vector for destinations w , y , and u.
b. Give a link-cost change for either c ( x , w ) or c ( x , y ) such that x will
inform its neighbors of a new minimum-cost path to u as a result of
executing the distance-vector algorithm.
c. Give a link-cost change for either c ( x , w ) or c ( x , y ) such that x will not
inform its neighbors of a new minimum-cost path to u as a result of
executing the distance-vector algorithm.
P8. Consider the three-node topology shown in Figure 5.6. Rather than having the link costs shown in Figure 5.6, the link costs are c ( x , y ) = 3 ,
c ( y , z ) = 6, c ( z , x ) = 4. Compute the distance tables after the initialization step and after each iteration of a synchronous version of the distance-vector algorithm (as we did in our earlier discussion of Figure 5.6).
P9. Consider the count-to-infinity problem in the distance vector routing.
Will the count-to-infinity problem occur if we decrease the cost of a link?
Why? How about if we connect two nodes which do not have a link?
P10. Argue that for the distance-vector algorithm in Figure 5.6, each value in
the distance vector D ( x ) is non-increasing and will eventually stabilize
in a finite number of steps.
P11. Consider Figure 5.7. Suppose there is another router w, connected to
router y and z. The costs of all links are given as follows: c ( x , y ) = 4 ,
c ( x , z ) = 50 , c ( y , w ) = 1, c ( z , w ) = 1, c ( y , z ) = 3. Suppose that poisoned reverse is used in the distance-vector routing algorithm.
a. When the distance vector routing is stabilized, router w , y , and z
inform their distances to x to each other. What distance values do they
tell each other?
b. Now suppose that the link cost between x and y increases to 60. Will
there be a count-to-infinity problem even if poisoned reverse is used?
Why or why not? If there is a count-to-infinity problem, then how
many iterations are needed for the distance-vector routing to reach a
stable state again? Justify your answer.
c. How do you modify c ( y , z ) such that there is no count-to-infinity
problem at all if c ( y , x ) changes from 4 to 60?
P12. Describe how loops in paths can be detected in BGP.
P13. Will a BGP router always choose the loop-free route with the shortest
ASpath length? Justify your answer.
P14. Consider the network shown below. Suppose AS3 and AS2 are running
OSPF for their intra-AS routing protocol. Suppose AS1 and AS4 are running RIP for their intra-AS routing protocol. Suppose eBGP and iBGP are
used for the inter-AS routing protocol. Initially suppose there is no physical link between AS2 and AS4.
a. Router 3c learns about prefix x from which routing protocol: OSPF,
RIP, eBGP, or iBGP?
b. Router 3a learns about x from which routing protocol?
c. Router 1c learns about x from which routing protocol?
d. Router 1d learns about x from which routing protocol?


The Network Layer: Control plane

P15. Referring to the previous problem, once router 1d learns about x it will
put an entry ( x , I ) in its forwarding table.
a. Will I be equal to I 1 or I 2 for this entry? Explain why in one sentence.
b. Now suppose that there is a physical link between AS2 and AS4,
shown by the dotted line. Suppose router 1d learns that x is accessible
via AS2 as well as via AS3. Will I be set to I 1 or I 2? Explain why in one
sentence.
c. Now suppose there is another AS, called AS5, which lies on the path
between AS2 and AS4 (not shown in diagram). Suppose router 1d
learns that x is accessible via AS2 AS5 AS4 as well as via AS3 AS4.
Will I be set to I 1 or I 2? Explain why in one sentence.
P16. Consider the following network. ISP B provides national backbone service to regional ISP A. ISP C provides national backbone service to
regional ISP D. Each ISP consists of one AS. B and C peer with each other
in two places using BGP. Consider traffic going from A to D. B would
prefer to hand that traffic over to C on the West Coast (so that C would
have to absorb the cost of carrying the traffic cross-country), while C
would prefer to get the traffic via its East Coast peering point with B (so
that B would have carried the traffic across the country). What BGP
mechanism might C use, so that B would hand over A-to-D traffic at its
East Coast peering point? To answer this question, you will need to dig
into the BGP specification.



P17. In Figure 5.13, consider the path information that reaches stub networks
W, X, and Y. Based on the information available at W and X, what are
their respective views of the network topology? Justify your answer. The
topology view at Y is shown below.

P18. Consider Figure 5.13. B would never forward traffic destined to Y via X
based on BGP routing. But there are some very popular applications for
which data packets go to X first and then flow to Y. Identify one such
application, and describe how data packets follow a path not given by
BGP routing.
P19. In Figure 5.13, suppose that there is another stub network V that is a
­customer of ISP A. Suppose that B and C have a peering relationship,
and A is a customer of both B and C. Suppose that A would like to have
the traffic destined to W to come from B only, and the traffic destined to
V from either B or C. How should A advertise its routes to B and C?
What AS routes does C receive?
P20. Suppose ASs X and Z are not directly connected but instead are connected by AS Y. Further suppose that X has a peering agreement with Y,
and that Y has a peering agreement with Z. Finally, suppose that Z wants
to transit all of Y’s traffic but does not want to transit X’s traffic. Does
BGP allow Z to implement this policy?
P21. Consider the two ways in which communication occurs between a
­managing entity and a managed device: request-response mode and
trapping. What are the pros and cons of these two approaches, in terms
of (1) overhead, (2) notification time when exceptional events occur, and
(3) robustness with respect to lost messages between the managing entity
and the device?
P22. In Section 5.7, we saw that it was preferable to transport SNMP messages
in unreliable UDP datagrams. Why do you think the designers of SNMP
chose UDP rather than TCP as the transport protocol of choice for SNMP?

Socket Programming Assignment 5: ICMP Ping
At the end of Chapter 2, there are four socket programming assignments. Here you will find a fifth
assignment which employs ICMP, a protocol discussed in this chapter.
Ping is a popular networking application used
to test from a remote location whether a particular
host is up and reachable. It is also often used to
measure latency between the client host and the

target host. It works by sending ICMP “echo
request” packets (i.e., ping packets) to the target
host and listening for ICMP “echo response” replies
(i.e., pong packets). Ping measures the RRT, records
packet loss, and calculates a statistical summary of
multiple ping-pong exchanges (the minimum,
mean, max, and standard deviation of the roundtrip times).


The Network Layer: Control plane

In this lab, you will write your own Ping application in Python. Your application will use ICMP.
But in order to keep your program simple, you will
not exactly follow the official specification in RFC
1739. Note that you will only need to write the client
side of the program, as the functionality needed on


the server side is built into almost all operating systems. You can find full details of this assignment, as
well as important snippets of the Python code, at
the Web site http://www.pearsonhighered.com/
cs-resources.

Programming Assignment: Routing
In this programming assignment, you will be writing a “distributed” set of procedures that implements a distributed asynchronous distance-vector
routing for the network shown below.
You are to write the following routines that will
“execute” asynchronously within the emulated
environment provided for this assignment. For
node 0, you will write the routines:

* rtinit0(). This routine will be called once at the
beginning of the emulation. rtinit0() has no
arguments. It should initialize your distance
table in node 0 to reflect the direct costs of 1, 3,
and 7 to nodes 1, 2, and 3, respectively. In the
figure above, all links are bidirectional and the
costs in both directions are identical. After initializing the distance table and any other data
structures needed by your node 0 routines, it
should then send its directly connected neighbors (in this case, 1, 2, and 3) the cost of its minimum-cost paths to all other network nodes.
This minimum-cost information is sent to
neighboring nodes in a routing update packet
by calling the routine tolayer2(), as described in
the full assignment. The format of the routing
update packet is also described in the full
assignment.

* rtupdate0(struct rtpkt *rcvdpkt). This routine will
be called when node 0 receives a routing packet
that was sent to it by one of its directly connected
neighbors. The parameter *rcvdpkt is a pointer to
the packet that was received. rtupdate0() is the
“heart” of the distance-vector algorithm. The
values it receives in a routing update packet from
some other node i contain i’s current shortestpath costs to all other network nodes. rtupdate0()
uses these received values to update its own distance table (as specified by the distance-vector
algorithm). If its own minimum cost to another
node changes as a result of the update, node 0
informs its directly connected neighbors of this
change in minimum cost by sending them a
routing packet. Recall that in the distance-vector
algorithm, only directly connected nodes will
exchange routing packets. Thus, nodes 1 and 2
will communicate with each other, but nodes 1
and 3 will not communicate with each other.
Similar routines are defined for nodes 1, 2, and 3.
Thus, you will write eight procedures in all: rtinit0(),
rtinit1(), rtinit2(), rtinit3(), rtupdate0(), rtupdate1(),
rtupdate2(), and rtupdate3(). These routines will
together implement a distributed, asynchronous
computation of the distance tables for the topology
and costs shown in the figure on the preceding page.
You can find the full details of the programming assignment, as well as C code that you will
need to create the simulated hardware/software
environment, at http://www.pearsonhighered.
com/cs-resource. A Java version of the assignment
is also available.

Wireshark Lab: ICMP
In the Web site for this textbook, www.pearsonhighered.com/cs-resources, you’ll find a Wireshark lab

assignment that examines the use of the ICMP protocol in the ping and traceroute commands.



AN INTERVIEW WITH...
Jennifer Rexford
Courtesy of Jennifer Rexford

Jennifer Rexford is the Provost of Princeton University, where she is also a Professor in the Computer Science department. Her research has the broad goal of making computer networks easier to design and manage, with particular emphasis on
programmable networks. Before joining the faculty at Princeton, she worked at
AT&T for eight years, developing techniques and tools for network measurement,
traffic engineering, and router configuration that were deployed in AT&T's backbone network. Jennifer is co-author of the books “Web Protocols and Practice:
Networking Protocols, Caching, and Traffic Measurement” (Addison-Wesley,
2001) and “The Real Internet Architecture: Past, Present, and Future Evolution”
(Princeton University Press, 2024). She served as the chair of ACM SIGCOMM
from 2003 to 2007. She received her BSE degree in electrical engineering from
Princeton University, and her PhD degree in electrical engineering and computer
science from the University of Michigan. Jennifer received the ACM Grace Murray Hopper Award, the ACM SIGCOMM Award, the IEEE Internet Award, and
the IEEE Alexander Graham Bell Medal. She is an ACM Fellow, an IEEE Fellow,
and a member of the National Academy of Engineering and the National Academy of Sciences.

Please describe one or two of the most
exciting projects you have worked on
during your career. What were the biggest
challenges?
When I was a researcher at AT&T, a group of us designed a new way to manage
routing in Internet Service Provider backbone networks. Traditionally, network
operators configure each router individually, and these routers run distributed protocols to compute paths through the network. We believed that network management would be simpler and more flexible if network operators could exercise direct
control over how routers forward traffic based on a network-wide view of the topology and traffic. The Routing Control Platform (RCP) we designed and built could
compute the routes for all of AT&T’s backbone on a single commodity computer, and
could control legacy routers without modification. To me, this project was exciting
because we had a provocative idea, a working system, and ultimately a real deployment in an operational network. Fast forward a few years, and software-defined
networking (SDN) has become a mainstream technology, and standard protocols
(like standard protocols (like OpenFlow) and languages (like P4) have made it much
easier to tell the underlying switches what to do.

How do you think software-defined
networking should evolve in the future?
In a major break from the past, the software controlling network devices can be
created by many different programmers, not just at companies selling network


The Network Layer: Control plane
equipment. Yet, unlike the applications running on a server or a smart phone, SDN
applications must work together to handle the same traffic. Network operators do
not want to perform load balancing on some traffic and routing on other traffic;
instead, they want to perform load balancing and routing, together, on the same
traffic. Future SDN platforms should offer good programming abstractions for
composing independently written multiple applications together. More broadly,
good programming abstractions can make it easier to create applications, without
having to worry about low-level details like flow table entries, traffic counters, bit
patterns in packet headers, and so on. Also, while an SDN controller is logically
centralized, the network still consists of a distributed collection of devices. Future
programmable networks should offer good abstractions for updating a distributed
set of devices, so network administrators can reason about what happens to packets
in flight while the devices are updated. Programming abstractions for programmable network is an exciting area for interdisciplinary research between computer
networking, distributed systems, and programming languages, with a real chance
for practical impact in the years ahead.

Where do you see the future of networking
and the Internet?
Networking is an exciting field because the applications and the underlying technologies change all the time. We are always reinventing ourselves! Who would
have predicted even ten years ago the dominance of smart phones, allowing
mobile users to access existing applications as well as new location-based services?
The emergence of cloud computing is fundamentally changing the relationship
between users and the applications they run, and networked sensors and actuators
(the “Internet of Things”) are enabling a wealth of new applications (and security
vulnerabilities!). The pace of innovation is truly inspiring.
The underlying network is a crucial component in all of these innovations.
Yet, the network is notoriously “in the way”—limiting performance, compromising
reliability, constraining applications, and complicating the deployment and
management of services. We should strive to make the network of the future as
invisible as the air we breathe, so it never stands in the way of new ideas and
valuable services. To do this, we need to raise the level of abstraction above
individual network devices and protocols (and their attendant acronyms!), so we
can reason about the network and the user’s high-level goals as a whole.

What people inspired you professionally?
I’ve long been inspired by Sally Floyd who worked for many years at the International Computer Science Institute. Her research was always purposeful, focusing
on the important challenges facing the Internet. She dug deeply into hard questions
until she understood the problem and the space of solutions completely, and she
devoted serious energy into “making things happen,” such as pushing her ideas
into protocol standards and network equipment. Also, she gave back to the community, through professional service in numerous standards and research organizations and by creating tools (such as the widely used ns-2 and ns-3 simulators) that
enable other researchers to succeed. She retired in 2009, and passed away in 2019,
but her influence on the field will be felt for years to come.




What are your recommendations for
students who want careers in computer
science and networking?
Networking is an inherently interdisciplinary field. Applying techniques from
other discipline’s breakthroughs in networking come from such diverse areas as
queuing theory, game theory, control theory, distributed systems, network optimization, programming languages, machine learning, algorithms, data structures,
and so on. I think that becoming conversant in a related field, or collaborating
closely with experts in those fields, is a wonderful way to put networking on a
stronger foundation, so we can learn how to build networks that are worthy of
society’s trust. Beyond the theoretical disciplines, networking is exciting because
we create real artifacts that real people use. Mastering how to design and build
systems—by gaining experience in operating systems, computer architecture, and
so on—is another fantastic way to amplify your knowledge of networking to help
make the world a better place.



