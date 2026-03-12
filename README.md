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

## Mysql

```
DELETE FROM media_videocategorypivot;
DELETE FROM media_videoitem;
DELETE FROM media_videocategory;
ALTER TABLE media_videoitem AUTO_INCREMENT = 1;
ALTER TABLE media_videocategorypivot AUTO_INCREMENT = 1;
ALTER TABLE media_videocategory AUTO_INCREMENT = 1;
```

## Manticore

`drop table videos_index;`