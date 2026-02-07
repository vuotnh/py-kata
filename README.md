# 🧠 Python Systems & Async Internals

> A curated knowledge base of **Python at the system level** — async runtimes, concurrency models, memory behavior, performance, and real-world backend patterns.

This repository is **not about basic Python syntax**.  
It focuses on **how Python actually behaves under the hood**, especially when building **high-performance, scalable, async systems**.

---

## 🎯 What this repo is about

This repo documents **hands-on knowledge** gained from building and analyzing:

- Async backends (asyncio, aiohttp, FastAPI, Flask async)
- High-concurrency systems
- Task scheduling & backpressure
- Performance bottlenecks
- Memory allocation & GC behavior
- Network & I/O patterns
- Real benchmark-driven decisions

Everything here answers questions like:

> *Why is this slow?*  
> *Where is the bottleneck?*  
> *What is actually blocking the system?*  
> *How does asyncio really schedule tasks?*

---

## 🧩 Topics Covered

### 🔁 Async & Concurrency
- `asyncio` event loop internals
- Coroutine lifecycle & scheduling
- Semaphore, Lock, Queue — **when and why**
- Backpressure patterns
- Client-side vs server-side concurrency limits
- `asyncio.create_task` vs `TaskGroup`
- Async + sync interop pitfalls

### ⚙️ System & Low-level Behavior
- Memory allocation (stack vs heap)
- Object lifetime & GC impact
- Hidden allocations in hot paths
- Python function call overhead
- GIL implications in real systems
- I/O vs CPU-bound workloads

### 🚀 Performance & Benchmarking
- Designing **correct benchmarks**
- Latency decomposition:
  - queue delay
  - request latency
  - end-to-end latency
- Percentiles (P50 / P95 / P99) vs averages
- Burst load vs steady-state load
- Client vs server bottleneck analysis

### 🌐 Networking & I/O
- HTTP connection pooling
- TCP behavior under high concurrency
- Async HTTP clients (aiohttp)
- Timeout, retry, and failure modes
- Rate limiting strategies

### 🧠 Architecture Patterns
- Fire-and-forget (202 + task_id)
- Async job orchestration
- In-memory vs external queues
- Graceful overload handling
- Designing for fairness

---

## 🧪 Philosophy

- **Measure first, optimize later**
- **Latency > throughput** in user-facing systems
- **Backpressure is a feature**, not a bug
- If you can’t explain *why* something is fast or slow — you don’t understand it yet
- “Async” does not automatically mean “scalable”

---

## ❌ What this repo is NOT

- ❌ Beginner Python tutorials  
- ❌ Framework marketing material  
- ❌ Copy-paste LeetCode solutions  
- ❌ Premature micro-optimizations  

This is about **understanding**, not memorizing APIs.

---

## 🧠 Who is this for?

- Backend engineers working with Python
- Developers moving from sync → async
- People debugging “mysterious” latency issues
- Anyone curious about how Python behaves **in production**, not just in examples

If you’ve ever asked:

> *“Why does this async code still feel slow?”*

You’re in the right place.

---

## 📌 Disclaimer

Some explanations are **opinionated** and based on real-world trade-offs.  
They may not match every workload — and that’s intentional.

The goal is to **build intuition**, not dogma.

---

## 📬 Contributions

This repo is primarily a **personal knowledge base**, but:
- Issues for discussion are welcome
- PRs with **deep technical insight** are appreciated

Shallow content will be rejected 🙂

---

## ⭐ Final note

If this repo helps you:
- debug faster
- design cleaner async systems
- or avoid one production incident

then it has done its job.

Happy hacking ⚙️
