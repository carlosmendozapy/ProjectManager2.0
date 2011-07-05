# -*- coding: utf-8 -*-
"""Sample controller module"""

# turbogears imports
from tg import expose, tmpl_context
from tg import redirect, validate, flash

# third party imports
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from repoze.what.predicates import has_permission

# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.model.entities import Item
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import Estado
from projectmanager.model.entities import TipoItem
from projectmanager.model.roles import Usuario

from projectmanager.widgets.new_itemForm import create_new_item
#from projectmanager.widgets.edit_itemForm import edit_item


class ItemController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    allow_only = has_permission('admin',
                                msg=l_('Solo para personas con permisos de  "Administracion"'))
               
    idFaseItem = 0
                 
    @expose('projectmanager.templates.items')
    def index(self):
        return dict(page='index')
        
    @expose('projectmanager.templates.items')
    def adminItem(self, faseid):
        """Let the user know that this action is protected too."""        
        idFaseItem = faseid
        items = DBSession.query(VersionItem).all()
        return dict(page='Administrar Items', items=items)
        
    @expose('projectmanager.templates.newItem')
    def newItem(self):
        tmpl_context.form = create_new_item
        return dict(page='Nuevo Item')    	        
    
    @expose()
    def saveItem(self, **kw):
        unItem = Item()
        unItem.nom_item = kw['nomItem']
        #aProject.des_proyecto = kw['descripcion']
        DBSession.add(unItem)

	unaVersionItem = VersionItem()
        unaVersionItem.item = unItem

        unEstado = DBSession.query(Estado).filter_by(id_estado=1).one()
        unTipoItem = DBSession.query(TipoItem).filter_by(id_tipo_item=1).one()
        unUsuario = DBSession.query(Usuario).filter_by(id_usuario=1).one()

        unaVersionItem.estado = unEstado
        unaVersionItem.tipoItem = unTipoItem
        unaVersionItem.usuarioModifico = unUsuario
        unaVersionItem.fecha = "10/06/2011"
 	unaVersionItem.observaciones = kw['observaciones']
 	#unaVersionItem.peso = kw['peso']

        DBSession.add(unaVersionItem)  
        
        for atributo in DBSession.query(Atributo).filter_by(tipoItem=unTipoItem):
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.atributo = atributo
            nuevoAtributoItem.versionItem = unaVersionItem        
            nuevoAtributoItem.val_atributo = atributo.val_default
            DBSession.add(nuevoAtributoItem)   
      
        flash(_("Se ha creado un nuevo Item: %s") %kw['itemName'],'info')
        redirect("adminItem")

            

	
    
    @expose('projectmanager.templates.editProject')
    def editProject(self, **kw):        
        tmpl_context.form = edit_project
        uProject = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==kw['id']).one()                
        return dict(proyecto=uProject)    
    
    @expose()
    def updateProject(self, **kw):
        aProject = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==kw['id_project']).one()
        aProject.nom_proyecto = kw['projectName']
        aProject.des_proyecto = kw['descripcion']
        #DBSession.add(aProject)
        redirect("adminProject")
        
    @expose()
    def delete(self, **kw):               
        dProject = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==kw['id']).one()
        DBSession.delete(dProject)
        redirect("adminProject")
    
    @expose('projectmanager.templates.items')
    def search(sefl, **kw):
        word = '%'+kw['key']+'%'        
        projects = DBSession.query(Proyecto).filter(Proyecto.nom_proyecto.like(word)).order_by(Proyecto.nom_proyecto)
        return dict(page='Administrar Items', items=items)
