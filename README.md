# lockerAPI


## Migrations

**Run commands inside a docker container**

Check current revision
```bash
.venv/bin/alembic current
```

To run all of your outstanding migrations, execute the `upgrade head` command
```bash
.venv/bin/alembic upgrade head
```

To roll back the latest migration operation, you may use the `alembic downgrade` command
```bash
.venv/bin/alembic alembic downgrade -1
```

Revision History: Use `.venv/bin/alembic history` to see the history of migrations and understand the steps involved.
Detailed View: Use `.venv/bin/alembic show <revision>` to get detailed information about specific revision scripts.
