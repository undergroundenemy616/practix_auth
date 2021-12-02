import json
from http import HTTPStatus

from db.pg_db import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.accounts import User
from models.rbac import Role
from schemas.rbac import (RoleAssignSchema, RoleCreateSchema, RoleSchema,
                          RoleUpdateSchema)
from utils import check_role
from werkzeug.exceptions import abort

rbac = Blueprint('rbac', __name__)


@rbac.cli.command("add_base_data")
def add_base_data():
    with open('db/fixtures/roles.json') as json_roles:
        roles_data = json.load(json_roles)
        for role in roles_data:
            if Role.query.filter_by(name=role['name']).first():
                continue
            role_obj = Role(**role)
            db.session.add(role_obj)
        db.session.commit()


@rbac.route('/check', methods=['GET'])
@jwt_required()
def role_check():
    """check
    ---
    get:
      description: check permission
      summary: check permission

    responses:
      200:
        description: Access granted
        schema:
         $ref: "#/definitions/ApiResponse"
      400:
        description: required_permission disabled
        schema:
         $ref: "#/definitions/ApiResponse"
      403:
        description: Access denied
        schema:
         $ref: "#/definitions/ApiResponse"
    tags:
      - permission
    definitions:
      ApiResponse:
        type: "object"
        properties:
          message:
            type: "string"
          status:
            type: "string"
    """

    required_role = request.args.get('required_role')
    if not required_role:
        return (
            jsonify(
                {"type": "error", "message": "required_role отсутствует в параметрах"}
            ),
            HTTPStatus.BAD_REQUEST,
        )
    login = get_jwt_identity()
    if not User.check_role(login=login, required_role=required_role):
        abort(HTTPStatus.FORBIDDEN)
    return jsonify({"status": "success", "message": "Доступ разрешен"}), HTTPStatus.OK


@rbac.route('/roles/<uuid:id>/assign', methods=['PUT'])
@jwt_required()
@check_role(required_role='admin')
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
       schema:
        $ref: "#/definitions/ApiResponse"
      404:
       description: Role not found
       schema:
        $ref: "#/definitions/ApiResponse"
      400:
       description: Permission disabled
       schema:
        $ref: "#/definitions/ApiResponse"
    tags:
      - role
      - permission
    definitions:
      ApiResponse:
        type: "object"
        properties:
          message:
            type: "string"
          status:
            type: "string"
    """

    role = Role.query.filter_by(id=id).first()
    if not role:
        return (
            jsonify(
                {
                    'status': "error",
                    'message': f'объект Role с id={id} не найден',
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    if request.method == 'PUT':
        assign_users = RoleAssignSchema().load(request.get_json())
        User.query.filter(User.id.in_([assign_users.pop('users')])).update(
            {'role_id': role.id}, synchronize_session=False
        )
        db.session.commit()

        return (
            jsonify({"status": "success", "message": "Роли обновлены"}),
            HTTPStatus.OK,
        )


@rbac.route('/roles', methods=['GET', 'POST'])
@jwt_required()
@check_role(required_role='admin')
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
        schema:
          $ref: "#/definitions/DefinitionResponse"
      201:
        description: Created
        schema:
          $ref: "#/definitions/DefinitionResponse"
      400:
        description: Permission disabled
        schema:
          $ref: "#/definitions/ApiResponse"
    tags:
      - role
      - permission
    definitions:
      ApiResponse:
        type: "object"
        properties:
          message:
            type: "string"
          status:
            type: "string"
      DefinitionResponse:
        type: "object"
        properties:
          status:
            type: "string"
          message:
            type: "string"
          data:
            type: "object"
            properties:
             id:
               type: "string"
             name:
               type: "string"


    """

    if request.method == 'POST':

        role = RoleCreateSchema().load(request.get_json())
        db.session.add(role)
        db.session.commit()
        return (
            jsonify(
                {
                    'status': 'success',
                    'message': 'Роль успешно создана',
                    'data': RoleSchema().dump(role),
                }
            ),
            HTTPStatus.CREATED,
        )
    else:
        paginated_roles = Role.query.paginate(
            page=request.args.get('page'), per_page=request.args.get('count')
        )
        return (
            jsonify(
                {
                    'status': 'success',
                    'message': 'Все роли',
                    'data': RoleSchema().dump(paginated_roles.items, many=True),
                }
            ),
            HTTPStatus.OK,
        )


@rbac.route('/roles/<uuid:id>', methods=['PUT', 'DELETE', 'GET'])
@jwt_required()
@check_role(required_role='admin')
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
       schema:
          $ref: "#/definitions/ApiResponse"
      204:
       description: Already deleted
       schema:
          $ref: "#/definitions/ApiResponse"

      404:
       description: Role not found
       schema:
          $ref: "#/definitions/ApiResponse"
    tags:
      - role
      - permission
    definitions:
      ApiResponse:
        type: "object"
        properties:
          message:
            type: "string"
          status:
            type: "string"

    """

    role = Role.query.filter_by(id=id).first()
    if not role:
        return (
            jsonify(
                {
                    'status': 'error',
                    'message': f'объект Role с id={id} не найден',
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    if request.method == 'PUT':
        data = request.get_json()
        data['id'] = id
        role = RoleUpdateSchema().load(data)
        db.session.add(role)
        db.session.commit()
        return (
            jsonify(
                {
                    'status': 'success',
                    'message': 'Роль успешно обновлена',
                    'data': RoleSchema().dump(role),
                }
            ),
            HTTPStatus.OK,
        )
    elif request.method == 'DELETE':
        db.session.delete(role)
        db.session.commit()
        return (
            jsonify({"status": "success", "message": f"объект Role с id={id} удален"}),
            HTTPStatus.NO_CONTENT,
        )
    else:
        return (
            jsonify(
                {
                    'status': 'success',
                    'message': f"Объект Role с id={id}",
                    'data': RoleSchema().dump(role),
                }
            ),
            HTTPStatus.OK,
        )
