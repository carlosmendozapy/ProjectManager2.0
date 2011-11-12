from repoze.what.predicates import Predicate
from repoze.what.predicates import has_permission
from sqlalchemy.orm.exc import NoResultFound

from projectmanager.model import DBSession, metadata
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import Rol
from projectmanager.model.roles import RolProyectoUsuario
from projectmanager.model.roles import RolFaseUsuario
from projectmanager.model.roles import Permisos
from projectmanager.model.roles import Privilegios
from projectmanager.model.roles import EntidadSistema
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import Fase
from tg import expose, flash, require, url, request, redirect

class has_rol_proyecto(Predicate):
    """Se utiliza para saber si el usuario actualmente logueado
    tiene un rol determinado en el proyecto elegido"""
    message = 'El usuario actual no posee el rol correspondiente'
    
    def __init__(self, rol, idProyecto, **kwargs):
        self.rol = DBSession.query(Rol).filter(Rol.nom_rol==rol).one()
        self.proyecto = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==int(idProyecto)).one()
        self.usuario = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()          
        super(has_rol_proyecto, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        posee_rol=True
        try:
            list_roles=DBSession.query(RolProyectoUsuario).\
                filter(RolProyectoUsuario.usuarios==self.usuario).\
                filter(RolProyectoUsuario.proyecto==self.proyecto).\
                filter(RolProyectoUsuario.roles==self.rol).one()
        except NoResultFound,e:
            posee_rol=False
            
        if posee_rol == False:
            '''No posee el rol'''
            self.unmet()

class is_type(Predicate):
    """Se utiliza para saber si un usuario es del tipo
    Administrador o Usuario"""
    message = 'El usuario actual no es del tipo'
    
    def __init__(self, tipo, **kwargs):
        self.tipo = tipo
        super(is_type, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        if not has_permission(self.tipo):
            self.unmet()       

class has_ProPriv(Predicate):
    """Se utiliza para saber si un usuario posee un cierto privilegio
    sobre una entidad en un proyecto"""
    message = 'El usuario actual no posee el privilegio adecuado para esta entidad'
    
    def __init__(self, nomPriv,nomEnt,idProy, **kwargs):
        self.privilegio = DBSession.query(Privilegios).\
            filter(Privilegios.nom_privilegio==nomPriv).one()
        self.entidad = DBSession.query(EntidadSistema).\
            filter(EntidadSistema.nom_entidad==nomEnt).one()
        self.proyecto = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==idProy).one()
            
        super(has_ProPriv, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):        
        user = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()
               
        roles = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.proyecto==self.proyecto).\
            filter(RolProyectoUsuario.usuarios==user)
        
        has = False
        for rol in roles.all():
            has_priv = DBSession.query(Permisos).\
                filter(Permisos.entidad==self.entidad).\
                filter(Permisos.privilegios.contains(self.privilegio))
                
            if has_priv.count() > 0:
                has = True
                break
            
        if has == False:
            '''No posee el privilegio'''
            self.unmet() 
            
class has_FasePriv(Predicate):
    """Se utiliza para saber si un usuario posee un cierto privilegio
    sobre una entidad en una Fase"""
    message = 'El usuario actual no posee el privilegio adecuado para esta entidad'
    
    def __init__(self, nomPriv,nomEnt,idFase, **kwargs):
        self.privilegio = DBSession.query(Privilegios).\
            filter(Privilegios.nom_privilegio==nomPriv).one()
        self.entidad = DBSession.query(EntidadSistema).\
            filter(EntidadSistema.nom_entidad==nomEnt).one()
        self.fase = DBSession.query(Fase).\
            filter(Fase.id_fase==idFase).one()
            
        super(has_FasePriv, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):        
        user = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()
               
        roles = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.fase==self.fase).\
            filter(RolFaseUsuario.usuarios==user)
        
        has = False
        for rol in roles.all():
            has_priv = DBSession.query(Permisos).\
                filter(Permisos.entidad==self.entidad).\
                filter(Permisos.privilegios.contains(self.privilegio))
                
            if has_priv.count() > 0:
                has = True
                break
            
        if has == False:
            '''No posee el privilegio'''
            self.unmet()

class has_AnyProPriv(Predicate):
    """Se utiliza para saber si un usuario posee cualquier privilegio
    sobre una entidad en un proyecto"""
    message = 'El usuario actual no posee el privilegio adecuado para esta entidad'
    
    def __init__(self, nomEnt,idProy, **kwargs):        
        self.entidad = DBSession.query(EntidadSistema).\
            filter(EntidadSistema.nom_entidad==nomEnt).one()
        self.proyecto = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==idProy).one()
            
        super(has_AnyProPriv, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):        
        user = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()
               
        roles = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.proyecto==self.proyecto).\
            filter(RolProyectoUsuario.usuarios==user)
        
        has = False
        for rol in roles.all():
            unRol=DBSession.query(Rol).\
            filter(Rol.id_rol==rol.id_rol_proyecto).one()
            
            misPermisos = unRol.permisos                
            
            for permiso in misPermisos:
                entidad = DBSession.query(EntidadSistema).\
                filter(EntidadSistema.id_entidad==permiso.id_entidad_sistema).one()
                
                if entidad.nom_entidad == self.entidad.nom_entidad:
                    has=True
                    break
                
            if has:
                break 
            
        if has == False:
            '''No posee el privilegio'''
            self.unmet() 
            
class has_AnyFasePriv(Predicate):
    """Se utiliza para saber si un usuario posee cualquier privilegio
    sobre una entidad en una fase"""
    message = 'El usuario actual no posee el privilegio adecuado para esta entidad'
    
    def __init__(self, nomEnt,idFase, **kwargs):
        
        self.entidad = DBSession.query(EntidadSistema).\
            filter(EntidadSistema.nom_entidad==nomEnt).one()
        self.fase = DBSession.query(Fase).\
            filter(Fase.id_fase==idFase).one()
            
        super(has_AnyFasePriv, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):        
        user = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()
               
        roles = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.fase==self.fase).\
            filter(RolFaseUsuario.usuarios==user)
        
        has = False
        for rol in roles.all():
            unRol=DBSession.query(Rol).\
            filter(Rol.id_rol==rol.id_rol).one()
            
            misPermisos = unRol.permisos                
            
            for permiso in misPermisos:
                entidad = DBSession.query(EntidadSistema).\
                filter(EntidadSistema.id_entidad==permiso.id_entidad_sistema).one()
                
                if entidad.nom_entidad == self.entidad.nom_entidad:
                    has=True
                    break
                
            if has:
                break 
                           
        if has == False:
            '''No posee el privilegio'''
            self.unmet()
