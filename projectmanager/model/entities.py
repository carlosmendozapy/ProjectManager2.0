# -*- coding: utf-8 -*-
"""Sample model module."""
import os
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from projectmanager.model import DeclarativeBase, metadata, DBSession
from sqlalchemy.orm.exc import NoResultFound
from projectmanager.model.roles import Usuario

#Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms.cycles import *
from pygraph.readwrite.dot import write

# Import graphviz
import sys
sys.path.append('..')
sys.path.append('/usr/share/pyshared/')
sys.path.append('/usr/lib/pyshared/python2.6/')
import gv

PadreVersionItem = Table('PADRE_VERSIONITEM', metadata,
    Column('id_padre', Integer, ForeignKey('PADRE.id_padre')),
    Column('id_version_item', Integer, ForeignKey('VERSION_ITEM.id_version_item')),
)

AntecesorVersionItem = Table('ANTECESOR_VERSIONITEM', metadata,
    Column('id_antecesor', Integer, ForeignKey('ANTECESOR.id_antecesor')),
    Column('id_version_item', Integer, ForeignKey('VERSION_ITEM.id_version_item')),
)

class Padre(DeclarativeBase):
    
    def __init__(self, id_version_item):
        self.id_version_item = id_version_item
        
    __tablename__ = 'PADRE'
    
    #{ Columns
    id_padre = Column(Integer, autoincrement=True, primary_key=True)
    id_version_item = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item'))
    
    #{ Relations
    hijos = relation('VersionItem', secondary=PadreVersionItem, backref=backref('Padres'))
    
