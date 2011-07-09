# -*- coding: utf-8 -*-
"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
#metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    DBSession.configure(bind=engine)
    # If you are using reflection to introspect your database and create
    # table objects for you, your tables must be defined and mapped inside
    # the init_model function, so that the engine is available if you
    # use the model outside tg2, you need to make sure this is called before
    # you use the model.

    #
    # See the following example:

    #global t_reflected

    #t_reflected = Table("Reflected", metadata,
    #    autoload=True, autoload_with=engine)

    #mapper(Reflected, t_reflected)

# Import your model modules here.
from projectmanager.model.auth import User
from projectmanager.model.auth import Group
from projectmanager.model.auth import Permission
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Rol, TipoRol 
from projectmanager.model.roles import TipoRol 
from projectmanager.model.roles import UsuarioRolSistema
from projectmanager.model.roles import RolPermisos 
from projectmanager.model.roles import Permisos
from projectmanager.model.roles import Privilegios
from projectmanager.model.roles import PrivilegiosPermisos
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import EntidadSistema
from projectmanager.model.roles import RolProyectoUsuario
from projectmanager.model.roles import RolFaseUsuario
from projectmanager.model.entities import TipoRelacion
from projectmanager.model.entities import Item
from projectmanager.model.entities import Estado
from projectmanager.model.entities import TipoDatoAtributo
from projectmanager.model.entities import TipoItem
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import RelacionItem
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import AtributoArchivo
from projectmanager.model.entities import Padre
from projectmanager.model.entities import Antecesor
from projectmanager.model.configuracion import LineaBase, ItemLineaBase, NroLineaBase

