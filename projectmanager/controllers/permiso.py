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
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.roles import Permisos
from projectmanager.model.roles import Rol
from projectmanager.model.roles import EntidadSistema
from projectmanager.model.roles import Privilegios


#project widgets forms
from projectmanager.widgets.new_permisoForm import create_new_permission
from projectmanager.widgets.add_privilegioForm import add_privilegios


class PermisoController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    
    @expose('projectmanager.templates.permisos.permisos')
    def index(self, **kw):
        Globals.current_rol = DBSession.query(Rol).\
                                filter(Rol.id_rol==int(kw['id_rol'])).one()                
        permisos_lista = DBSession.query(Permisos).\
                            filter(Permisos.rol.contains(Globals.current_rol))
        
                
        return dict(permisos = permisos_lista)

    @expose('projectmanager.templates.permisos.newPermiso')
    def newPermission(self, **kw):
        tmpl_context.form = create_new_permission
        return dict(page='newPermision')
    
    @validate(create_new_permission,error_handler=newPermission)
    @expose()
    def savePermiso(self, **kw):
        new_permiso = Permisos()
        new_permiso.entidad = DBSession.query(EntidadSistema).\
                filter(EntidadSistema.id_entidad==int(kw['entidad'])).one()
        
        if kw['privilegios'] != None:
            for id_privilegio in kw['privilegios']:
                privilegio = DBSession.query(Privilegios).\
                                filter(Privilegios.id_privilegio==\
                                       int(id_privilegio)).one()
                new_permiso.privilegios.append(privilegio)
        
        rol = DBSession.query(Rol).\
                        filter(Rol.id_rol == \
                               Globals.current_rol.id_rol).one()
        
        rol.permisos.append(new_permiso)
        
        redirect('index?id_rol='+str(Globals.current_rol.id_rol))
    
    @expose('projectmanager.templates.permisos.addPrivilegio')
    def addPrivilegio(self, **kw):
        permiso = DBSession.query(Permisos).\
                filter(Permisos.id_permiso==int(kw['id_permiso'])).one()
                
        opciones = DBSession.query(Privilegios.id_privilegio,\
                                   Privilegios.nom_privilegio).\
                    filter(~Privilegios.permiso.contains(permiso))
        
        tmpl_context.form = add_privilegios
                    
        return dict(option_list=opciones, idPermiso=int(kw['id_permiso']))
    
    @validate(add_privilegios,error_handler=addPrivilegio)    
    @expose()
    def appendPrivilegio(self, **kw):
        permiso = DBSession.query(Permisos).\
                filter(Permisos.id_permiso==int(kw['id_permiso'])).\
                one()
              
        if kw['privilegios'] != None:
            for id_privilegio in kw['privilegios']:
                privilegio = DBSession.query(Privilegios).\
                                filter(Privilegios.id_privilegio==\
                                       int(id_privilegio)).one()
                permiso.privilegios.append(privilegio)
         
        redirect('index?id_rol='+str(Globals.current_rol.id_rol))
    
    @expose()
    def delPermiso(self, **kw):
        permiso = DBSession.query(Permisos).\
                filter(Permisos.id_permiso==int(kw['id_permiso'])).one()
        DBSession.delete(permiso)
        redirect('index?id_rol=' + str(Globals.current_rol.id_rol))
        
    @expose()
    def delPrivilegio(self, **kw):
        permiso=DBSession.query(Permisos).\
                filter(Permisos.id_permiso==int(kw['id_permiso'])).one()
                    
        privilegio=DBSession.query(Privilegios).\
                filter(Privilegios.id_privilegio==\
                       int(kw['id_privilegio'])).one()
                          
        permiso.privilegios.remove(privilegio)
        
        redirect('index?id_rol='+str(Globals.current_rol.id_rol))
                
        
