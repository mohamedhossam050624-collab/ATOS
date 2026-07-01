# ATOS - Artificial Trading Operating System

ATOS is a personal, institutional-grade AI trading operating system.

The system is being built to support market research, reasoning, risk management, decision-making, monitoring, learning, and future autonomous trading.

ATOS is not a simple trading bot. It is designed as a modular, event-driven, plugin-based, multi-agent AI trading platform.

---

## Current Status

Current phase:

```text
Phase 1 - Platform Foundation
```

Current focus:

```text
Kernel foundation stabilization
```

The current goal is to build a clean and reliable Kernel before adding AI agents, trading logic, brokers, strategies, or live execution.

---

## Current Implemented Components

```text
kernel/
  __init__.py
  exceptions.py
  kernel.py
  lifecycle.py
  registry.py
  service.py
  state.py

services/
  dummy_service.py

shared/
  logger.py

main.py
requirements.txt
```

---

## Current Kernel Features

- Service registration
- Service lifecycle management
- Service startup
- Graceful shutdown
- Health checks
- Kernel exception hierarchy
- Shared logging
- Smoke-test service

---

## Target Architecture

ATOS will follow:

- Clean Architecture
- Domain-Driven Design
- Event-Driven Architecture
- Plugin-Based Architecture
- Microkernel Architecture
- Multi-Agent AI Architecture
- SOLID Principles
- Strong risk management
- Explainable decision-making

---

## Core Trading Rule

No trade decision may bypass:

```text
Research
→ Data Engineering
→ Intelligence
→ Reasoning
→ Risk Validation
→ Execution Approval
→ Monitoring
→ Learning
```

---

## Current Runtime Dependency

```text
loguru
```

---

## Run the Current Smoke Test

From the project root:

```powershell
python main.py
```

Expected result:

```text
ATOS Kernel smoke test completed successfully.
```

---

## Development Philosophy

ATOS prioritizes:

```text
Architecture > Features
Correctness > Speed
Reliability > Shortcuts
Testing > Guessing
Security > Convenience
Risk Control > Profit Chasing
```

---

## Personal Development Notice

This project is currently being developed as a personal professional-grade AI trading operating system.

Public release, licensing, SaaS features, and commercial deployment are not the current priority.

The current priority is building the strongest possible foundation.