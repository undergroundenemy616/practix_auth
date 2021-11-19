import functools
import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from db.pg_db import db
from models import Permission, Role, User
from schemas import (PermissionSchema, RoleCreateSchema, RoleSchema,
                     RoleUpdateSchema, RoleAssignSchema)
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils import check_permission

rbac = Blueprint('rbac', __name__)


@rbac.cli.command("add_base_data")
def add_base_data():
    with open('db/fixtures/roles.json') as json_roles, open('db/fixtures/permissions.json') as json_permissions:
        roles_data = json.load(json_roles)
        permissions_data = json.load(json_permissions)
        for permission in permissions_data:
            if Permission.query.filter_by(name=permission['name']).first():
                continue
            db.session.add(Permission(name=permission['name']))
        db.session.commit()
        for role in roles_data:
            if Role.query.filter_by(name=role['name']).first():
                continue
            role_permissions = role.pop('permissions', None)
            role_obj = Role(**role)
            if role_permissions:
                role_permissions = [Permission.query.filter_by(name=permission).first() for permission in role_permissions]
            role_obj.permissions.extend(role_permissions)
            db.session.add(role_obj)
        db.session.commit()


@rbac.route('/check', methods=['GET'])
@jwt_required()
def permission_check():
    """check
        ---
        get:
          description: check permission
          summary: check permission

        responses:
          200:
            description: Access granted
          400:
            description: required_permission disabled
          403:
            description: Access denied
        tags:
          - permission
        """

    required_permission = request.args.get('required_permission')
    if not required_permission:
        return jsonify({"type": "error", "message": "required_permission отсутствует в параметрах"}), 400
    login = get_jwt_identity()
    if not User.check_permission(login=login, required_permission=required_permission):
        return jsonify({"status": "error", "message": "Доступ запрещен"}), 403
    return jsonify({"status": "success", "message": "Доступ разрешен"}), 200


@rbac.route('/roles/<uuid:id>/assign', methods=['PUT'])
@jwt_required()
@check_permission(required_permission='role')
def role_assign(id):
    """role assign
         ---
         put:
           description: check permission
           summary: check permission
           parameters:
           - name: id
             in: path
             description: id
             schema:
              type: string
         responses:
           201:
            description: Roles updated
           404:
            description: Role not found
           400:
            description: Permission disabled
         tags:
           - role
           - permission
         """

    if not Role.query.filter_by(id=id).first():
        return jsonify({
            'status': "error",
            'message': f'объект Role с id={id} не найден',
        }), 404
    if request.method == 'PUT':
        data = request.get_json()
        data['role_id'] = id
        try:
            RoleAssignSchema().load(data)
        except ValidationError as e:
            return jsonify({
                'status': 'error',
                'message': e.messages,
            }), 400
        return jsonify({"status": "success",
                        "message": "Роли обновлены"}), 200


@rbac.route('/roles', methods=['GET', 'POST'])
@jwt_required()
@check_permission(required_permission='roles')
def roles_list():
    """roles
         ---
         get:
           description: get roles
           summary: get roles
         post:
           description: get roles
           summary: get roles

         responses:
           200:
             description: Ok
           400:
             description: Permission disabled
         tags:
           - role
           - permission
         """

    if request.method == 'POST':
        try:
            role = RoleCreateSchema().load(request.get_json())
        except ValidationError as e:
            return jsonify({
                'status': 'error',
                'message': e.messages,
            }), 400
        return jsonify({
                'status': 'success',
                'message': 'Роль успешно создана',
                'data': RoleSchema().dump(role)
            }), 201
    else:
        paginated_roles = Role.get_paginated_data(page=request.args.get('page'),
                                                  count=request.args.get('count'),
                                                  schema=RoleSchema)
        return jsonify({
                'status': 'success',
                'message': 'Все роли',
                'data': paginated_roles
            }), 200


@rbac.route('/roles/<uuid:id>', methods=['PUT', 'DELETE', 'GET'])
@jwt_required()
@check_permission(required_permission='role')
def role_detail(id):
    """role
         ---
         get:
           description: get role
           summary: get role
           parameters:
             - name: id
               in: path
               description: id
               schema:
                type: string

         delete:
           description: delete role
           summary: delete role
           parameters:
             - name: id
               in: path
               description: id
               schema:
                type: string

         put:
           description: put role
           summary: put role
           parameters:
             - name: id
               in: path
               description: id
               schema:
                type: string


         responses:
           200:
            description: Ok
           204:
            description: Already deleted
           404:
            description: Role not found
         tags:
           - role
           - permission
         """

    role = Role.query.filter_by(id=id).first()
    if not role:
        return jsonify({
            'status': 'error',
            'message': f'объект Role с id={id} не найден',
        }), 404
    if request.method == 'PUT':
        data = request.get_json()
        data['id'] = id
        try:
            role = RoleUpdateSchema().load(data)
        except ValidationError as e:
            return jsonify({
                'status': 'error',
                'message': e.messages,
            }), 400
        return jsonify({
                'status': 'success',
                'message': 'Роль успешно обновлена',
                'data': RoleSchema().dump(role)
            }), 200
    elif request.method == 'DELETE':
        db.session.delete(role)
        db.session.commit()
        return jsonify({"status": "success",
                        "message": f"объект Role с id={id} удален"}), 204
    else:
        return jsonify({
            'status': 'success',
            'message': f"Объект Role с id={id}",
            'data': RoleSchema().dump(role)
        }), 200


@rbac.route('permissions', methods=['POST', 'GET'])
@jwt_required()
@check_permission(required_permission='permissions')
def permission_list():
    """permissions list
          ---
          get:
            description: get permissions
            summary: get permissions
          post:
            description: post permissions
            summary: post permissions

          responses:
            200:
              description: Ok
            201:
             description: Ok
            400:
             description: Permission disabled
          tags:
            - permission
          """

    if request.method == 'POST':
        try:
            permission = PermissionSchema().load(request.get_json())
        except ValidationError as e:
            return jsonify({
                'status': 'error',
                'message': e.messages,
            }), 400
        return jsonify({
            'status': 'success',
            'message': f"Разрешение успешно создано",
            'data': PermissionSchema().dump(permission)
        }), 201
    else:
        paginated_permissions = Permission.get_paginated_data(page=request.args.get('page'),
                                                              count=request.args.get('count'),
                                                              schema=PermissionSchema)
        return jsonify({
            'status': 'success',
            'message': 'Все разрешения',
            'data': paginated_permissions
        }), 200


@rbac.route('permissions/<uuid:id>', methods=['DELETE'])
@jwt_required()
@check_permission(required_permission='permission')
def permission_delete(id):
    """permission delete
          ---
          delete:
            description: get roles
            summary: get roles
            parameters:
             - name: id
               in: path
               description: id
               schema:
                type: string


          responses:
            204:
              description: Permission deleted
            404:
              description: Permission not fount
          tags:
            - permission
          """

    permission = Permission.query.filter_by(id=id).first()
    if not permission:
        return jsonify({
            'status': 'error',
            'message': f'объект Permission с id={id} не найден',
        }), 404
    db.session.delete(permission)
    db.session.commit()
    return jsonify({"status": "success",
                    "message": f"объект Permission с id={id} удален"}), 204
