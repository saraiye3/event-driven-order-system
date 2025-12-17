1. full name: Sarai Yehezkel 
   ID: 314919044

2. producer application URL: http://localhost:5000/create-order
   method: POST
   
   consumer application URL: http://localhost:5001/order-details?orderId=<ORDER_ID>
   method: GET
   example: GET http://localhost:5001/order-details?orderId=ORD-14

3. I chose a topic exchange.
   The assignment states that the system must support multiple downstream consumers, and each one may want to filter messages differently, such as receiving only orders with a certain status, currency, or any other future criteria. A topic exchange supports this flexibility by using structured routing keys (e.g., order.new or order.new.ILS) and allowing each consumer to subscribe with wildcard patterns that match its own filtering needs. This makes the system much more scalable and adaptable than a direct exchange.
  
4. Yes. The consumer binds to the routing key "order.new.#"
Since the consumer should receive only orders whose status is "new", it subscribes to the pattern that matches all routing keys starting with "order.new". The # wildcard allows the system to be extended in the future (e.g., order.new.ILS) without changing the consumer’s configuration. This ensures the consumer always receives every “new” order event, even if additional fields are added to the routing key later.
   
5. The producer declared the exchange because it controls how messages should be routed and must ensure the exchange exists before
   publishing to it. This follows the separation of concerns: the producer handles message routing, while the consumer focuses only on receiving and processing messages from queues.
   The consumer declared the queue, because the queue belongs to the consumer, 
   and only it knows which routing key it needs to bind with.
   
# Important: Run the producer’s docker-compose first.
  The producer declares the RabbitMQ exchange, so the consumer should only be started after the producer and RabbitMQ are up.