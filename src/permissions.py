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

permissions = Blueprint('permissions', __name__)


@permissions.cli.command("add_base_data")
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


@permissions.route('/check', methods=['GET'])
@jwt_required()
def permission_check():
    required_permission = request.args.get('required_permission')
    if not required_permission:
        return jsonify({"type": "error", "message": "required_permission отсутствует в параметрах"}), 400
    login = get_jwt_identity()
    if not User.check_permission(login=login, required_permission=required_permission):
        return jsonify({"type": "error", "message": "Доступ запрещен"}), 403
    return jsonify({"type": "success", "message": "Доступ разрешен"}), 200


@permissions.route('/role/<uuid:id>/assign', methods=['PUT'])
@jwt_required()
@check_permission(required_permission='role')
def role_assign(id):
    if not Role.query.filter_by(id=id).first():
        return jsonify({
            'error': f'объект Role с id={id} не найден',
        }), 404
    if request.method == 'PUT':
        data = request.get_json()
        data['role_id'] = id
        try:
            RoleAssignSchema().load(data)
        except ValidationError as e:
            return jsonify(e.messages), 400
        return jsonify({"type": "success", "message": "Роли обновлены"}), 200


@permissions.route('/roles', methods=['GET', 'POST'])
@jwt_required()
@check_permission(required_permission='roles')
def roles_list():
    if request.method == 'POST':
        try:
            role = RoleCreateSchema().load(request.get_json())
        except ValidationError as e:
            return jsonify(e.messages), 400
        return jsonify(RoleSchema().dump(role)), 200
    else:
        paginated_roles = Role.get_paginated_data(page=request.args.get('page'),
                                                  count=request.args.get('count'),
                                                  schema=RoleSchema)
        return jsonify(paginated_roles), 200


@permissions.route('/role/<uuid:id>', methods=['PUT', 'DELETE', 'GET'])
@jwt_required()
@check_permission(required_permission='role')
def role_detail(id):
    role = Role.query.filter_by(id=id).first()
    if not role:
        return jsonify({
            'error': f'объект Role с id={id} не найден',
        }), 404
    if request.method == 'PUT':
        data = request.get_json()
        data['id'] = id
        try:
            role = RoleUpdateSchema().load(data)
        except ValidationError as e:
            return jsonify(e.messages), 400
        return jsonify(RoleSchema().dump(role)), 200
    elif request.method == 'DELETE':
        db.session.delete(role)
        db.session.commit()
        return jsonify({"success": f"объект Role с id={id} удален"}), 204
    else:
        return jsonify(RoleSchema().dump(role)), 200


@permissions.route('/permissions', methods=['POST', 'GET'])
@jwt_required()
@check_permission(required_permission='permissions')
def permission_list():
    if request.method == 'POST':
        try:
            permission = PermissionSchema().load(request.get_json())
        except ValidationError as e:
            return jsonify(e.messages), 400
        return jsonify(PermissionSchema().dump(permission)), 201
    else:
        paginated_permissions = Permission.get_paginated_data(page=request.args.get('page'),
                                                              count=request.args.get('count'),
                                                              schema=PermissionSchema)
        return jsonify(paginated_permissions), 200


@permissions.route('/permission/<uuid:id>', methods=['DELETE'])
@jwt_required()
@check_permission(required_permission='permission')
def permission_delete(id):
    permission = Permission.query.filter_by(id=id).first()
    if not permission:
        return jsonify({
            'error': f'объект Permission с id={id} не найден',
        }), 404
    db.session.delete(permission)
    db.session.commit()
    return jsonify({"success": f"объект Permission с id={id} удален"}), 204
