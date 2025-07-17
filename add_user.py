# add_user.py
from database import SessionLocal
from models import User
import bcrypt

# パスワードのハッシュ化
raw_password = "secret"
hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

# DBセッション
db = SessionLocal()

# ユーザー追加
user = User(username="admin", password=hashed_password.decode('utf-8'))
db.add(user)
db.commit()

print("User 'admin' created.")
