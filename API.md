# API reference (for frontend)

Base URL: `http://127.0.0.1:8000` (change for production).

Interactive docs: `/docs`

---

## Order to wire up

1. `GET /health` — API + DB OK?
2. `POST /user/signup` or `POST /user/login` — get `user_id` for chat (optional)
3. `POST /chat/load-conversation` — open an existing thread
4. `POST /chat` — send message, get full reply
5. `POST /chat/stream` — send message, streamed reply (SSE)

---

## `GET /health`

**200:** `{ "status": "healthy", "database": "connected" }`

**503:** `{ "status": "unhealthy", "database": "disconnected", "detail": "..." }`

---

## `GET /`

**200:** `{ "message": "Hello, World!" }`

---

## `POST /user/signup`

**Body (JSON):**

```json
{ "email": "user@example.com", "password": "plain text — sent over HTTPS in production" }
```

**200:** `{ "message": "User created successfully", "user_id": "<uuid>" }`

**409:** `{ "detail": "Email already registered" }`

Password is stored as a bcrypt hash on the server, not plaintext.

---

## `POST /user/login`

**Body (JSON):**

```json
{ "email": "user@example.com", "password": "..." }
```

**200:** `{ "message": "Login successful", "user_id": "<uuid>" }`

**401:** `{ "detail": "Invalid credentials" }` (wrong email or password)

Use the returned `user_id` in `POST /chat` and `POST /chat/stream` when the user is logged in.

---

## `POST /chat/load-conversation`

**Body (JSON):**

```json
{ "conversation_id": "<uuid>" }
```

**200:**

```json
{
  "conversation_id": "<uuid>",
  "messages": [
    { "role": "user", "content": "...", "created_at": "..." },
    { "role": "assistant", "content": "...", "created_at": "..." }
  ]
}
```

---

## `POST /chat`

**Body (JSON):**

```json
{
  "message": "required",
  "conversation_id": "<uuid optional — same id per thread>",
  "user_id": "<uuid optional — only if user exists in DB>"
}
```

**200:** `{ "reply": "..." }`

---

## `POST /chat/stream`

Same body as `POST /chat`.

**Response:** `text/event-stream` (SSE). Lines look like: `data: <text>\n\n`

If the guard rejects the topic, you still get SSE (often one short event).

---

## Notes

- Send UUIDs as strings in JSON.
- After signup or login, keep `user_id` on the client and pass it on chat requests.
- Reuse one `conversation_id` for all messages in the same chat.
- Chat works without `user_id` (anonymous); add it once the user has signed up.
