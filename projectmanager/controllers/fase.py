# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash, tmpl_context, redirect, validate, request
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous

#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from sqlalchemy.sql import exists
from sqlalchemy.orm.exc import NoResultFound
from projectmanager.lib.base import BaseController
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.proyecto import Proyecto
from projectmanager.model.proyecto import Fase
from projectmanager.model.entities import Estado
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Item
from projectmanager.model.entities import TipoItem
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import TipoDatoAtributo
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import RolFaseUsuario
from projectmanager.model.roles import RolProyectoUsuario
from projectmanager.model.roles import Rol
from projectmanager.model.roles import TipoRol

from sqlalchemy import func

#widgets
from projectmanager.widgets.new_phaseForm import create_new_phase
from projectmanager.widgets.edit_phaseForm import edit_phase
from projectmanager.widgets.new_tipoItemForm import create_new_tipoItem
from projectmanager.widgets.new_atributoForm import create_new_atributo
__all__ = ['AdminController']


class FaseController(BaseController):
    """Controlador de la Pagina de Administración del Sistema"""
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')    
               
    @expose('projectmanager.templates.fases.fases')
    def index(self,**kw):        
        
        Globals.current_project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==int(kw['id_proyecto'])).one()             
               
        lider_rol=DBSession.query(Rol).\
                    filter(Rol.nom_rol=='Lider de Proyecto').one()
        user = DBSession.query(Usuario).\
            filter(Usuario.login_name==\
                   request.identity['repoze.who.userid']).one()
        
        rol_project = DBSession.query(RolProyectoUsuario).\
                filter(RolProyectoUsuario.roles==lider_rol).\
                filter(RolProyectoUsuario.proyecto==Globals.current_project).\
                filter(RolProyectoUsuario.usuarios==user)
        
        if rol_project.count > 0:
            fases_lista = DBSession.query(Fase).\
                filter(Fase.id_proyecto == int(kw['id_proyecto'])).\
                order_by(Fase.nro_fase)
        else:
            fases_lista = DBSession.query(Fase).\
                filter(Fase.id_proyecto==int(kw['id_proyecto'])).\
                filter(Fase.usuarios.contains(user))
        
        if fases_lista.count() == 0:
            flash(_('No se han encontrado Fases'),'info')  
                    
        return dict(fases=fases_lista)           
   
    @expose('projectmanager.templates.fases.newPhase')
    def newPhase(self, **kw):
        valid_nro_fases = DBSession.query(Fase.nro_fase).\
            filter(Fase.id_proyecto == Globals.current_project.id_proyecto).all()
        tmpl_context.form = create_new_phase
        return dict(nro_fases=valid_nro_fases)
        
    @validate(create_new_phase,error_handler=newPhase)
    @expose()
    def savePhase(self, **kw):
        Phase = Fase()
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto == Globals.current_project.id_proyecto).one()
        estado =DBSession.query(Estado).\
            filter(Estado.nom_estado == 'Inicial').one()
        Phase.proyectoFase = project
        Phase.estadoFase = estado
        Phase.nro_fase = kw['nroPhase']
        Phase.nom_fase = kw['phaseName']
        Phase.des_fase = kw['descripcion']                
        DBSession.add(Phase)                
        flash(_("Se ha creado una nueva Fase: %s") %kw['phaseName'],'info')
        redirect("index?id_proyecto="+str(Globals.current_project.id_proyecto))
    
    @expose('projectmanager.templates.fases.editPhase')
    def editPhase(self, **kw):        
        tmpl_context.form = edit_phase
        Globals.nro_fase_to_edit = kw['idPhase']
        phase = DBSession.query(Fase).filter(Fase.id_fase==kw['idPhase']).one()                
        return dict(fase=phase)
    
    @validate(edit_phase,error_handler=editPhase)    
    @expose()
    def updatePhase(self, **kw):
        phase = DBSession.query(Fase).filter(Fase.id_fase==kw['idPhase']).one()
        phase.nro_fase = kw['nroPhase']
        phase.nom_fase = kw['phaseName']
        phase.des_fase = kw['descripcion']        
        redirect("index?id_proyecto="+str(Globals.current_project.id_proyecto))
        
    @expose()
    def delete(self, **kw):               
        phase = DBSession.query(Fase).filter(Fase.id_fase==kw['id']).one()
        
        rol_fase = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.fase==phase)
            
        rol_fase.delete()
        
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(phase)).all()
            
        for user in users:
            phase.usuarios.remove(user)
        
        DBSession.delete(phase)
        
        redirect("index?id_proyecto="+str(Globals.current_project.id_proyecto))
        
    @expose('projectmanager.templates.fases.fases')
    def search(self, **kw):
        word = '%'+kw['key']+'%'        
        fases_lista = DBSession.query(Fase).\
            filter(Fase.nom_fase.like(word)).\
            filter(Fase.id_proyecto == Globals.current_project.id_proyecto).\
            order_by(Fase.nom_fase)
            
        if fases_lista.count() == 0:
            flash(_('No se han encontrado Fases'),'info')        
        
        return dict(fases=fases_lista)
        
    '''********** ADMINISTRACION DE FASES INDIVIDUALES **********'''

    @expose('projectmanager.templates.items.items')
    def itemsFase(self, **kw):
        Globals.current_phase = DBSession.query(Fase).\
                        filter(Fase.id_fase==int(kw['id_fase'])).one()
                   
        return dict(page='items')
        
    #******************* USUARIOS DE FASE *****************
    
    @expose('projectmanager.templates.fases.usersPhase')
    def listUsers(self, **kw):
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(fase)).all()
            
        return dict(usuarios=users)
        
    @expose('projectmanager.templates.fases.asignUsers')
    def asignUsers(self, **kw):
        #Obtenemos los usuarios del proyecto actual y que todavia no
        #pertenecen a esta fase     
        
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        
        list = DBSession.query(Usuario).\
                filter(Usuario.proyecto.contains(project)).\
                filter(~Usuario.fases.contains(fase)).all()
                     
        return dict(usuarios=list)
    
    @expose()
    def saveUserToPhase(self, **kw):
        usuario = DBSession.query(Usuario).\
                    filter(Usuario.id_usuario==int(kw['id_user'])).one()
                    
        fase = DBSession.query(Fase).\
                filter(Fase.id_fase == Globals.current_phase.id_fase).one()
                
        fase.usuarios.append(usuario)
        
        redirect('asignUsers')
                    
    @expose('projectmanager.templates.fases.deasignUsers')
    def quitUsers(self, **kw):
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(fase)).all()
            
        return dict(usuarios=users)
        
    @expose()
    def delUserOfPhase(self, **kw):
        usuario = DBSession.query(Usuario).\
                    filter(Usuario.id_usuario==int(kw['id_user'])).one()
                    
        fase = DBSession.query(Fase).\
                filter(Fase.id_fase == Globals.current_phase.id_fase).one()
         
        #Desvincular usuario de la fase
        fase.usuarios.remove(usuario)
        
        #Sacarle todos los roles que tenia en esa fase
        roles_fase= DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.usuarios==usuario).\
            filter(RolFaseUsuario.fase==fase)
            
        roles_fase.delete()
        
        redirect('quitUsers')
        
    #******************* ROLES DE USUARIO *****************
    @expose('projectmanager.templates.fases.usersPhaseRoles')
    def usersRol(self, **kw):
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
            
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(fase)).all()
        
        return dict(usuarios=users)
        
    @expose('projectmanager.templates.fases.asignRolPhase')
    def asignRolPhase(self, **kw):
        user = DBSession.query(Usuario).\
            filter(Usuario.id_usuario==int(kw['id_usuario'])).one()
        
        tipo_rol = DBSession.query(TipoRol).\
            filter(TipoRol.nom_tipo_rol=='De Proyecto').one()
            
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase == Globals.current_phase.id_fase).one()
        
        #Obtenemos todos los roles disponibles    
        list1 = DBSession.query(Rol).\
            filter(Rol.tipoRol == tipo_rol).all()
        
        #Obtenemos los roles de este usuario
        list2 = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.usuarios == user).\
            filter(RolFaseUsuario.fase == fase).all()
            
        list=[]
        for rol in list1:
            encontrado=0
            for element in list2:
                if rol.id_rol == element.roles.id_rol:
                    encontrado=1
                    break
            
            if encontrado == 0:
                list.append(rol)
        
        return dict(roles = list, usuario=user)
    
    @expose()
    def saveRolPhase(self, **kw):
        rol = DBSession.query(Rol).\
            filter(Rol.id_rol == int(kw['id_rol'])).one()
            
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase == Globals.current_phase.id_fase).one()
            
        user = DBSession.query(Usuario).\
            filter(Usuario.id_usuario==int(kw['id_usuario'])).one()
            
        rol_fase = RolFaseUsuario()
        rol_fase.roles = rol
        rol_fase.fase = fase
        rol_fase.usuarios = user
             
        redirect('asignRolPhase?id_usuario=' + str(user.id_usuario))
        
    @expose()
    def quitRolPhase(self, **kw):
        rol = DBSession.query(Rol).\
            filter(Rol.id_rol==int(kw['id_rol'])).one()
            
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==Globals.current_phase.id_fase).one()
            
        usuario = DBSession.query(Usuario).\
            filter(Usuario.id_usuario==int(kw['id_usuario'])).one()
            
        element = DBSession.query(RolFaseUsuario).\
            filter(RolFaseUsuario.roles==rol).\
            filter(RolFaseUsuario.fase==fase).\
            filter(RolFaseUsuario.usuarios==usuario).one()
            
        DBSession.delete(element)
        
        redirect('usersRol')
            
    #******************* TIPOS DE ITEM *****************    
    
    @expose('projectmanager.templates.fases.listTiposItems')
    def listTiposItem(self, **kw):
		fase = DBSession.query(Fase).\
			filter(Fase.id_fase==Globals.current_phase.id_fase).one()
			
		list_tipos=DBSession.query(TipoItem).\
			filter(TipoItem.fase==fase).all()
			
		return dict(tiposItem=list_tipos)
	
    @expose('projectmanager.templates.fases.addTiposItems')	
    def addTiposItem(self, **kw):
		fase = DBSession.query(Fase).\
			filter(Fase.id_fase==Globals.current_phase.id_fase).one()
			
		list_tipos=DBSession.query(TipoItem).\
			filter(TipoItem.fase==fase).all()
		return dict(tiposItem=list_tipos)
		
    @expose('projectmanager.templates.fases.newTipoItem')
    def newTipoItem(self, **kw):
        tmpl_context.form=create_new_tipoItem
        return dict(page='new tipo de item')
	
    @validate(create_new_tipoItem,error_handler=newTipoItem)
    @expose()
    def saveTipoItem(self, **kw):
		fase = DBSession.query(Fase).\
			filter(Fase.id_fase==Globals.current_phase.id_fase).one()
		
		newTipo=TipoItem()
		newTipo.nom_tipo_item=kw['nom_tipo']
		newTipo.fase=fase
		
		prefi=u''
		cont=0
		for letra in kw['nom_tipo']:
			prefi = prefi + letra
			cont=cont+1
			if cont==3:
				break
				
		newTipo.prefijo=prefi
		newTipo.cont_prefijo=0
		
		redirect('/fase/addTiposItem')
	
    @expose()
    def delTipoItem(self, **kw):
        tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['id_tipo'])).one()
        atributos = DBSession.query(Atributo).filter(Atributo.tipoItem==tipoItem)
        atributos.delete()
        DBSession.delete(tipoItem)
        redirect('/fase/addTiposItem')
        
    @expose('projectmanager.templates.fases.addAtributos')
    def addAtributo(self, **kw):
		tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['id_tipo'])).one()
		tmpl_context.form=create_new_atributo
		return dict(idTipoItem=tipoItem.id_tipo_item)
		
    @validate(create_new_atributo,error_handler=addAtributo)
    @expose()
    def saveAtributo(self, **kw):
		tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==(kw['id_tipo'])).one()
		tipoDato = DBSession.query(TipoDatoAtributo).filter(TipoDatoAtributo.id_tipo_dato==int(kw['tipo_dato'])).one()
		
		newAtri = Atributo(kw['nom_atributo'], tipoDato, tipoItem)
				
		redirect('/fase/addTiposItem')
        
    @expose()
    def delAtributo(self, **kw):
        atributo = DBSession.query(Atributo).\
            filter(Atributo.id_atributo == int(kw['id_atributo'])).one()
            
        DBSession.delete(atributo)
        redirect('/fase/addTiposItem')
		
    @expose('projectmanager.templates.fases.importTipoItem')
    def importTipoItem(self,**kw):
		
        fase=DBSession.query(Fase).filter(Fase.id_fase==Globals.current_phase.id_fase).one()
        
        list1=DBSession.query(TipoItem).filter(TipoItem.fase!=fase).all()
        tipos_fase =DBSession.query(TipoItem).filter(TipoItem.fase==fase).all()
		
        list_tipos=[]
        for tipo in list1:
            esta=False
            for tipofase in tipos_fase:
                if tipo.nom_tipo_item == tipofase.nom_tipo_item:
                    esta=True
                    break
			
            if esta==False:
                list_tipos.append(tipo)
               	    
        return dict(tiposItem=list_tipos)
	
    @expose()
    def saveImport(self,**kw):
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==Globals.current_phase.id_fase).one()
		
        tipo=DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['id_tipo'])).one()
        		
        tipoNew = TipoItem()		
        tipoNew.nom_tipo_item = tipo.nom_tipo_item
        tipoNew.fase = fase
        tipoNew.prefijo = tipo.prefijo
        tipoNew.cont_prefijo = 0
               
        list_atributos = []       
        for atributo in tipo.Atributo:
            list_atributos.append(Atributo(atributo.nom_atributo, 
                                           atributo.tipoDatoAtributo, 
                                           tipoNew))
        
        DBSession.add(tipoNew)
        DBSession.add_all(list_atributos)           
        redirect('/fase/importTipoItem')	
				
      
    #******************* BUSCADORES *****************
    
    @expose('projectmanager.templates.fases.asignUsers')
    def searchNoUsersOfPhase(self, **kw):
        word = '%'+kw['key']+'%'
        
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        project = DBSession.query(Proyecto).\
            filter(Proyecto.id_proyecto==\
                    Globals.current_project.id_proyecto).one()
        
        list = DBSession.query(Usuario.id_usuario,Usuario.nom_usuario).\
                filter(Usuario.proyecto.contains(project)).\
                filter(~Usuario.fases.contains(fase)).\
                filter(Usuario.nom_usuario.like(word)).all()
                
        return dict(usuarios = list)
    
    @expose('projectmanager.templates.fases.deasignUsers')
    def searchUsersOfPhase_quit(self, **kw):
        word = '%'+kw['key']+'%'
        
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(fase)).\
            filter(Usuario.nom_usuario.like(word)).all()
            
        return dict(usuarios=users)

    @expose('projectmanager.templates.fases.usersPhase')
    def searchUsersOfPhase_list(self, **kw):
        word = '%'+kw['key']+'%'
                
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==\
                   Globals.current_phase.id_fase).one()
                   
        users = DBSession.query(Usuario).\
            filter(Usuario.fases.contains(fase)).\
            filter(Usuario.nom_usuario.like(word)).all()
            
        return dict(usuarios=users)
