# -*- coding: utf-8 -*-
"""Sample controller module"""

# turbogears imports
from tg import expose, tmpl_context
from tg import redirect, validate, flash

# third party imports
from pylons.i18n import ugettext as _
from repoze.what import predicates
from repoze.what.predicates import not_anonymous

# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.model.roles import Rol
from projectmanager.model.roles import TipoRol
from projectmanager.model.roles import RolProyectoUsuario
from projectmanager.model.roles import RolFaseUsuario

from projectmanager.controllers.permiso import PermisoController

#project widgets forms
from projectmanager.widgets.new_rolForm import create_new_rol
from projectmanager.widgets.edit_rolForm import edit_rol

class RolController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    
    permisos = PermisoController()
    
    @expose('projectmanager.templates.roles.index')
    def index(self):        
        roles_lista = DBSession.query(Rol)
        
        if roles_lista.count() == 0:
            flash(_('No se han encontrado Roles'),'info')
        return dict(roles = roles_lista)
        
    @expose('projectmanager.templates.roles.newRol')
    def newRol(self, **kw):
        """
        Muestra el formulario para crear un nuevo rol
        """
        options = DBSession.query(TipoRol.id_tipo, TipoRol.nom_tipo_rol)
        tmpl_context.form = create_new_rol
        return dict(page='Nuevo Proyecto', type_options = options) 
    
    @validate(create_new_rol, error_handler=newRol)
    @expose()
    def saveRol(self, **kw):
        """Crea un objeto Rol y lo guarda en la base de datos. Los 
        datos son proveídos desde el formulario de crear rol"""
        
        rol = Rol()
        tipo_rol = DBSession.query(TipoRol).filter(TipoRol.id_tipo==kw['tipoRol']).one()
        rol.tipoRol = tipo_rol
        rol.nom_rol = kw['nombreRol']
        rol.des_rol = kw['descripcion']
        DBSession.add(rol)
        redirect("index")    
    
    @expose('projectmanager.templates.roles.editRol')
    def editRol(self, **kw):
        """ Edita los datos del rol seleccionado"""
        aRol = DBSession.query(Rol).filter(Rol.id_rol==kw['id']).one()
        options = DBSession.query(TipoRol.id_tipo, TipoRol.nom_tipo_rol)
        tmpl_context.form = edit_rol
        return dict(rol = aRol, type_options = options)
    
    @validate(edit_rol, error_handler=editRol)
    @expose()
    def updateRol(self, **kw):
        """Obtiene el objeto Rol de la base de datos. Se modifican
        los datos que son proveídos desde el formulario de editar rol
        y se guardan las modificaciones en la Base de Datos"""
        
        rol = DBSession.query(Rol).filter(Rol.id_rol==kw['idRol']).one()
        tipo_rol = DBSession.query(TipoRol).filter(TipoRol.id_tipo==kw['tipoRol']).one()
        rol.tipoRol = tipo_rol
        rol.nom_rol = kw['nombreRol']
        rol.des_rol = kw['descripcion']        
        redirect("index")   
    
    @expose()
    def deleteRol(self, **kw):
               
        rol = DBSession.query(Rol).filter(Rol.id_rol==kw['id']).one()
        
        rol_proyecto = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.roles==rol)
            
        rol_proyecto.delete()
        
        rol_fase = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.roles==rol)
            
        rol_fase.delete()
            
        DBSession.delete(rol);
        
        
        redirect('index')
    
    @expose('projectmanager.templates.roles.index')
    def search(self, **kw):
        word = '%'+kw['key']+'%'        
        roles_lista = DBSession.query(Rol).filter(Rol.nom_rol.like(word))
        
        if roles_lista.count() == 0:
            flash(_('No se han encontrado Roles'),'info')
        return dict(roles = roles_lista)
