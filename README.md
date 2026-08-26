# FlyRank Task API

This is a small CRUD API that manages a to-do list in memory. You can create, read, update, and delete tasks. Built with Python and FastAPI.

## How to Run
To set up an isolated virtual environment, install the dependencies, and start the server on localhost, run these commands in order:

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic
uvicorn main:app

## Endpoints

| CRUD Operation | HTTP Method | Endpoint | Description |
|---|---|---|---|
| Read | GET | `/` | API Information |
| Read | GET | `/health` | Server health check |
| Read | GET | `/tasks` | List all tasks |
| Create | POST | `/tasks` | Add a new task |
| Read | GET | `/tasks/{task_id}` | Get a specific task |
| Update | PUT | `/tasks/{task_id}` | Update a specific task |
| Delete | DELETE | `/tasks/{task_id}` | Remove a specific task |

## Example Request
Here is a test using `curl -i` to hit the health endpoint:

```bash
curl -i http://localhost:8000/health

HTTP/1.1 200 OK
date: Wed, 26 Aug 2026 18:50:00 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}