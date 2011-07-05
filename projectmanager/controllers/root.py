# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg.i18n import set_lang
from catwalk.tg2 import Catwalk
from repoze.what import predicates
from tg import tmpl_context
from sqlalchemy.orm.exc import NoResultFound

from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.controllers.error import ErrorController
from projectmanager import model
from projectmanager.controllers.secure import SecureController
from projectmanager.controllers.admin import AdminController
from projectmanager.controllers.proyecto import ProyectoController
from projectmanager.controllers.usuario import UsuarioController
from projectmanager.controllers.fase import FaseController
from projectmanager.controllers.rol import RolController
from projectmanager.controllers.permiso import PermisoController
from projectmanager.controllers.item import ItemController
from projectmanager.controllers.lineaBase import lineabaseController
from projectmanager.controllers.itemLineaBase import itemLineaBaseController
from projectmanager.controllers.cambiarEstadoPendiente import cambiarEstadoPendienteController
from projectmanager.controllers.file_upload import FileUploadController

from projectmanager.model import Usuario

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the ProjectManager application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    secc = SecureController()    
   
    admin = AdminController()
    
    proyecto = ProyectoController()
    
    usuario = UsuarioController()
    
    fase = FaseController()
    
    roles = RolController()
    
    item = ItemController()
    
    lineaBase = lineabaseController()
    
    itemLineaBase = itemLineaBaseController()
    
    cambiarEstadoPendiente = cambiarEstadoPendienteController()
        
    error = ErrorController()
    
    file_upload = FileUploadController()   

    userid = ""
    
    permisos = PermisoController()
        
    @expose('projectmanager.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')        

    @expose('projectmanager.templates.index')
    @require(predicates.has_permission('admin', msg=l_('Solo para Administradores')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('projectmanager.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Usuario y/o Password Incorrectos'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = DBSession.query(Usuario).filter(Usuario.login_name==request.identity['repoze.who.userid']).one()
        flash(_('Bienvenido, %s!') % userid.nom_usuario)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('Lo esperamos para su proxima sesion!'))
        redirect('/index')    
