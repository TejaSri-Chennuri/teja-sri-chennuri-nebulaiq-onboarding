Backend Person 1: Network Protocol Detection & Parsing
Objective: Become the expert in how observability systems capture and parse network traffic.
1. Protocol Detection
What to cover:
- The Problem: Given raw network packets, how do you identify what protocol it is?
- Is it HTTP? gRPC? MySQL? Redis? Kafka? PostgreSQL?

  Actually I thought what is the problem when we are given raw network packets. later now i got clarity that the raw network packets contain only the raw data or raw bytes, but we dont know which protocol it is, there are different protocols like  HTTPS,gPRPC, MySQL, Redis, Kafka, Postgre SQL. In order to find which protocol we use different protocol detection methods. there are 3 types. 
              1. Port - Based Detection
              2. Payload based detection
              3. State machine approach

- Port-Based Detection:
- Using well-known ports (80=HTTP, 3306=MySQL, 6379=Redis)

     Every protocol contains a default port 

                https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2020.jpg

- Limitations: non-standard ports, port reuse

     Actually there are many services they run on non standard ports or on the custom ports and also the containers reuse the port but the limitation is it cannot detect the gRPC AND HTTP particularly.Port based detection is useful as a first guess

- Payload-Based Detection:

    This method detects the content present in the packet.Every protocol has a unique signature.

- Protocol signatures and magic bytes
- HTTP: "GET", "POST", "HTTP/1.1"
     HTTP is very simple and very easy the HTTP request starts with GET, POST or PUT and then the url . HTTP responses start with HTTP/1.1 so that it identifies the protocol versionso that the traffic will be detected.

              https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2024.jpg 
    
- MySQL: packet structure, handshake patterns

    The first packet from server is a handshake packet. This packet contains protocol version and the server version written in ASCII and also it contains capability flags.
The handshake packet will make easy way to understand MYSQL traffic.

            https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2023.jpg

- Redis: RESP protocol format

    Redis uses a lightweight text based protocol called RESP. RESP message start with characters like *, $, +, :, -.
          https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2022.jpg 

- gRPC: HTTP/2 with specific headers
                
             https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2021.jpg

- State Machine Approach:

     Some protocols cannot be identified from a single packet because they involve multi-step communication. In such cases, a state machine approach is used, where the system keeps track of the sequence of messages exchanged in a connection.This approach is extremely useful because it handles multi-step protocols, recovers from missing packets, and helps resolve ambiguous or incomplete patterns. State machines are essential for correctly identifying protocols with complex handshakes or multi-phase interactions.

- Deep Packet Inspection (DPI) techniques
       Sometimes the basic checks—like looking at ports or searching for simple protocol signatures—are not enough to identify what protocol is being used. In these tricky situations, we rely on Deep Packet Inspection (DPI). DPI takes a much closer and more detailed look at the traffic. Instead of checking just the first packet, it observes multiple packets and examines the payload more deeply. It looks for patterns in the bytes, how the messages are structured, and even the behavior of the connection over time.Because DPI studies more information, it is slower and uses more resources, but it is also far more accurate. It is especially helpful when dealing with traffic that looks similar to multiple protocols, when the protocol is custom or has been modified, or when the real protocol is hidden behind tools like proxies or gateways. In short, DPI is the final and most powerful method we use when simple detection techniques fail. It helps ensure that we identify the correct protocol with high confidence, even in the most complicated network scenarios.
                          https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2025.jpg

        Protocol detection is not always easy because real network traffic can behave unpredictably. Sometimes the traffic is encrypted, so we cannot see what is inside the packet. Services may also run on different ports, so port numbers cannot be trusted. Packets may arrive out of order, or a single message may be split into many packets, making it harder to detect the protocol. In some cases, different protocols may look similar in the beginning, causing confusion or wrong detection. Traffic going through proxies or sidecars can also hide the original protocol details. All these situations make protocol detection challenging and require careful handling.

2. eBPF for Network Observability
What to cover:
- What is eBPF?
      eBPF is a technology in the Linux kernel that make us to run small, safe and sandboxed programs inside the kernel without modifying code. Using it we can observe network traffic,trace application behavior,collect metrics,track system events
      
- Why is it revolutionary for observability?

actually observability depend on agents running in user space and heavy tools like tcpdump/pcap but after using ebpf it runs inside the kernel and we will not change any code and it run safe and sandboxed programs.

Manual instrumentation
     it says how eBPF programs attach to different parts of the Linux kernel to observe what the system is doing. At the bottom, there is Linux Kernel, which is where all low-level system operations happen. Above the kernel, there are four different points

    1.kprobes – These attach to kernel functions.

    2.tracepoints – These attach to built-in kernel events.
 when a program calls sys_enter_exec, the eBPF program can capture that event.

    3.XDP – This sits right at the start of the network path.eBPF can see network packets as soon as they arrive, even before the kernel processes them.

    4.Socket filters / cgroup hooks – These attach to socket-level or container-level activities.
