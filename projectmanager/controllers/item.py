# -*- coding: utf-8 -*-
"""Sample controller module"""

import os

# turbogears imports
from tg import expose, tmpl_context, response, request
from tg import redirect, validate, flash
from tg import session
from tg.controllers import CUSTOM_CONTENT_TYPE

# third party imports
from datetime import datetime
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from repoze.what.predicates import has_permission
from repoze.what.predicates import not_anonymous

'''import cherrypy
from cherrypy.lib.static import serve_file'''

from sqlalchemy import func

# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.model.entities import Item
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import AtributoArchivo
from projectmanager.model.entities import Estado
from projectmanager.model.entities import TipoItem
from projectmanager.model.entities import RelacionItem
from projectmanager.model.proyecto import Fase
from projectmanager.model.roles import Usuario

from projectmanager.widgets.new_itemForm import create_new_item
#from projectmanager.widgets.edit_itemForm import edit_item
from projectmanager.lib.app_globals import Globals

class ItemController(BaseController):
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')    
    
        
    @expose('projectmanager.templates.items.items')
    def adminItem(self, faseid):                       
	       
        Globals.current_phase = DBSession.query(Fase).filter(Fase.id_fase == int(faseid)).one()
        
        list_items = DBSession.query(VersionItem).\
            filter(TipoItem.fase==Globals.current_phase).\
            filter(VersionItem.ultima_version=='S').all()

        return dict(items=list_items)
        
    @expose('projectmanager.templates.items.newItem')
    def newItem(self, **kw):
	
        fase = DBSession.query(Fase).\
            filter(Fase.id_fase==Globals.current_phase.id_fase).one()
	
        listTipoItem = DBSession.query(TipoItem.id_tipo_item,\
                                   TipoItem.nom_tipo_item).\
                   filter(TipoItem.fase == fase).all()
		
        tmpl_context.form = create_new_item
        
        return dict(type_options = listTipoItem)    	        
    
    @validate(create_new_item,error_handler=newItem)
    @expose()
    def saveItem(self, **kw):
        estado = DBSession.query(Estado).filter(Estado.nom_estado=='En Modificacion').one()
        tipoItem = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item==int(kw['tipoItem'])).one()                      
        lg_name=request.identity['repoze.who.userid']
        usuario = DBSession.query(Usuario).filter(Usuario.login_name==lg_name).one()
        
        item = Item()
        item.cod_item = str(tipoItem.prefijo) + str(tipoItem.cont_prefijo)
        tipoItem.cont_prefijo = tipoItem.cont_prefijo + 1
               
        item.nom_item = kw['nomItem']
        item.tipoItem = tipoItem          
        
        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = item        
        nuevaVersionItem.nro_version_item = 0
        nuevaVersionItem.estado = estado       
        nuevaVersionItem.tipoItem = tipoItem         
        nuevaVersionItem.usuarioModifico = usuario
        nuevaVersionItem.fecha = str(datetime.now())
        nuevaVersionItem.observaciones = kw['observaciones']
        nuevaVersionItem.ultima_version = 'S'
        nuevaVersionItem.peso = int(kw['peso'])
               
        for atributo in DBSession.query(Atributo).filter(Atributo.tipoItem==tipoItem):
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.atributo = atributo
            nuevoAtributoItem.versionItem = nuevaVersionItem        
            nuevoAtributoItem.val_atributo = atributo.val_default
            DBSession.add(nuevoAtributoItem)   
      
        flash(_("Se ha creado un nuevo Item: %s") %kw['nomItem'],'info')
        redirect("adminItem?faseid="+str(Globals.current_phase.id_fase))

    @expose('projectmanager.templates.items.atributosItem')
    def atributosItem(self, **kw):                        
        unaVersionItem = DBSession.query(VersionItem).filter(VersionItem.id_version_item==kw['id_version']).one()
        Globals.current_item = unaVersionItem
        atributosItem = DBSession.query(AtributoItem).filter(AtributoItem.versionItem==unaVersionItem)                
        return dict(atributosItem=atributosItem)            

    @expose('projectmanager.templates.relacionesItem')
    def relacionesItem(self, **kw):        
        unaVersionItem = DBSession.query(VersionItem).filter(VersionItem.id_version_item==kw['id']).one()
        relacionesItem = DBSession.query(RelacionItem).filter(RelacionItem.versionItem==unaVersionItem)                
        return dict(versionItem=unaVersionItem,relacionesItem=relacionesItem)            

    	
    
    @expose('projectmanager.templates.revivirItem')
    def revivirItem(self, **kw):        
        idFaseItem = session.get('idFaseItem',None)
        
        query = DBSession.query(VersionItem)             
        query = query.from_statement('SELECT VI.id_version_item,VI.id_item,VI.id_estado,VI.id_tipo_item,VI.id_usuario_modifico,VI.nro_version_item, VI.observaciones, VI.fecha, VI.peso FROM "VERSION_ITEM" VI INNER JOIN (SELECT id_item as ID, MAX(id_version_item) as MAX_VERSION FROM "VERSION_ITEM" GROUP BY id_item) MAX ON VI.id_item=MAX.ID AND VI.id_version_item=MAX.MAX_VERSION INNER JOIN "TIPO_ITEM" AS TIP ON VI.id_tipo_item = TIP.id_tipo_item INNER JOIN "FASE" AS FAS ON TIP.id_fase = FAS.id_fase INNER JOIN "ESTADO" AS EST ON EST.id_estado = VI.id_estado WHERE FAS.id_fase=:idFase AND EST.nom_estado=\'Eliminado\'')
        query = query.params(idFase=idFaseItem)
        items = list(query)                
        return dict(page='Recuperar Item Eliminado', items=items, idFase=idFaseItem)
        
    @expose()
    def recuperarItem(self, **kw):        
        idVersionItem = kw['id']        
        idFaseItem = session.get('idFaseItem',None)
        
        versionItemRecuperado = DBSession.query(VersionItem).filter (VersionItem.id_version_item==idVersionItem).one()            
        
        estadoEnModificacion = DBSession.query(Estado).filter_by(nom_estado="En Modificacion").one()

        versionItemRecuperado.estado = estadoEnModificacion
        DBSession.flush()

        redirect("revivirItem?id="+idFaseItem)

        
    @expose()
    def delete(self, **kw):
        idFaseItem = session.get('idFaseItem',None)
        
        quedarianHuerfanos = false

        #OBSERVACION RELACION_ITEM ACTUALMENTE NO PUEDE SER AUTOSECUENCIAL

        '''for relacionItem in DBSession.query(RelacionItem).filter_by(RelacionItem.versionItem.id_version_item=unTipoItem):
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.atributo = atributo
            nuevoAtributoItem.versionItem = nuevaVersionItem        
            nuevoAtributoItem.val_atributo = atributo.val_default
            DBSession.add(nuevoAtributoItem)   '''
       
        idVersionItem = DBSession.query(VersionItem).filter(VersionItem.id_version_item==kw['id']).one()
	estadoEliminado = DBSession.query(Estado).filter_by(nom_estado="Eliminado").one()
	idVersionItem.estado = estadoEliminado
        DBSession.flush()
        redirect("adminItem?faseid="+idFaseItem)
    
    @expose('projectmanager.templates.items')
    def search(sefl, **kw):
        word = '%'+kw['key']+'%'        
        projects = DBSession.query(VersionItem).filter(VersionItem.item.nom_item.contains(word)).order_by(VersionItem.item.nom_item)
        return dict(page='Administrar Items', items=items)

    '''@expose()
    def calcularImpactoHaciaAtras(self, idVersionItem):
	for relacionItem in DBSession.query(RelacionItem).filter_by(RelacionItem.versionItem.id_version_item=idVersionItem):        
	    sumaPeso = sumaPeso + calcularImpactoHaciaAtras(relacionItem.versionItem.id_version_item)
        sumaPeso = sumaPeso'''

    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def download(self, **kw):
        idAtributo = kw['idAtributo']
        idVersionItem = kw['idVersionItem']        

        q = DBSession.query(AtributoItem)
        q = q.from_statement('SELECT * FROM \"ATRIBUTO_ITEM\" WHERE id_atributo=:idAtributoArch AND id_version_item=:idVersionItemArch')
        q=  q.params(idAtributoArch=idAtributo)
        q=  q.params(idVersionItemArch=idVersionItem)        
        atributoItem = q.first()        

        #archivo = UploadedFile.byFilename(filename)
        archivoAtributo = DBSession.query(AtributoArchivo).filter(AtributoArchivo.id == atributoItem.id_archivo).first()
        
        '''return serve_file(archivoAtributo.abspath,contentType="application/x-download",dispositon="attachment", archivo.filename)'''

        '''log.debug(os.path.join(os.path.dirname(projectmanager.__file__)))'''

        '''response.headers["Content-disposition"] = "attachment; filename="+archivoAtributo.filename
	response.headers["Content-Type"] = archivoAtributo.filecontent
	response.write(archivoAtributo.filecontent)
	return response'''

        content_types = {
            'download': {'.png': 'image/jpeg', '.jpeg':'image/jpeg', '.jpg':'image/jpeg', '.gif':'image/jpeg', '.txt': 'text/plain', '.pdf':'application/pdf', '.zip':'application/zip', '.rar':'application/x-rar-compressed'}
        }        
        for file_type in content_types['download']:
            if archivoAtributo.filename.endswith(file_type):
                response.headers["Content-Type"] = content_types['download'][file_type]
                response.headers["Content-Disposition"] = 'attachment; filename="'+archivoAtributo.filename+'"'
        if archivoAtributo.filename.find(".") == -1:
            '''response.headers["Content-Type"] = "text/plain"'''
            response.headers["Content-Type"] =  content_types['download']
            response.headers["Content-Disposition"] = 'attachment; filename="'+archivoAtributo.filename+'"'
        return archivoAtributo.filecontent

        '''return serve_file(log.debug(os.path.join(os.path.dirname(projectmanager.__file__))) + archivoAtributo.filename,"application/x-download","attachment")'''

