Assignment 2: Observability Systems Deep Dive







1\. Observability Fundamentals

What to cover:

\- Define the three pillars:

            The entire system depends on three types of data - Metrics, Logs, and Traces. They tell different stories about what is happening inside a system.



(https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/Types.jpg)

 



\- What is each pillar? What data does it contain?



   1. Metrics: They are numbers always changing with time. Metrics help us detect something is wrong. They are lightweight because they are only numbers.It mailnly says What is happening in the system



   2. Logs : Logs are text messages written by application.It mainly says why something is happened. As the Logs are text so they are heavier than the metrics.

&nbsp;        (https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/logs.jpg)



   3. Traces : They show how a request moves through different services.Traces contain small units called spans.Each span means one step in the request. They tell us where the time was spent. Traces mainly tell us where the issue is happening.





(https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/venndiagram.jpg)



\- When do you use each? What problems does each solve?



  1. Metrics : When I want to check system health and also when we want to know what is the issue or what is happening in the system. They detect the issues immediately.

  2. Logs : When I need to know why the issue happened and for debugging the issue.They tell the exact reason for the issue. They store complete context.

  3. Traces : When I want to see which service took the most time. They show where the issue is happening. They show parent-child relationships between services. They show which part of the system is slow.



\- How do they complement each other?

   Let me tell an example related to the medical analogy and below is the complement table

&nbsp;      (https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/complement.jpg)

\- Data types and formats:

\- Metrics: counters, gauges, histograms, summaries



  1. Counters : A number that only increases. it only goes up.They give Total errors, total API requests, total messages processed. For Example: car odometer it only goes up.

  2. Gauges : A number that goes up and down. It gives CPU usage, temperature, number of active users. For Example: Car Speedometer.

  3. Histogram : It groups data into buckets. Used to understand the latency.For Example: How many requests finished under 0.45s.

  4. Summary : It is similar to histogram and calculates percentiles inside the application. used for the App-side percentiles. Modern tools prefer Histogram over summary.



\- Logs: structured vs unstructured



  Logs are text messages that describe what happened inside a system.There are 2 types



       1. Unstructured Logs : It is the old style. These are the free form text and easily understandable by human but hard to search for the machines.

 

       2. Structured Logs : It is the modern style. These are written in JSON and are easy for machines to search and filter.





\- Traces: spans, trace context, baggage

    Traces show us how a request travelled through multiple services. Traces are made of spans.



    A. Span : It represents one operation. It contains start time, end time, span id, parent id



    B. Trace Context : It travels across all the services. It contains trace\_id which is the id for the whole request and span\_id which is the id of the current span.



    C. Baggage : They are small key-value pairs that travel with the request. These are used for debugging or personalization. For example customer\_tier=premium. So much baggage increases header size.



 

\- Common protocols: OTLP, Prometheus exposition format, StatsD, Syslog, Jaeger Thrift

  1. OTLP (OpenTelemetry Protocol) : It is Modern standard. It Supports metrics, logs, and traces. It works over gRPC or HTTP.



  2. Prometheus Exposition Format : It is in text based format. It is used mostly for metrics. It uses pull model.



  3. StatsD : It is very old and simple. It sends metrics using UDP (fire-and-forget).It is good for speed, bad for reliability.



  4. Syslog : It is the Old protocol for logs. It is used for system and network logs.



  5. Jaeger Thrift : It is the format used by Jaeger for sending traces. It uses Thrift encoding, works over UDP or TCP.

&nbsp;      

&nbsp;                   (https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/Common%20protocal.jpg)





\- Cardinality: What is it? Why does it matter? What causes cardinality explosion?

      Cardinality is the number of unique combinations of labels. It matters because more cardinality leads to more memory, database becomes slow, queries become slow, system can crash and also high cardinality increases storage cost.. The Cardinality explosion is due to adding labels like user\_id,IP address, transaction\_id, and storing trace\_id inside metrics. These should only be in logs or traces and not in metrics.

 

