# 🧭 Ticketonomics — Project Context Export for Gemini

## 1. Overview

Ticketonomics is a digital ecosystem built around a community-driven virtual economy integrated primarily through Telegram bots.

It introduces a virtual currency ("tickets") used for transactions, reputation, and engagement inside communities and connected platforms.

Originally developed as part of a software engineering practicum, it has since evolved into a living project combining social mechanics, gamification, and programmable financial systems.

## 2. Core Vision

The goal of Ticketonomics is to simulate a transparent and self-sustaining digital economy that encourages collaboration, fairness, and creative participation.

**Key principles:**
- **Community as economy** — user interactions form the foundation of value
- **Automation** — most economic processes are handled by bots and APIs
- **Transparency** — all user actions and balances are visible and verifiable
- **Scalability** — the architecture supports expansion to games, web apps, and APIs
- **Gamified engagement** — users are rewarded for participation, creativity, and cooperation
- **Multi-Audience UX** — the system is designed to cater to casual ("tappers"), engaged ("consumers"), and hardcore ("proactive") users simultaneously.

The system functions as both a social incentive engine and a prototype of decentralized micro-economies.

## 3. Architectural Model

Ticketonomics follows a modular, layered architecture. While technically structured into a **Communication Layer**, **Service Layer**, and **Repository Layer**, it is strategically defined by a **Two-Layer (L1/L2) Economy**:

- **L1 (Foundation):** The core protocol and economic "mainnet." It is responsible for foundational elements: user balances, the "ticket" as a unit of value, the AMM, and core governance. This layer is "budget-less"—its fees are **ticket sinks** designed to regulate the macro-economy.

- **L2 (Application Layer):** These are the "budgeted" applications and integrations that build *on top* of L1. L2 entities include player-run **Companies**, community-run "States," and external integrations like the **Minecraft Server**. They collect fees into their own treasuries to create cyclical economies.

The design emphasizes asynchronous, event-driven logic, enabling responsive and scalable interaction handling.

## 4. Technology Stack

- **Language:** Python
- **Frameworks:** Aiogram (Telegram), FastAPI for API gateways
- **Database:** SQLite (for rapid development), migrating to **SQLAlchemy ORM** (for L2 complexity and production)
- **Versioning and DevOps:** Git, modular environment configuration
- **Integrations:** Web dashboards, Game Servers (e.g., Minecraft via API), REST APIs

## 5. Data and Economy Model

Ticketonomics revolves around a detailed, player-driven production economy.

- **Hybrid Market Model:** Solves low-liquidity by combining a core **L1 AMM** (for raw materials, using a ratio-based dynamic price) with a player-driven **L2 P2P Market** (for crafted products).
- **Production & Crafting:** A core L2 loop where players use **Modular Factories** and **Components** (e.g., "Forge," "Lab") to produce goods. Crafting is **time-consuming**, managed by a Job Queue.
- **Intellectual Property:** Inventors can propose custom recipes to the Parliament. Upon approval, they receive a **Patent** asset, which can be **Licensed** to other players.
- **Digital Assets:** Includes "tickets" (currency) and "game objects" (e.g. gemstones, products, patents).
- **Economic Regulation:** Uses a dual model of **L1 Ticket Sinks** (permanent removal) and **L2 Cyclical Economies** (application budgets).

## 6. Governance and Philosophy

Ticketonomics treats software not only as infrastructure but as a living culture of digital interaction.

**Philosophical underpinnings:**
- Economic interaction as communication
- **Community feedback as regulation**
- Playfulness as sustainability

This is implemented via:
- **The Parliament (L1):** A governance body where players vote on new, community-proposed crafting recipes.
- **Fair Voting:** Employs a **"One Person, One Vote"** model, protected by **Voter Eligibility** rules (e.g., account activity) to prevent bot manipulation.
- **Creator Veto:** A final administrative check to maintain game balance.

## 7. Integration and Ecosystem

Ticketonomics is designed to interconnect platforms (L2 Applications) via the shared L1 economic layer.

**Integrations include:**
- **Telegram Communities:** The primary interface for L1 (governance) and L2 (company) interactions.
- **L2 Organizations (Companies):** Player-run groups with shared **budgets** and **inventories**. They can build **Assembly Lines** for automation.
- **Game Servers (e.g., Minecraft):** Treated as an L2 Organization with its own budget. It uses the L1 API for balance checks and transfers, creating a cyclical economy for server-specific fees (e.g., land rent) and rewards (e.g., quest payouts).
- **API Endpoints (FastAPI):** A full API layer for all L2 applications and external partners.

## 8. Development Approach

The development strategy prioritizes:

- **Testability** — isolated modules, clear data boundaries
- **Extensibility** — ability to attach new services (banking, artifacts, analytics)
- **Educational and experimental value** — each component serves as a learning ground for applied economics and software design

## 9. Future Directions

**Long-term goals include:**
- **Implementation:** Building the L1/L2 framework with the defined Production, Governance, and Company services.
- **Transition to SQLAlchemy ORM:** A confirmed requirement for the new, complex data models.
- **Expansion:** Launching the L2 Company system and the Minecraft integration.
- **Analytics:** Developing a public dashboard to monitor L1/L2 economic health.
- **Microservice architecture:** Potential for future scalability and modular development.

## 10. Summary for Gemini

You are to internalize this as the complete conceptual context of Ticketonomics.

**When reasoning or generating content related to this project:**
- Treat Ticketonomics as an evolving social-economy framework with a strong **L1/L2 modular architecture**.
- Assume that individual command names, APIs, or implementation details may change — your focus is the conceptual continuity and architectural consistency.
- When proposing features, maintain alignment with the project's economic, social, and gamified principles.
- Use this context as a semantic base for any further reasoning, integration planning, or technical generation.

## Keywords

ticketonomics, telegram, bot, aiogram, python, tickets, virtual currency, community economy, gamification, economic system, digital artifact, microservice, api, postgresql, sqlite, sqlalchemy, fastapi, automation, modular architecture, ecosystem, economics, L1, L2, AMM, patent, license, crafting, governance, company, budget, minecraft