# TaskForge

**TaskForge** is a production-oriented Python backend project for building, scheduling, executing, and monitoring background jobs.

The purpose of this project is not simply to make a working application.

The goal is to use one progressively evolving project to learn how real backend systems are designed:

- API design
- PostgreSQL
- database modeling
- asynchronous/background processing
- queues
- workers
- concurrency
- retries
- failure handling
- idempotency
- observability
- testing
- Docker
- deployment
- system design

---

## 1. What Are We Building?

TaskForge will eventually look roughly like this:

```text
                         ┌──────────────────┐
                         │      Client      │
                         │  curl / frontend │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API        │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │   PostgreSQL     │
                         │   Job metadata   │
                         └──────────────────┘
                                  │
                                  │
                         ┌────────▼─────────┐
                         │      Redis       │
                         │      Queue       │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
             ┌────────────┐ ┌────────────┐ ┌────────────┐
             │  Worker 1  │ │  Worker 2  │ │  Worker 3  │
             └──────┬─────┘ └──────┬─────┘ └──────┬─────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                            Execute the job
```

The final system should allow a user to submit a job and have TaskForge execute it asynchronously.

For example:

```text
POST /jobs
```

could create:

```json
{
    "type": "send_email",
    "payload": {
        "to": "user@example.com"
    }
}
```

TaskForge would then:

1. Store the job in PostgreSQL.
2. Put the job into a queue.
3. Have a worker pick it up.
4. Execute the job.
5. Update its status.
6. Record success or failure.
7. Retry when appropriate.
8. Expose the job's state through the API.

---

# 2. Core Goal

The central question of TaskForge is:

> **How does a backend system reliably execute work outside the HTTP request/response cycle?**

We will answer that question by building the system ourselves.

We will not start with Redis, Celery, Kafka, Kubernetes, or other abstractions.

We will first understand the fundamentals.

---

# 3. Development Philosophy

TaskForge will be built incrementally.

Each milestone should produce a working system.

```text
Milestone 1
    │
    ▼
Working API + PostgreSQL
    │
    ▼
Milestone 2
    │
    ▼
Job execution
    │
    ▼
Milestone 3
    │
    ▼
Redis queue
    │
    ▼
Milestone 4
    │
    ▼
Workers
    │
    ▼
Milestone 5
    │
    ▼
Retries + failure handling
    │
    ▼
Milestone 6
    │
    ▼
Concurrency + reliability
    │
    ▼
Milestone 7
    │
    ▼
Testing + observability
    │
    ▼
Milestone 8
    │
    ▼
Docker + deployment
```

The project should become more sophisticated only after the underlying concept is understood.

---

# 4. Technology Stack

## Current

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- psycopg

## Later

- Redis
- Background workers
- pytest
- Alembic
- Docker
- Docker Compose
- logging/observability

## Optional Advanced Topics

Depending on how far we take the project:

- async SQLAlchemy
- Redis Streams
- task scheduling
- dead-letter queues
- rate limiting
- distributed locking
- metrics
- tracing
- horizontal worker scaling
- graceful shutdown
- Kubernetes

---

# 5. Project Milestones

## Milestone 1 — API + PostgreSQL

### Goal

Build the foundation of TaskForge.

The API should be able to create and retrieve jobs.

### Learn

- FastAPI
- HTTP methods
- request/response models
- SQLAlchemy
- PostgreSQL
- database connections
- transactions
- database modeling
- CRUD operations

### Initial Job Model

Conceptually:

```text
Job
├── id
├── type
├── payload
├── status
├── created_at
├── updated_at
└── ...
```

Initial statuses:

```text
PENDING
RUNNING
SUCCESS
FAILED
```

### API

Initial endpoints:

```text
POST /jobs
GET  /jobs/{job_id}
GET  /jobs
```

### Definition of Done

- [ ] FastAPI application runs
- [ ] PostgreSQL database exists
- [ ] Python connects to PostgreSQL
- [ ] SQLAlchemy model exists
- [ ] Jobs can be created
- [ ] Jobs are persisted
- [ ] Jobs can be retrieved
- [ ] Invalid requests return proper errors
- [ ] Basic tests exist

---

# 6. Milestone 2 — Job Execution

### Goal

Actually execute a job.

Initially, execution can happen inside the Python application.

For example:

```text
POST /jobs
      │
      ▼
Create job
      │
      ▼
Execute job
      │
      ▼
Update status
```

This is intentionally NOT the final architecture.

The purpose is to understand:

- job lifecycle
- execution
- exceptions
- status transitions
- failure handling

### Definition of Done

- [ ] Jobs can execute
- [ ] Successful jobs become `SUCCESS`
- [ ] Failed jobs become `FAILED`
- [ ] Exceptions are captured
- [ ] Job results/errors are persisted

---

# 7. Milestone 3 — Redis Queue

### Goal

Separate job submission from job execution.

Instead of:

