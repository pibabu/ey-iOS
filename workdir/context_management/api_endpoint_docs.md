# API Documentation

**Call Dockerhost Fastapi Endpoint:**
```bash
export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

curl -s -X POST "${API_BASE}/api/conversation/export" \
  -H "Content-Type: application/json" \
  -d "{\"user_hash\": \"$USER_HASH\"}"
```


## LLM Router (`/api/llm`)

### POST `/api/llm/quick`
One-time isolated LLM execution with bash tool support.

**Request Body:**
```json
{
  "prompt": "string (required)",
  "system_prompt": "string (optional)",
  "user_hash": "string (optional)"
}
```

**Response:**
```json
{
  "result": "string",
  "tool_calls": [{"command": "string", "output": "string", "timestamp": "number"}],
  "container": "string",
  "timestamp": "number"
}
```

**Notes:**
- Stateless execution
- Max 5 recursive tool calls
---

## Conversation Router (`/api/conversation`)

### POST `/api/conversation/edit`
Modify conversation history.

**Request Body:**
```json
{
  "user_hash": "string (required)",
  "action": "clear | replace_last | inject | remove_last (required)",
  "count": "integer (1-20, optional, default: 1)",
  "new_messages": [
    {
      "role": "user | assistant | tool",
      "content": "string"
    }
  ]
}
```

**Actions:**
- `clear`: Wipe all messages
- `replace_last`: Replace last N messages with new ones (requires `new_messages`)
- `inject`: Append new messages (requires `new_messages`)
- `remove_last`: Delete last N messages

**Response:**
```json
{
  "status": "success",
  "action": "string",
  "removed": "integer (optional)",
  "added": "integer (optional)",
  "total": "integer"
}
```

### POST `/api/conversation/export`
Export full conversation data.

**Request Body:**
```json
{
  "user_hash": "string (required)"
}
```

**Response:**
Full conversation data structure.

---
