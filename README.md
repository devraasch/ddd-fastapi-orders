# fastapi-ordering-ddd

Simple ordering system built with FastAPI, Clean Architecture, PostgreSQL, RabbitMQ and Docker.

## Overview

This project is a minimal MVP for order creation, designed to evolve with DDD concepts and event-driven architecture.

Current features:
- create orders
- health check endpoint
- PostgreSQL persistence
- RabbitMQ event publishing
- automated tests
- coverage support
- Docker-based local environment

## Architecture

The project follows a simplified Clean Architecture structure:

```text
app/
  domain/
  application/
  infrastructure/
  presentation/
