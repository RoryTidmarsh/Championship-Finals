
# API Structure (FastAPI)

## File Organization

Think of it like a restaurant:

```
/src/api/
├── __init__.py       → The kitchen setup (gets everything ready)
├── routes.py         → The menu (what requests you can make)
├── models.py         → The order forms (what data you're sending/receiving)
└── handlers.py       → The chefs (does the actual work)
```

## Each File - Simple Explanation

### `__init__.py` - The Setup
Creates and configures the FastAPI app, sets up CORS (allows frontend to talk to backend).

**In simple terms:** It's like opening the restaurant and turning on the lights. Without this, nothing runs.

---

### `routes.py` - The Menu
Defines all the endpoints (URLs) your frontend can call, like `/api/shows`, `/api/combined-results`.

**In simple terms:** If your API is a restaurant, this is the menu. It says "You can order a burger from `/food`, pizza from `/pizza`, etc."

**Example endpoints:**
- `GET /api/shows` → "Give me list of shows"
- `GET /api/combined-results?agility=123&jumping=456` → "Give me results for these classes"
- `GET /api/requirements?agility=123&jumping=456` → "Tell me what competitors need to qualify"

---

### `models.py` - The Order Forms
Defines what data goes in and comes out. Validates incoming data automatically using Pydantic.

**In simple terms:** When you place an order, the restaurant needs to know: Is it a valid order? Do you have the right info? These are the templates for that.

**Examples:**
```python
ShowItem = {name: "Crufts", date: "2025-03-14", id: "123"}
CombinedResults = {agility_status, jumping_status, combined_results, height}
RequirementsResponse = {cutoff_position, requirements: [list of competitors]}
```

---

### `handlers.py` - The Chefs
Contains the actual logic. Takes requests from `routes.py`, uses your core modules (`KC_ShowProcesser`, `plaza_scraper`, etc.), and returns data.

**In simple terms:** When someone orders from the menu, the chef is who actually makes it. This file orchestrates your core modules to fetch and process data.

**Flow:**
1. Frontend asks for combined results
2. `routes.py` receives the request
3. `handlers.py` uses your core modules to fetch and combine data
4. Returns formatted data back to frontend

---

## Request Flow (End-to-End)

```
Frontend (browser)
    ↓ calls /api/combined-results?agility=123&jumping=456
    ↓
routes.py (checks if request is valid)
    ↓ calls handler function
    ↓
handlers.py (uses core modules to fetch data)
    ↓ calls KC_ShowProcesser, plaza_scraper, etc.
    ↓
models.py (validates/formats response data)
    ↓ returns JSON
    ↓
Frontend (gets data, displays it)
```

---

## Quick Summary Table

| File | Job | Analogy |
|------|-----|---------|
| `__init__.py` | Start the app | Opening the restaurant |
| `routes.py` | Define endpoints | The menu |
| `models.py` | Validate data | Order forms/templates |
| `handlers.py` | Do the work | The chefs cooking |

---

## FastAPI Advantages

✅ **Automatic validation** - Pydantic models validate incoming params automatically  
✅ **Built-in docs** - `/docs` gives you interactive Swagger UI automatically  
✅ **Type safety** - Mypy can catch errors, IDE autocomplete works better  
✅ **Async support** - Better for concurrent requests (web scraping, DB queries)  
✅ **Cleaner code** - No need for separate response formatting  
✅ **Better performance** - Async by default