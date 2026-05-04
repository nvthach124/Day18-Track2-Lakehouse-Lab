import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, TimestampType, StructType, StructField
from spark_session import get_spark

# Constants
LATENCY_PROFILES = {
    "claude-haiku-4-5":   (450,  150),
    "claude-sonnet-4-6":  (1100, 350),
    "claude-opus-4-7":    (2400, 700),
}
MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-7"]
MODEL_WEIGHTS = [6, 3, 1]
DUP_RATE = 0.05
DAYS_SPAN = 7
START_DATE = datetime(2026, 4, 1, tzinfo=timezone.utc)

def generate_row_udf(id_val, total_rows):
    """Generate a single row of data based on an incrementing ID."""
    # Deterministic randomness based on ID
    rng = random.Random(id_val)
    
    ts = START_DATE + timedelta(seconds=int(id_val * (DAYS_SPAN * 24 * 3600) / total_rows))
    model = rng.choices(MODELS, weights=MODEL_WEIGHTS)[0]
    pt = rng.randint(50, 4000)
    ct = rng.randint(20, 2000)
    base, jitter = LATENCY_PROFILES[model]
    latency_ms = max(50, int((base / 800.0) * ct + rng.gauss(0, jitter)))
    status = rng.choices(["ok", "rate_limited", "error"], weights=[95, 3, 2])[0]
    
    # Simple duplicate logic: reuse a previous ID occasionally
    # In distributed mode, we can't easily see previous IDs, so we use a hash-based dup
    request_id = str(uuid.UUID(int=rng.getrandbits(128)))
    if rng.random() < DUP_RATE:
        # Pick a "nearby" ID to simulate a retry
        nearby_id = max(0, id_val - rng.randint(1, 100))
        rng_dup = random.Random(nearby_id)
        request_id = str(uuid.UUID(int=rng_dup.getrandbits(128)))

    raw_json = json.dumps({
        "model": model,
        "user_id": f"u_{rng.randint(1, 5000)}",
        "usage": {"input": pt, "output": ct},
        "latency_ms": latency_ms,
        "status": status,
    })
    
    return (request_id, ts, raw_json)

def main(n_rows: int = 1_000_000, out: str = "s3a://bronze/llm_calls_raw") -> None:
    spark = get_spark("generate_data_optimized")
    
    # Schema for the UDF
    schema = StructType([
        StructField("request_id", StringType(), False),
        StructField("ts", TimestampType(), False),
        StructField("raw_json", StringType(), False),
    ])
    
    # Generate data using mapPartitions or similar for efficiency
    # We use a simple range and then map it to rows
    df = spark.range(0, n_rows, numPartitions=32).rdd.map(
        lambda r: generate_row_udf(r.id, n_rows)
    ).toDF(schema)
    
    print(f"Writing {n_rows:,} rows to {out}...")
    df.write.format("delta").mode("overwrite").save(out)
    
    n_unique = df.select("request_id").distinct().count()
    print(
        f"Wrote {n_rows:,} rows to {out}\n"
        f"  unique request_ids: {n_unique:,}  ({n_rows - n_unique:,} duplicates seeded)\n"
        f"  date span: {DAYS_SPAN} UTC days from 2026-04-01"
    )
    spark.stop()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-rows", type=int, default=1_000_000)
    parser.add_argument("--out", type=str, default="s3a://bronze/llm_calls_raw")
    args = parser.parse_args()
    main(n_rows=args.n_rows, out=args.out)