\- Time-series nature of observability data

       Metrics are stored as timestamps and value pairs. It allows graphs, trends, alerts, and forecasting. Logs and traces also include timestamps to show when events happened.For example CPU = 70% at 10:01, CPU = 75% at 10:02. The time dimension is critical for observability.





2\. Data Collection Architecture

What to cover:



\- What is a collector? Why do we need it instead of directly sending to backend?

       In the beginning, I thought the application can just send logs and metrics directly to the backend database but this creates many problems. A collector is like the middle person between the app and the backend observability system. The collector is needed for decoupling, Traffic control, Security, Translation. The collector protects the system from overload, changes, format issues, and security.



          (https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram1.jpg)

 

\- Collection models:



\- Agent-based collection (DataDog agent, OTEL collector as agent)

         We need to install an agent like Datadog Agent or OTEL Collector on the server or as a sidecar in Kubernetes. It can read system metrics like CPU, memory. It can batch and buffer data. It can apply sampling and filtering.But the only disadvantage is it consumes CPU/RAM on our machine.

               https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram2.jpg



\- Agentless collection

         As the name tells there is no agent. that means we wont install anything here. we directly use cloud platforms like AWS, Azure and GCP they automatically send metrics to the backend.But only limited details are sent.

               https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram3.jpg

 

\- eBPF-based collection - how is it different? What are advantages?



         It is modern and powerful because the code runs inside the Linux kernel. eBPF can watch network packets, system calls, file reads, etc.



         The advantages are we wont change code everytime.It can see every network packet and every file write.



               https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram4.jpg



\- Push vs Pull models - when to use which?



             https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram444.jpg

 

\- What processing happens at collection point?

      This is the main "processing pipeline".

The collector does multiple steps:

 

\- Filtering unwanted data



      Unwanted data like debug logs can be removed and money can be saved.



\- Sampling strategies (head-based, tail-based)

      This is where we keep only useful data.



      1.Head-Based Sampling : We decide at the start . It is simple , cheap but we may miss important errors.



      2.Tail-Based Sampling : We decide at the end. It waits until the request finishes. If it is error then keep it. if it success then keep 10%. It never misses error. But it is expensive and requires more memory because we store everything until the request finishes.



\- Buffering and batching

     Instead of sending one log per request, the collector groups them in one batch. It makes faster. This reduces network cost.



\- Metadata enrichment (adding tags, labels, context)

     Collector adds extra context or extra metadata like region, host name, service name. This makes debugging easier.



\- Protocol translation (e.g., StatsD → OTLP)

     Different applications speak different languages when they send observability data.

A collector acts like a translator that converts one format into another so the backend system can understand it.Protocol translation means the collector accepts data in one format like StatsD and converts it into a structured format like OTLP so modern backends can understand it.



                https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram5.jpg



\- Collection at different layers:

\- Application layer (instrumented code)

        The code we wrote, instrumented with libraries. It cannot see the hardware.

\- System layer (host metrics, system logs)

        System layer is the environment our code lives and the Operating System (Linux/Windows) and the physical/virtual hardware collected by agents.

 



\- Network layer (packet capture)

        This is the black hole between services. These are the communication pipes between our microservices.



\- Kernel layer (eBPF)

        It is the deepest level and sees everything.It is the heart of the OS. eBPF allows us to run safe programs here.



             https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%207.jpg



\- Auto-instrumentation vs manual instrumentation - pros and cons





              https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%206.jpg



3\. Backend Pipeline Architecture





\- End-to-end data flow: Ingestion → Processing → Storage → Query

                    https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%208.jpg

 

\- Ingestion Layer:



       This is the entry gate where all data comes into the observability backend.

\- How does data arrive? (HTTP, gRPC, TCP)

       Data can reach the system through different network protocols like HTTP, gRPC, TCP/UDP



\- Load balancing and high availability



       The Ingestion layer needs a Load Balancer like Nginx and a Buffer like Kafka to absorb this spike so the database doesnot die. Here it uses loadbalancers to distribute traffic.



\- Initial validation and routing

        The ingestion layer checks whether the data is valid or whether the data is metrics or logs or traces and also which pipeline should it go to.



