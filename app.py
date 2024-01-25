from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
redis_client = redis.Redis(host='my-redis', port=6379, db=0, password='123456')

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# 创建数据库表格
with app.app_context():
    db.create_all()

# 注册路由
@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']

        # 检查 Redis 缓存中是否存在用户信息
        cached_username = redis_client.get(user_id)

        if cached_username:
            return f"Hello, {cached_username.decode()} (from cache)"
        else:
            # 如果缓存不存在，从数据库中获取用户信息
            user = User.query.get(user_id)

            if user:
                # 将用户信息存储到 Redis 缓存中，设置过期时间为 1 小时
                redis_client.setex(user_id, 3600, user.username)

                return f"Hello, {user.username} (from database)"
            else:
                return "User not found"
    return "Welcome to the user management system!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # 检查邮箱是否已经存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already exists"

        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()

        # 将用户信息存储到 Redis 缓存中，设置过期时间为 1 小时
        redis_client.setex(new_user.id, 3600, new_user.username)

        return redirect('/')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id

            # 将用户信息存储到 Redis 缓存中，设置过期时间为 1 小时
            redis_client.setex(user.id, 3600, user.username)

            return redirect('/')
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)

    # 从 Redis 缓存中删除用户信息
    redis_client.delete(user_id)

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # 在Flask应用程序中，确保将app.run()方法更改为app.run(host='0.0.0.0')，以便Flask应用程序可以在Docker容器外部访问。

