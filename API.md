 producer application URL: http://localhost:5000/create-order
   method: POST
   
   consumer application URL: http://localhost:5001/order-details?orderId=<ORDER_ID>
   method: GET
   example: GET http://localhost:5001/order-details?orderId=ORD-14