\- Processing Stages:

        This is the brain of the pipeline where data is cleaned, transformed, and made ready for storage.



\- Parsing and normalization



        It is the process of converting data into a common format like OTLP. It Ensures label names, field names, and timestamp formats are correct and normalize different formats.

 

\- Aggregation (e.g., computing rates, percentiles)

         It is used mainly for metrics for converting a counter into requests per second ad to calculate percentiles and also to reduce raw data size.

 

\- Rollups for long-term storage

         Rollups are used for the long-term optimization by keeping high-resolution data  only for a short time and by converting older data into 1-minute, 5-minute, or 1-hour rollups so this saves storage cost \& speeds queries



\- Indexing strategies

         Indexing structure depends on data type, if it is Metrics then we use time series index , if the data is logs then we use inverted index, if the data is traces then we use trace ID index. if the indexing is good then the searching will be fast.



 

\- Data transformation and enrichment



        Adding extra context like region, host, service name, deployment version.this helps in debugging and root cause analysis.



\- Storage Layer:

     Each data type needs different storage because metrics/logs/traces behave differently.

\- Time-series databases: Prometheus, InfluxDB, M3DB, VictoriaMetrics,

ClickHouse



    There are time series databases like  Prometheus, InfluxDB, M3DB, VictoriaMetrics,

ClickHouse.These databases are optimized for High-write volume, Fast time-series queries and Compression.



\- Log storage: Elasticsearch, Loki, ClickHouse

     Logs are heavy and text-based. The tools are like elasticsearch, loki, cickHouse. They support full text search and indexing millions of log lines fastly.



\- Trace storage: Jaeger (Cassandra/Elasticsearch), Tempo (S3/GCS)

     Traces are structured graphs. Tools are Jaeger (Cassandra/Elasticsearch) and Tempo (Object storage like S3/GCS)

 

\- Why different storage for different data types?

     as the metrics are numeric so they are small and fast. as the logs are heavy text they are big and expensive and the traces are tree structures so required special indexing.



\- Hot vs Warm vs Cold storage - what goes where?



      Hot storage is fast and expensive it means recent data. Warm storage is chepear and slower whereas cold storage is very cheap the data is yrs or months and is stored in s3/gcs.



\- Retention policies :

      Metrics will keep high resolution for 15–30 days whereas Logs will keep resolution for 7–30 days (too costly) whereas Traces are  sampled, kept for few days





\- Query Layer:

     This is the layer where the user interacts it contains dashboards, alerts, queries.

\- Query languages: PromQL, LogQL, TraceQL, SQL

      Each datatype has its own query language PromQL is used for metrics, LogQL used for logs , TraceQL used for traces and SQL used for clickhouse



\- How are queries optimized?

      The backend optimizes queries using indices, caching, pre aggregated data and parallelexecution.



\- Aggregation at query time vs storage time - trade-offs



                 https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%209.jpg



\- Caching strategies:

    There are some caching stratergies like Query cache, result caching, downsampled cache for old data.



\- Compare architectures of 2-3 solutions (DataDog, Grafana Stack, etc.) using simple

comparison tables



           https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram10.jpg



4\. Intelligence Layer: Insights, Anomalies, RCA



A. Insights:

\- What are "insights" in observability?

&nbsp;    Insights are conclusions given by the observability system that gives from the raw data , where the raw data is the data of metrics , logs and traces.



\- How are insights generated from raw data?

&nbsp;    Insights actually come from statistical analysis, Trend analysis, correlation analysisand some machine learing techniques.

&nbsp;

\- Pattern recognition techniques:

\- Statistical analysis (mean, median, percentiles, std dev)

&nbsp;       Statistical analysis gives the mesn, median, percentiles, and the standard deviation.



\- Trend analysis

&nbsp;      Here in this analysis the system checks how values change over time an the time changes then it checks the values.



\- Correlation analysis

&nbsp;      Here in this analysis the system check which metrics changed together



\- Machine learning approaches:



&nbsp;    there are some machine learning techniques like clustering, forecasting, classification and these are used by advanced platforms like DataDog, New Relic, Dynatrace

