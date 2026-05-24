# Pulse

<img width="1908" height="934" alt="image" src="https://github.com/user-attachments/assets/bf9c8eb4-86f2-4751-8328-ff906d9e9270" />

fast, containerized c++ telemetry pipeline. scrapes host cpu and shoves it into grafana via redis/postgres.

**Live Demo:** [http://13.236.184.173:3000](http://13.236.184.173:3000) *(Read-only Viewer Mode)*

### the stack
- **agent (`/agent`)**: c++ daemon. runs with `pid: host` to scrape true system cpu, not docker's.
- **api (`/api`)**: c++ crow server. ingests json payloads and dumps them into redis queue.
- **worker (`/worker`)**: python script. drains redis queue and flushes to postgres.

### exposed ports
| port | service | what it does |
|---|---|---|
| `8080` | api | `POST /ingest` endpoint |
| `3000` | grafana | dashboards |
| `5432` | postgres | persistent storage |
| `6379` | redis | fast queue buffer |

### default creds (change these)
* **grafana**: `admin` 
* **postgres**: user `admin`, pass `secret`, db `telemetry`

---

### quick start

1. setup env:
```bash
cp .env.example .env
```

2. pull the pre-built images and run (fastest way):
```bash
docker compose pull
docker compose up -d
```

*(Run `docker compose up -d --build` if you want to compile it manually).*

3. check if the agent is shipping:
```bash
docker compose logs -f pulse-agent
```

open `localhost:3000` to see the dashboard. 

Inside the dashboard, your PostgreSQL isn't probably initially set up. Go to the **connections** tab and fill up these variables:
- Host URL: postgres-db:5432
- Database name: telemetry
- Username: admin
- Password: secret

``Take note that these are the default values inside .env. It is recommended to change these values.``

Put this in the query just below setting up the dashboard to see the cpu usage:
```sql
SELECT 
  ingested_at AS "time", 
  cpu_usage, 
  server_id
FROM server_health
WHERE $__timeFilter(ingested_at)
ORDER BY ingested_at ASC;
```
To kill the containers:
```bash
docker compose down
```
