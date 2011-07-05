# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.entities import Item, Estado, TipoDatoAtributo
from projectmanager.model.entities import TipoItem, VersionItem, Atributo
from projectmanager.model.entities import RelacionItem, AtributoItem, AtributoArchivo
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Usuario

class LineaBase(DeclarativeBase):
    __tablename__ = 'LINEA_BASE'
    
    #{ Columns
    
    id_linea_base = Column(Integer, Sequence('id_LineaBase_seq'), primary_key=True)
    id_fase = Column(Integer, ForeignKey('FASE.id_fase',onupdate="CASCADE", ondelete="CASCADE"))
    nom_linea_base = Column(String)
    descripcion = Column(String)
    
    #}

ItemLineaBase = Table('ITEM_LINEA_BASE', metadata,
    Column('id_nro_lb', Integer, ForeignKey('NRO_LINEA_BASE.id_nro_lb')),
    Column('id_version_item', Integer, ForeignKey('VERSION_ITEM.id_version_item')),
)    

class NroLineaBase(DeclarativeBase):
    __tablename__ = 'NRO_LINEA_BASE'
    
    #{ Columns    
    id_nro_lb = Column(Integer, Sequence('id_NroLineaBase_seq'), primary_key=True)
    id_linea_base = Column(Integer, ForeignKey('LINEA_BASE.id_linea_base',onupdate="CASCADE"))
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado',onupdate="CASCADE"))
    id_usuario_aprobo = Column(Integer, ForeignKey('USUARIO.id_usuario',onupdate="CASCADE"))
    nro_linea_base = Column(Integer, nullable=False)        
    #}
    
    #{ Relations
    lineaBase = relation("LineaBase", backref=backref('NroLineaBase',order_by=id_nro_lb))
    item = relation("VersionItem", secondary=ItemLineaBase, backref=backref('NroLineaBase',order_by=id_nro_lb))
    estado = relation("Estado", backref=backref('NroLineaBase',order_by=id_estado))