&nbsp;

\- Clustering similar patterns

&nbsp;      clustering means grouping similar patterns

\- Forecasting

&nbsp;      forecasting means predicting the future values.



\- Classification (error types, incident types)

&nbsp;      classification means detecting the type of error or incident.

B. Anomalies:

\- What is an anomaly in observability context?

&nbsp;      Anomaly is something that doesnot look normal based on system usual behaviour or the abnormal behaviour like abnormal memory usage of the system.



\- Anomaly detection methods:

&nbsp;      there are anamoly detection methods like Threshold based, statistical methods, machine learning

\- Threshold-based (static and dynamic thresholds)



&nbsp;   these are the simple rules acting like a fixed boundary. 

&nbsp;   1.static threshold:

&nbsp;        we set a single fixed number when the metric crosses that number then it gives an alert.it is easy to setup and understand.

&nbsp;   2. Dynamic Threshold:

&nbsp;        the alert boundary depends on past patterns it is auto adjusting.



\- Statistical methods: Z-score, IQR, moving averages

&nbsp;    these methods compare the current data point against its recent history using basic statistics



&nbsp; 1.zscore : It measures how many standard deviations the currec=nt data point is away from the average.

&nbsp; 2.IQR :  it is interquartile range 

&nbsp;  .It is a robust methos for defining the middle 50% of our data.if beyond this range is considered as tg=he outlier or anomaly.

&nbsp; 3. Moving averages : it calculate the average of last N data points . the anomaly is detected when the current data point deviates too sharply.



\- Machine learning: isolation forests, autoencoders, LSTM



&nbsp;1. Isolation Forest :

&nbsp;        it isolates the rare patterns.

&nbsp;2. Autoencoders : it detect the unusual behaviour.

&nbsp;3. Moving averages : it smooths data to detect unusual spikes.



\- Handling seasonality and trends



&nbsp;The system removes daily patterns so it does not alert wrongly. 



\- False positive reduction

&nbsp;   we can reduce the false positives by combining multiple signals, adding cool down period, using correlation, using dynamic thresholds.



\- Severity classification

&nbsp;   Ssytems always label anomalies as the info, warning, critical.



C. Root Cause Analysis (RCA):

\- What is RCA? Why is it hard in distributed systems?



&nbsp;   	RCA means Root Cause Analysis, it means finding the real reason behind the issue. May be real cause be new deployment, slow DB query, network issue, faulty service.RCA is difficult in distributed systems because there are many microservices, many logs and metrics and there will be asynchronous communication. if there is a small service failure then entire system breaks. so it is difficult.



&nbsp;             https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2012.jpg



\- RCA techniques:



\- Correlation analysis 

&nbsp;    it checks which metrics changes at the same time . this helps identify the root cause or where the issue is happening.



\- Dependency mapping 

&nbsp;    It understands connection between services . is the DB os slow then the services show latency. for this we use service mesh diagrams and call graphs



\- Trace analysis for bottlenecks

&nbsp;    traces show where exactly the time was spent.



\- Log aggregation and pattern matching

&nbsp;    it is the pattern matching in logs.



\- Change event correlation

&nbsp;    it check what changed before the issue.



\- How do observability tools help in RCA?

&nbsp;    Observability tools make RCA faster, clearer, and more accurate. Instead of manually checking logs or guessing what's wrong, these tools connect metrics + logs + traces + events to show where a problem actually started.



\- Example RCA workflow: High latency alert → Identify affected service → Find slow

traces → Analyze span breakdown → Correlate with logs → Find deployment change

&nbsp;   

&nbsp;     https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram13.jpg



5\. Observability User Experience

What to cover:

A. Dashboard Patterns:

&nbsp;   When we open observability tool, the first thing we see is a dashboard. A dashboard shows important information at one place, so we can quickly understand what is happening.



\- Common visualization types:



&nbsp;   There are most popular visualizations they are



\- Time-series graphs:

&nbsp;   They show how a value changes over time. it can be a line, area or stacked graphs



