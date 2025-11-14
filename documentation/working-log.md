## 1\. Core Architecture & Database

  * **Primary Language:** Python
  * **Telegram Framework:** Aiogram
  * **API Framework:** FastAPI (for L2 integrations and gateways)
  * **Database:**
      * **Development:** SQLite
      * **Production/Migration Target:** PostgreSQL
  * **ORM:** **SQLAlchemy ORM** (confirmed as the standard for all new data models).
  * **Architectural Pattern:** **L1/L2 (Foundation/Application)**
      * **L1:** "Budget-less" core services (AMM, Balances, Governance). Fees are "sinks."
      * **L2:** "Budgeted" applications (Companies, Minecraft Server) that have their own treasuries and participate in the economy.

## 2\. Economic System: Automated Market Maker (AMM)

  * **Purpose:** Provides a stable, automated market for **raw materials** to solve for low user liquidity.
  * **Core Parameters (Config):**
      * `BasePrice`: The admin-set "fair" value (e.g., 10 tickets).
      * `TargetInventory`: The ideal amount the AMM *wants* to hold (e.g., 1000 units).
  * **Pricing Algorithm (Final, V2):**
      * `Central_Price = BasePrice * (TargetInventory / CurrentInventory)`
  * **Buy/Sell Spread (Ticket Sink):**
      * A `Spread` value (e.g., 1 ticket) is used, or a percentage.
      * **AMM Buys At:** `Central_Price - Spread`
      * **AMM Sells At:** `Central_Price + Spread`
  * **Test Cases (using `BasePrice=10`, `Target=1000`):**
      * `Current = 1000` (Balanced): Price = 10.0
      * `Current = 1200` (High Supply): Price = 8.33
      * `Current = 4000` (Extreme Supply): Price = 2.5
      * `Current = 700` (High Demand): Price = 14.28

## 3\. Core Services & Data Models (Proposals)

### 3.1. Inventory Service

  * **Table: `items`**
      * `item_id` (PK)
      * `name`
      * `description`
      * `type` (e.g., 'raw', 'classic', 'custom', 'alive', 'patent')
  * **Table: `user_inventory`**
      * `user_id` (FK)
      * `item_id` (FK)
      * `quantity`
  * **Table: `company_inventory`**
      * `company_id` (FK)
      * `item_id` (FK)
      * `quantity`

### 3.2. Crafting Service

  * **Table: `recipes`**
      * `recipe_id` (PK)
      * `name`
      * `type` ('classic', 'custom')
      * `status` ('active', 'proposed')
      * `owner_id` (FK to `user` or `company`, for patent)
  * **Table: `recipe_inputs`**
      * `recipe_id` (FK)
      * `item_id` (FK)
      * `quantity_required`
  * **Table: `recipe_outputs`**
      * `recipe_id` (FK)
      * `item_id` (FK)
  * **Table: `crafting_jobs`** (For time-consuming crafts)
      * `job_id` (PK)
      * `user_id` (FK)
      * `recipe_id` (FK)
      * `status` ('queued', 'running', 'complete')
      * `eta_timestamp`
      * `is_automated` (bool, for Assembly Lines)
  * **Table: `factory_components`**
      * `owner_id` (FK to `user` or `company`)
      * `component_type` (e.g., 'forge', 'lab', 'assembly\_line')
  * **Table: `licenses`** (For Patent system)
      * `license_id` (PK)
      * `patent_recipe_id` (FK to `recipes`)
      * `owner_id` (FK to `user`)
      * `licensee_id` (FK to `user` or `company`)
      * `duration` / `quantity_limit`

### 3.3. Governance Service

  * **Table: `proposals`**
      * `proposal_id` (PK)
      * `proposer_user_id` (FK)
      * `proposed_recipe_data` (JSON/Text)
      * `status` ('voting', 'approved', 'rejected', 'vetoed')
      * `timestamp`
  * **Table: `votes`**
      * `proposal_id` (FK)
      * `user_id` (FK)
      * `vote_choice` (bool/int)

## 4\. Feature Implementations

### 4.1. Crafting & Factories

  * **Mechanism:** Crafting is not instant. It creates an entry in the `crafting_jobs` table. A separate worker/scheduler will process this queue.
  * **Modular Factories:** A recipe will define `component_required: 'forge'`. The `CraftingService` must check if the user's factory (via `factory_components` table) has this component installed.
  * **Alive Objects:** A **Scheduled Service (Cron Job)** must run (e.g., daily) to scan all `alive_objects` in `user_inventory` and apply the "Upkeep Cost," deducting tickets or items.

### 4.2. Governance (Parliament)

  * **Voting:** "One Person, One Vote."
  * **Voter Eligibility Rule:** To prevent bot manipulation, the `GovernanceService` must check for eligibility before accepting a vote.
      * *Rule (Example):* `user.account_age > 7 days` AND (`user.balance > 100 tickets` OR `user.owns_factory == True`).

### 4.3. L2 Companies

  * **Rule:** 3-person minimum for creation.
  * **Accounts:** A company has its own `company_id` which acts like a `user_id` for balances, `company_inventory`, etc.
  * **Role System:** A simple role model is required (e.g., `Owner`, `Officer`, `Member`) to manage permissions for treasury withdrawals and production.
  * **Automation:** "Assembly Lines" are special `factory_components` only buildable by companies. They allow `is_automated=True` jobs in the `crafting_jobs` queue.
  * **Bot-Enforced Contracts (Escrow):**
    1.  Company posts a contract.
    2.  The `ContractService` creates an `escrow` entry and *immediately* transfers the tickets/items from the company to an internal "escrow" account.
    3.  A player accepts.
    4.  The service validates and swaps the assets, releasing the escrow.

## 5\. L2 Integration: Minecraft Server

  * **Wallet:** Create a virtual user/wallet for the server (e.g., `minecraft_server_budget`).
  * **API (FastAPI):** Must provide at least two endpoints for the MC plugin.
      * **Check Balance:**
          * `GET /balance/<user_id>`
          * *Returns:* `{ "user_id": ..., "balance": ... }`
      * **Transfer Funds:**
          * `POST /transfer`
          * *Body:* `{ "from": "player_id_123", "to": "minecraft_server_budget", "amount": 100 }`
          * *Returns:* `{ "success": true, "transaction_id": ... }`

## 6\. UI / Commands (UX Layer)

  * **/inventory:** (DM) Check personal inventory.
  * **/recipes:** (DM) View available recipes.
  * **/craft \<recipe\_name\>:** (DM) Starts a new job in the `crafting_jobs` queue.
  * **/propose:** (DM) Starts the "Parliament" proposal flow for a new recipe.
  * **/license \<@user\> \<recipe\_name\> [options]:** (DM) Grants a patent license to a user/company.
  * **/produce \<item\> \<quantity\>:** (DM, Company-only) Queues automated jobs for an Assembly Line.
  * **/mine:** (Group) Inline button for "Resource Spawn" events.
  * **/trade @user ...:** (Group) P2P trading (may be replaced by contracts).
  * **/contract [WTB/WTS] ...:** (Group/DM) Company command to post a public, bot-enforced contract.
  * **/fill\_contract \<id\> [amount]:** (DM) Player command to fill an open contract.
  * **/proposal\_status \<id\>:** (Group) Check the status of a vote.