```text
HTTP request
    │
    ▼
Execute job
```

we move toward:

```text
HTTP request
    │
    ▼
PostgreSQL
    │
    ▼
Redis
    │
    ▼
Worker
```

### Learn

- queues
- producers
- consumers
- Redis
- serialization
- message delivery

### Definition of Done

- [ ] Redis runs locally
- [ ] API can enqueue jobs
- [ ] Queue contains job information
- [ ] Jobs can be consumed
- [ ] Job state remains in PostgreSQL

---

# 8. Milestone 4 — Worker System

### Goal

Create an independent worker process.

The API should no longer execute background work itself.

```text
FastAPI
   │
   ▼
Redis
   │
   ▼
Worker
```

The worker should continuously:

```text
while running:

    get job

    execute job

    update database
```

### Learn

- processes
- worker loops
- concurrency
- graceful shutdown
- process lifecycle
- separation of responsibilities

### Definition of Done

- [ ] API runs independently
- [ ] Worker runs independently
- [ ] Worker consumes jobs
- [ ] Multiple workers can run
- [ ] API remains responsive while jobs execute

---

# 9. Milestone 5 — Reliability

A jobs system becomes interesting when things fail.

We will intentionally introduce failures.

Examples:

```text
Worker crashes
Database temporarily unavailable
Job raises exception
Redis unavailable
Network failure
Process killed during execution
```

### Features

- retries
- retry limits
- exponential backoff
- failure recording
- dead-letter queue
- timeout handling

Example:

```text
PENDING
   │
   ▼
RUNNING
   │
   ├──── SUCCESS
   │
   └──── FAILED
            │
            ▼
          RETRY
            │
            ▼
          RUNNING
```

### Definition of Done

- [ ] Failed jobs can retry
- [ ] Retry count is persisted
- [ ] Maximum retries are enforced
- [ ] Permanent failures are identifiable
- [ ] Worker failures do not corrupt job state

---

# 10. Milestone 6 — Idempotency & Concurrency

This is where TaskForge starts becoming a serious backend engineering exercise.

We need to answer:

> What happens if the same job is executed twice?

For example:

```text
Worker A
   │
   └── executes job #123

Worker B
   │
   └── accidentally executes job #123
```

We need mechanisms to prevent or safely handle duplicate execution.

### Learn

- idempotency
- race conditions
- database locking
- atomic operations
- transactions
- distributed systems fundamentals

### Topics

- job claiming
- atomic state transitions
- locking
- duplicate delivery
- exactly-once vs at-least-once processing

A major principle:

> **Assume the infrastructure can deliver a job more than once.**

Design accordingly.

---

# 11. Milestone 7 — Testing

TaskForge should eventually have tests at multiple levels.

```text
Unit Tests
    │
    ▼
Integration Tests
    │
    ▼
API Tests
    │
    ▼
Worker Tests
    │
    ▼
End-to-End Tests
```

### Test Areas

- API validation
- database operations
- job execution
- retries
- failures
- worker behavior
- concurrency
- idempotency

### Learn

- pytest
- fixtures
- mocking
- integration testing
- test databases
- test isolation

---

# 12. Milestone 8 — Observability

A production backend needs to tell us what it is doing.

We will add:

### Logging

```text
Job 123 created
Job 123 queued
Worker 2 claimed Job 123
Job 123 started
Job 123 failed
Job 123 retrying
Job 123 succeeded
```

### Metrics

Eventually:

```text
jobs_created_total
jobs_completed_total
jobs_failed_total
jobs_retried_total
job_execution_duration
queue_depth
```

### Learn

- structured logging
- log levels
- metrics
- monitoring
- debugging production systems

---

# 13. Milestone 9 — Docker

Containerize the system.

Eventually:

```text
docker-compose
│
├── api
├── worker
├── postgres
└── redis
```

A developer should be able to start the entire system with one command.

---

# 14. Milestone 10 — Production Deployment

The final goal is to deploy TaskForge.

Possible architecture:

```text
                  Internet
                     │
                     ▼
                Load Balancer
                     │
                     ▼
                FastAPI API
                  /     \
                 /       \
                ▼         ▼
          PostgreSQL     Redis
                            │
                   ┌────────┼────────┐
                   ▼        ▼        ▼
                Worker   Worker   Worker
```

Topics:

- environment variables
- secrets
- production configuration
- database migrations
- process management
- health checks
- logging
- monitoring
- scaling

---

# 15. Database Evolution

The database schema should evolve through migrations.

We will eventually use:

```text
Alembic
```

Instead of manually modifying production tables.

The evolution might look like:

```text
Migration 001
    ↓
jobs table

Migration 002
    ↓
retry fields

Migration 003
    ↓
execution timestamps

Migration 004
    ↓
worker information

Migration 005
    ↓
dead-letter information
```

---

# 16. Job Lifecycle

The job lifecycle is one of the most important concepts in the project.

Initially:

