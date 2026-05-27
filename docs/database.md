# Server

## Export

mysqldump --single-transaction --skip-lock-tables --no-tablespaces -u root -p'xxx' automationapp > export.sql

## Copy

docker cp automationapp-mysql:/export.sql ./export.sql

# Locally

## Copy

docker cp export.sql automationapp-mysql:/home/export.sql

## Import locally

mysql -u root -p'xxx' automationapp < home/export.sql 