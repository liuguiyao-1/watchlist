from flask import Flask

app = Flask(__name__)  # 创建 Flask 应用


@app.route("/")  # 访问首页时执行这个函数
def hello():
    return "Welcome to My Watchlist!"


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # 5001 避开 Docker 使用的 5000 端口