```text
             ┌──────────┐
             │ PENDING  │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │ RUNNING  │
             └────┬─────┘
                  │
             ┌────┴─────┐
             ▼          ▼
       ┌──────────┐ ┌──────────┐
       │ SUCCESS  │ │  FAILED  │
       └──────────┘ └────┬─────┘
                         │
                         ▼
                       RETRY
                         │
                         ▼
                      RUNNING
```

The exact state machine will evolve as reliability features are introduced.

---

# 17. Important Backend Questions

Throughout the project, we should repeatedly ask:

### API

- What happens if the client sends invalid data?
- What HTTP status should we return?
- What happens if a job doesn't exist?

### Database

- What happens if two requests modify the same job?
- Where should transactions begin and end?
- What indexes do we need?

### Queue

- What happens if Redis goes down?
- What happens if a message is delivered twice?

### Worker

- What happens if the worker crashes?
- What happens if the job takes 30 minutes?
- What happens if the job never finishes?

### Reliability

- Can a job execute twice?
- Can a job disappear?
- Can a job become permanently stuck?

### Production

- How do we know the system is healthy?
- How do we debug a failed job?
- How do we scale workers?

These questions are more important than simply making endpoints work.

---

# 18. Suggested Repository Structure

The structure will evolve as the project grows.

A likely final structure:

```text
TaskForge/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── jobs.py
│   │   └── health.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── jobs.py
│   │
│   ├── services/
│   │   └── jobs.py
│   │
│   ├── queue/
│   │   └── redis.py
│   │
│   ├── workers/
│   │   └── worker.py
│   │
│   └── core/
│       └── config.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
│
├── migrations/
│
├── docker/
│
├── .env
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

**Do not create all of this at the beginning.**

The repository structure should grow naturally as the architecture grows.

---

# 19. Learning Rules

TaskForge is also a learning project.

Therefore:

### Rule 1 — Understand before abstracting

Do not introduce a library simply because it makes something easier.

First understand what problem it solves.

### Rule 2 — Build progressively

Don't jump straight to:

```text
FastAPI + Redis + Celery + Docker + Kubernetes
```

Build the underlying concepts one at a time.

### Rule 3 — Debug before asking for the solution

When something breaks:

```text
Observe
   ↓
Form hypothesis
   ↓
Test hypothesis
   ↓
Inspect evidence
   ↓
Fix
```

Debugging is part of the project, not an interruption to it.

### Rule 4 — Keep the system working

After every milestone:

```text
Build
→ Test
→ Break
→ Debug
→ Fix
→ Commit
```

### Rule 5 — Don't chase perfection

A simple working implementation is better than an elaborate unfinished architecture.

---

# 20. Current Progress

## PostgreSQL

- [x] PostgreSQL installed
- [x] Connected using `psql`
- [x] Created `taskforge` database
- [x] Connected to `taskforge`
- [x] Verified database with `SELECT current_database()`

## Milestone 1

- [ ] Set up Python environment
- [ ] Set up project structure
- [ ] Install FastAPI
- [ ] Install SQLAlchemy
- [ ] Install psycopg
- [ ] Configure database connection
- [ ] Create Job model
- [ ] Create database table through migrations
- [ ] Create `POST /jobs`
- [ ] Create `GET /jobs/{id}`
- [ ] Create `GET /jobs`
- [ ] Add tests

## Later

- [ ] Job execution
- [ ] Redis
- [ ] Worker
- [ ] Retries
- [ ] Failure handling
- [ ] Idempotency
- [ ] Concurrency
- [ ] Observability
- [ ] Docker
- [ ] Deployment

---

# 21. Definition of the Finished Project

TaskForge is finished when we can demonstrate something like:

```text
Client
  │
  │ POST /jobs
  ▼
FastAPI
  │
  ├── PostgreSQL
  │      └── stores job state
  │
  └── Redis
         │
         ▼
       Worker
         │
         ▼
    Execute job
         │
         ├── SUCCESS
         │
         └── FAILURE
                │
                ▼
              RETRY
```

And we can confidently explain:

> How a job enters the system, how it is persisted, how it is queued, how a worker claims and executes it, how failures are handled, how duplicate execution is controlled, and how the entire system is tested, monitored, and deployed.

That explanation is ultimately more valuable than the code itself.

---

# 22. The Ultimate Goal

TaskForge is not meant to be a toy CRUD application.

It is a **backend engineering laboratory**.

The project should take us from:

```text
"I know Python"
```

to:

```text
"I understand how a backend system actually works."
```

The final objective is not to memorize FastAPI, PostgreSQL, Redis, or Docker.

It is to develop the ability to look at a backend problem and reason about:

```text
Data
  ↓
API
  ↓
Persistence
  ↓
Processing
  ↓
Concurrency
  ↓
Failures
  ↓
Reliability
  ↓
Observability
  ↓
Scale
```

**Build slowly. Understand deeply. Break things deliberately. Debug everything.**