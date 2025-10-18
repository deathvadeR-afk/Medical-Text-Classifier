import os
import logging
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@" \
         f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def ingest_csv(csv_path):
    df = pd.read_csv(csv_path)
    logging.info(f"Loaded {len(df)} rows from {csv_path}")

    # Map column names if needed (ensure columns match your schema)
    expected = {"question", "answer", "source", "focusarea"}
    if not expected.issubset(set(df.columns)):
        raise ValueError(f"CSV must have columns: {expected}")

    # Insert rows with transaction safety
    session = SessionLocal()
    try:
        df["focusgroup"] = df["focusarea"].apply(lambda x: x.split()[0] if isinstance(x, str) else None)
        for _, row in df.iterrows():
            sql = """
            INSERT INTO medical_texts (question, answer, source, focusarea, focusgroup)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """
            session.execute(sql, (
                row["question"], row["answer"], row["source"], row["focusarea"], row["focusgroup"]
            ))
        session.commit()
        logging.info("All rows committed.")
    except Exception as e:
        session.rollback()
        logging.error("Error during ingest, rollback. Details: %s", e)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), '../data/medical_texts.csv')
    ingest_csv(csv_path)
