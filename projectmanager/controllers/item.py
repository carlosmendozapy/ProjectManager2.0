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

# Import graphviz
import sys
sys.path.append('..')
sys.path.append('/usr/share/pyshared/')
sys.path.append('/usr/lib/pyshared/python2.6/')
import gv

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
        
        self.eliminar = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminar').one()
        
        self.rechazado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Rechazado').one()
            
        self.pendiente = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Pendiente').one()
        
        self.confirmado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Confirmado').one()
            
        self.modificacion = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'En Modificacion').one()
            
    @expose('projectmanager.templates.items.items')
    def adminItem(self, **kw):                       
	    
        if 'msg' in kw:
           flash(_(kw['msg']),'warning')
               
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminado').one()
        
        rechazado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Rechazado').one()
            
        Globals.current_phase = DBSession.query(Fase).\
            filter(Fase.id_fase == kw['faseid']).one()
                   
        list_items = DBSession.query(VersionItem).\
            filter(VersionItem.ultima_version=='S').\
            filter(VersionItem.fase==Globals.current_phase).\
            filter(VersionItem.id_estado!=eliminado.id_estado).\
            order_by(VersionItem.id_item).all()
        
        list_items.sort(cmp=None, key= lambda item: item.item.nom_item, reverse=False)
        
        return dict(items=list_items)
        
    @expose('projectmanager.templates.items.newItem')
    def newItem(self, **kw):
	
        if 'ciclo' in kw:
            return dict(ciclo=1)
            
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
                    padres = options_padres,
                    ciclo= 0)    	        
    
    @validate(create_new_item,error_handler=newItem)
    @expose()
    def saveItem(self, **kw):
        fase_list = DBSession.query(Fase).\
                    filter(Fase.id_proyecto == Globals.current_project.id_proyecto).\
                    order_by(Fase.nro_fase)
                    
        if fase_list.first().nro_fase != Globals.current_phase.nro_fase and\
        len(kw['antecesor']) == 0 and\
        len(kw['padres']) == 0:
            
            flash(_('Debe elegir al menos un Antecesor o un Padre'),'warning')
            redirect('newItem')
                
        estado = DBSession.query(Estado).filter(Estado.nom_estado=='En Modificacion').one()
        tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['tipoItem'])).one()                      
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).filter(Usuario.login_name==lg_name).one()
        
        if len(kw['padres']) > 0:
            ciclo = self.controlCiclo(kw['padres'],999999)
            if ciclo:
                flash(_("Se ha detectado un ciclo: Favor seleccione otro padre"), 'warning')
                redirect('/item/newItem?ciclo=1')
            
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
        
        '''PADRES'''                   
        if len(kw['padres']) > 0:
        
            padres_list=[]
            for padreID in kw['padres']:                    
                try:
                    unPadre = DBSession.query(Padre).\
                        filter(Padre.id_version_item == int(padreID)).one()
                    nuevaVersionItem.Padres.append(unPadre)
                except NoResultFound,e:                    
                    nuevaVersionItem.Padres.append(Padre(int(padreID)))
            
        '''ANTECESORES'''
        if len(kw['antecesor']) > 0:
            for antecesorID in kw['antecesor']:
                try:
                    unAntecesor= DBSession.query(Antecesor).\
                    filter(Antecesor.id_version_item == int(antecesorID)).\
                    one()
                    nuevaVersionItem.Antecesores.append(unAntecesor)
                except NoResultFound,e:
                    nuevaVersionItem.Antecesores.append(Antecesor(int(antecesorID)))
                                                        
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
            
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado=='Eliminado').one()
        
        Globals.current_item = unaVersionItem
        
        atributosItem = DBSession.query(AtributoItem).\
            filter(AtributoItem.versionItem==unaVersionItem).\
            order_by(AtributoItem.id_atributo).all()                
        
        Relaciones=[]
        #Recuperar Nombre de los Padres de esta Version de Item
        Padres = []
        for padre in unaVersionItem.Padres:            
            unPadre = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == padre.id_version_item).\
                one()            
            
            if unPadre.ultima_version == 'S' and\
            unPadre.id_estado != eliminado.id_estado:
                Padres.append(unPadre)    
            
        #Recuperar Nombre de los Hijos de esta Version de Item
        Hijos=[]
        try:
            yoPadre = DBSession.query(Padre).\
                filter(Padre.id_version_item==unaVersionItem.id_version_item).one()
                
            Hijos = DBSession.query(VersionItem).\
            filter(VersionItem.Padres.contains(yoPadre)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
        except NoResultFound,e:                    
            existe=False
            
        #Recuperar Nombre de los Antecesores de esta Version de Item
        Antecesores=[]
        for antecesor in unaVersionItem.Antecesores:
            unAntecesor = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==antecesor.id_version_item).\
                one()
            if unAntecesor.ultima_version == 'S' and\
            unAntecesor.id_estado != eliminado.id_estado:
                Antecesores.append(unAntecesor)
            
        #Recuperar Nombre de los Sucesores de esta Version de Item
        Sucesores=[]
        try:
            yoAntecesor = DBSession.query(Antecesor).\
                filter(Antecesor.id_version_item==unaVersionItem.id_version_item).one()
                
            Sucesores= DBSession.query(VersionItem).\
            filter(VersionItem.Antecesores.contains(yoAntecesor)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
        except NoResultFound,e:                    
            existe=False
            
        Relaciones.append(Padres)
        Relaciones.append(Hijos)
        Relaciones.append(Antecesores)
        Relaciones.append(Sucesores)
        
        self.graficarRelaciones(unaVersionItem.id_version_item)
        
        return dict(atributosItem=atributosItem, relaciones=Relaciones,\
                    frompage = str(kw['frompage']))  
        
    @expose('projectmanager.templates.items.atributosVersion')
    def atributosVersion(self, **kw):                        
        unaVersionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==kw['id_version']).one()
            
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado=='Eliminado').one()
        
        Globals.current_item = unaVersionItem
        
        atributosItem = DBSession.query(AtributoItem).\
            filter(AtributoItem.versionItem==unaVersionItem).\
            order_by(AtributoItem.id_atributo).all()                
        
        Relaciones=[]
        #Recuperar Nombre de los Padres de esta Version de Item
        Padres = []
        for padre in unaVersionItem.Padres:            
            unPadre = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == padre.id_version_item).\
                one()            
            
            if unPadre.ultima_version == 'S' and\
            unPadre.id_estado != eliminado.id_estado:
                Padres.append(unPadre)    
            
        #Recuperar Nombre de los Hijos de esta Version de Item
        Hijos=[]
        try:
            yoPadre = DBSession.query(Padre).\
                filter(Padre.id_version_item==unaVersionItem.id_version_item).one()
                
            Hijos = DBSession.query(VersionItem).\
            filter(VersionItem.Padres.contains(yoPadre)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
        except NoResultFound,e:                    
            existe=False
            
        #Recuperar Nombre de los Antecesores de esta Version de Item
        Antecesores=[]
        for antecesor in unaVersionItem.Antecesores:
            unAntecesor = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==antecesor.id_version_item).\
                one()
            if unAntecesor.ultima_version == 'S' and\
            unAntecesor.id_estado != eliminado.id_estado:
                Antecesores.append(unAntecesor)
            
        #Recuperar Nombre de los Sucesores de esta Version de Item
        Sucesores=[]
        try:
            yoAntecesor = DBSession.query(Antecesor).\
                filter(Antecesor.id_version_item==unaVersionItem.id_version_item).one()
                
            Sucesores= DBSession.query(VersionItem).\
            filter(VersionItem.Antecesores.contains(yoAntecesor)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
        except NoResultFound,e:                    
            existe=False
            
        Relaciones.append(Padres)
        Relaciones.append(Hijos)
        Relaciones.append(Antecesores)
        Relaciones.append(Sucesores)
        
        self.graficarRelaciones(unaVersionItem.id_version_item)
        
        return dict(atributosItem=atributosItem, relaciones=Relaciones)

# **********************************************************************
# ********************* Modificacion de Atributos **********************

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
        
         # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
            str(Globals.current_item.id_version_item) +\
            ";frompage=item")  
                   
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
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
        
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
        if not kw['valor'] == None:
            nuevoAtributoItem.val_atributo = kw['valor'].strftime('%d/%m/%y')
        else:
            nuevoAtributoItem.val_atributo = kw['valor']
            
        DBSession.add(nuevoAtributoItem)
        
        Globals.current_item = nuevaVersionItem
        
        redirect('atributosItem?id_version=' +\
            str(Globals.current_item.id_version_item) +\
            ";frompage=item")
    
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
        
         # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
            str(Globals.current_item.id_version_item) +\
            ";frompage=item")    
            
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
       
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
            str(Globals.current_item.id_version_item) +\
            ";frompage=item")
    
