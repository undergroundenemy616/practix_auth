import os

import grpc

import notify_registration_pb2
import notify_registration_pb2_grpc

notify_channel = grpc.insecure_channel(
    f"{os.getenv('NOTIFY_GRPC_HOST')}:{os.getenv('NOTIFY_GRPC_PORT')}"
)
notify_client = notify_registration_pb2_grpc.NotifyRegisterStub(notify_channel)


def send_register_notification(email: str, login: str, password: str):
    notification_request = notify_registration_pb2.UserRegisteredRequest(
        email=email, login=login, password=password
    )
    auth_response = notify_client.UserRegisterEvent(
        notification_request
    )
    return auth_response.result
