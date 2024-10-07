from flask_redis import FlaskRedis

def init_redis(app):
    app.config['REDIS_URL'] = 'redis://localhost:6379'
    return FlaskRedis(app)