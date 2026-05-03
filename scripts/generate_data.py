"""Generate 1M synthetic LLM-observability records and write to MinIO `bronze`.

Schema mirrors slide §6 medallion example: raw LLM API call logs.
"""
import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

# Make this script runnable both as `python /workspace/scripts/generate_data.py`
# and via `python -m scripts.generate_data` from /workspace.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyspark.sql import Row

from spark_session import get_spark


def _row(start: datetime, i: int) -> Row:
    ts = start + timedelta(seconds=i // 10)
    model = random.choices(
        ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-7"],
        weights=[6, 3, 1],
    )[0]
    prompt_tokens = random.randint(50, 4000)
    completion_tokens = random.randint(20, 2000)
    # Simulate latency proportional to completion_tokens + noise
    latency_ms = int(completion_tokens * random.uniform(8, 25) + random.gauss(200, 50))
    status = random.choices(["ok", "rate_limited", "error"], weights=[95, 3, 2])[0]
    return Row(
        request_id=str(uuid.uuid4()),
        ts=ts,
        raw_json=json.dumps(
            {
                "model": model,
                "user_id": f"u_{random.randint(1, 5000)}",
                "usage": {"input": prompt_tokens, "output": completion_tokens},
                "latency_ms": latency_ms,
                "status": status,
            }
        ),
    )


def main(n_rows: int = 1_000_000, out: str = "s3a://bronze/llm_calls_raw") -> None:
    spark = get_spark("generate_data")
    start = datetime(2026, 4, 1, tzinfo=timezone.utc)
    rdd = spark.sparkContext.parallelize(range(n_rows), numSlices=16).map(
        lambda i: _row(start, i)
    )
    df = spark.createDataFrame(rdd)
    df.write.format("delta").mode("overwrite").save(out)
    print(f"Wrote {n_rows:,} rows to {out}")
    spark.stop()


if __name__ == "__main__":
    main()
