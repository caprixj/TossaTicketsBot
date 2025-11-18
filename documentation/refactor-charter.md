# 🚀 Ticketonomics: Refactor Charter (AS-IS vs. TO-BE)

This document serves as the "source of truth" for the Ticketonomics refactoring, migrating the system from a complex monolithic bot to a modular L1/L2 production economy.

## 1. "AS-IS" State: Monolithic Bot

This analysis describes the codebase as it exists *before* the refactor, based on direct schema and service-layer inspection.

### 1.1. Architecture Summary

The current system is a **monolithic Aiogram bot** with a single, massive service layer (`service_core.py`) and a hand-written repository layer. It uses raw `aiosqlite` queries to interact with a complex, highly relational database.

The core design issue is a **lack of transactional integrity and separation of concerns**. Business logic functions (e.g., `msell`) are long, procedural scripts that manually execute multiple, separate database updates (for tickets, taxes, and materials) without an atomic "Unit of Work."

### 1.2. Core Component Analysis

* **`command/handlers/`**: A large directory of bot command handlers. These are coupled to the service layer, parsing user input and calling functions in `service_core.py`.
* **`service/service_core.py`**: The "God file" (1300+ lines). It imports from all other parts of the system (repository, models, utils) and contains all business logic. This includes user-facing info, admin commands, material trading, and salary payouts, all in one place.
* **`repository/repository_core.py`**: A data access layer that abstracts the execution of raw SQL queries.
* **`repository/sql/`**: Contains the raw SQL strings, critically including `schemas.py` (the complete `CREATE TABLE` statements) and query files (`inserts.py`, `selects.py`, etc.).
* **`model/database/`**: Contains simple Python `class` definitions (e.g., `Member`, `TicketTransaction`). These are **not ORM models** but basic data containers, sometimes with minor logic (e.g., `funcs.to_utc`).

### 1.3. "AS-IS" Data Model (Corrected)

The data model is **highly complex, relational, and feature-rich**, with over 25 tables. It already implements V1 versions of many "TO-BE" concepts.

* **Core Entities:**
    * `members`: The central user table with ticket balances.
    * `del_members`: A table for deleted members.
    * `vars`: A key-value store for global system variables.
* **Ticket Economy:**
    * `ticket_txns`: Logs all ticket transfers with a `type` enum.
    * `tax_txns`: Logs all tax-related transfers, linked to a parent transaction.
* **Pricing:**
    * `prices`, `price_history`: Tracks material and product prices.
    * `rate_history`: Tracks economic indicators like inflation (emulated).
* **Employment System:**
    * `jobs`: Defines available positions and their salaries. The employer is the Ticketonomics system itself.
    * `employees`: A join table linking `members` to `jobs` (current employment).
    * `employment_history`: A log of all past jobs.
    * `salary_payouts`: A log for the salary payout schedule.
* **Asset System (Materials):**
    * `materials`: The "master list" of all materials (e.g., gems, intermediates).
    * `member_materials`: A join table linking `members` to `materials` with a `quantity` (the inventory system).
    * `mat_txns`: Logs all material transfers (e.g., crafting, trading).
* **P2P Trading System:**
    * `mat_orders`: A log of active P2P trade offers.
    * `mat_deals`: A log of completed or canceled trades.
    * `mat_trading_blacklist`: A user-level block list for P2P trading.
* **Asset System (Digital Items):**
    * `artifacts`: A table for unique, created digital items with an owner and creator (not working. will be remade from scratch).
    * `awards`, `award_member`: A system for granting achievements/awards to members from the system.
* **Logging & Utility:**
    * `daily_schedules`, `activity_data`: Tables for system scheduling and user activity logging (not working yet, not incorporated into the project).

---

## 2. "TO-BE" Vision: L1/L2 Production Economy

This describes the target architecture as defined in the `ticketonomics-export.md`.

### 2.1. Core Architectural Shift

The new architecture is a **modular, event-driven ecosystem** defined by an economic **Two-Layer (L1/L2) Model**.

* **L1 (Foundation):** The "mainnet" or core protocol. It is "budget-less" and manages system-wide concerns. Its fees are **ticket sinks** to regulate the macro-economy.
    * **Responsibilities:** User Balances, L1 AMM (for raw materials), Core Governance (The Parliament).
* **L2 (Application Layer):** "Budgeted" applications that build *on top* of L1. These are cyclical economies with their own treasuries.
    * **Responsibilities:** Player-run **Companies**, **Crafting/Production** systems, Game Server integrations (e.g., Minecraft), P2P Markets.

### 2.2. New "TO-BE" Features

* **Technology:** Migration to **SQLAlchemy ORM** is mandatory. A **FastAPI** gateway is required to serve the L1 API to L2 applications.
* **Economy:** A **Hybrid Market** (L1 AMM + L2 P2P Market) and a **Production & Crafting** loop (managed by a Job Queue).
* **Assets:** Introduction of **Patents** as a new asset class that can be **Licensed**.
* **Governance:** A new **L1 Parliament** module for community voting on new recipes, with a "One Person, One Vote" model.
* **Entities:** Formal introduction of **L2 Companies** as player-run organizations with shared budgets and inventories.

---

## 3. Key Architectural Gaps (The Refactor Plan)

This section identifies the "from-scratch" work needed to bridge the "AS-IS" monolith to the "TO-BE" platform, now factoring in the existing complexity.

| Gap | "AS-IS" State (Current) | "TO-BE" Target (Required) |
| --- | --- | --- |
| **Database Layer & Transactional Integrity** | **Raw SQL** (`aiosqlite`) via a repository. Logic is **non-transactional** (e.g., `msell` makes 5+ separate `UPDATE`/`INSERT` calls). | **SQLAlchemy ORM** with declarative models. Logic must be **transactional** using the "Unit of Work" (Session) pattern. **This is the #1 technical priority.** |
| **L1/L2 Separation** | Monolithic `service_core.py` handles all logic (L1-like balance changes, L2-like P2P trades, and L2-like employment) in one file. | A clear directory and service separation. Logic from `service_core.py` must be broken apart and moved into `services/l1/` (e.g., core balance transfers) and `services/l2/` (e.g., trading, employment). |
| **L2 Entities (Companies)** | Has V1 precursors: `jobs`, `employees`, `business_account`. These are tied to *individual users*. | **New L2 Company Service**. This will *evolve* the existing V1 concepts into a true multi-member entity with a shared budget, inventory, and "Assembly Lines" (automation). |
| **Economy Core (Markets)** | Has a functional **L2 P2P Market** (`mat_orders`, `mat_deals`). | **New L1 AMM Service** must be built. The architecture must define how this new L1 market for raw materials coexists with the *existing* L2 P2P market. |
| **Governance** | None. No voting or proposal logic. | **New L1 Governance Service** (Parliament, Voting, Eligibility checks). This is a "from-scratch" build. |
| **New Asset Types** | Has `artifacts` and `materials`. | **New Patent/License Service**. This is a "from-scratch" build, likely modeling `patents` as a new asset type. |
| **API Layer** | None (Bot-only). | **New FastAPI Gateway** to expose L1/L2 services (e.g., balances, company info) to external apps (like Minecraft or dashboards). |