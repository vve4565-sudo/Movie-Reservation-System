# CINEMA landing

Статический адаптивный лендинг для бронирования билетов в кино.

`admin.html` — отдельная страница администратора. После входа с ролью `admin`
пользователь автоматически перенаправляется туда; сохранённая в рамках вкладки
авторизация используется на обеих страницах.
При ответе API `401` или `403` с `Token expired` клиент запрашивает новый access-токен
через `/auth/refresh` и один раз повторяет исходный запрос.

Лендинг учитывает эндпоинты из предоставленной OpenAPI-схемы:

- POST /auth/login
- POST /auth/registration
- GET /auth/logout
- GET /auth/refresh
- GET /movies/
- POST /movies/
- PATCH /movies/{id}
- DELETE /movies/{id}
- GET/POST /shows/
- GET /hall/
- POST /shows/?movie_id={movie_id}&hall_id={hall_id}&start={start}
- GET /shows/hall/{hall_id}
- GET /shows/avalabile
- GET/DELETE /shows/{id}
- GET/POST /reservation/
- GET /reservation/{show_id}
- DELETE /reservation/{reservation_id}
- Административные операции доступны только авторизованной роли `admin`.

При открытии бронирования кресла загружаются из `/shows/hall/{hall_id}`, а занятые места определяются по ответу `/reservation/{show_id}`.
