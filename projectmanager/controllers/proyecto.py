# -*- coding: utf-8 -*-
"""Sample controller module"""

# turbogears imports
from tg import expose, tmpl_context
from tg import redirect, validate, flash
from tg import request

# third party imports
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy import and_
from projectmanager.lib.mypredicates import is_type

# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import ProyectoUsuario
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import Rol
from projectmanager.model.roles import RolProyectoUsuario
from projectmanager.model.roles import RolFaseUsuario
from projectmanager.model.entities import Estado
from projectmanager.model.auth import Group
from projectmanager.controllers.fase import FaseController


from projectmanager.widgets.new_projectForm import create_new_project
from projectmanager.widgets.edit_projectForm import edit_project

class ProyectoController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
   
    fase = FaseController()
               
    @expose('projectmanager.templates.proyectos.proyectos')
    def adminProject(self):
        """
        Muestra todos los proyectos existentes al administrador del 
        sistema o los proyectos del usuario que ha ingresado al sistema
        """
         
        if is_type('admin'):
            projects = DBSession.query(Proyecto).order_by(Proyecto.nom_proyecto)            
        else:
            user = DBSession.query(Usuario).\
                filter(Usuario.login_name==request.identity['repoze.who.userid']).one()
            
            projects = DBSession.query(Proyecto).\
                filter(Proyecto.usuarios.contains(user)).all()
            
        return dict(proyectos=projects)
                
    @expose('projectmanager.templates.proyectos.newProject')
    def newProject(self):
        """
        Muestra el formulario para crear un nuevo proyecto
        """
        tmpl_context.form = create_new_project
        return dict(page='Nuevo Proyecto')
      
    
    @expose()
    def saveProject(self, **kw):
        """
        Funcion que se encarga de guardar los datos introducidos en el formulario
        para el nuevo proyecto.
        Al crear un nuevo proyecto se establece el estado de este
        en 'No Iniciado'
        """
        aProject = Proyecto()
        estado =DBSession.query(Estado).filter(Estado.nom_estado == 'No Iniciado').one()
        aProject.estadoProyecto = estado
        aProject.nom_proyecto = kw['projectName']
        aProject.des_proyecto = kw['descripcion']
        DBSession.add(aProject)                
        flash(_("Se ha creado un nuevo Proyecto: %s") %kw['projectName'],'info')
        redirect("adminProject")
    
    @expose('projectmanager.templates.proyectos.editProject')
    def editProject(self, **kw): 
        """       
        Muestra el formulario para editar el proyecto elegido"""
        tmpl_context.form = edit_project
        uProject = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==kw['id']).one()                
        return dict(proyecto=uProject)    
    
    @expose()
    def updateProject(self, **kw):
        """
        Funcion que se encarga de guardar los datos modificados 
        del proyecto editado"""
        aProject = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==kw['id_project']).one()
        aProject.nom_proyecto = kw['projectName']
        aProject.des_proyecto = kw['descripcion']
        #DBSession.add(aProject)
        redirect("adminProject")
        
    @expose()
    def delete(self, **kw):    
        """ Funcion que borra un proyecto seleccionado"""
        dProject = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==kw['id']).one()
        
        fases = DBSession.query(Fase).\
            filter(Fase.proyectoFase==dProject)
        
        for fase in fases.all():
            users=DBSession.query(Usuario).\
                filter(Usuario.fases.contains(fase)).all()
                
            for user in users:
                fase.usuarios.remove(user)
                       
        rol_proyecto = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.proyecto==dProject)            
        rol_proyecto.delete()             
        
        rol_fase = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.fase.has(proyectoFase=dProject))        
        rol_fase.delete()
               
        fases.delete()                  
        DBSession.delete(dProject)
        redirect("adminProject")
    
    @expose()
    def startProject(self, **kw):
        """Funcion que cambia el estado de una fase No Inciada a 
        Iniciada"""
        project = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==int(kw['id'])).one()
        estado =DBSession.query(Estado).filter(Estado.nom_estado == 'Iniciado').one()
        project.estadoProyecto = estado
        redirect('adminProject')
        
    @expose()
    def stopProject(self, **kw):
        """Funcion que cambia el estado de una fase Inciada a 
        Finalizada"""
        project = DBSession.query(Proyecto).filter(Proyecto.id_proyecto==int(kw['id'])).one()
        estado =DBSession.query(Estado).filter(Estado.nom_estado == 'Finalizado').one()
        project.estadoProyecto = estado
        redirect('adminProject')   
    
    #******************** USUARIOS DE PROYECTO ********************
        
    @expose('projectmanager.templates.proyectos.asignUser')
    def userToProject(self, **kw):
        """
        Asignar Usuarios al Proyecto Elegido"""         
        #Obtenemos los usuarios que tienen proyectos asignados
        #menos el actual       
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list1 = DBSession.query(Usuario).\
                filter(Usuario.groups.any(group_name='user')).\
                filter(~Usuario.proyecto.contains(project))
                
        #Obtenemos los usuarios del tipo user y los que no 
        #tienen ningun proyecto asignado
        list2 = DBSession.query(Usuario).\
                filter(Usuario.proyecto==None).\
                filter(Usuario.groups.any(group_name='user'))   
        
        user_list = list1.union(list2).order_by(Usuario.nom_usuario).all()
            
        return dict(usuarios=user_list)
                    
    @expose()
    def saveUserToProject(self, **kw):    
        """Funcion que se encarga de guardar en la base de datos
        la relacion del usuario seleccionado con el proyecto
        actual"""
        
        proyecto = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto == \
                    Globals.current_project.id_proyecto).one()
        
        usuario = DBSession.query(Usuario).\
                    filter(Usuario.id_usuario == int(kw['id_user'])).\
                    one()
        proyecto.usuarios.append(usuario)
            
        redirect('userToProject')
                
    @expose('projectmanager.templates.proyectos.deasignUser')
    def quitUserOfProject(self, **kw):
        """Lista de usuarios para
        Desasignar del Proyecto Elegido"""         
        #Obtenemos los usuarios del proyecto actual       
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.proyecto.contains(project))
        
        return dict(usuarios=list)
    
    @expose()
    def delUserOfProject(self, **kw):
        """ Función que elimina la relacion del usuario pasado
        en el argumento con el proyecto actual"""
        usuario = DBSession.query(Usuario).\
                filter(Usuario.id_usuario==int(kw['id_user'])).one()
        
        proyecto = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==Globals.current_project.id_proyecto).one()
        
        #Desvinculamos al usuario del proyecto actual
        proyecto.usuarios.remove(usuario)
        
        #Borramos todos sus roles de proyecto
        rol_proyecto = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.usuarios==usuario)
        
        rol_proyecto.delete()
        
        #Desvinculamos al usuario de todas las fases de este proyecto
        fases = DBSession.query(Fase).\
            filter(Fase.proyectoFase==proyecto).\
            filter(Fase.usuarios.contains(usuario)).all()
            
        for fase in fases:
            fase.usuarios.remove(usuario)
            
        #Borramos todos sus roles de fases
        rol_fases = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.usuarios==usuario)
            
        rol_fases.delete()
        
        
        redirect('quitUserOfProject')
         
    @expose('projectmanager.templates.proyectos.listUsersProject')
    def listUsersProject(self):
        """Envia al template la lista de usuarios que pertenecen
        al proyecto actual para mostrar una lista de estos"""
        #Obtenemos los usuarios del proyecto actual       
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.proyecto.contains(project))
        
        return dict(usuarios=list)
    
     #******************** LIDER DE PROYECTO ********************
     
    @expose('projectmanager.templates.proyectos.asignLider')
    def liderToProject(self, **kw):
        """Envia la lista de usuarios que pertenecen al proyecto 
        elegido y pueden ser electos para ser lideres del proyecto"""
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
                    
        lider_rol = DBSession.query(Rol).\
                    filter(Rol.nom_rol==u'Lider de Proyecto').one()
        
        #Obtenemos los usuarios del proyecto actual
        list1 = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.proyecto.contains(project)).all()
                    
        #Obtenemos los usuarios que ya son Lideres del Proyecto actual                    
        
        list2 = DBSession.query(RolProyectoUsuario).\
                filter(RolProyectoUsuario.proyecto==project).\
                filter(RolProyectoUsuario.roles==lider_rol).all()
        
        list=[]
        for usr in list1:
            encontrado=0
            for element in list2:
                if usr.id_usuario == element.usuarios.id_usuario:
                    encontrado=1
                    break
            
            if encontrado == 0:
                list.append(usr)
                          
        return dict(usuarios=list)
    
    @expose()
    def saveLiderToProject(self, **kw):    
        """Funcion que se encarga de guardar en la base de datos
        la relacion del usuario seleccionado con el proyecto
        actual como Lider del Proyecto"""
                
        usuario = DBSession.query(Usuario).\
                    filter(Usuario.id_usuario == int(kw['id_user'])).\
                    one()
        lider_rol = DBSession.query(Rol).\
                    filter(Rol.nom_rol==u'Lider de Proyecto').one()
        
        proyecto = DBSession.query(Proyecto).\
                    filter(Proyecto.id_proyecto==\
                           Globals.current_project.id_proyecto).one()
        
        new_lider = RolProyectoUsuario()
        new_lider.roles = lider_rol
        new_lider.usuarios = usuario
        new_lider.proyecto = proyecto
            
        redirect('liderToProject')
        
    @expose('projectmanager.templates.proyectos.listLider')
    def listLideres(self, **kw):
        """ Pasa la lista de usuarios que poseen el rol de Lider
        de Proyecto en el Proyecto actual elegido"""
        lider_rol = DBSession.query(Rol).\
                    filter(Rol.nom_rol==u'Lider de Proyecto').one()
               
        list1 = DBSession.query(RolProyectoUsuario).\
                filter(RolProyectoUsuario.roles==lider_rol).\
                filter(RolProyectoUsuario.proyecto==Globals.current_project).all()
        
        list=[]    
        for element in list1:
            list.append(element.usuarios)       
                        
        return dict(usuarios = list)
    
    @expose('projectmanager.templates.proyectos.quitLider')
    def quitLiderOfProject(self, **kw):
        """ Pasa la lista de usuarios que poseen el rol de Lider
        de Proyecto en el Proyecto actual elegido al template
        que utilizara estos datos para eliminar el usuario seleccionado
        como lider del proyecto"""
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
                    
        lider_rol = DBSession.query(Rol).\
                    filter(Rol.nom_rol==u'Lider de Proyecto').one()
                    
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.RolProyectoUsuario.\
                    any(RolProyectoUsuario.id_rol_proyecto==\
                        lider_rol.id_rol)).\
                filter(Usuario.RolProyectoUsuario.\
                    any(RolProyectoUsuario.id_proyecto_==\
                        project.id_proyecto)).all()
        return dict(usuarios = list)
        
    @expose()
    def delLiderOfProject(self, **kw):
        """Funcion que se encarga de sacar el rol de Lider de Proyecto
        a un usuario seleccionado en un proyecto dado"""
        usuario = DBSession.query(Usuario).\
                filter(Usuario.id_usuario==int(kw['id_user'])).one()
        
        lider_rol = DBSession.query(Rol).\
            filter(Rol.nom_rol==u'Lider de Proyecto').one()
        
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        
        rol_usr_pro = DBSession.query(RolProyectoUsuario).\
            filter(RolProyectoUsuario.usuarios == usuario).\
            filter(RolProyectoUsuario.roles == lider_rol).\
            filter(RolProyectoUsuario.proyecto == project).one()
            
        DBSession.delete(rol_usr_pro)
        
        redirect('quitLiderOfProject')
    
     #******************** BUSCADORES ********************
             
    @expose('projectmanager.templates.proyectos.proyectos')
    def search(self, **kw):
        """Realiza la busqueda de proyectos que pertenecen al usuario
        actualmente logueado"""
        word = '%'+kw['key']+'%'        
        
        if is_type('admin'):
            projects = DBSession.query(Proyecto).\
                    filter(Proyecto.nom_proyecto.like(word)).\
                    order_by(Proyecto.nom_proyecto)
        else:
            projects = DBSession.query(Proyecto).\
                filter(Proyecto.nom_proyecto.like(word)).\
                filter(Proyecto.usuarios.any(login_name=request.identity['repoze.who.userid']))
            
        return dict(proyectos=projects)
    
    @expose('projectmanager.templates.proyectos.asignUser')
    def searchNoUsers(self, **kw):
        """Realiza la busqueda de usuarios que NO pertenecen al proyecto
        actual. Esta busqueda se utiliza para ASIGNAR usuarios al proyecto
        elegido"""
        word = '%'+kw['key']+'%'        
        
        #Obtenemos los usuarios que tienen proyectos asignados
        #menos el actual       
        project = DBSession.query(Proyecto).\
                    filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list1 = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.groups.any(group_name='user')).\
                filter(~Usuario.proyecto.contains(project))
                
        #Obtenemos los usuarios del tipo user y los que no 
        #tienen ningun proyecto asignado
        list2 = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).filter(Usuario.proyecto==None).\
                filter(Usuario.groups.any(group_name='user'))   
        
        user_list = list1.union(list2).order_by(Usuario.nom_usuario)
        
        user_list = user_list.filter(Usuario.nom_usuario.like(word))
            
        return dict(usuarios=user_list)

    @expose('projectmanager.templates.proyectos.deasignUser')    
    def searchUsers(self, **kw):
        """Realiza la busqueda de usuarios que SI pertenecen al proyecto
        actual. Esta busqueda se utiliza para DESASIGNAR usuarios del 
        proyecto elegido"""
        word = '%'+kw['key']+'%'        
        
        #Obtenemos los usuarios del proyecto actual       
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.nom_usuario.like(word)).\
                filter(Usuario.proyecto.contains(project))
            
        return dict(usuarios=list)

    @expose('projectmanager.templates.proyectos.asignLider')
    def searchUsers2(self, **kw):
        """Realiza la busqueda de usuarios que SI pertenecen al proyecto
        actual. Esta busqueda se utiliza para DESASIGNAR usuarios del 
        proyecto elegido"""
        word = '%'+kw['key']+'%'        
        
        #Obtenemos los usuarios del proyecto actual       
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.nom_usuario.like(word)).\
                filter(Usuario.proyecto.contains(project))
            
        return dict(usuarios=list)
