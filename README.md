# lockerAPI

## Migrations

New migration

```bash
alembic revision -m "create XXX table"
```

> [!NOTE]  
> Run below commands inside a docker container

Check current revision

```bash
docker exec -it lockerapi-web .venv/bin/alembic current
```

To run all of your outstanding migrations, execute the `upgrade head` command

```bash
docker exec -it lockerapi-web .venv/bin/alembic upgrade head
```

To roll back the latest migration operation, you may use the `alembic downgrade` command

```bash
docker exec -it lockerapi-web .venv/bin/alembic alembic downgrade -1
```

To run rolled back migration again: 
```bash
docker exec -it lockerapi-web .venv/bin/alembic alembic downgrade +1
```

Revision History: Use `.venv/bin/alembic history` to see the history of migrations and understand the steps involved.
Detailed View: Use `.venv/bin/alembic show <revision>` to get detailed information about specific revision scripts.

## Update python dependencies

```bash
uv lock --upgrade
```
### Check & format project
```bash
ruff check app/
```

```bash
ruff check app/ --fix
```

## Cold start

- alembic migration
- insert geo data `uv run locations.py`

### Truncate PG data
```postgresql
TRUNCATE TABLE locations RESTART IDENTITY CASCADE ;
```

## ADR

http://localhost:5000/{language}/{room_name}
http://localhost:5000/{language}/l/{location}
http://localhost:5000/{language}/l/{location}/{tag}
http://localhost:5000/{language}/c/{company_name}

## TODO:
 - don't allow to add duplicated departments