Each of these hooks has an eBPF program connected to it. Arrows show how the programs attach to the kernel. 
          
               https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2026.jpg

- eBPF programs and verification
- eBPF maps for data storage

     eBPF programs store data in special memory structures called maps, such as Hash maps, Arrays,LRU caches, Ring buffers.These maps allow data exchange between kernel and user space.
- Ring buffers and perf buffers for data transfer to userspace

            https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2027.jpg

- eBPF for Network Capture:

Because it can record traffic directly within the Linux kernel without requiring complete packet dumps, eBPF is incredibly effective for network observability. It can observe network activity as soon as an application sends or receives data by attaching to socket-level functions like tcp_sendmsg and tcp_recvmsg. eBPF extracts only the crucial L4 and L7 data (such as IPs, ports, HTTP methods, URLs, DNS queries, or SQL commands) rather than copying entire packets like conventional tools do. Zero-copy techniques are used in this selective reading, meaning that data is accessed directly in kernel memory without costly copying operations. Because of its incredibly high performance and low overhead, eBPF can be used for real-time monitoring even on busy systems.

eBPF is significantly lighter than more traditional tools like tcpdump or pcap, and it doesn't require the installation of agents or the addition of instrumentation within applications. It offers kernel-level visibility, allowing it to see everything that occurs in processes, microservices, and containers. It does have certain drawbacks, though, such as the need for eBPF programs to adhere to stringent safety regulations, their inability to execute sophisticated logic, and their restricted visibility into encrypted payloads. Despite these drawbacks, eBPF is still among the safest and most effective methods for recording network activity in contemporary systems.

                       https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2028.jpg

eBPF acts as the data-collection engine at the lowest layer of an observability system. It sits inside the Linux kernel and captures important events On the security side, eBPF programs are extremely safe because the kernel includes a strict verifier that checks every instruction before allowing the program to run eBPF delivers strong performance benefits because it runs inside the kernel and uses techniques like zero-copy data access, selective packet parsing, and event-based capturing.

3. Protocol Parsing Deep Dive
What to cover:
- Pick 2-3 protocols (must include HTTP/1.1 or HTTP/2, plus one database protocol like
MySQL or Redis)
- For each protocol:
- Wire Format: How is data structured in packets?
  1. HTTP/1.1 : HTTP/1.1 is a text-based protocol, so the request and response messages are easy to read in Wireshark. A request normally starts with a line like GET /path HTTP/1.1 followed by a series of headers such as Host, User-Agent, Accept, and Content-Length. The headers always end with a blank line (\r\n\r\n). After this blank line, the body begins, if the request has one. The response also follows a similar format, starting with something like HTTP/1.1 200 OK, then response headers, then a blank line, and finally the response body.

                 https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2029.jpg

 2. MySQL :MySQL uses a binary protocol instead of text like HTTP. Every MySQL packet begins with a small 4-byte header. The first 3 bytes tell you the length of the payload, and the fourth byte is the sequence number. After this header, the actual content of the packet begins. The server starts the communication with a handshake packet, which includes the protocol version and the MySQL server version written in plain text. When the client sends a query, the first byte of the payload tells what type of command it is. For example, if the first byte is 0x03, then the packet contains a SQL query. The query text follows right after this byte in plain ASCII. Wireshark can decode the handshake packet clearly, and you can also see the SQL text when following the TCP stream.

            https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2030.jpg

- Request/Response Parsing:
  1. HTTP/1.1 : To parse an HTTP request, I first collect all the TCP payload data for that connection into a single buffer. Then I scan the buffer to find the header terminator (\r\n\r\n). If it is not there yet, I wait for more data. Once the terminator is found, I split the header block into lines. The first line gives me the method (GET, POST, etc.), the URL or path, and the HTTP version. The remaining lines are key-value headers like Host and User-Agent. If the Content-Length header is present, I read exactly that many bytes after the header section as the body. If the server uses chunked encoding, I would need to decode the chunks, but for basic cases, Content-Length is enough. I also record the timestamp of when the request started and later use it to calculate latency when the response arrives
  2. MySQL : MySQL uses a binary protocol instead of text like HTTP. Every MySQL packet begins with a small 4-byte header. The first 3 bytes tell you the length of the payload, and the fourth byte is the sequence number. After this header, the actual content of the packet begins. The server starts the communication with a handshake packet, which includes the protocol version and the MySQL server version written in plain text. When the client sends a query, the first byte of the payload tells what type of command it is. For example, if the first byte is 0x03, then the packet contains a SQL query. The query text follows right after this byte in plain ASCII. Wireshark can decode the handshake packet clearly, and you can also see the SQL text when following the TCP stream.

