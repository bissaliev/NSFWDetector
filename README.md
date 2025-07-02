# NSFWDetector

Простое приложение для модерации изображений через DeepAI NSFW API.

## Установка

```bash
git clone git@github.com:bissaliev/NSFWDetector.git
cd NSFWDetector/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создайте файл .env и добавьте в него ваш ключ DeepAI:

```bash
DEEPAI_API_KEY=your_deepai_api_key
```

Запуск

```bash
uvicorn app.main:app --reload
```

Пример запроса

```bash
curl -X POST -F "file=@example.jpg" http://localhost:8000/moderate
```

Ответы:

- Безопасное изображение:

    ```json
    { "status": "OK" }
    ```

- Обнаружен NSFW контент:

    ```json
    { "status": "REJECTED", "reason": "NSFW content" }
    ```