\- Gauges and single-stat panels

&nbsp;   They show one number clearly.



\- Heatmaps

&nbsp;   They show distribution of values.



\- Histograms

&nbsp;   It shows how many requests fall into each bucket of duration.

&nbsp;    

\- Tables and logs view

&nbsp;   It shows raw logs or lists of events. It is used for reading exact error messages.



\- Dashboard organization:

\- Infrastructure dashboards show the health of the servers and machines that run the application. They usually display CPU usage, memory consumption, disk usage, and network activity. These dashboards are mostly used by DevOps or SRE teams to check whether the underlying system is stable or overloaded.



\- Application dashboards focus on how the application itself is performing.They track things like how many requests are coming in, how many errors are happening, and how long the system is taking to respond.



\- Business KPI dashboards show information that matters to the business side, such as conversion rate, number of orders per minute, and total revenue. These dashboards connect engineering work with actual business results



\- Variables and templating for filtering

&nbsp;    Dashboards should allow filtering by environment, service name, host name, region. This makes investigation faster. 



\- Information density - how much to show?



&nbsp;    if there is so much information confuses users.if it has too little information hides important issues. so good dashboard balances both.



B. User Workflows:



&nbsp;                https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2014.jpg



\- How do users navigate between metrics, logs, and traces?

&nbsp;  Users normally start with metrics to notice something unusual, like a spike or drop.From there, they click into logs of the same service to see error messages or warnings.Then they move to traces to find which request or span became slow and where exactly the issue happened.

&nbsp;                https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram15.jpg



\- Time range selection and time-sync across views



&nbsp;  When debugging, time range is the most important thing.The user picks a time range then all dashboards sync to that same time . When user switches to logs or traces, they see data only from that exact time window



\- Search and filtering patterns



&nbsp;   Users mostly type keywords like error, timeout, or payment to quickly narrow down large data.They apply filters such as service name, host, status code, or environment to isolate only the relevant signals. Good tools update results instantly as filters change, making it easy to zoom into the exact problem area without noise

C. Tool Analysis:

\- Study 2-3 tools: Grafana, DataDog, New Relic (use demo videos, screenshots, trial

accounts)



&nbsp;           https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2016.jpg

&nbsp;                

\- What makes a dashboard intuitive?



&nbsp;   Some parameters like clear labels, no unnecessary colors ,Important numbers highlighted

,easy filtering, Charts should be grouped logically.



\- How do they handle large datasets? 

&nbsp; They handle large datasets using 

&nbsp; 1.Pagination which means avoid loading too many rows

&nbsp; 2.Aggregation which means summarize data

&nbsp; 3.Virtualization whic load rows only when user scrolls



\- Real-time updates vs static snapshots



&nbsp;          https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2017.jpg



\- How are insights/anomalies/alerts presented?



&nbsp;  Tools show insights as cards, coloured boxes, or notifications highlighting unusual behaviour. Anomalies are often marked with red/yellow indicators on graphs with messages like “Latency spike detected.” Alerts appear as pop-ups, banner messages, or items in an alert list so the user can click and drill down.



\- What UX patterns work well? What's confusing?

&nbsp;  Good UX patterns include clear time-range sync, easy switching between metrics/logs/traces, and clean dashboards with no clutter. Confusing patterns include dashboards with too many panels, unclear labels, or too much information on one screen.

It also becomes confusing when alerts and anomalies are scattered instead of shown in one consistent place.



D. Insight Presentation:

\- How are insights surfaced to users? 

&nbsp;      Most tools show insights in these forms:

&nbsp;                1.Cards 

&nbsp;                2.Notification bars

&nbsp;                3.Highlighted alerts on graphs

&nbsp;                4.Dedicated “Insights” tab

\- Anomaly visualization techniques

&nbsp;          1.Highlight sections of the graph

&nbsp;          2.Show dotted lines for expected values

&nbsp;          3.Show colored areas when something is abnormal

&nbsp;          4.Present confidence intervals

\- RCA presentation - how do tools guide users to root cause?



