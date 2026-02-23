import os
import re
import subprocess
import sys
from pathlib import Path

def get_next_revision_id():
    # Đường dẫn thư mục versions
    versions_path = Path("migrations/versions")
    
    if not versions_path.exists():
        versions_path.mkdir(parents=True, exist_ok=True)
        return "001"
    
    # Lấy danh sách các file .py
    files = [f for f in os.listdir(versions_path) if f.endswith(".py")]
    
    if not files:
        return "001"
    
    # Tìm số thứ tự lớn nhất
    pattern = re.compile(r"^(\d{3})_")
    max_id = 0
    found_any = False
    
    for f in files:
        match = pattern.match(f)
        if match:
            found_any = True
            max_id = max(max_id, int(match.group(1)))
    
    if not found_any:
        return "001"
        
    return f"{(max_id + 1):03d}"

def run_alembic_revision():
    next_id = get_next_revision_id()
    msg = sys.argv[1] if len(sys.argv) > 1 else "migration"
    
    command = [
        "venv/bin/alembic", "revision", "--autogenerate",
        "--rev-id", next_id,
        "-m", msg
    ]
    
    print(f"🚀 [LOCAL] Đang tạo migration {next_id}...")
    try:
        subprocess.run(command, check=True)
        print(f"✅ Đã tạo file: {next_id}_{msg}.py")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi: Có thể Postgres chưa chạy hoặc chưa tạo Database 'crypto_db'.")
        sys.exit(1)

if __name__ == "__main__":
    run_alembic_revision()
