import os
import sys
from pathlib import Path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from flask import request, url_for, redirect, flash

# 兼容 Windows / Mac/Linux 的 SQLite 路径前缀
SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'

app = Flask(__name__)  # 创建 Flask 应用
app.config['SECRET_KEY'] = 'dev'

# 配置数据库地址：在项目根目录生成 data.db 文件
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_PREFIX + str(Path(app.root_path) / 'data.db')

# 模型基类（固定写法，所有数据表类都继承它）
class Base(DeclarativeBase):
    pass

# 初始化数据库扩展，把 Flask 应用和数据库绑定
db = SQLAlchemy(app, model_class=Base)

# 用户表：保存用户名
class User(db.Model):
    __tablename__ = 'user'       # 数据库里的表名
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键，自动编号
    name: Mapped[str] = mapped_column(String(20))      # 姓名字段，最长20字符

# 电影表：保存电影名称和年份
class Movie(db.Model):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))     # 电影标题
    year: Mapped[str] = mapped_column(String(4))       # 上映年份

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否是表单提交
        # 获取表单里输入的内容
        title = request.form.get('title').strip()
        year = request.form.get('year').strip()

        # 后端验证输入是否合法
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回首页

        # 保存到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')  # 显示成功提示
        return redirect(url_for('index'))  # 重定向回首页

    # GET 请求：正常渲染电影列表
    movies = db.session.execute(select(Movie)).scalars().all()
    return render_template('index.html', movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    if request.method == 'POST':
        title = request.form.get('title').strip()
        year = request.form.get('year').strip()

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.context_processor
def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # 5001 避开 Docker 使用的 5000 端口
import click

@app.cli.command()
def forge():
    """生成测试数据"""
    db.drop_all()
    db.create_all()

    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')