class Antecesor(DeclarativeBase):
    
    def __init__(self, id_version):
        self.id_version_item = id_version
        
    __tablename__ = 'ANTECESOR'
    
    #{ Columns
    id_antecesor = Column(Integer, autoincrement=True, primary_key=True)
    id_version_item = Column(Integer, ForeignKey('VERSION_ITEM.id_version_item'))
    
    #{ Relations
    sucesores = relation('VersionItem', secondary=AntecesorVersionItem, backref=backref('Antecesores'))
    
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
    tipoItem = relation("TipoItem", backref=backref('Item', order_by=cod_item))    
     
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
    
    def initGraph(self,itemVersion):
        self.impacto_graph = digraph()
        self.impacto_graph.add_node(itemVersion.id_version_item,
        [('label',itemVersion.item.nom_item + "\n" + str(itemVersion.peso)),
        ('color','gold'),('root','true')])
        
    def drawGraph(self):
        dot = write(self.impacto_graph)        
        gvv = gv.readstring(dot)                                
        gv.layout(gvv,'dot')
        gv.render(gvv,'png',os.path.abspath("projectmanager/public/images/calculoImpacto.png"))
    
    def getRelacionesDer(self,idVersion):
        derecha=[]
        abajo=[]
               
        sucesores = self.getSucesores(idVersion)
        derecha.extend(sucesores)
        
        hijos=self.getHijos(idVersion) 
        abajo.extend(self.getHijosNietos(hijos))
        
        if len(abajo) > 0:
            for hijo in abajo:
                sucesores = self.getSucesores(hijo.id_version_item)
                derecha.extend(sucesores)
                    
        for item in derecha:
            sucesores = self.getSucesores(item.id_version_item)
            derecha.extend(sucesores)
            hijos=self.getHijos(item.id_version_item)
            derecha.extend(hijos)
           
        return derecha
        
    def getRelacionesIzq(self, idVersion):
        
        izquierda=[]
        abajo=[]         
        antecesores = self.getAntecesores(idVersion)               
        izquierda.extend(antecesores)
        
        hijos=self.getHijos(idVersion) 
        abajo.extend(self.getHijosNietos(hijos))
        
        if len(abajo) > 0:
            for hijo in abajo:
                antecesores =  self.getAntecesores(hijo.id_version_item)
                izquierda.extend(antecesores)
                
        for item in izquierda:
            antecesores = self.getAntecesores(item.id_version_item)
            izquierda.extend(antecesores)
            hijos = self.getHijos(item.id_version_item)                        
            izquierda.extend(hijos)
            
        return izquierda
        
    def getAntecesoresAll(self, lista):
        for item in lista:
            lista.extend(self.getAntecesores(item.id_version_item))
            
        return lista
    
    def getSucesoresAll(self, lista):
        
        for item in lista:
            lista.extend(self.getSucesores(item.id_version_item))
            
        return lista
        
    def getHijosNietos(self, lista):
        
        for item in lista:
            lista.extend(self.getHijos(item.id_version_item))            
        
        return lista
        
    def getSucesores(self, idVersion):
        sucesores=[]
        item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == idVersion).one()
            
        try:
            yoAntecesor=DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item==int(idVersion)).one()
            
            if not self.impacto_graph.has_node(idVersion):
                self.impacto_graph.add_node(idVersion,
                [('label',item.item.nom_item + "\n" + str(item.peso)),
                ('shape','box'),('rankdir','LR')])
            
            for sucesor in yoAntecesor.sucesores:
                if sucesor.ultima_version=='S' and\
                sucesor.estado.nom_estado!='Eliminado':
                    sucesores.append(sucesor)
                    
                    if not self.impacto_graph.\
                    has_node(sucesor.id_version_item):
                        self.impacto_graph.add_node(sucesor.id_version_item,
                        [('label',sucesor.item.nom_item + "\n" + str(sucesor.peso)),
                        ('shape','box'),('rankdir','LR')])
                        
                    if not self.impacto_graph.\
                    has_edge((idVersion,sucesor.id_version_item)):
                        self.impacto_graph.add_edge((idVersion,
                        sucesor.id_version_item),
                        label='Sucesor')                                        
            
        except NoResultFound,e:
            existe=False
            
        return sucesores
                    
    def getAntecesores(self, idVersion):
        itemVersion = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == int(idVersion)).one()
        
        if not self.impacto_graph.has_node(idVersion):
            self.impacto_graph.add_node(idVersion,
            [('label',itemVersion.item.nom_item + "\n" + str(itemVersion.peso)),
            ('shape','box'),('rankdir','RL')])           
            
        antecesores=[]
        
        for antecesor in itemVersion.Antecesores:
            unItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==antecesor.id_version_item).one()
            
            if unItem.ultima_version=='S' and\
            unItem.estado.nom_estado!='Eliminado':
                antecesores.append(unItem)
                
                if not self.impacto_graph.has_node(unItem.id_version_item):
                    self.impacto_graph.add_node(unItem.id_version_item,
                    [('label',unItem.item.nom_item + "\n" + str(unItem.peso)),
                    ('shape','box'),('rankdir','RL')])
                
                if not self.impacto_graph.\
                has_edge((unItem.id_version_item,idVersion)):
                    self.impacto_graph.\
                        add_edge((idVersion,unItem.id_version_item),
                                 label='Antecesor')
        
        return antecesores
        
    def getHijos(self, idVersion):
        item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==idVersion).one()
            
        hijos=[]
       
        try:
            
            itemPadre=DBSession.query(Padre).\
            filter(Padre.id_version_item==int(idVersion)).\
            one()
            
            if not self.impacto_graph.has_node(idVersion):
                self.impacto_graph.add_node(idVersion,
                [('label',item.item.nom_item + "\n" + str(item.peso))])
                                        
            for hijo in itemPadre.hijos:
                if hijo.ultima_version=='S' and\
                hijo.estado.nom_estado!='Eliminado':
                    hijos.append(hijo)                    
                                        
                    if not self.impacto_graph.has_node(hijo.id_version_item):
                        self.impacto_graph.add_node(hijo.id_version_item,
                        [('label',hijo.item.nom_item + "\n" + str(hijo.peso))])
                    
                    if not self.impacto_graph.\
                    has_edge((idVersion,hijo.id_version_item)):                      
                        self.impacto_graph.\
                            add_edge((idVersion,hijo.id_version_item),
                                      label='Hijo')
                    
        except NoResultFound,e:
            existe=False
       
        return hijos
            
        
    #{ Columns    

    id_version_item = Column(Integer, Sequence('id_VersionItem_seq'), primary_key=True)                                       
    ultima_version = Column(Unicode(1))
    id_item = Column(Integer, ForeignKey('ITEM.id_item'))                                                                
    id_estado = Column(Integer, ForeignKey('ESTADO.id_estado'))
    id_tipo_item = Column(Integer, ForeignKey('TIPO_ITEM.id_tipo_item'))
    id_usuario_modifico = Column(Integer, ForeignKey('USUARIO.id_usuario'))    
    id_fase = Column(Integer, ForeignKey('FASE.id_fase'))    
    nro_version_item = Column(Integer) 
    observaciones = Column(Unicode(255))
    fecha = Column(DateTime)    
    peso = Column(Integer)

    #{ Relations
    
    item = relation("Item", backref=backref('VersionItem', order_by=id_version_item),order_by="Item.cod_item")
    estado = relation("Estado", backref=backref('VersionItem', order_by=id_version_item))
    tipoItem = relation("TipoItem", backref=backref('VersionItem', order_by=id_version_item))
    usuarioModifico  = relation("Usuario", backref=backref('VersionItem', order_by=id_version_item))	    
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

    atributo  = relation("Atributo", backref=backref('AtributoItem'),order_by=Atributo.nom_atributo)	
    versionItem = relation("VersionItem", backref=backref('AtributoItem', order_by=Atributo.nom_atributo), order_by=Atributo.nom_atributo)	
    atributoArchivo = relation("AtributoArchivo", backref=backref('AtributoItem', order_by=Atributo.nom_atributo),order_by=Atributo.nom_atributo)	   
     
class AtributoArchivo(DeclarativeBase):    
    
    def __init__(self, filename, filecontent):
        self.filename = filename
        self.filecontent = filecontent

    __tablename__ = 'ATRIBUTO_ARCHIVO'
    
    #{ Columns    
    
    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(255), nullable=False)
    filecontent = Column(LargeBinary)
    