# **********************************************************************
# *********************** Modificar Estados ****************************    
    
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
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
    
    @expose()
    def rechazar(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
                   
        anteriorItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == versionItem.id_item).\
            filter(VersionItem.nro_version_item == \
            (versionItem.nro_version_item-1)).one()
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
        
        rechazado = DBSession.query(Estado).\
            filter(Estado.nom_estado=='Rechazado').one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = anteriorItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = rechazado       
        nuevaVersionItem.tipoItem = anteriorItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = anteriorItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = anteriorItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        # Agregar los antecesores del item viejo
        for antecesor in anteriorItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == anteriorItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in anteriorItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == anteriorItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == anteriorItem.id_version_item).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
                   
        redirect('adminItem?faseid=' +\
            str(nuevaVersionItem.id_fase))
   
    @expose()
    def aModificar(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        # Para el caso en que este en Revision controlar que la Linea Base
        # este Abierta
        LBases = versionItem.NroLineaBase
        has_lb = False
        if len(LBases) > 0:
            has_lb = True            
            estado = None
            for lb in LBases:
                estado = lb.estado.nom_estado
                
            if estado != 'Abierta':
                flash(_('Solicite primero la Apertura de la Linea Base Correspondiente'),'warning')
                redirect('adminItem?faseid=' +  str(versionItem.id_fase))
            
        
        versionItem.ultima_version = 'N'
        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
                   
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = versionItem.item        
        nuevaVersionItem.nro_version_item = versionItem.nro_version_item+1
        nuevaVersionItem.estado = self.modificacion       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
        
        #Solo si tiene una linea base le avisara a sus relacionados
        #que deben estar en revision
        if has_lb:           
            self.aRevision(nuevoAtributoItem.id_version_item)
        
        redirect('adminItem?faseid=' +\
            str(nuevaVersionItem.id_fase))
           
    @expose()
    def aPendiente(self, **kw):
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
        nuevaVersionItem.estado = self.pendiente       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
            
    @expose()
    def aEliminar(self, **kw):
        
        if self.quedanHuerfanos(kw['id_version_item']):
            flash(_("La Eliminacion de este Item producira huerfanos en la siguiente fase"),'warning')
            redirect("/item/adminItem?faseid=" + str(Globals.current_phase.id_fase))
            
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
        nuevaVersionItem.estado = self.eliminar       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
    
    @expose()
    def aEliminado(self, **kw):
                
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
        nuevaVersionItem.estado = self.eliminado       
        nuevaVersionItem.tipoItem = versionItem.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = versionItem.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = versionItem.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
        
        DBSession.flush()
                   
        redirect('adminItem?faseid=' +\
            str(nuevaVersionItem.id_fase))
      
    
    def aRevision(self, idVersion, **Kw):
            """Metodo interno que se encarga de pasar al estado
            En Revision a todos los items relacionados con el item
            que se esta modificando"""
            
            revision=DBSession.query(Estado).\
            filter(Estado.nom_estado=='En Revision').one()
            
            #Obtener el item a modificar
            item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==idVersion).one()
            
            #Obtener la red de relaciones desde este item
            item.initGraph(item)
            
            ListaItems = []  
             
            #Izquierda
            ListaItems.extend(item.getRelacionesIzq(item.id_version_item))
            
            #Abajo
            hijos=item.getHijos(item.id_version_item)        
            ListaItems.extend(item.getHijosNietos(hijos))
            
            #Derecha
            ListaItems.extend(item.getRelacionesDer(item.id_version_item))
            
            for unItem in ListaItems:
                unItem.estado = revision
                
                