- Handling TCP Segmentation:
  1. HTTP/1.1 : HTTP messages do not always come in a single packet. The headers or body can be split across multiple TCP packets. To handle this, I keep a buffer for each TCP connection and append new payload bytes as they arrive. Only when I have enough continuous data in the buffer do I try to parse a full HTTP message. If the request is incomplete, I simply wait for the next packet. Tools like Wireshark automatically reassemble TCP segments, but when writing a parser, I must make sure to handle partial data and only parse when a complete header or body is available.
  2. MySQL : MySQL packets can also be split across multiple TCP segments, especially when the query or the result is large. To handle this, I keep a buffer for each connection and add incoming bytes to it. I only parse a MySQL message when I have at least 4 bytes to read the header and then the full number of payload bytes specified in the header. This makes parsing simple and reliable because MySQL clearly tells us how long each packet is. For multi-packet responses, the sequence number helps us join them together in the correct order.
 
- Metadata Extraction:

  1. HTTP/1.1 : From each HTTP request and response, I extract useful metadata. For requests, I record the method, path, host, headers, and body size. For responses, I record the status code, content type, and body size. Most importantly, I calculate the latency by subtracting the request timestamp from the response timestamp. I also keep track of how many bytes were transferred. These metadata fields are very important for observability because they help measure performance, detect errors, and understand traffic patterns.
 2. MySQL : From each MySQL query, I extract useful information such as the SQL text, the type of query (SELECT, INSERT, UPDATE, DELETE), the timestamp of when the query was sent, and the timestamp of the server’s response. From the server’s replies, I can capture whether the query succeeded or failed based on the first byte of the response. If needed, I can also record how many rows were returned, but that requires reading the result set packets. The difference between the request and response timestamps gives the query latency, which is very helpful for performance monitoring.

- Performance Considerations:
  1. HTTP/1.1 : Parsing HTTP at high rates requires care. Searching for the header terminator (\r\n\r\n) in a large buffer can be expensive, so I limit the amount of data I inspect, usually to the first few kilobytes. Memory usage can also grow if many connections are active because each one needs its own buffer. For example, at 10,000 requests per second with around 1,000 active connections, even a small buffer per connection adds up. CPU usage stays low as long as the parser avoids heavy operations like creating too many string objects or using complex regular expressions. Persistent HTTP connections may also carry multiple requests back to back, so the parser must be able to detect and extract more than one request from the same buffer.
                   https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/codesnippet/code2

 2. MySQL :There are several edge cases to keep in mind when parsing MySQL. During the handshake, the client may request SSL encryption, and once encryption starts, the traffic can no longer be parsed. Different MySQL versions or MariaDB may add small variations to the protocol, especially in authentication methods. Large result sets may come in multiple packets, so the parser needs to handle packet sequences correctly. If packets arrive out of order or are retransmitted, the parser must wait until the correct sequence is available. Error packets also contain codes and messages that should be extracted carefully. Keeping proper timeouts is important to avoid holding memory indefinitely if a client stops in the middle of sending a packet.
                  https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/codesnippet/code3

4. Practical Analysis
What to do:
1. Install Wireshark or use tcpdump

          https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot2.png

2. Capture real traffic:
- Mgivake HTTP requests to a website
- Connect to a MySQL/PostgreSQL database (local or remote)
- Or use Redis CLI
                  https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot3.png

3. Analyze packet captures:
- Identify protocol signatures
- Trace a complete request-response flow
- Annotate interesting packets (use Wireshark or screenshots with your
annotations)
             https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot5.png
            https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot6.png

4. Write pseudocode:
                https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/codesnippet/code1

       In my parsing logic, the first step is always validation to ensure we aren't wasting CPU cycles on garbage data; I scan the buffer specifically for the "HTTP/1.1" version tag to confirm the protocol type. Once validated, the most critical task is locating the metadata boundary. I wrote the parser to search for the "Double CRLF" sequence (\r\n\r\n) because this is the universal signal in text-based protocols that the headers have ended. After isolating the header block, I parse the very first line by splitting it on spaces to grab the method—in this specific capture, identifying "M-SEARCH". Finally, to make the data useful, I loop through the remaining lines, splitting each one by the first colon found to build a dictionary of key-value pairs, which allows us to easily extract critical routing information like the HOST address.

5. Performance Analysis:
        When I analyzed what happens at 10,000 requests per second, I understood that the biggest challenge is not the network itself but how memory is handled during parsing. In the basic pseudocode, every time we call .split() or create new strings for headers, the system ends up creating thousands of tiny temporary objects. At high request rates, this becomes a disaster because the Garbage Collector has to clean up these objects constantly, causing slowdowns and pauses.
To handle this kind of load in real systems, parsers avoid creating new strings altogether. Instead, they use a zero-copy approach where they keep the raw byte buffer and only store the start and end positions of each header. This avoids unnecessary memory allocations.
Another issue is the cost of scanning for \r\n to find the end of headers. If we scan one byte at a time, it becomes slow at high traffic rates. That’s why high-performance parsers use SIMD instructions, which let the CPU scan 16–32 bytes at once.
There’s also a risk of running out of memory if many clients send incomplete data and then stop transmitting — similar to a Slow Loris attack. The parser would keep buffers open, waiting for the rest of the message. This makes timeout management and buffer limits very important in a production parser.
         https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot4.png

