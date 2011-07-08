# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.roles import Usuario

class Item(DeclarativeBase):
    
    def __init__(self,**kw):
        cont_prefijo = 0
              
    __tablename__ = 'ITEM'
    
    #{ Columns    

    id_item = Column(Integer, Sequence('id_item_seq'), primary_key=True)   
    nom_item = Column(Unicode(255), nullable=False)     
    cod_item = Column(Unicode(255))          
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item'))
    
    #{ Relations
    tipoItem = relation("TipoItem", backref=backref('Item', order_by=id_item))    
     
class Estado(DeclarativeBase):

    def __init__(self, nom_estado):
        self.nom_estado = nom_estado
   
    __tablename__ = 'ESTADO'
    
    #{ Columns    

    id_estado = Column(Integer, Sequence('id_estado_seq'), primary_key=True)    
    nom_estado = Column(Unicode(255), nullable=False)
        
class TipoDatoAtributo(DeclarativeBase):

    def __init__(self, nombre):
		self.nom_tipo_dato=nombre
   
    	
    __tablename__ = 'TIPO_DATO_ATRIBUTO'
    
    #{ Columns    

    id_tipo_dato = Column(Integer, Sequence('id_tipo_dato_seq'), primary_key=True)    
    nom_tipo_dato = Column(Unicode(255), nullable=False)
       
class TipoItem(DeclarativeBase):

    __tablename__ = 'TIPO_ITEM'
    
    #{ Columns    

    id_tipo_item = Column(Integer, Sequence('id_tipo_item_seq'), primary_key=True)
    nom_tipo_item = Column(Unicode(255), nullable=False)    
    id_proyecto = Column(Integer, ForeignKey('PROYECTO.id_proyecto',onupdate="CASCADE", ondelete="CASCADE"))
    id_fase = Column(Integer, ForeignKey('FASE.id_fase',onupdate="CASCADE", ondelete="CASCADE"))
    prefijo = Column(Unicode(255))    
    cont_prefijo = Column(Integer) 

    #{ Relations

    proyecto  = relation("Proyecto", backref=backref('TipoItem', order_by=id_tipo_item))	
    fase = relation("Fase", backref=backref('TipoItem', order_by=id_tipo_item))	
   
class VersionItem(DeclarativeBase):
            
    __tablename__ = 'VERSION_ITEM'
    
    #{ Columns    

    id_version_item = Column(Integer, Sequence('id_VersionItem_seq'), primary_key=True)                                       
    ultima_version = Column(Unicode(1))
    id_item = Column(Integer, ForeignKey('ITEM.id_item'))                                                                
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado'))
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item'))
    id_usuario_modifico = Column(Integer, ForeignKey('USUARIO.id_usuario'))
    id_antecesor = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item'))
    id_fase = Column(Integer, ForeignKey('FASE.id_fase'))    
    nro_version_item = Column(Integer) 
    observaciones = Column(Unicode(255))
    fecha = Column(DateTime)    
    peso = Column(Integer)

    #{ Relations
    
    item = relation("Item", backref=backref('VersionItem', order_by=id_version_item))
    estado = relation("Estado", backref=backref('VersionItem', order_by=id_version_item))
    tipoItem = relation("TipoItem", backref=backref('VersionItem', order_by=id_version_item))
    usuarioModifico  = relation("Usuario", backref=backref('VersionItem', order_by=id_version_item))	
    antecesor = relation("VersionItem", backref=backref('Sucesor',remote_side=id_version_item))
    fase = relation("Fase", backref=backref('VersionItem'))
        
class Atributo(DeclarativeBase):

    def __init__(self, nombre, tipoDato, tipoItem):
        self.nom_atributo = nombre
        self.tipoDatoAtributo = tipoDato
        self.tipoItem = tipoItem
    
    
    __tablename__ = 'ATRIBUTO'
    
    #{ Columns    

    id_atributo = Column(Integer, Sequence('id_atributo_seq'), primary_key=True)    
    nom_atributo = Column(Unicode(255), nullable=False)    
    val_default = Column(Unicode(255), nullable=True)    
    id_tipo_dato = Column(Integer, ForeignKey('TIPO_DATO_ATRIBUTO.id_tipo_dato',onupdate="CASCADE"))
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item',onupdate="CASCADE"))

    #{ Relations	
    tipoDatoAtributo  = relation("TipoDatoAtributo", backref=backref('Atributo', order_by=id_atributo))	
    tipoItem = relation("TipoItem", backref=backref('Atributo', order_by=id_atributo))	
       
class TipoRelacion(DeclarativeBase):
    
    def __init__(self,nom_tipo_relacion):
        self.nom_tipo = nom_tipo_relacion   

    __tablename__ = 'TIPO_RELACION'
    
    #{ Columns
    
    id_tipo_relacion = Column(Integer, Sequence('id_tiporelacion_seq'), primary_key=True)
    nom_tipo = Column(Unicode(255), nullable=False)

class RelacionItem(DeclarativeBase):

    __tablename__ = 'RELACION_ITEM'
    
    #{ Columns    

    id_relacion = Column(Integer, Sequence('id_relacion_seq'), primary_key=True)    
    id_version_item = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item',onupdate="CASCADE"))
    id_tipo_relacion= Column(Integer, ForeignKey('TIPO_RELACION.id_tipo_relacion',onupdate="CASCADE"))

    #{ Relations    
    versionItem = relation("VersionItem", backref=backref('relacionItem', order_by=id_relacion))	
    tipoRelacion = relation("TipoRelacion", backref=backref('relacionItem', order_by=id_relacion))
    
class AtributoItem(DeclarativeBase):

    
    '''def __init__(self, filename, filecontent):
        self.filename = filename
        self.filecontent = filecontent'''

    __tablename__ = 'ATRIBUTO_ITEM'
    
    #{ Columns    

    id_atributo = Column(Integer, ForeignKey('ATRIBUTO.id_atributo'),primary_key=True)
    id_version_item = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item'),primary_key=True)
    val_atributo = Column(Unicode(255), nullable=True)
    id_archivo = Column(Integer, ForeignKey('ATRIBUTO_ARCHIVO.id'),nullable=True)

    
    #{ Relations

    atributo  = relation("Atributo", backref=backref('AtributoItem', order_by=id_atributo))	
    versionItem = relation("VersionItem", backref=backref('AtributoItem', order_by=id_atributo))	
    atributoArchivo = relation("AtributoArchivo", backref=backref('AtributoItem', order_by=id_atributo))	   
     
class AtributoArchivo(DeclarativeBase):    
    
    def __init__(self, filename, filecontent):
        self.filename = filename
        self.filecontent = filecontent

    __tablename__ = 'ATRIBUTO_ARCHIVO'
    
    #{ Columns    
    
    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(255), nullable=False)
    filecontent = Column(Binary)
    
