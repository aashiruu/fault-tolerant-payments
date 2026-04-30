from services.shared.database import init_db
import sys
import os

sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("🚀 Initializing Postgres Tables...")
    init_db()
    print("✅ Done.")
