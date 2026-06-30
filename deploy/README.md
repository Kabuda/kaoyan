# Public Deployment

This project is ready for a single-server public deployment with Docker Compose and Caddy.

## Server Requirements

- Ubuntu 22.04 or newer
- Docker and Docker Compose plugin
- A domain name with an A record pointing to the server IP
- Open firewall ports: `80` and `443`

Do not expose MySQL or the FastAPI backend directly to the public internet. In production Compose, only Caddy publishes ports.

## First Deploy

```bash
git clone https://github.com/Kabuda/kaoyan.git
cd kaoyan
cp .env.production.example .env
```

Edit `.env`:

- `DOMAIN`: your real domain, for example `kaoyan.example.com`
- `CORS_ORIGINS`: `https://<your-domain>`
- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `JWT_SECRET`
- `INITIAL_ADMIN_PASSWORD`

Then start:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Check status:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f caddy
docker compose -f docker-compose.prod.yml logs -f backend
```

Visit:

```text
https://<your-domain>
```

## Update Deploy

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

The backend container runs `alembic upgrade head` during startup.

## Backup

Create a database backup before risky updates:

```bash
docker compose -f docker-compose.prod.yml exec mysql \
  mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" > backup.sql
```

Restore:

```bash
docker compose -f docker-compose.prod.yml exec -T mysql \
  mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" < backup.sql
```

## Useful Commands

```bash
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml down --volumes
```

Only use `down --volumes` when you intentionally want to delete the database volume.
