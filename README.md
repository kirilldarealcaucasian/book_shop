# About the project

## Flow:
![alt text](readme_imgs/gist.GIF "Title")

### *Project hasn't been fully tested yet and has bugs*

## This is ecommerce book shop API

## Features of the project
### 1. Books management:  create, edit, delete, get, get by filters books

### 2. User management and permissions: register, login, authentication via JWT tokens, permissions for different types of actions (such permissions for performing actions on order / cart)

### 3. Shopping cart: CRUD for cart, implemented caching for cart via Redis and update of cart items right in the cache using redis-set and redis-hash

### 4. Order management: create and manage orders, update order status

### 5. Created 2 implementations for storing pictures for books. You can use Object storage (I integrated with *Cloud.ru* to get access to free s3 buckets) or store pictures in the project folder. I used PIL to manage picture dimensions in conjunction with Celery for creating file structure for storing images

### 6. Search and filtering: Created module that allows to create flexible filters (you can filter by related fields) on the basis of Pydantic models

### 7. Services interaction: used RabbitMQ to perform inter-service interaction. In the Generic Service there is a Celery scheduled task that parses logs file, constructs a message and pushes it to RabbitMQ exchange. Logs service consumes messages and saves them to MongoDB


### 8. Payment Gateway Integration: integrated with YooKassa payment service in test mode and implemented logic for making payments


### 9. Implemented request limiter with Redis by creating middleware

### 10. Created integration tests (not finished with it yet)

### In the Logs Service I didn't use any specific libraries or technologies. It's a simple REST service built with Go standard library and Mongo driver that also can consume messages from the queue 

## Modules architecture overview

![alt text](readme_imgs/modules.GIF "Title")

#### While building this project, I tried to follow principles of layered architecture. In the picture you can see 2 patterns of 1-directional interaction between modules (I don't include presentational and domain layers because I want to focus on services and repositories). For implementing service to repository interaction, I used repository pattern. Each service may call directly to the injected repository to use one of its methods, but there are CRUD methods that are repeated for each repository, therefore I implement EntityBaseService. EntityBaseService performs exception handling and logging for exceptions raised in the repository layer. It helps to cut down code, by moving repeated exception-handling and logging logic from each service to EntityBaseService. It catches storage exceptions, loggs them and returns http-level exceptions.

### Languages and tech used: Python 3.10, Go 1.22.0, FastAPI, SqlAlchemy 2.0, Pydantic, Alembic, AioRedis, PIL, Python-json-logger, Pytest, Celery, PIL, RabbitMQ, Postgres, MongoDB

# How to use the project
### Coming soon . . . (project is not finished yet)



