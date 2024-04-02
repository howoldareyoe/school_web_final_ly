from flask import Flask
from flask_cors import CORS

from News.shared_lib.config.constant import Config  # 确保从正确的位置导入 Config
# 导入蓝图
from News.app.views.news_views import news_bp
from News.app.views.search_views import search_bp
from News.app.views.stats_views import stats_bp
from News.app.views.subs_views import subs_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 从配置文件或环境变量中加载应用配置
    app.config.from_object(Config)

    # 注册蓝图
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(stats_bp, url_prefix='/api/stati')
    app.register_blueprint(subs_bp, url_prefix='/api/subs')

    return app


app = create_app()

if __name__ == '__main__':
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=8088, debug=False)
