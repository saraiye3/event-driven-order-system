# Event-Driven Order System

An event-driven order processing system built with Python, RabbitMQ and Docker.  
The project includes two independent services (Producer and Consumer) that communicate through RabbitMQ using a topic exchange.

## Overview
**Producer Service**  
Receives order requests through a REST API, validates the input, generates the full order data and publishes an event to RabbitMQ.

**Consumer Service**  
Listens for incoming order events, processes them asynchronously, calculates the shipping cost, stores the results in memory, and exposes an endpoint for retrieving processed orders.

## Technologies
- Python (Flask, Quart, aio-pika)  
- RabbitMQ (direct exchange, routing keys)  
- Docker & Docker Compose  
- Asynchronous event processing  

## Flow
1. Client sends a `POST /create-order` request to the Producer.  
2. Producer publishes the order event to RabbitMQ.  
3. Consumer receives and processes the event.  
4. Client retrieves the processed order with `GET /order-details?orderId=...`.

## Purpose
This project demonstrates a simple but realistic event-driven architecture with microservices, asynchronous processing, message routing, and containerized deployment.