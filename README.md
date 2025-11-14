# 🎫 Ticketonomics

> Community-driven virtual economies, primarily on Telegram.

Ticketonomics is a software project that simulates a self-sustaining digital economy. It introduces a virtual currency (called "tickets") that users can earn, spend, and trade within a community.

The primary interface is a **Telegram bot**, which functions as the system's "central bank," marketplace, and engagement hub. It's part social experiment, part gamification engine, and part prototype for decentralized micro-economies.

---

## 💡 Core Concepts

The system is designed to be a transparent and self-sustaining digital economy that encourages collaboration, fairness, and creative participation.

Our architecture is built on a modular, **Two-Layer (L1/L2) Economic Model**:

* **L1 (Foundation):** The core "mainnet" protocol. It is "budget-less" and responsible for foundational elements: user balances, the 'ticket' as a unit of value, and core governance (The Parliament). It acts as the ultimate source of truth and a regulator for the macro-economy.

* **L2 (Application Layer):** These are the "budgeted" applications and integrations built *on top* of L1. This includes player-run **Companies**, community-run "States," and external integrations like the **Minecraft Server**. L2 entities collect fees into their own treasuries to create cyclical, self-funding economies.

Other key principles include:
* **Community as Economy:** User interactions and collaboration form the foundation of all value.
* **Gamified Engagement:** Users are rewarded for participation, creativity, and cooperation.
* **Transparency:** All major economic actions are designed to be visible and verifiable.

## 🛠️ Technology Stack

This project is built with a focus on modularity, scalability, and asynchronous performance, all orchestrated with Docker.

* **Core Language:** **Python 3.9**
* **Bot Framework:** **Aiogram 3.15** (for the primary asynchronous Telegram bot)
* **API & Web:**
    * **FastAPI:** For the API gateway, web dashboards, and external integrations.
    * **Uvicorn:** As the high-performance ASGI server for FastAPI.
* **Data & Storage:**
    * **Redis:** Used as a persistent state management (e.g., FSM).
    * **aiosqlite:** For lightweight, asynchronous local database storage.
* **Task Management:**
    * **APScheduler:** For managing time-based events, job queues, and automated tasks.
* **Data Validation:**
    * **Pydantic:** For robust data validation and settings management across the API and bot.
* **Deployment & Infrastructure:**
    * **Docker & Docker Compose:** For complete containerization and orchestration of all services (bot, website, API, database, proxy).
    * **NGINX:** As a reverse proxy and web server.

## 🚀 Project Status

This project is currently in **active development**. The L1 foundation is being solidified, and L2 applications (like the Company system and game integrations) are in the design and prototyping phase.