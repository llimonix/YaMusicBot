![Logo](https://github.com/user-attachments/assets/bffa69ff-51e8-4e54-bf4b-741e2663ed98)

— это Discord-бот, который воспроизводит музыку из Яндекс Музыки.

## Особенности
- Поиск и проигрывание треков с Яндекс Музыки.
- Поддержка потокового воспроизведения через Lavalink.
- Простая настройка и использование.

## Установка и запуск

### 1. Клонирование репозитория
Склонируйте проект на ваш локальный компьютер:

```bash
git clone https://github.com/llimonix/YaMusicBot
cd YaMusicBot
```

### 2. Установка зависимостей
Убедитесь, что у вас установлен Python 3.9+ и виртуальная среда активирована. Затем установите зависимости:

```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации
1. Переименуйте файл `.env.example` в `.env`:
    ```bash
    mv .env.example .env
    ```
2. Откройте файл `.env` и настройте параметры подключения к Discord, Lavalink и другим сервисам. Пример:
    ```env
    TOKEN=MTE...
    HOST_WAVELINK=http://localhost
    PORT_WAVELINK=4444
    PASS_WAVELINK=pass
    DATABASE=servers.db
    ```

### 4. Установка и настройка Lavalink
Для работы бота необходимо скачать и настроить **Lavalink**.  

1. Скачайте последнюю версию Lavalink:
   [Ссылка на Lavalink](https://github.com/lavalink-devs/Lavalink/releases)

2. Скачайте плагины **LavaSrc** и **LavaSearch**:
   - [LavaSrc](https://github.com/topi314/LavaSrc)
   - [LavaSearch](https://github.com/topi314/LavaSearch)

3. Поместите плагины в папку `plugins` рядом с исполняемым файлом Lavalink.

4. Запустите Lavalink:
    ```bash
    java -jar Lavalink.jar
    ```

### 5. Запуск бота
После настройки выполните команду для запуска бота:

```bash
python main.py
```

## Использование
- Пригласите бота в ваш сервер через ссылку OAuth2.
- Используйте команды бота для поиска и воспроизведения музыки.

## Поддержка
Если у вас возникли вопросы или проблемы, создайте тикет в разделе Issues этого репозитория.

## Лицензия
Этот проект распространяется под лицензией MIT.

## Скриншоты

| Плеер с кнопками  | Очередь треков |
| ------------- | ------------- |
| ![](https://github.com/user-attachments/assets/04b04a5e-f186-4244-9c6d-da6fc27b1406)  | ![](https://github.com/user-attachments/assets/ae46c1ed-fb1c-4742-8679-91257c611447)  |
