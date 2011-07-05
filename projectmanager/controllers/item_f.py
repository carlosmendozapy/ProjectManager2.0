
# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash, tmpl_context, redirect, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous

#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from sqlalchemy.sql import exists
from projectmanager.lib.base import BaseController
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import Fase
from projectmanager.model.entities import Estado
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Item
from projectmanager.controllers.lineaBase import lineabaseController


__all__ = ['AdminController']


class ItemController(BaseController):
    """Controlador de la Pagina de Administración del Sistema"""
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')    
    lineaBase = lineabaseController()

    @expose('projectmanager.templates.items.items')
    def itemsFase(self,**kw):
        #ACA VA LO DE CRISTIHIAN
        return()         
    
    
    
    
    
    