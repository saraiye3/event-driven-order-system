
1. full name: Sarai Yehezkel 
   ID: 314919044

2. producer application URL: http://localhost:5000/create-order
   method: POST
   
   consumer application URL: http://localhost:5001/order-details?orderId=<ORDER_ID>
   method: GET
   example: GET http://localhost:5001/order-details?orderId=ORD-14

3. I chose a direct exchange.
   The producer publishes each order using its status as the routing key,
   and the consumer binds with the routing key "new".
   This lets the producer send all orders, while the consumer automatically receives only new orders, exactly as required.
  
4. Yes. The consumer uses the binding key "new" so it will receive only messages for orders whose status is "new". 
   This matches the requirement that the consumer should process only new orders.
   
5. The producer declared the exchange, because it must ensure the exchange exists before publishing messages to it.
   The consumer declared the queue, because the queue belongs to the consumer, 
   and only it knows which routing key it needs to bind with.