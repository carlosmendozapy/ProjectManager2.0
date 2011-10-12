# -*- coding: utf-8 -*-
"""Sample controller module"""

import os

# turbogears imports
from tg import expose, tmpl_context, response, request
from tg import redirect, validate, flash
from tg import session
from tg.controllers import CUSTOM_CONTENT_TYPE
from tg.decorators import paginate as paginatedeco
from webhelpers import paginate

# third party imports
from datetime import datetime
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous
# Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms.cycles import *
from pygraph.readwrite.dot import write

from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.query import Query


# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.model.entities import Item
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import AtributoArchivo
from projectmanager.model.entities import Estado
from projectmanager.model.entities import TipoItem
from projectmanager.model.entities import RelacionItem
from projectmanager.model.entities import Padre
from projectmanager.model.entities import Antecesor
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Usuario

from projectmanager.widgets.new_itemForm import create_new_item
from projectmanager.widgets.edit_fechaForm import edit_atributo_fecha
from projectmanager.widgets.edit_numericoForm import edit_atributo_numerico
from projectmanager.widgets.edit_textoForm import edit_atributo_texto
from projectmanager.widgets.edit_pesoForm import edit_atributo_peso

from projectmanager.lib.app_globals import Globals

class ItemController(BaseController):
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')    
      
    def __init__(self):
        self.eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminado').one()
        
        self.rechazado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Rechazado').one()
            
        self.pendiente = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Pendiente').one()
        
        self.confirmado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Confirmado').one()
            
    @expose('projectmanager.templates.items.items')
    def adminItem(self, faseid,**kw):                       
	    
        if 'msg' in kw:
           flash(_(kw['msg']),'warning')
               
        Globals.current_phase = DBSession.query(Fase).\
            filter(Fase.id_fase == int(faseid)).one()
                   
        list_items = DBSession.query(VersionItem).\
            filter(VersionItem.ultima_version=='S').\
            filter(VersionItem.fase==Globals.current_phase).\
            filter(VersionItem.estado!=self.eliminado).\
            filter(VersionItem.estado!=self.rechazado).\
            order_by(VersionItem.item).all()

        return dict(items=list_items)
        
    @expose('projectmanager.templates.items.newItem')
    def newItem(self, **kw):
	
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==Globals.current_phase.id_fase).one()
	
        listTipoItem = DBSession.query(TipoItem.id_tipo_item,\
                                   TipoItem.nom_tipo_item).\
                   filter(TipoItem.fase == fase).all()
		
        fase_list = DBSession.query(Fase).\
                    filter(Fase.id_proyecto == Globals.current_project.id_proyecto).\
                    order_by(Fase.nro_fase)
        
        estado = DBSession.query(Estado).\
            filter(Estado.nom_estado=='Aprobado').one()
        
        options_ancestros=[]            
        if fase_list.first().nro_fase != Globals.current_phase.nro_fase:
            anterior = fase_list.first()
            for fase in fase_list.all():
                if fase.nro_fase < Globals.current_phase.nro_fase:
                    anterior = fase
                else:
                    break
            items = DBSession.query(VersionItem).\
                filter(VersionItem.estado==estado).\
                filter(VersionItem.fase==anterior)
                        
            if items.count() != 0:                
                for item in items.all():
                    options_ancestros.append([item.id_version_item,item.item.nom_item])
            else:
                warn='La Fase Anterior no Posee Items en Linea Base '+\
                     'necesarios para la creacion de Items en esta '+\
                     'fase'
                redirect('adminItem?faseid=' +\
                    str(Globals.current_phase.id_fase)+';msg='+warn)
        
        estadoConfirmado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Confirmado').one()
            
        options_padres=[]
        list_items = DBSession.query(VersionItem).\
            filter(or_(VersionItem.estado==estado, 
                       VersionItem.estado==estadoConfirmado)).\
            filter(VersionItem.fase==fase).\
            filter(VersionItem.ultima_version=='S').all()
            
        for item in list_items:
            options_padres.append([item.id_version_item, item.item.nom_item])
            
        tmpl_context.form = create_new_item
               
        return dict(type_options = listTipoItem, 
                    ancestros = options_ancestros,
                    padres = options_padres)    	        
    
    @validate(create_new_item,error_handler=newItem)
    @expose()
    def saveItem(self, **kw):
        fase_list = DBSession.query(Fase).\
                    filter(Fase.id_proyecto == Globals.current_project.id_proyecto).\
                    order_by(Fase.nro_fase)
                    
        if fase_list.first().nro_fase != Globals.current_phase.nro_fase and\
           len(kw['antecesor']) == 0:
            flash(_('Debe elegir al menos un Antecesor'),'warning')
            redirect('newItem')
        
        estado = DBSession.query(Estado).filter(Estado.nom_estado=='En Modificacion').one()
        tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['tipoItem'])).one()                      
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).filter(Usuario.login_name==lg_name).one()
        
        item = Item()
        item.cod_item = str(tipoItem.prefijo) + str(tipoItem.cont_prefijo)
        tipoItem.cont_prefijo = tipoItem.cont_prefijo + 1
               
        item.nom_item = kw['nomItem']
        item.tipoItem = tipoItem          
        
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = item        
        nuevaVersionItem.nro_version_item = 0
        nuevaVersionItem.estado = estado       
        nuevaVersionItem.tipoItem = tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        dt = datetime.now()
        nuevaVersionItem.fecha = dt.strftime('%d/%m/%Y %I:%M%p')
        nuevaVersionItem.observaciones = kw['observaciones']
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = int(kw['peso'])
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
                                 
        '''ANTECESORES'''
        if len(kw['antecesor']) > 0:
            for antecesorID in kw['antecesor']:
                nuevaVersionItem.Antecesores.append(Antecesor(antecesorID))
        
        '''PADRES'''
                   
        if len(kw['padres']) > 0:
            
            padres_list=[]
            for padreID in kw['padres']:
                existe=True
                try:
                    unPadre = DBSession.query(Padre).\
                        filter(Padre.id_version_item == int(padreID)).one()
                except NoResultFound,e:                    
                    nuevaVersionItem.Padres.append(Padre(int(padreID)))
                    existe=False
                
                if existe:
                    elPadre = DBSession.query(Padre).\
                        filter(Padre.id_version_item==int(padreID)).one()
                    nuevaVersionItem.Padres.append(elPadre)
         
            ''' CONTROL CON GRAFO
            aprobado = DBSession.query(Estado).\
                filter(Estado.nom_estado == 'Aprobado').one()
            
            confirmado = DBSession.query(Estado).\
                filter(Estado.nom_estado == 'Confirmado').one()
            
            list= DBSession.query(VersionItem).\
                filter(or_(VersionItem.estado==aprobado, 
                       VersionItem.estado==confirmado)).\
                filter(VersionItem.id_fase==Globals.current_phase.id_fase).\
                filter(VersionItem.ultima_version=='S').all()            
        
            graph_rel =graph()
            graph_rel.add_node(int(nuevaVersionItem.id_version_item))
            for nodo in list:
                graph_rel.add_node(nodo.id_version_item)
                       
            nodos_list = graph_rel.nodes()
            
            for nodo in nodos_list:
                #Padres del item actual                            
                item=DBSession.query(VersionItem).\
                    filter(VersionItem.id_version_item == nodo).one()
                
                if item.Padres != None:
                    for obj in item.Padres:
                        if not graph_rel.has_edge((nodo,int(obj.id_version_item))):
                            graph_rel.add_edge((nodo,int(obj.id_version_item)))
                                                    
                #Hijos del item actual                                
                try:
                    padre=DBSession.query(Padre).\
                        filter(Padre.id_version_item == int(nodo)).one()
                except NoResultFound,e:
                    padre = None
                 
                if padre != None:                                  
                    for obj in padre.hijos:
                        if not graph_rel.has_edge((nodo,int(obj.id_version_item))):
                            graph_rel.add_edge((nodo,int(obj.id_version_item)))                        
                        
            ciclos = find_cycle(graph_rel)
            if len(ciclos) > 0:
                DBSession.rollback()
                flash(_('Modifique su Seleccion de Padres: Se ha detectado uno o más ciclos'),'warning')
                redirect('newItem')
            '''   
        for atributo in DBSession.query(Atributo).filter(Atributo.tipoItem==tipoItem):
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.atributo = atributo
            nuevoAtributoItem.versionItem = nuevaVersionItem        
            nuevoAtributoItem.val_atributo = atributo.val_default
            DBSession.add(nuevoAtributoItem)   
        
        flash(_("Se ha creado un nuevo Item: %s") %kw['nomItem'],'info')        
        redirect("adminItem?faseid="+str(Globals.current_phase.id_fase))
           
    @expose('projectmanager.templates.items.atributosItem')
    def atributosItem(self, **kw):                        
        unaVersionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==kw['id_version']).one()
        
        Globals.current_item = unaVersionItem
        
        atributosItem = DBSession.query(AtributoItem).\
            filter(AtributoItem.versionItem==unaVersionItem).\
            order_by(AtributoItem.id_atributo).all()                
        
        Padres = []
        for padre in unaVersionItem.Padres:
            unPadre = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == padre.id_version_item).\
                one()
            Padres.append(unPadre)    
        
        return dict(atributosItem=atributosItem, padres=Padres)  
        
    @expose('projectmanager.templates.items.atributosVersion')
    def atributosVersion(self, **kw):                        
        unaVersionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==kw['id_version']).one()
        
        Globals.current_item = unaVersionItem
        
        atributosItem = DBSession.query(AtributoItem).\
            filter(AtributoItem.versionItem==unaVersionItem).\
            order_by(AtributoItem.id_atributo).all()                
            
        return dict(atributosItem=atributosItem)

    @expose('projectmanager.templates.items.editAtributo')
    def editAtributo(self, **kw):
        
        if 'id_atributo' in kw and int(kw['id_atributo'])>=0:
            Globals.current_atributo = DBSession.query(AtributoItem).\
                filter(AtributoItem.id_atributo==int(kw['id_atributo'])).\
                filter(AtributoItem.id_version_item==int(kw['id_version_item'])).\
                one()
        
            if Globals.current_atributo.atributo.tipoDatoAtributo.\
                nom_tipo_dato == 'fecha':           
                tmpl_context.form = edit_atributo_fecha
        
            elif Globals.current_atributo.atributo.tipoDatoAtributo.\
                nom_tipo_dato == 'numerico':
                tmpl_context.form = edit_atributo_numerico
            
            elif Globals.current_atributo.atributo.tipoDatoAtributo.\
                nom_tipo_dato == 'texto':
                tmpl_context.form = edit_atributo_texto
               
            return dict(idAtributo = Globals.current_atributo.id_atributo,
                    idVersionItem = Globals.current_atributo.id_version_item,
                    value = Globals.current_atributo.val_atributo)
        
        elif 'peso' in kw or ('id_atributo' in kw and int(kw['id_atributo']) == -1):
            tmpl_context.form = edit_atributo_peso
            
            return dict(idAtributo = -1,
                        idVersionItem = Globals.current_item.id_version_item,
                        value = Globals.current_item.peso)  
        
        elif 'obs' in kw or ('id_atributo' in kw and int(kw['id_atributo']) == -2):
            tmpl_context.form = edit_atributo_texto
            
            return dict(idAtributo = -2,
                        idVersionItem = Globals.current_item.id_version_item,
                        value = Globals.current_item.observaciones)
    
    @validate(edit_atributo_peso, error_handler=editAtributo)
    @expose()
    def updateAtributoPeso(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = versionItem.estado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = int(kw['valor'])
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
              
        Globals.current_item = nuevaVersionItem
        
        redirect('atributosItem?id_version=' +\
            str(Globals.current_item.id_version_item))  
                   
    @validate(edit_atributo_fecha,error_handler=editAtributo)
    @expose()
    def updateAtributoFecha(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = versionItem.estado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
            
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
        
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).\
            filter(AtributoItem.id_atributo != int(kw['id_atributo'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
       
        nuevoAtributoItem = AtributoItem()
        nuevoAtributoItem.id_atributo = int(kw['id_atributo'])
        nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item                
        nuevoAtributoItem.val_atributo = kw['valor'].strftime('%d/%m/%y')
        DBSession.add(nuevoAtributoItem)
        
        Globals.current_item = nuevaVersionItem
        
        redirect('atributosItem?id_version=' +\
            str(Globals.current_item.id_version_item))
    
    @validate(edit_atributo_numerico,error_handler=editAtributo)
    @expose()
    def updateAtributoNumerico(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = versionItem.estado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).\
            filter(AtributoItem.id_atributo != int(kw['id_atributo'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
       
        nuevoAtributoItem = AtributoItem()
        nuevoAtributoItem.id_atributo = int(kw['id_atributo'])
        nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item                
        nuevoAtributoItem.val_atributo = kw['valor']
        DBSession.add(nuevoAtributoItem)
        
        Globals.current_item = nuevaVersionItem
        
        redirect('atributosItem?id_version=' +\
            str(Globals.current_item.id_version_item))    
            
    @validate(edit_atributo_texto,error_handler=editAtributo)
    @expose()
    def updateAtributoTexto(self, **kw):
                        
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = versionItem.estado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        if int(kw['id_atributo']) < 0:
            nuevaVersionItem.observaciones = kw['valor']
        else:
            nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
       
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        if int(kw['id_atributo']) < 0:
            for atributo in DBSession.query(AtributoItem).\
                filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
                nuevoAtributoItem = AtributoItem()
                nuevoAtributoItem.id_atributo = atributo.id_atributo
                nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
                nuevoAtributoItem.val_atributo = atributo.val_atributo
                nuevoAtributoItem.id_archivo = atributo.id_archivo
                DBSession.add(nuevoAtributoItem)
        else:
            for atributo in DBSession.query(AtributoItem).\
                filter(AtributoItem.id_version_item == int(kw['id_version_item'])).\
                filter(AtributoItem.id_atributo != int(kw['id_atributo'])).all():
                
                nuevoAtributoItem = AtributoItem()
                nuevoAtributoItem.id_atributo = atributo.id_atributo
                nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
                nuevoAtributoItem.val_atributo = atributo.val_atributo
                nuevoAtributoItem.id_archivo = atributo.id_archivo
                DBSession.add(nuevoAtributoItem)
       
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = int(kw['id_atributo'])
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item                
            nuevoAtributoItem.val_atributo = kw['valor']
            DBSession.add(nuevoAtributoItem)
    
        Globals.current_item = nuevaVersionItem
        
        redirect('atributosItem?id_version=' +\
            str(Globals.current_item.id_version_item))
    
    @expose()
    def confirmar(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
                   
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = self.confirmado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
                   
        redirect('adminItem?faseid=' +\
            str(nuevaVersionItem.id_fase)) 
           
    @expose('projectmanager.templates.items.itemHistory')   
    def history(self, **kw):
              
        versiones = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == int(kw['id_item'])).\
            order_by(VersionItem.nro_version_item)
        
        Globals.current_item = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == int(kw['id_item'])).\
            filter(VersionItem.ultima_version == 'S').one()
                
        return dict(versiones = versiones)
        
    @expose('projectmanager.templates.items.atributosComparar')
    def comparar(self, **kw):        
        atributos_list = []
        
                                
        if 'item' in kw and str(type(kw['item'])) == '<type \'list\'>' :            
            for id in kw['item']:
                atributos = DBSession.query(AtributoItem).\
                    filter(AtributoItem.id_version_item == int(id))
                atributos_list.append(atributos)
        else:
            flash(_('Favor Seleccione al menos dos elementos'), 'warning')
       
        return dict(atributos = atributos_list)
    
    @expose()
    def revertir(self, **kw):
        anteriorVersion = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == int(kw['id_item'])).one()
            
        ultimaVersion = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == anteriorVersion.id_item).\
            filter(VersionItem.ultima_version == 'S').one()
            
        ultimaVersion.ultima_version = 'N'
                        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
                  
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = anteriorVersion.item        
        nuevaVersionItem.nro_version_item = ultimaVersion.nro_version_item+1
        nuevaVersionItem.estado = self.pendiente       
        nuevaVersionItem.tipoItem = anteriorVersion.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = anteriorVersion.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = anteriorVersion.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
                      
        for padre in anteriorVersion.Padres:
            itemPadre = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == padre.id_version_item).\
                one()
            
            if itemPadre.estado != self.eliminado:
                nuevaVersionItem.padres.append(padre)
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == anteriorVersion.id_version_item):
                            
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
                      
        Globals.current_item = nuevaVersionItem
        
        redirect('/item/history?id_item=' + str(Globals.current_item.id_item))
        
    #**************************** BUSQUEDA Y OTROS **********************************    
    @expose('projectmanager.templates.items.items')
    def search(self, **kw):
        word = kw['key']
        estado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminado').one()
            
        items = DBSession.query(VersionItem).\
            filter(VersionItem.ultima_version=='S').\
            filter(VersionItem.fase==Globals.current_phase).\
            filter(VersionItem.id_estado!=estado.id_estado).all()
            
        items_list = []
        for item in items:
            if item.item.nom_item.find(word) != -1:
                items_list.append(item)
                
        return dict(items=items_list)
    
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def download(self, **kw):
        idAtributo = kw['idAtributo']
        idVersionItem = kw['idVersionItem']        

        q = DBSession.query(AtributoItem)
        q = q.from_statement('SELECT * FROM \"ATRIBUTO_ITEM\" WHERE id_atributo=:idAtributoArch AND id_version_item=:idVersionItemArch')
        q=  q.params(idAtributoArch=idAtributo)
        q=  q.params(idVersionItemArch=idVersionItem)        
        atributoItem = q.first()        
       
        archivoAtributo = DBSession.query(AtributoArchivo).filter(AtributoArchivo.id == atributoItem.id_archivo).first()
               
        content_types = {
            'download': {'.png': 'image/jpeg', '.jpeg':'image/jpeg', '.jpg':'image/jpeg', '.gif':'image/jpeg', '.txt': 'text/plain', '.pdf':'application/pdf', '.zip':'application/zip', '.rar':'application/x-rar-compressed'}
        }        
        for file_type in content_types['download']:
            if archivoAtributo.filename.endswith(file_type):
                response.headers["Content-Type"] = content_types['download'][file_type]
                response.headers["Content-Disposition"] = 'attachment; filename="'+archivoAtributo.filename+'"'
        if archivoAtributo.filename.find(".") == -1:
            '''response.headers["Content-Type"] = "text/plain"'''
            response.headers["Content-Type"] =  content_types['download']
            response.headers["Content-Disposition"] = 'attachment; filename="'+archivoAtributo.filename+'"'
        return archivoAtributo.filecontent        
