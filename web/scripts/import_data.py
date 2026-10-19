import argparse
from pathlib import Path
from bson import json_util
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


def load_json(path):
    print(f"Dang doc: {path}")
    text = Path(path).read_text(encoding="utf-8")
    return json_util.loads(text)


def import_collection(db, name, path, drop=False, batch_size=2000):
    docs = load_json(path)
    col = db[name]
    if drop:
        col.drop()
    if not docs:
        print(name, "khong co du lieu")
        return
    for i in range(0, len(docs), batch_size):
        col.insert_many(docs[i:i+batch_size], ordered=False)
        print(f"{name}: {min(i+batch_size, len(docs))}/{len(docs)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nguoidung", required=True)
    parser.add_argument("--vieclam", required=True)
    parser.add_argument("--ungtuyen", required=True)
    parser.add_argument("--drop", action="store_true")
    args = parser.parse_args()

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client[os.getenv("MONGO_DB", "QL_TuyenDung")]
    import_collection(db, "QL_NguoiDung", args.nguoidung, args.drop)
    import_collection(db, "QL_ViecLam", args.vieclam, args.drop)
    import_collection(db, "QL_UngTuyen", args.ungtuyen, args.drop)
    print("Hoan tat import.")


if __name__ == "__main__":
    main()