# **********************************************************************
# ********************* Versionado de Item *****************************

    @expose('projectmanager.templates.items.itemHistory')   
    def history(self, **kw):
              
        versiones = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == int(kw['id_item'])).\
            order_by(VersionItem.nro_version_item)
                
        Globals.current_item = DBSession.query(VersionItem).\
            filter(VersionItem.id_item == int(kw['id_item'])).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.estado!=self.eliminado).one()
                
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
            
        fases = DBSession.query(Fase).\
            filter(Fase.id_proyecto==Globals.current_project.id_proyecto)
            
        # Controlar que no se revierta como huerfano o que deje
        # huerfano a sus hijos      
        if fases.first().nro_fase != Globals.current_phase.nro_fase:
            
            antecesoresValidos=[]                        
            for antecesor in anteriorVersion.Antecesores:
                item = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==antecesor.id_version_item).\
                one()
                
                if item.ultima_version=='S' and\
                item.estado.nom_estado!='Eliminado':
                    antecesoresValidos.append(item)
                    
            if len(antecesoresValidos) == 0:
                flash(_("No se puede revertir a esta version: El item quedaria huerfano"),'warning')
                redirect('/item/history?id_item=' + str(Globals.current_item.id_item))            
                        
        #Controlar que no queden hijos del item ultima version como
        #huerfanos
           
            ultimoHijos=[]
            anteriorHijos=[]
            try:
                ultimoPadre=DBSession.query(Padre).\
                filter(Padre.id_version_item==ultimaVersion.id_version_item).\
                one()
               
                anteriorPadre=DBSession.query(Padre).\
                filter(Padre.id_version_item==anteriorVersion.id_version_item).\
                one()
            
                for hijo in ultimoPadre.hijos:
                    if hijo.ultima_version=='S' and\
                    hijo.estado.nom_estado!='Eliminado':
                        ultimoHijos.append(hijo.id_version_item)
                       
                for hijo in anteriorPadre.hijos:
                    if hijo.ultima_version=='S' and\
                    hijo.estado.nom_estado!='Eliminado':
                        anteriorHijos.append(hijo.id_version_item)
                        
                for hijo in ultimoHijos:
                    if not hijo in anteriorHijos:
                        
                        has_antecesores=False
                        
                        itemHijo = DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item==hijo).one()
                        
                        for antecesor in itemHijo.Antecesores:
                            item = DBSession.query(VersionItem).\
                                filter(VersionItem.id_version_item==\
                                    antecesor.id_version_item).one()
                                   
                            if item.ultima_version=='S' and\
                            item.estado.nom_estado!='Eliminado':
                                has_antecesores=True
                        
                        if not has_antecesores:
                            flash(_("No se puede revertir a esta version: El Item " + itemHijo.item.nom_item + " quedaria huerfano"),'warning')
                            redirect('/item/history?id_item=' + str(Globals.current_item.id_item))
                               
            except NoResultFound,e:                
                flash(_("No se puede revertir a esta version: Existen Items que podrian quedar huerfanos"),'warning')
                redirect('/item/history?id_item=' + str(Globals.current_item.id_item))
                
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
                      
        # Agregar los antecesores del item viejo        
        for antecesor in anteriorVersion.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
                
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == anteriorVersion.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in anteriorVersion.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == anteriorVersion.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
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
    
        
    @expose('projectmanager.templates.items.revivirItem')
    def revivirItem(self, **kw):
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminado').one()
            
        listItems = DBSession.query(VersionItem).\
            filter(VersionItem.fase == Globals.current_phase).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.estado == eliminado).\
            order_by(VersionItem.id_item).all()
            
        return dict(items=listItems)
    
    @expose()
    def revivir(self, **kw):
        itemRevivir = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == int(kw['id_item'])).one()
        
        fases = DBSession.query(Fase).\
            filter(Fase.id_proyecto==Globals.current_project.id_proyecto)
            
        # Controlar que no se reviva como huerfano 
        if fases.first().nro_fase != Globals.current_phase.nro_fase:
            
            padres=[]
            for padre in itemRevivir.Padres:
                item=DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==\
                padre.id_version_item).one()
                
                if item.ultima_version=='S' and\
                item.estado.nom_estado!='Eliminado':
                    padres.append(padre)
                    
            antecesores=[]
            for antecesor in itemRevivir.Antecesores:
                item=DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==\
                antecesor.id_version_item).one()
                
                if item.ultima_version=='S' and\
                item.estado.nom_estado!='Eliminado':
                    antecesores.append(antecesor)
                    
            if len(padres) <= 0 and len(antecesores) <= 0:
                flash(_("No se puede revivir este Item porque quedaria"
                " huerfano"),'warning')
                redirect('/item/revivirItem')
        
        itemRevivir.ultima_version = 'N'
                        
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).\
                  filter(Usuario.login_name==lg_name).one()
        
        pendiente = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Pendiente').one()
            
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = itemRevivir.item        
        nuevaVersionItem.nro_version_item = itemRevivir.nro_version_item+1
        nuevaVersionItem.estado = pendiente       
        nuevaVersionItem.tipoItem = itemRevivir.tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = itemRevivir.observaciones
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = itemRevivir.peso
        nuevaVersionItem.id_fase = Globals.current_phase.id_fase
                      
        # Agregar los antecesores del item viejo
        for antecesor in itemRevivir.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == itemRevivir.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo       
        for padre in itemRevivir.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == itemRevivir.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == itemRevivir.id_version_item):
                            
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
                      
        redirect('/item/revivirItem')