&nbsp;     Observability tools make RCA easier by automatically connecting metrics, logs, and traces so the user doesn’t have to jump around blindly. They also show dependency maps that reveal how services talk to each other, which helps you see where delays or failures begin. Most tools highlight slow spans or abnormal behavior so the root problem becomes obvious. They also display recent changes like deployments or config updates, which helps you quickly see if the issue started right after a change.



\- Alert management UX

&nbsp;     A good alerting experience lets users silence or mute alerts for some time so they don’t get flooded with noise. Tools group related alerts together so the user doesn’t feel overwhelmed when multiple errors come from the same issue. Alerts are linked directly to dashboards so the user can jump into the investigation quickly. They also show alert history, which helps understand if this issue is recurring or completely new.



My opinion is dashboards should start simple and let the user drill down only when needed. Tools that make you scroll too much or switch between too many screens become difficult during an incident. When metrics, logs, and traces are separated, it becomes confusing, so linking them in one place is very helpful. Tools like Grafana Tempo and DataDog make RCA easier because clicking one thing shows all related data instantly.



&nbsp;            https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/Screenshots/Screenshot1.png



6\. Technical Challenges \& Trade-offs

What to cover:

\- Data Volume \& Cost:

&nbsp;       Modern applications generate a huge amount of observability data. Every request creates metrics, logs and traces, and when traffic grows, this data grows extremely fast. Storing all of this is expensive because time-series databases and log systems need a lot of disk and memory. Even sending this data across the network costs bandwidth, especially when thousands of services are pushing data every second.



\- Cardinality Explosion:

&nbsp;       Cardinality means how many unique combinations of labels exist in your metrics. It becomes a problem when developers add high-cardinality labels like user\_id, session\_id, or trace\_id. These create millions of time-series and the database cannot index them quickly. This slows down queries and increases memory usage drastically. The trade-off is clear: more labels give more detail, but too many labels break the system



\- Sampling Trade-offs:

&nbsp;       Sampling helps reduce the amount of trace data. If we store every trace, the system becomes heavy and expensive. Head-based sampling is fast and cheap, but it may miss important failures because it samples before knowing if the request will fail. Tail-based sampling keeps all error traces but needs more memory and CPU because the collector must wait until the entire request finishes. So the trade-off is between accuracy and resource cost.



\- Real-time vs Batch Processing:

&nbsp;               https://github.com/TejaSri-Chennuri/teja-sri-chennuri-nebulaiq-onboarding/blob/main/diagrams/diagram%2019.jpg





\- Storage Optimization:

&nbsp;     Because data increases very quickly in observability systems, teams usually cannot store everything forever. So they compress old data to save space, but this sometimes slows down queries because compressed data takes more time to read. To handle long-term trends, older metrics are downsampled — instead of keeping every single data point, they keep only averages or summaries, which is good for seeing patterns but not useful for deep-level debugging. Retention rules decide how long data stays in the system, and each type of data (metrics, logs, traces) may have a different duration.



\- Query Performance at Scale:

&nbsp;     Querying observability data at scale is challenging because metrics, logs, and traces grow extremely fast. Good indexing makes searching easier but costs memory. Pre-aggregating data makes dashboards faster but reduces flexibility. On-demand calculations are flexible but may lag during incidents.



\- Alert Fatigue:

&nbsp;     If the system sends too many alerts, engineers start ignoring them. This is called alert fatigue. Often alerts fire because rules are too sensitive or not grouped well. Good systems reduce noise by grouping alerts, deduplicating them, and showing only the meaningful ones. The challenge is finding the balance between alerting too little (risk missing incidents) and alerting too much (people ignore alerts).



\- Context Correlation:

&nbsp;     The hardest part of observability is connecting metrics, logs and traces. To correlate them, all systems must share the same identifiers like trace\_id, span\_id, and service names. If these IDs are missing or inconsistent, RCA becomes very hard because the data doesn’t link together. Tools try to solve this by injecting context automatically, but the trade-off is complexity the more automation, the harder it becomes to debug the observability system itself.







references : https://www.youtube.com/@TechUpskill





