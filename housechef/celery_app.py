from housechef.app import init_celery

app = init_celery()
# app.config
print(f'Current database URL: {app.conf.get("SQLALCHEMY_DATABASE_URI")}')
app.conf.imports = app.conf.imports + ("housechef.tasks",)
