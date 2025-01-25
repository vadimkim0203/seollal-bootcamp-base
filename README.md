# Seollal Bootcamp 2025 Backend

## Setup for Development

```shell
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

## Configuration

### Environment Variables

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| PUBLIC_BASE_URL | http://localhost:5000 | Used for generating internal links, like next and previous page. Don't include the trailing slash. Do include the protocol. |
| HOST_ADDRESS | 0.0.0.0 | The IP address that the server should bind to. In most cases, the default is okay. |
| PORT | 5000 | The port that the server should bind to. The default is good for development, but production should use a more appropriate port. |
| DB_HOST | localhost | The resolvable hostname or IP address to use for connecting to the PostgreSQL database server. |
| DB_PORT | 5432 | The port to use for connecting to the PostgreSQL database server. |
| DB_USERNAME | root | The username to use when logging into the PostgreSQL database server. Note that the default value should absolutely not be used in production. (Also note that "root" is also not the default superuser in PostgreSQL anyway.) |
| DB_PASSWORD | root | The password to use when logging into the PostgreSQL database server. Note that the default value should absolutely not be used in production. |
| DB_DATABASE | ecommerce | The name of the database on the PostgreSQL server to connect to. |
=======

## Formatting

```shell
ruff check --fix .
```

## Running

### For Dev

```shell
source .venv/bin/activate  # if not done already
docker compose up -d
alembic upgrade head
run
```

### Dockerized

#### Build the Image

```shell
# Build the image defined in the current directory, tagging it with the name "seollal-bootcamp"
docker build . -t seollal-bootcamp
```

#### Run the Container

```shell
docker compose up -d
# This runs the image as a container named backend-server, deletes the container when it stops,
# joins it to the network of the containers running via docker compose, publishes the container's
# port 80 to our port 8080, and sets the environment variables properly
docker run --name backend-server --rm \
    --network seollal-bootcamp-2025-backend_default \
    --env DB_HOST=database \
    --publish 8080:80 \
    seollal-bootcamp
```

## Stopping

Ctrl + C, then

```shell
docker compose down
```
