### .env
Пример конфигурации файла .env [здесь](https://github.com/KociHH/Invisibly/blob/main/env.txt)


### Запуск
Всех контейнеров:
```bash
docker compose up -d --build
```

Определенный контейнер (пример):
```bash
docker compose up -d --build service_frontend
```

**Важно:** Для корректного запуска отдельных контейнеров сначала поднять общий сервис в корне проекта, который инициализирует volumes, затем запускать нужные контейнеры.