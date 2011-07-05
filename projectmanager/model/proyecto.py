'''
Created on 01/05/2011

@author: diana
'''

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.entities import Estado
from projectmanager.model.roles import Rol
from projectmanager.model.roles import Usuario

ProyectoUsuario = Table('USUARIO_PROYECTO', metadata,
    Column('id_usuario', Integer, ForeignKey('USUARIO.id_usuario')),
    Column('id_proyecto',Integer, ForeignKey('PROYECTO.id_proyecto')),
) 

FaseUsuario = Table('USUARIO_FASE', metadata,
    Column('id_usuario', Integer, ForeignKey('USUARIO.id_usuario')),
    Column('id_fase',Integer, ForeignKey('FASE.id_fase')),
)  

FaseRol = Table('FASE_ROL', metadata,
    Column('id_fase', Integer, ForeignKey('FASE.id_fase')),
    Column('id_rol',Integer, ForeignKey('ROL.id_rol')),
)
   
class Proyecto(DeclarativeBase):
    
    __tablename__ = 'PROYECTO'
    
    #{ Columns
    
    id_proyecto = Column(Integer, Sequence('id_proyecto_seq'), primary_key=True)
    nom_proyecto = Column(Unicode(25), nullable=False)
    des_proyecto = Column(Unicode(200), nullable=False)
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado', onupdate="CASCADE", ondelete="CASCADE"))
    
    #{ Relations
    estadoProyecto= relation("Estado", backref=backref('proyecto',order_by=id_proyecto))
    usuarios = relation("Usuario", secondary=ProyectoUsuario, backref=backref('proyecto',order_by=id_proyecto))
    
class Fase (DeclarativeBase):

    __tablename__ = 'FASE'
    
    #{ Columns
    
    id_fase = Column(Integer, autoincrement=True, primary_key=True)
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado', onupdate="CASCADE", ondelete="CASCADE"))
    id_proyecto = Column(Integer, ForeignKey('PROYECTO.id_proyecto', onupdate="CASCADE", ondelete="CASCADE"))
    nro_fase = Column(Integer, nullable=False)
    nom_fase = Column(Unicode(25), nullable=False)
    des_fase = Column(Unicode(200), nullable=False)
   
    #{ Relations
    estadoFase = relation("Estado", backref=backref('fase', order_by=id_fase))
    proyectoFase = relation("Proyecto", backref=backref('fase', order_by=id_fase))   
    usuarios = relation("Usuario", secondary=FaseUsuario, backref=backref('fases',order_by=nom_fase))
    roles = relation("Rol", secondary=FaseRol, backref=backref('fases',order_by=nom_fase))
