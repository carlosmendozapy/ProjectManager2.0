# -*- coding: utf-8 -*-
"""Sample model module."""
import os
from datetime import datetime
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')
             
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, synonym
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import backref

from projectmanager.model import DeclarativeBase, metadata, DBSession


UsuarioRolSistema = Table('USUARIO_ROL_SISTEMA', metadata,
    Column('id_usuario', Integer, ForeignKey('USUARIO.id_usuario')),
    Column('id_rol',Integer, ForeignKey('ROL.id_rol')),
)       

RolPermisos = Table('ROL_PERMISOS', metadata,
    Column('id_rol', Integer, ForeignKey('ROL.id_rol')),
    Column('id_permiso', Integer, ForeignKey('PERMISOS.id_permiso')),
)

PrivilegiosPermisos = Table('PRIVILEGIOS_PERMISOS', metadata,
    Column('id_privilegio', Integer, ForeignKey('PRIVILEGIOS.id_privilegio')),
    Column('id_permiso', Integer, ForeignKey('PERMISOS.id_permiso')),
)

UsuarioRol = Table('USUARIO_ROL', metadata,
    Column('id_usuario', Integer, ForeignKey('USUARIO.id_usuario')),
    Column('id_rol', Integer, ForeignKey('ROL.id_rol')),
)
   
class RolFaseUsuario(DeclarativeBase):

    __tablename__ = 'ROL_FASE_USUARIO'
    
    #{ Columns
    id_rolfaseusuario = Column(Integer, autoincrement=True, primary_key=True)
    id_fase = Column(Integer, ForeignKey('FASE.id_fase',
        onupdate="CASCADE"))
    id_rol = Column(Integer, ForeignKey('ROL.id_rol',
        onupdate="CASCADE"))
    id_usuario = Column(Integer, ForeignKey('USUARIO.id_usuario',
        onupdate="CASCADE"))
    
    #{ Relations
    fase = relation("Fase",backref="RolFaseUsuario")
    usuarios = relation("Usuario", backref="RolFaseUsuario")
    roles = relation("Rol", backref="RolFaseUsuario")    
    
class RolProyectoUsuario(DeclarativeBase):
    
    __tablename__ = 'ROL_PROYECTO_USUARIO'
    
    #{ Columns
    
    
    id_rol_proyecto_usuario = Column(Integer, autoincrement=True, primary_key=True)    
    id_rol_proyecto = Column(Integer, ForeignKey('ROL.id_rol',
        onupdate="CASCADE"))    
    id_proyecto_ = Column(Integer, ForeignKey('PROYECTO.id_proyecto',
        onupdate="CASCADE"))    
    id_usuario_proyecto = Column(Integer, ForeignKey('USUARIO.id_usuario',
        onupdate="CASCADE"))
    
    #{ Relations
    usuarios = relation("Usuario", backref="RolProyectoUsuario")
    roles = relation("Rol", backref="RolProyectoUsuario")
    proyecto = relation("Proyecto", backref="RolProyectoUsuario")

class Usuario(DeclarativeBase):
    
    __tablename__ = 'USUARIO'


    #{ Columns
    
    id_usuario = Column(Integer, autoincrement=True, primary_key=True)
    nom_usuario = Column(Unicode(25), nullable=False)
    login_name = Column(Unicode(25), nullable=False)
    _password = Column('password',Unicode(80), info={'rum': {'field':'Password'}})
    
    
    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        hashed_password = password
        
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hashed password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # columns
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))
    
    #}
    
    def validate_password(self, password):
        """
        Check the password against existing credentials.
        
        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()
     
class Rol(DeclarativeBase):
    
    __tablename__ = 'ROL'

    #{ Columns
    id_rol = Column(Integer, autoincrement=True, primary_key=True)
    id_tipo_rol = Column(Integer, ForeignKey('TIPO_ROL.id_tipo',
        onupdate="CASCADE", ondelete="CASCADE"))
    nom_rol = Column(Unicode(20))
    des_rol = Column(Unicode(200))    
        
    #{ Relations    
    tipoRol = relation("TipoRol", backref=backref('rol', order_by=nom_rol))
    permisos = relation("Permisos", secondary=RolPermisos, backref=backref('rol',order_by=nom_rol))
    usuarios = relation("Usuario", secondary=UsuarioRol, backref=backref('roles',order_by=nom_rol))
        
class TipoRol(DeclarativeBase):
   
    __tablename__ = 'TIPO_ROL'
    
    #{ Columns    
    id_tipo = Column(Integer, autoincrement=True, primary_key=True)
    nom_tipo_rol = Column(Unicode(20))

    #}
    
class Permisos(DeclarativeBase):  
    
    __tablename__ = 'PERMISOS'
    
    #{ Columns    
    id_permiso = Column(Integer, autoincrement=True, primary_key=True)
    id_entidad_sistema = Column(Integer, ForeignKey('ENTIDAD_SISTEMA.id_entidad',
        onupdate="CASCADE", ondelete="CASCADE"))
    
    #{ Relations
    privilegios = relation("Privilegios", secondary=PrivilegiosPermisos, backref=backref('permiso', order_by=id_permiso))
    entidad = relation("EntidadSistema", backref=backref('permisos', order_by=id_permiso))
    
class Privilegios(DeclarativeBase):
    
    def __init__(self, nombre,descripcion):
        self.nom_privilegio=nombre
        self.des_privilegio=descripcion
    
    __tablename__ = 'PRIVILEGIOS'

    #{ Columns

    id_privilegio = Column(Integer,autoincrement=True, primary_key=True)
    nom_privilegio = Column(Unicode(20))
    des_privilegio = Column(Unicode(200))    
    
    #}
   
class EntidadSistema(DeclarativeBase):

    __tablename__ = 'ENTIDAD_SISTEMA'

    #{ Columns
    
    id_entidad = Column(Integer,autoincrement=True, primary_key=True)
    nom_entidad = Column(Unicode(20))
    des_entidad = Column(Unicode(200))    
    
    #}
    

