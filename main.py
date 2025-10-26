from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import asyncio
import sqlite3

app = FastAPI()

# Pydantic models
class WebhookRequest(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str

class TransactionResponse(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: str
    created_at: str
    processed_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    current_time: str

# Initialize database
def init_db():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            source_account TEXT NOT NULL,
            destination_account TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT DEFAULT 'PROCESSING',
            created_at TEXT NOT NULL,
            processed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Background task
async def process_transaction(transaction_id: str):
    await asyncio.sleep(30)  # 30-second delay
    
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET status = 'PROCESSED', processed_at = ? WHERE transaction_id = ?",
        (datetime.now(timezone.utc).isoformat(), transaction_id)
    )
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="HEALTHY",
        current_time=datetime.now(timezone.utc).isoformat()
    )

@app.post("/v1/webhooks/transactions")
async def receive_webhook(webhook_data: WebhookRequest, background_tasks: BackgroundTasks):
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    
    # Check for duplicate
    cursor.execute("SELECT id FROM transactions WHERE transaction_id = ?", (webhook_data.transaction_id,))
    if cursor.fetchone():
        conn.close()
        return {"message": "Transaction already exists"}
    
    # Insert transaction
    cursor.execute('''
        INSERT INTO transactions (transaction_id, source_account, destination_account, amount, currency, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        webhook_data.transaction_id,
        webhook_data.source_account,
        webhook_data.destination_account,
        webhook_data.amount,
        webhook_data.currency,
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()
    
    # Start background processing
    background_tasks.add_task(process_transaction, webhook_data.transaction_id)
    
    return {"message": "Webhook received"}

@app.get("/v1/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        transaction_id=row[1],
        source_account=row[2],
        destination_account=row[3],
        amount=row[4],
        currency=row[5],
        status=row[6],
        created_at=row[7],
        processed_at=row[8]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
