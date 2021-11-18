from gevent import monkey
from flasgger import Swagger

monkey.patch_all()

from app import create_app

app = create_app()
swagger = Swagger(app)

