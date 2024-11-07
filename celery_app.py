from flask import Flask, current_app
from celery import Celery, Task

class ContextTask(Task):
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return super().__call__(*args, **kwargs)


def make_celery(app: Flask) -> Celery:
    class FlaskTask(ContextTask):
        def __call__(self, *args: object, **kwargs: object) -> object:
            return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app