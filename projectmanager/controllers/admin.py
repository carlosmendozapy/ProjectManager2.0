"""HOLA"""
# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata

__all__ = ['AdminController']


class AdminController(BaseController):
    """Controlador de la Pagina de Administración del Sistema"""
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('admin',msg='Debe Ingresar al Sistema para ver esta pagina') 
            
    @expose('projectmanager.templates.admin')
    def index(self):
        """Let the user know that's visiting a protected controller."""        
        return dict(page='index')
            
   
    
