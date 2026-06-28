# Sessions

Rotas relacionadas ao ciclo de uma sessão de pomodoro (foco).

Todas as rotas exigem autenticação via cookie httpOnly + CSRF token no header `X-CSRF-TOKEN`.

---

## POST /sessions/start

Inicia uma sessão de foco. Gera um token de sessão (diferente do token de autenticação) que deve ser enviado de volta em `/sessions/complete`.

### Request

Sem body.

### Response `201 Created`

```json
{
  "data": {
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

## POST /sessions/complete

Finaliza uma sessão de foco. Valida que o `session_token` é válido, pertence ao usuário autenticado, e que passou tempo suficiente desde o início.

### Request

```json
{
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Response `201 Created`

```json
{
  "message": "sessão registrada"
}
```

### Response `400 Bad Request`

```json
{
  "error": "session_token é obrigatório"
}
```

```json
{
  "error": "sessão expirada"
}
```

```json
{
  "error": "token inválido"
}
```

```json
{
  "error": "sessão muito curta"
}
```

### Response `403 Forbidden`

```json
{
  "error": "token não pertence a esse usuário"
}
```

---

## GET /sessions/history

Retorna o histórico de sessões do usuário agrupado por dia, em ordem decrescente (mais recente primeiro), com suporte a paginação por cursor de data.

### Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `before_cursor` | `string` (YYYY-MM-DD) | Não | Retorna dias anteriores a essa data |
| `limit` | `integer` | Não | Quantidade de dias a retornar (padrão: 7, máximo: 14) |

### Response `200 OK`

```json
{
  "data": {
    "2026-06-26": 1,
    "2026-06-21": 2,
    "2026-06-20": 1
  },
  "next_cursor": "2026-06-20"
}
```

Quando não há mais páginas, `next_cursor` é `null`.

---

## Regras de negócio

- Duração mínima de uma sessão: **25 minutos** (configurável via variável de ambiente `MIN_SESSION_MINUTES` para ambiente de desenvolvimento)
- Tempo máximo de validade do `session_token`: **30 minutos** (5 minutos de tolerância após os 25 minutos mínimos)
- O `session_token` é assinado com uma chave secreta diferente do token de autenticação, e carrega um campo `"type": "session_token"` — isso impede que ele seja usado como token de acesso em outras rotas protegidas.
- Apenas sessões de foco completas geram registro — pausas não contam.

---

## Pendências conhecidas

### Agrupamento por dia em UTC

O histórico agrupa sessões por `DATE(completed_at)`, onde `completed_at` está salvo em UTC. Isso pode causar inconsistência para usuários em fusos diferentes de UTC: uma sessão completada às 23:30 no horário local pode ser agrupada no dia seguinte.

**Soluções mapeadas:**
1. Salvar o timezone do usuário no modelo `User` e converter no `DATE()` via `AT TIME ZONE` no PostgreSQL — exige migração, mudança no frontend e backend, e lida mal com mudança de região do usuário.
2. Frontend manda o timezone do usuário via header em cada requisição — menos invasivo, mas ainda dá trabalho.

**Decisão:** deixado como pendência para após o MVP. Só afeta usuários fora do UTC.