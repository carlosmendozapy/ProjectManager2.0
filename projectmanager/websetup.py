# -*- coding: utf-8 -*-
"""Setup the ProjectManager application"""

import logging

import transaction
from tg import config

from projectmanager.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup projectmanager here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from projectmanager import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
   
    ''' VALORES INICIALES '''    
   
    group = model.Group()
    group.group_name = u'user'
    group.display_name = u'Usuario'

    model.DBSession.add(group)

    permission = model.Permission()
    permission.permission_name = u'user'
    permission.description = u'Permisos de usuario de Proyecto'
    permission.groups.append(group)

    model.DBSession.add(permission)
    
    model.DBSession.flush()
       
    admin = model.Usuario()
    admin.login_name = u'admin'
    admin.nom_usuario = u'Administrador'    
    admin.password = u'admin'
        
    model.DBSession.add(admin)
    
    groupA = model.Group()
    groupA.group_name = u'admin'
    groupA.display_name = u'Administrador'
    groupA.users.append(admin)

    model.DBSession.add(groupA)

    permissionA = model.Permission()
    permissionA.permission_name = u'admin'
    permissionA.description = u'Permisos de Administrador de Sistema'
    permissionA.groups.append(groupA)
        
    model.DBSession.flush()
    
    ''' Entidades del Sistema'''
    
    #PROYECTO
    proyecto = model.EntidadSistema()
    proyecto.nom_entidad = u'Proyecto'
    proyecto.des_entidad = u'Identifica a los proyectos'
    model.DBSession.add(proyecto)
    
    #FASE
    fase = model.EntidadSistema()
    fase.nom_entidad = u'Fase'
    fase.des_entidad = u'Identifica a las Fases de los proyectos'
    model.DBSession.add(fase)
    
    #ITEM
    item = model.EntidadSistema()
    item.nom_entidad = u'Item'
    item.des_entidad = u'Identifica a los Items de los proyectos'
    model.DBSession.add(item)
    
    #ESTADOS DE ITEM
    estadosItem = model.EntidadSistema()
    estadosItem.nom_entidad = u'Estados de Item'
    estadosItem.des_entidad = u'Indentifica a los estados de los items'
    model.DBSession.add(estadosItem)
    
    #LINEA BASE
    lb = model.EntidadSistema()
    lb.nom_entidad = u'Linea Base'
    lb.des_entidad = u'Identifica a las Linea Base de las fases'
    model.DBSession.add(lb)
    
    #USUARIO
    usuario = model.EntidadSistema()
    usuario.nom_entidad = u'Usuario'
    usuario.des_entidad = u'Identifica a los usuarios registrados en el Sistema'
    model.DBSession.add(usuario)
    
    #ROL
    rol = model.EntidadSistema()
    rol.nom_entidad = u'Rol'
    rol.des_entidad = u'Identifica a los roles del sistema o proyecto'
    model.DBSession.add(rol)   
    
    #TIPO DE ITEM
    tipoItem = model.EntidadSistema()
    tipoItem.nom_entidad = u'Tipo de Item'
    tipoItem.des_entidad = u'Identifica a los Tipos de Items del Sistema'
    model.DBSession.add(tipoItem)
    
    #ATRIBUTO
    atributo = model.EntidadSistema()
    atributo.nom_entidad = u'Atributo de Item'
    atributo.des_entidad = u'Identifica a los atributos que componen a un item o tipo de item'
    model.DBSession.add(atributo)
    
    model.DBSession.flush()
    
     #TIPO_RELACION
    model.DBSession.add_all([
                            model.TipoRelacion(u'PADRE'),
                            model.TipoRelacion(u'HIJO'),
                            model.TipoRelacion(u'ANTECESOR'),
                            model.TipoRelacion(u'SUCESOR')                                                     
                            ])
    model.DBSession.flush()
    '''Tipo de Datos Atributo'''
    model.DBSession.add_all([
                             model.TipoDatoAtributo(u'texto'),
							 model.TipoDatoAtributo(u'numerico'),
							 model.TipoDatoAtributo(u'fecha'),
							 model.TipoDatoAtributo(u'archivo')	
							])
    '''Estados'''
    
    model.DBSession.add_all([
                            model.Estado(u'Inicial'),
                            model.Estado(u'En Desarrollo'),
                            model.Estado(u'Con LB Parciales'),
                            model.Estado(u'Finalizado'),
                            model.Estado(u'No Iniciado'),
                            model.Estado(u'Iniciado'),
                            model.Estado(u'En Modificacion'),
                            model.Estado(u'Pendiente'),
                            model.Estado(u'Aprobado'),
                            model.Estado(u'Rechazado'),
                            model.Estado(u'Eliminado'),
                            model.Estado(u'En Revision'),
                            model.Estado(u'Abierta'),
                            model.Estado(u'Confirmado'),
                            model.Estado(u'Eliminar'),
                            model.Privilegios(u'crear',u'Permite la Creacion de una entidad'),
                            model.Privilegios(u'modificar',u'Permite la Modificacion de una entidad'),
                            model.Privilegios(u'eliminar',u'Permite la Eliminacion de una entidad'),
                            model.Privilegios(u'listar',u'Permite listar las entidades'),
                            model.Privilegios(u'ver',u'Permite visualizar una entidad'),
                            model.Privilegios(u'revivir',u'Aplicable solo a la Entidad Item; permite revivir un Item'),
                            model.Privilegios(u'revertir',u'Aplicable solo a la Entidad Item; permite revertir a una version anterior un Item'),
                            model.Privilegios(u'confirmar',u'Aplicable solo a la Entidad Item; permite confirmar un cambio, reversion o revivir un Item'),
                            model.Privilegios(u'rechazar',u'Aplicable solo a la Entidad Item; permite rechazar un cambio, reversion o revivir un Item'),
                            ])
    model.DBSession.flush()
    
    ''' Tipos de Rol'''
    tipo_sistema = model.TipoRol()
    tipo_sistema.nom_tipo_rol = u'De Sistema'
    
    model.DBSession.add(tipo_sistema)
    
    tipo_proyecto = model.TipoRol()
    tipo_proyecto.nom_tipo_rol = u'De Proyecto'
    
    model.DBSession.add(tipo_proyecto)
    
    ''' Rol Lider de Proyecto'''              
    lider_rol = model.Rol()
    lider_rol.nom_rol=u'Lider de Proyecto'
    lider_rol.des_rol=u'Rol que se encarga de administrar un proyecto específico'
    lider_rol.tipoRol= tipo_sistema   
       
    model.DBSession.add(lider_rol) 
    
    ''' Rol Administrador de Lineas Base'''
    admin_lb = model.Rol()
    admin_lb.nom_rol=u'Admin de LB'
    admin_lb.des_rol=u'Rol que se encarga de administrar las Lineas Bases de un proyecto'
    admin_lb.tipoRol= tipo_proyecto
    
    permisos = model.Permisos()
    permisos.entidad = lb
    for privilegio in model.DBSession.query(model.Privilegios).all():                
                permisos.privilegios.append(privilegio)
                
    admin_lb.permisos.append(permisos)             
    
    model.DBSession.add(admin_lb)
    
    model.DBSession.flush()
    
    transaction.commit()
    print "Successfully setup"    
    
