from gevent import monkey

monkey.patch_all()

from core.app import create_app

app = create_app()
