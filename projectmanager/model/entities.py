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
   
    def get_tablename__(self):
        return self.__tablename__


    def get_id_item(self):
        return self.__id_item


    def get_nom_item(self):
        return self.__nom_item


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_item(self, value):
        self.__id_item = value


    def set_nom_item(self, value):
        self.__nom_item = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_item(self):
        del self.__id_item


    def del_nom_item(self):
        del self.__nom_item
        
    __tablename__ = 'ITEM'
    
    #{ Columns    

    id_item = Column(Integer, Sequence('id_item_seq'), primary_key=True)   
    nom_item = Column(Unicode(255), nullable=False)     
    cod_item = Column(Unicode(255))     
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item'))
    
    #{ Relations
    tipoItem = relation("TipoItem", backref=backref('Item', order_by=id_item))    
     
class Estado(DeclarativeBase):

    def get_tablename__(self):
        return self.__tablename__


    def get_id_estado(self):
        return self.__id_estado


    def get_nom_estado(self):
        return self.__nom_estado


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_estado(self, value):
        self.__id_estado = value


    def set_nom_estado(self, value):
        self.__nom_estado = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_estado(self):
        del self.__id_estado


    def del_nom_estado(self):
        del self.__nom_estado


    def __init__(self, nom_estado):
        self.nom_estado = nom_estado
   
    __tablename__ = 'ESTADO'
    
    #{ Columns    

    id_estado = Column(Integer, Sequence('id_estado_seq'), primary_key=True)    
    nom_estado = Column(Unicode(255), nullable=False)
        
class TipoDatoAtributo(DeclarativeBase):

    def __init__(self, nombre):
		self.nom_tipo_dato=nombre
   
    def get_tablename__(self):
        return self.__tablename__


    def get_id_tipo_dato(self):
        return self.__id_tipo_dato


    def get_nom_tipo_dato(self):
        return self.__nom_tipo_dato


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_tipo_dato(self, value):
        self.__id_tipo_dato = value


    def set_nom_tipo_dato(self, value):
        self.__nom_tipo_dato = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_tipo_dato(self):
        del self.__id_tipo_dato


    def del_nom_tipo_dato(self):
        del self.__nom_tipo_dato
	
    __tablename__ = 'TIPO_DATO_ATRIBUTO'
    
    #{ Columns    

    id_tipo_dato = Column(Integer, Sequence('id_tipo_dato_seq'), primary_key=True)    
    nom_tipo_dato = Column(Unicode(255), nullable=False)
       
class TipoItem(DeclarativeBase):

    def get_tablename__(self):
        return self.__tablename__


    def get_id_tipo_item(self):
        return self.__id_tipo_item


    def get_nom_tipo_item(self):
        return self.__nom_tipo_item


    def get_id_proyecto(self):
        return self.__id_proyecto


    def get_id_fase(self):
        return self.__id_fase


    def get_proyecto(self):
        return self.__proyecto


    def get_fase(self):
        return self.__fase


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_tipo_item(self, value):
        self.__id_tipo_item = value


    def set_nom_tipo_item(self, value):
        self.__nom_tipo_item = value


    def set_id_proyecto(self, value):
        self.__id_proyecto = value


    def set_id_fase(self, value):
        self.__id_fase = value


    def set_proyecto(self, value):
        self.__proyecto = value


    def set_fase(self, value):
        self.__fase = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_tipo_item(self):
        del self.__id_tipo_item


    def del_nom_tipo_item(self):
        del self.__nom_tipo_item


    def del_id_proyecto(self):
        del self.__id_proyecto


    def del_id_fase(self):
        del self.__id_fase


    def del_proyecto(self):
        del self.__proyecto


    def del_fase(self):
        del self.__fase


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
    
    def get_tablename__(self):
        return self.__tablename__


    def get_id_version_item(self):
        return self.__id_version_item


    def get_nro_version_item(self):
        return self.__nro_version_item


    def get_id_item(self):
        return self.__id_item


    def get_id_estado(self):
        return self.__id_estado


    def get_id_tipo_item(self):
        return self.__id_tipo_item


    def get_observaciones(self):
        return self.__observaciones


    def get_fecha(self):
        return self.__fecha


    def get_id_usuario_modifico(self):
        return self.__id_usuario_modifico


    def get_peso(self):
        return self.__peso


    def get_item(self):
        return self.__item


    def get_estado(self):
        return self.__estado


    def get_tipo_item(self):
        return self.__tipoItem


    def get_usuario_modifico(self):
        return self.__usuarioModifico


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_version_item(self, value):
        self.__id_version_item = value


    def set_nro_version_item(self, value):
        self.__nro_version_item = value


    def set_id_item(self, value):
        self.__id_item = value


    def set_id_estado(self, value):
        self.__id_estado = value


    def set_id_tipo_item(self, value):
        self.__id_tipo_item = value


    def set_observaciones(self, value):
        self.__observaciones = value


    def set_fecha(self, value):
        self.__fecha = value


    def set_id_usuario_modifico(self, value):
        self.__id_usuario_modifico = value


    def set_peso(self, value):
        self.__peso = value


    def set_item(self, value):
        self.__item = value


    def set_estado(self, value):
        self.__estado = value


    def set_tipo_item(self, value):
        self.__tipoItem = value


    def set_usuario_modifico(self, value):
        self.__usuarioModifico = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_version_item(self):
        del self.__id_version_item


    def del_nro_version_item(self):
        del self.__nro_version_item


    def del_id_item(self):
        del self.__id_item


    def del_id_estado(self):
        del self.__id_estado


    def del_id_tipo_item(self):
        del self.__id_tipo_item


    def del_observaciones(self):
        del self.__observaciones


    def del_fecha(self):
        del self.__fecha


    def del_id_usuario_modifico(self):
        del self.__id_usuario_modifico


    def del_peso(self):
        del self.__peso


    def del_item(self):
        del self.__item


    def del_estado(self):
        del self.__estado


    def del_tipo_item(self):
        del self.__tipoItem


    def del_usuario_modifico(self):
        del self.__usuarioModifico
    
    __tablename__ = 'VERSION_ITEM'
    
    #{ Columns    

    id_version_item = Column(Integer, Sequence('id_VersionItem_seq'), primary_key=True)                                       
    id_item = Column(Integer, ForeignKey('ITEM.id_item'))                                                                
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado'))
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item'))
    id_usuario_modifico = Column(Integer, ForeignKey('USUARIO.id_usuario'))
    nro_version_item = Column(Integer) 
    observaciones = Column(Unicode(255))
    fecha = Column(DateTime)    
    peso = Column(Integer)

    #{ Relations
    
    item = relation("Item", backref=backref('VersionItem', order_by=id_version_item))
    estado = relation("Estado", backref=backref('VersionItem', order_by=id_version_item))
    tipoItem = relation("TipoItem", backref=backref('VersionItem', order_by=id_version_item))
    usuarioModifico  = relation("Usuario", backref=backref('VersionItem', order_by=id_version_item))	
        
