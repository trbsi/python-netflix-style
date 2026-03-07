# Local setup

## Start docker

1. Copy env files in root directory and in ./docker directory
2. Build docker

``` 
cd docker
docker compose up -d --build
```

3. Manticore config

SSH into manticore container and enter mysql:

```mysql -h 127.0.0.1 -P 9306;```

Create table:

```
CREATE TABLE IF NOT EXISTS videos_index (
    id BIGINT,
    title TEXT,
    thumbnail STRING,
    duration INT,
    categories TEXT
);
```

# Deployment

Run `./scripts/production_deployment.sh`