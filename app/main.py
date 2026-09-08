from fastapi import FastAPI
import os
import asyncpg
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "secret"),
        database=os.getenv("DB_NAME", "appdb"),
        min_size=1,
        max_size=5
    )
    yield
    await app.state.db_pool.close()

app = FastAPI(title="Test Service", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
async def health():
    return Response(status_code=500)

#@app.get("/health")
#async def health():
#    async with app.state.db_pool.acquire() as conn:
#        result = await conn.fetchval("SELECT 1")
#    return {"status": "healthy", "db": "ok" if result == 1 else "error"}

@app.get("/db")
async def db_check():
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT NOW()")
        return {"time": str(rows[0]["now"])}
