# -*- coding: utf-8 -*-

"""The application's Globals object"""

__all__ = ['Globals']

from projectmanager import model
from projectmanager.model.entities import Estado
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Rol
from projectmanager.model import DBSession, metadata

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """
    
    current_rol = Rol() 
    current_project = Proyecto()
    current_phase = Fase()
    lista_actualizados = []
    lista_no_actualizados = []
    lista_version_anterior = []
    
    id_user_to_edit = 0
    nro_fase_to_edit = 0
     
    def __init__(self):
        """Do nothing, by default."""
        pass
