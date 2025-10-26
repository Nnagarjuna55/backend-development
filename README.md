# Transaction Webhook Service

A FastAPI-based service for processing transaction webhooks with background processing and idempotency.

## Features

- ✅ **Webhook Endpoint**: `POST /v1/webhooks/transactions`
- ✅ **Health Check**: `GET /`
- ✅ **Transaction Query**: `GET /v1/transactions/{transaction_id}`
- ✅ **Fast Response**: Returns 202 status within 500ms
- ✅ **Background Processing**: 30-second delay simulation
- ✅ **Idempotency**: Prevents duplicate transaction processing
- ✅ **Data Storage**: SQLite database for persistence

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /
```
Response:
```json
{
  "status": "HEALTHY",
  "current_time": "2024-01-15T10:30:00Z"
}
```

### Webhook Endpoint
```http
POST /v1/webhooks/transactions
Content-Type: application/json

{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
```

### Transaction Query
```http
GET /v1/transactions/{transaction_id}
```
Response:
```json
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 150.50,
  "currency": "USD",
  "status": "PROCESSED",
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:30:30Z"
}
```

## Testing

### Test Single Transaction
```bash
curl -X POST "http://localhost:8000/v1/webhooks/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_test_123",
    "source_account": "acc_user_123",
    "destination_account": "acc_merchant_456",
    "amount": 100.50,
    "currency": "USD"
  }'
```

### Check Transaction Status
```bash
curl "http://localhost:8000/v1/transactions/txn_test_123"
```

### Test Duplicate Prevention
```bash
# Send the same webhook multiple times
curl -X POST "http://localhost:8000/v1/webhooks/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_duplicate_test",
    "source_account": "acc_user_123",
    "destination_account": "acc_merchant_456",
    "amount": 200.00,
    "currency": "USD"
  }'
```

## Technical Details

- **Framework**: FastAPI
- **Database**: SQLite (file-based)
- **Background Processing**: FastAPI BackgroundTasks
- **Data Validation**: Pydantic models
- **Server**: Uvicorn ASGI server

## Success Criteria

1. **Single Transaction**: Send webhook → verify processed after ~30 seconds
2. **Duplicate Prevention**: Send same webhook multiple times → verify only one processed
3. **Performance**: Webhook responds quickly even under processing load
4. **Reliability**: Service handles errors gracefully without losing transactions
