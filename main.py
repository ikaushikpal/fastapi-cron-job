from fastapi import FastAPI, HTTPException
import mysql.connector
import psycopg2
from redis import asyncio as aioredis
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database configurations from environment variables
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "port": int(os.getenv("MYSQL_PORT")),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "user": os.getenv("POSTGRES_USER"),
    "port": int(os.getenv("POSTGRES_PORT")),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DATABASE"),
}


REDIS_CONFIG = {
    "url": os.getenv("REDIS_URL")
}

@app.get("/api/v1/ping")
async def ping():
    try:
        # Connect to MySQL
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT NOW()")  # Fetch current timestamp
        mysql_result = mysql_cursor.fetchone()
        mysql_cursor.close()
        mysql_conn.close()

        # Connect to PostgreSQL
        postgres_conn = psycopg2.connect(**POSTGRES_CONFIG)
        postgres_cursor = postgres_conn.cursor()
        postgres_cursor.execute("SELECT NOW()")
        postgres_result = postgres_cursor.fetchone()
        postgres_cursor.close()
        postgres_conn.close()

        # Connect to Redis
        redis_conn = await aioredis.from_url(REDIS_CONFIG["url"])
        redis_key = "last_ping_time"
        await redis_conn.set(redis_key, str(datetime.now(timezone.utc)))
        redis_value = await redis_conn.get(redis_key)
        await redis_conn.close()

        return {
            "mysql_timestamp": mysql_result[0],
            "postgres_timestamp": postgres_result[0],
            "redis_timestamp": redis_value.decode("utf-8"),
        }
    except Exception as e:
        raise e
        # raise HTTPException(
        #     status_code=500, detail=f"Database connection error: {str(e)}"
        # )
