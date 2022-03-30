from datetime import datetime
from hmac import compare_digest
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()