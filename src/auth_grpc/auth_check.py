from concurrent import futures

import grpc
import jwt
from core.app import create_app
from db.pg_db import db
from models.accounts import User
from models.rbac import Role

import auth_pb2
import auth_pb2_grpc

app = create_app()


class CheckAuth(auth_pb2_grpc.AuthServicer):
    def CheckRole(self, request, context):

        with app.app_context():
            if not request.access_token or not request.roles:
                return auth_pb2.CheckRoleResponse(result=False, status="Error")
            decoded = jwt.decode(
                request.access_token, options={"verify_signature": False}
            )
            login = decoded.get('sub', None)
            if not login:
                return auth_pb2.CheckRoleResponse(result=False, status="Error")
            user = User.query.filter_by(login=login).first()
            role = Role.query.filter_by(id=user.role_id).first()
            if user and role and role.name in request.roles:
                return auth_pb2.CheckRoleResponse(result=True, status="Success")

            return auth_pb2.CheckRoleResponse(result=False, status="Success")

    def SetRole(self, request, context):

        with app.app_context():
            user_id = request.uuid
            role_name = request.role
            if not user_id or not role_name:
                return auth_pb2.CheckRoleResponse(result=False, status="Not found user or role")
            user = User.query.filter_by(id=user_id).first()
            role = Role.query.filter_by(name=user.role_name).first()
            user.role_id = role.id
            db.session.commit()
            if user and role and role.name in request.roles:
                return auth_pb2.CheckRoleResponse(result=True, status="Success")

            return auth_pb2.CheckRoleResponse(result=False, status="Success")


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServicer_to_server(CheckAuth(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
