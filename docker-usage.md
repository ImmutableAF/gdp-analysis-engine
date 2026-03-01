# Docker Usage Guide — GDP Analysis Engine

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- Git installed

---

## Prod User

Just wants to run the app. No dev tools, no source mounts — pure execution.

```bash
git clone https://github.com/ImmutableAF/gdp-analysis-engine/tree/development-v3
cd gdp-analysis-engine
docker compose -f docker-compose.prod.yaml up --build
```

| Service       | URL                   |
| ------------- | --------------------- |
| Streamlit UI  | http://localhost:8501 |
| Core API      | http://localhost:8010 |
| Analytics API | http://localhost:8011 |

To stop:

```bash
docker compose -f docker-compose.prod.yaml down
```

---

## Dev User

Wants live reload, tests, profiling, and analysis reports.

```bash
https://github.com/ImmutableAF/gdp-analysis-engine/tree/development-v3
cd gdp-analysis-engine
docker compose -f docker-compose.dev.yaml up --build
```

Source changes in `./src` reflect instantly inside the container via the volume mount — no rebuild needed.

### Running Dev Tools

Open a shell inside the running container:

```bash
docker exec -it <container_name> bash
```

> Find the container name with `docker ps`.

Then run any of the following:

**Tests & coverage**

```bash
pytest --cov=src --cov-report=html:reports/coverage
```

**Dead code detection (vulture)**

```bash
vulture src/ > .dev/reports/vulture.txt
```

**Cyclomatic complexity (radon)**

```bash
radon cc src/ -a > .dev/reports/radon.txt
```

**Dependency diagram (pydeps)**

```bash
pydeps src/
```

**Dynamic profiling (snakeviz)**

```bash
python -m cProfile -o .dev/reports/profile.out src/main.py
snakeviz .dev/reports/profile.out
```

**Flamegraph (py-spy)**

```bash
py-spy record -o .dev/reports/profile.svg -- python -m src.main
```

All output lands in `.dev/reports/` on your **host machine** via the volume mount and persists after the container stops.

To stop:

```bash
docker compose -f docker-compose.dev.yaml down
```

---

## File Structure

```
gdp-analysis-engine/
├── src/                        # Application source (mounted in dev)
├── data/                       # Data files (mounted in both)
├── logs/                       # Logs (mounted in dev)
├── .dev/
|------reports/                    # Dev tool outputs (mounted in dev)
├── requirements.prod.txt       # Runtime dependencies only
├── requirements.dev.txt        # Dev/analysis tools (additive on top of prod)
├── Dockerfile.prod
├── Dockerfile.dev
├── docker-compose.prod.yaml
└── docker-compose.dev.yaml
```

---

## Key Differences Between Images

|                           | Prod    | Dev    |
| ------------------------- | ------- | ------ |
| Source mounted as volume  | ✗       | ✅     |
| Live reload               | ✗       | ✅     |
| pytest / coverage         | ✗       | ✅     |
| vulture / radon           | ✗       | ✅     |
| pydeps / graphviz         | ✗       | ✅     |
| snakeviz / yappi / py-spy | ✗       | ✅     |
| flamegraph.pl             | ✗       | ✅     |
| Sphinx docs               | ✗       | ✅     |
| Image size                | smaller | larger |
