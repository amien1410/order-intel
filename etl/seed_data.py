import os, random, uuid, datetime as dt
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient

load_dotenv()

# Postgres connect
pg = psycopg2.connect(
    host=os.getenv("PGHOST"), port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDB"), user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)
pg.autocommit = True

# Mongo connect
mongo = MongoClient(os.getenv("MONGO_URI"))
mdb = mongo[os.getenv("MONGO_DB")]

# Insert customers & orders
with pg.cursor() as cur:
    for i in range(50):
        cid = str(uuid.uuid4())
        cur.execute("INSERT INTO customers (id,email,full_name) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                    (cid, f"user{i}@mail.com", f"User {i}"))
        for _ in range(random.randint(1,5)):
            oid = str(uuid.uuid4())
            status = random.choice(['pending','paid','shipped','cancelled'])
            total = round(random.uniform(20,500),2)
            cur.execute("""INSERT INTO orders (id,customer_id,status,total_amount,created_at)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (oid, cid, status, total, dt.datetime.utcnow()))
            # items
            for j in range(random.randint(1,4)):
                cur.execute("""INSERT INTO order_items (order_id, sku, qty, unit_price)
                               VALUES (%s,%s,%s,%s)""",
                            (oid, f"SKU-{random.randint(1,30)}", random.randint(1,3), round(random.uniform(5,200),2)))

# Mongo events/docs
events = mdb.events
documents = mdb.documents
chunks = mdb.chunks

for i in range(200):
    oid = str(uuid.uuid4())
    events.insert_one({
        "event_type": random.choice(["order_created","order_paid","order_shipped"]),
        "order_id": oid,
        "customer_id": str(uuid.uuid4()),
        "at": dt.datetime.utcnow(),
        "payload": {"note": "synthetic"},
        "_schemaVersion": 1
    })

# Example: create one doc with 6 chunks
doc_id = "DOC-0001"
documents.insert_one({
    "doc_id": doc_id,
    "order_id": str(uuid.uuid4()),
    "type": "policy",
    "source": "local",
    "content_text": "Company shipping policy... (long text)",
    "created_at": dt.datetime.utcnow(),
    "_schemaVersion": 1
})
for i in range(6):
    chunks.insert_one({
        "doc_id": doc_id,
        "chunk_id": f"{doc_id}#{i:02d}",
        "chunk_index": i,
        "text": f"Policy section {i} ...",
        "tokens": 120,
        "meta": {"type":"policy"},
        "_schemaVersion": 1
    })

print("Seed complete")
