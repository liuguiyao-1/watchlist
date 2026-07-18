from flask import Flask, render_template

app = Flask(__name__)  # 创建 Flask 应用


@app.route("/")  # 访问首页时执行这个函数
def hello():
    name = "饼干"

    movies = [
        "千与千寻",
        "盗梦空间",
        "星际穿越"
    ]

    return render_template(
        "index.html",
        name=name,
        movies=movies
    )
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # 5001 避开 Docker 使用的 5000 端口