class Atributo(DeclarativeBase):

    def __init__(self, nombre, tipoDato, tipoItem):
        self.nom_atributo = nombre
        self.tipoDatoAtributo = tipoDato
        self.tipoItem = tipoItem
        
    def get_tablename__(self):
        return self.__tablename__

    def get_id_atributo(self):
        return self.__id_atributo

    def get_nom_atributo(self):
        return self.__nom_atributo

    def get_id_tipo_dato(self):
        return self.__id_tipo_dato

    def get_id_tipo_item(self):
        return self.__id_tipo_item

    def get_tipo_dato_atributo(self):
        return self.__tipoDatoAtributo

    def get_tipo_item(self):
        return self.__tipoItem

    def set_tablename__(self, value):
        self.__tablename__ = value

    def set_id_atributo(self, value):
        self.__id_atributo = value


    def set_nom_atributo(self, value):
        self.__nom_atributo = value


    def set_id_tipo_dato(self, value):
        self.__id_tipo_dato = value

    def set_id_tipo_item(self, value):
        self.__id_tipo_item = value

    def set_tipo_dato_atributo(self, value):
        self.__tipoDatoAtributo = value

    def set_tipo_item(self, value):
        self.__tipoItem = value

    def del_tablename__(self):
        del self.__tablename__

    def del_id_atributo(self):
        del self.__id_atributo

    def del_nom_atributo(self):
        del self.__nom_atributo


    def del_id_tipo_dato(self):
        del self.__id_tipo_dato

    def del_id_tipo_item(self):
        del self.__id_tipo_item

    def del_tipo_dato_atributo(self):
        del self.__tipoDatoAtributo

    def del_tipo_item(self):
        del self.__tipoItem

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

    def get_tablename__(self):
        return self.__tablename__

    def get_id_relacion(self):
        return self.__id_relacion


    def get_id_version_item_antecesor(self):
        return self.__id_version_item_antecesor


    def get_id_version_item(self):
        return self.__id_version_item


    def get_version_item_antecesor(self):
        return self.__versionItemAntecesor


    def get_version_item(self):
        return self.__versionItem


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_relacion(self, value):
        self.__id_relacion = value


    def set_id_version_item_antecesor(self, value):
        self.__id_version_item_antecesor = value


    def set_id_version_item(self, value):
        self.__id_version_item = value


    def set_version_item_antecesor(self, value):
        self.__versionItemAntecesor = value


    def set_version_item(self, value):
        self.__versionItem = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_relacion(self):
        del self.__id_relacion


    def del_id_version_item_antecesor(self):
        del self.__id_version_item_antecesor


    def del_id_version_item(self):
        del self.__id_version_item


    def del_version_item_antecesor(self):
        del self.__versionItemAntecesor


    def del_version_item(self):
        del self.__versionItem


    __tablename__ = 'RELACION_ITEM'
    
    #{ Columns    

    id_relacion = Column(Integer, Sequence('id_relacion_seq'), primary_key=True)    
    id_version_item = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item',onupdate="CASCADE"))
    id_tipo_relacion= Column(Integer, ForeignKey('TIPO_RELACION.id_tipo_relacion',onupdate="CASCADE"))

    #{ Relations    
    versionItem = relation("VersionItem", backref=backref('relacionItem', order_by=id_relacion))	
    tipoRelacion = relation("TipoRelacion", backref=backref('relacionItem', order_by=id_relacion))
    
class AtributoItem(DeclarativeBase):

    def get_tablename__(self):
        return self.__tablename__


    def get_id_atributo(self):
        return self.__id_atributo


    def get_id_version_item(self):
        return self.__id_version_item


    def get_val_atributo(self):
        return self.__val_atributo


    def get_atributo(self):
        return self.__atributo


    def get_version_item(self):
        return self.__versionItem


    def set_tablename__(self, value):
        self.__tablename__ = value


    def set_id_atributo(self, value):
        self.id_atributo = value


    def set_id_version_item(self, value):
        self.id_version_item = value


    def set_val_atributo(self, value):
        self.__val_atributo = value


    def set_atributo(self, value):
        self.__atributo = value


    def set_version_item(self, value):
        self.__versionItem = value


    def del_tablename__(self):
        del self.__tablename__


    def del_id_atributo(self):
        del self.__id_atributo


    def del_id_version_item(self):
        del self.__id_version_item


    def del_val_atributo(self):
        del self.__val_atributo


    def del_atributo(self):
        del self.__atributo


    def del_version_item(self):
        del self.__versionItem

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
    
