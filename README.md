# Local setup

## Start docker

1. Copy .env file in root directory and .env in ./docker directory
2. Build docker

``` 
cd docker
docker compose up -d --build
```

# Manticore

SSH into manticore container and enter mysql:

```mysql -h 127.0.0.1 -P 9306;```

# Deployment

Run `./scripts/production_deployment.sh`

# Various

```
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE media_videocategorypivot;
TRUNCATE TABLE media_videoitem;
ALTER TABLE media_videoitem AUTO_INCREMENT = 1;
ALTER TABLE media_videocategorypivot AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS=1;
```