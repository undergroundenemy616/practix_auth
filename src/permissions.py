from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from db.pg_db import db
from models import Permission, Role
from schemas import (PermissionSchema, RoleCreateSchema, RoleSchema,
                     RoleUpdateSchema)

permissions = Blueprint('permissions', __name__)


@permissions.route('/roles', methods=['GET', 'POST'])
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
def permission_delete(id):
    permission = Permission.query.filter_by(id=id).first()
    if not permission:
        return jsonify({
            'error': f'объект Permission с id={id} не найден',
        }), 404
    db.session.delete(permission)
    db.session.commit()
    return jsonify({"success": f"объект Permission с id={id} удален"}), 204