#***********************************************************************
#**************************** RELACIONES *******************************                

    @expose('projectmanager.templates.items.addRelaciones')
    def addRelaciones(self,**kw):
        itemVersion = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==\
            int(kw['id_version_item'])).one()
            
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==Globals.current_phase.id_fase).one()
		
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
                filter(VersionItem.ultima_version=='S').\
                filter(VersionItem.fase==anterior)
                        
            if items.count() != 0:                 
                antList =[]
                for antecesor in itemVersion.Antecesores:
                    antList.append(antecesor.id_version_item)

                for item in items.all():
                    if not item.id_version_item in antList:
                        options_ancestros.append(item)
            
        estadoConfirmado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Confirmado').one()
            
        options_padres=[]
        list_items = DBSession.query(VersionItem).\
            filter(or_(VersionItem.estado==estado, 
                       VersionItem.estado==estadoConfirmado)).\
            filter(VersionItem.fase==fase).\
            filter(VersionItem.ultima_version=='S').all()
        
        padList=[]
        for padre in itemVersion.Padres:
            padList.append(padre.id_version_item)
                    
        for item in list_items:
            if not item.id_version_item in padList:
                options_padres.append(item)
        
        return dict(padres=options_padres,
                    antecesores=options_ancestros,
                    id_version_item=int(kw['id_version_item']))
        
    @expose()
    def addPadre(self, **kw):
               
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   int(kw['id_version_item'])).one()
        
        padres =[]
        padres.append(int(kw['id_padre']))     
        ciclo = self.controlCiclo(padres,int(kw['id_version_item']))
        if ciclo:
            flash(_("Se ha detectado un ciclo: Favor seleccione otro padre"), 'warning')
            redirect('/item/addRelaciones?id_version_item=' +\
                     str(kw['id_version_item']))
            
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
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo + el nuevo padre
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        try:
            nuevoPadre = DBSession.query(Padre).\
                filter(Padre.id_version_item == int(kw['id_padre'])).\
                one()
            nuevaVersionItem.Padres.append(nuevoPadre)
        except NoResultFound,e:                    
            nuevaVersionItem.Padres.append(Padre(int(kw['id_padre'])))
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == versionItem.id_version_item).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
        
        DBSession.flush()
               
        redirect('/item/addRelaciones?id_version_item=' +\
        str(nuevaVersionItem.id_version_item))
        
    @expose()
    def delPadre(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   Globals.current_item.id_version_item).one()
                         
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
        
        # Agregar los antecesores del item viejo
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo - el padre a eliminar
        # Primero controlar si se puede quitar ese padre
        fases = DBSession.query(Fase).\
        filter(Fase.id_proyecto==Globals.current_project.id_proyecto).\
        order_by(Fase.nro_fase)
        
        padresValidos=[]
        for padre in versionItem.Padres:
            item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==padre.id_version_item).\
            one()
            
            if item.ultima_version=='S' and\
            item.estado.nom_estado!='Eliminado' and\
            item.id_version_item != int(kw['id_version_item']):
                padresValidos.append(padre)
            
        if fases.first().nro_fase != Globals.current_phase.nro_fase and\
        len(padresValidos) <= 0:
            flash(_("No se puede eliminar: El Item podria quedar huerfano"),'warning')
            redirect("/item/atributosItem?id_version="+\
                    str(Globals.current_item.id_version_item) +
                    ";frompage=${'item'}")
            
        for padre in versionItem.Padres:
            if padre.id_version_item != int(kw['id_version_item']):
                nuevaVersionItem.Padres.append(padre)       
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
               
        Globals.current_item = nuevaVersionItem
        
        redirect("/item/atributosItem?id_version="+\
                str(Globals.current_item.id_version_item) +
                ";frompage=item")
    
    @expose()
    def addAntecesor(self, **kw):
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
        
        # Agregar los antecesores del item viejo + el nuevo antecesor
        for antecesor in versionItem.Antecesores:
            nuevaVersionItem.Antecesores.append(antecesor)
            
        try:
            nuevoAntecesor = DBSession.query(Antecesor).\
                filter(Antecesor.id_version_item == int(kw['id_antecesor'])).\
                one()
            nuevaVersionItem.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            nuevaVersionItem.Antecesores.append(Antecesor(int(kw['id_antecesor'])))       
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo + el nuevo padre
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
                   
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == versionItem.id_version_item).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
        
        DBSession.flush()
               
        redirect('/item/addRelaciones?id_version_item=' +\
        str(nuevaVersionItem.id_version_item))
        
    @expose()
    def delAntecesor(self, **kw):
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == \
                   Globals.current_item.id_version_item).one()
                         
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
        
        # Agregar los antecesores del item viejo - el antecesor
        # que queremos eliminar y controlar que no quede huerfano
        padres=[]
        antecesores=[]
        
        for padre in versionItem.Padres:
            item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==padre.id_version_item).\
            one()
            
            if item.ultima_version=='S' and\
            item.estado.nom_estado!='Eliminado':
                padres.append(item)
                
        for antecesor in versionItem.Antecesores:
            item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==antecesor.id_version_item).\
            one()
            
            if item.ultima_version=='S' and\
            item.estado.nom_estado!='Eliminado' and\
            item.id_version_item!=int(kw['id_version_item']):
                antecesores.append(antecesor)
                
        if len(padres) <= 0 and len(antecesores) <= 0:
            flash(_("No se puede eliminar el antecesor: "
                    "El item quedaria Huerfano"),'warning')
            redirect("/item/atributosItem?id_version="+\
                    str(Globals.current_item.id_version_item) +
                    ";frompage=item")
        
        for antecesor in versionItem.Antecesores:
            if antecesor.id_version_item!=int(kw['id_version_item']):
                nuevaVersionItem.Antecesores.append(antecesor)
        
        # Agregar los sucesores del item viejo
        try:
            antecesor = DBSession.query(Antecesor).\
            filter(Antecesor.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoAntecesor = Antecesor(nuevaVersionItem.id_version_item)
           
            sucesores = antecesor.sucesores
            for sucesor in sucesores:
                sucesor.Antecesores.append(nuevoAntecesor)
        except NoResultFound,e:                    
            existe=False
        
        # Agregar los padres del item viejo - el padre a eliminar
        # Primero controlar si se puede quitar ese padre
        for padre in versionItem.Padres:
            nuevaVersionItem.Padres.append(padre)
            
        # Agregar los hijos del item viejo
        try:
            padre = DBSession.query(Padre).\
            filter(Padre.id_version_item == versionItem.id_version_item).\
            one()
            
            nuevoPadre = Padre(nuevaVersionItem.id_version_item)
           
            hijos = padre.hijos
            for hijo in hijos:                
                hijo.Padres.append(nuevoPadre)
        except NoResultFound,e:
            existe=False
            
        for atributo in DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item == int(kw['id_version_item'])).all():
                
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.id_atributo = atributo.id_atributo
            nuevoAtributoItem.id_version_item = nuevaVersionItem.id_version_item        
            nuevoAtributoItem.val_atributo = atributo.val_atributo
            nuevoAtributoItem.id_archivo = atributo.id_archivo
            DBSession.add(nuevoAtributoItem)
               
        Globals.current_item = nuevaVersionItem
        
        redirect("/item/atributosItem?id_version="+\
                str(Globals.current_item.id_version_item) +
                ";frompage=item")
        
