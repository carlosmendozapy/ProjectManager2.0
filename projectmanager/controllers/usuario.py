"""Sample controller with all its actions protected."""
from tg import expose, flash, tmpl_context, redirect, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous

#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

from projectmanager.lib.base import BaseController
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import Rol
from projectmanager.model.auth import Group, Permission
from projectmanager.controllers.proyecto import ProyectoController

from projectmanager.widgets.new_userForm import create_new_user
from projectmanager.widgets.edit_userForm import edit_user
from projectmanager.widgets.rol_toUserForm import asignRol_to_user

__all__ = ['UsuarioController']


class UsuarioController(BaseController):
    """Controlador de la Pagina de Administracion del Sistema"""
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
               
    @expose('projectmanager.templates.usuarios.usuarios')
    def adminUsers(self):
        """Let the user know that this action is protected too."""        
        users = DBSession.query(Usuario).order_by(Usuario.nom_usuario)
        return dict(page='Administrar Usuarios', usuarios = users)
       
    @expose('projectmanager.templates.usuarios.newUser')
    def newUser(self, **kw):
        tmpl_context.form = create_new_user
        return dict(page='Nuevo Usuario')
        
    @validate(create_new_user, error_handler=newUser)
    @expose()
    def saveUser(self, **kw):
        """Create a movie object and save it to the database."""
        user = Usuario()
        user.nom_usuario = kw['userName']
        user.login_name = kw['loginName']
        user._set_password(kw['password'])
        type = int(kw['userType'])        
        DBSession.add(user)
                
        if type == 1:            
            grupo = DBSession.query(Group).filter(Group.group_name=='admin').one()
            grupo.users.append(user)                                    
        else:
            grupo = DBSession.query(Group).filter(Group.group_name=='user').one()
            grupo.users.append(user)                                    
                
        DBSession.flush()    
            
        
        #flash("El Usuario ha sido registrado satisfactoriamente.")
        redirect("adminUsers")                  
    
    @expose('projectmanager.templates.usuarios.updateUser')
    def editUser(self, **kw):   
        tmpl_context.form = edit_user 
        Globals.id_user_to_edit = kw['id']                  
        return dict(aUser=DBSession.query(Usuario).filter(Usuario.id_usuario==kw['id']).one())
    
    @validate(edit_user, error_handler=editUser)        
    @expose()
    def updateUser(self, **kw):       
        user = DBSession.query(Usuario).filter(Usuario.id_usuario==kw['id']).one()
        user.nom_usuario = kw['userName']
        user.login_name = kw['loginName']                                
        redirect("adminUsers")
        
        
    @expose()
    def delete(self, **kw):                
        user = DBSession.query(Usuario).filter(Usuario.id_usuario==kw['id']).one()
        DBSession.delete(user)
        redirect("adminUsers")
        
    @expose('projectmanager.templates.usuarios.asignRol')
    def asignRol(self, **kw):
        tmpl_context.form = asignRol_to_user
        options = DBSession.query(Rol.id_rol,Rol.nom_rol)
        return dict(rol_options=options,idUsuario=int(kw['id']))
    
    @expose('projectmanager.templates.usuarios.usuarios')
    def search(self, **kw):
        word = '%'+kw['key']+'%'        
        usuarios_lista = DBSession.query(Usuario).filter(Usuario.nom_usuario.like(word)).\
                                            order_by(Usuario.nom_usuario)
        return dict(page='Administrar Proyectos', usuarios = usuarios_lista)