#***********************************************************************
#**************************** BUSQUEDA Y OTROS *************************
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
        
    @expose()
    def advertirItemsRelacionados(self, itemVersion):
        lista_items = []
        return lista_items
        
    @expose()
    def controlCiclo(self, padres, itemActual):
        #CONTROL CON GRAFO
        
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado=='Eliminado').one()
            
        AllItems= DBSession.query(VersionItem).\
            filter(VersionItem.estado!= eliminado).\
            filter(VersionItem.id_fase==Globals.current_phase.id_fase).\
            filter(VersionItem.ultima_version=='S').all()            
        
        graph_rel =graph()        
        
        for nodo in AllItems:
            graph_rel.add_node(nodo.id_version_item,[('label',nodo.item.nom_item)])
        
        for nodo in graph_rel.nodes():
            #Padres del nodo item actual                            
            item=DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == nodo).one()
                
            if item.Padres != None:
                for obj in item.Padres:
                    itemPadre = DBSession.query(VersionItem).\
                    filter(VersionItem.id_version_item== obj.id_version_item).\
                    one()
                   
                    if itemPadre.ultima_version=='S' and\
                    (itemPadre.estado.nom_estado!='Eliminado') and\
                    not graph_rel.has_edge((obj.id_version_item,int(nodo))):                        
                       
                        graph_rel.add_edge((itemPadre.id_version_item,int(nodo)))
        
        listaAllItems=[]
        for item in AllItems:
            listaAllItems.append(item.id_version_item)
        
        if not itemActual in listaAllItems:
            graph_rel.add_node(itemActual,[('label','Nuevo'),('color','gold')])
        
        for padre in padres:
            graph_rel.add_edge((int(padre),itemActual))
           
        dot = write(graph_rel)
        gvv = gv.readstring(dot)
        gv.layout(gvv,'dot')
        gv.render(gvv,'png',os.path.abspath("projectmanager/public/images/ciclo.png"))
        
        ciclos = find_cycle(graph_rel)
        if len(ciclos) > 0: 
            return True
        else:           
            #flash(_('No Se han detectado ciclos'),'info')
            return False
            
    @expose()
    def quedanHuerfanos(self, id_version):
        
        itemEliminar = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==id_version).one()
            
        Sucesores=[]
        Hijos=[]
        existeSucesores=True
        existeHijos=True
        huerfanos = True
        #Examinamos todos los sucesores que dependen del item
        try:
            yoAntecesor = DBSession.query(Antecesor).\
                filter(Antecesor.id_version_item==int(id_version)).one()
                
            Sucesores=[]
            
            for sucesor in yoAntecesor.sucesores:
                if sucesor.ultima_version=='S' and\
                sucesor.estado.nom_estado!='Eliminado':
                    Sucesores.append(sucesor)            
                    
            if len(Sucesores) <= 0:
                existeSucesores=False
                huerfanos=False
                                
            for sucesor in Sucesores:
                #Si el sucesor tiene un padre entonces no quedara 
                #huerfano y pasamos al sgte sucesor
                tienePadres = False
                padres = sucesor.Padres
                
                for padre in padres:
                    item=DBSession.query(VersionItem).\
                    filter(VersionItem.id_version_item==padre.id_version_item).one()
                    
                    if item.estado.nom_estado != 'Eliminado' and\
                    item.ultima_version=='S':
                        tienePadres = True
                
                if sucesor.ultima_version=='S' and\
                sucesor.estado.nom_estado != 'Eliminado' and\
                not tienePadres:
                    huerfanos=True
                    antecesores = sucesor.Antecesores
                    
                    for antecesor in antecesores:
                        item = DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item==\
                               antecesor.id_version_item).one()                    
                    
                        if item.estado.nom_estado != 'Eliminado' and\
                        item.ultima_version == 'S' and\
                        item.id_item != int(itemEliminar.id_item):                        
                            # Si encuentra al menos otro item antecesor, 
                            # entonces se puede eliminar
                            huerfanos = False     
            
        except NoResultFound,e:                    
            existeSucesores= False
                
        if existeSucesores and huerfanos:
            return True
                          
        #Si el hijo esta en la primera fase entonces no controlar 
        #antecesores, solo controlar si estamos en otras fases
                
        fase_list = DBSession.query(Fase).\
        filter(Fase.id_proyecto == Globals.current_project.id_proyecto).\
        order_by(Fase.nro_fase)
                    
        if fase_list.first().nro_fase != Globals.current_phase.nro_fase:
            
            # Examinamos todos los hijos que dependen del item        
            try:
                yoPadre = DBSession.query(Padre).\
                    filter(Padre.id_version_item==int(id_version)).one()
            
                huerfanos=True    
                Hijos= yoPadre.hijos
                        
                for hijo in Hijos:                
                    #Si el hijo tiene otro antecesor entonces no quedara 
                    #huerfano y pasamos al sgte hijo
                    tieneAntecesores = False
                    antecesores = hijo.Antecesores
                
                    for antecesor in antecesores:
                        item=DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item==antecesor.id_version_item).one()
                    
                        if item.estado.nom_estado != 'Eliminado':
                            tieneAntecesores = True
                        
                    if hijo.ultima_version=='S' and\
                    hijo.estado.nom_estado != 'Eliminado' and\
                    not tieneAntecesores:
                
                        padres = hijo.Padres
                
                        for padre in padres:
                            item = DBSession.query(VersionItem).\
                            filter(VersionItem.id_version_item==padre.id_version_item).\
                            one()                    
                    
                            if item.estado.nom_estado != 'Eliminado' and\
                            item.ultima_version == 'S' and\
                            item.id_item != int(itemEliminar.id_item):                        
                                # Si encuentra al menos otro item padre, 
                                # entonces se puede eliminar
                                huerfanos=False
            except NoResultFound,e:                    
                existeHijos=False
                        
        if existeHijos and huerfanos:    
            return True
        else:
            return False
      
    @expose()
    def graficarRelaciones(self, itemVersion):
        unaVersionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == itemVersion).one()
        eliminado = DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Eliminado').one()
            
        graph_rel = digraph()
                       
        graph_rel.add_node(unaVersionItem.id_version_item,\
                           [('label',unaVersionItem.item.nom_item),\
                           ('color','gold')])
                           
        #Recuperar Nombre de los Padres de esta Version de Item        
        for padre in unaVersionItem.Padres:            
            unPadre = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item == padre.id_version_item).\
                one()            
            
            if unPadre.ultima_version == 'S' and\
            unPadre.id_estado != eliminado.id_estado:                
                graph_rel.add_node(unPadre.id_version_item,
                                   [('label',unPadre.item.nom_item)])
                graph_rel.add_edge((unPadre.id_version_item,
                                   unaVersionItem.id_version_item),
                                   label='Padre')
            
        #Recuperar Nombre de los Hijos de esta Version de Item        
        try:
            yoPadre = DBSession.query(Padre).\
                filter(Padre.id_version_item==unaVersionItem.id_version_item).one()
                
            Hijos = DBSession.query(VersionItem).\
            filter(VersionItem.Padres.contains(yoPadre)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
            
            for hijo in Hijos:
                graph_rel.add_node(hijo.id_version_item,
                                   [('label',hijo.item.nom_item)])
                graph_rel.add_edge((unaVersionItem.id_version_item,
                                    hijo.id_version_item),
                                    label='Hijo')
                                    
        except NoResultFound,e:                    
            existe=False
            
        #Recuperar Nombre de los Antecesores de esta Version de Item
        for antecesor in unaVersionItem.Antecesores:
            unAntecesor = DBSession.query(VersionItem).\
                filter(VersionItem.id_version_item==antecesor.id_version_item).\
                one()
            if unAntecesor.ultima_version == 'S' and\
            unAntecesor.id_estado != eliminado.id_estado:
                graph_rel.add_node(unAntecesor.id_version_item,
                                  [('label',unAntecesor.item.nom_item),
                                  ('shape','box')])
                graph_rel.add_edge((unAntecesor.id_version_item,
                                    unaVersionItem.id_version_item),
                                    label='Antecesor')
                            
        #Recuperar Nombre de los Sucesores de esta Version de Item
        try:
            yoAntecesor = DBSession.query(Antecesor).\
                filter(Antecesor.id_version_item==unaVersionItem.id_version_item).one()
                
            Sucesores= DBSession.query(VersionItem).\
            filter(VersionItem.Antecesores.contains(yoAntecesor)).\
            filter(VersionItem.ultima_version == 'S').\
            filter(VersionItem.id_estado!=eliminado.id_estado).all()
            
            for sucesor in Sucesores:
                graph_rel.add_node(sucesor.id_version_item,
                                  [('label',sucesor.item.nom_item),
                                  ('shape','box')])
                graph_rel.add_edge((unaVersionItem.id_version_item,
                                    sucesor.id_version_item),
                                    label='Sucesor')
                                    
        except NoResultFound,e:                    
            existe=False
            
        dot = write(graph_rel)        
        gvv = gv.readstring(dot)                        
        gv.layout(gvv,'dot')
        gv.render(gvv,'png',os.path.abspath("projectmanager/public/images/esquemaRelaciones.png"))
        
    @expose('projectmanager.templates.items.calculoImpacto')
    def calcularImpacto(self,**kw):
     
        itemVersion = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == kw['idVersion']).\
            one()
        
        itemVersion.initGraph(itemVersion)
              
        izquierda=[]
        derecha=[]
        abajo=[]
        sumaIzq = 0
        sumaDer = 0
        sumaAbj = 0
        total = 0
                
        izquierda.extend(itemVersion.getRelacionesIzq(itemVersion.id_version_item))
        hijos=itemVersion.getHijos(itemVersion.id_version_item)        
        abajo.extend(itemVersion.getHijosNietos(hijos))
        derecha.extend(itemVersion.getRelacionesDer(itemVersion.id_version_item))
                
        for item in izquierda:                    
            sumaIzq = sumaIzq + item.peso
            
        for item in derecha:
            sumaDer = sumaDer + item.peso
    
        for item in abajo:
            sumaAbj = sumaAbj + item.peso
            
        total = itemVersion.peso + sumaIzq + sumaDer + sumaAbj
        
        itemVersion.drawGraph()
                        
        return dict(impactoIzq=sumaIzq,
                    impactoDer=sumaDer,
                    impactoAbj=sumaAbj,
                    impactoTot=total)
        
