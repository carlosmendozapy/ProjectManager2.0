# -*- coding: utf-8 -*-
"""Sample controller module"""

import os

# turbogears imports
from tg import expose, tmpl_context, response, request
from tg import redirect, validate, flash
from tg import session
from tg.controllers import CUSTOM_CONTENT_TYPE

# third party imports
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
    idFaseItem = None
    # The predicate that must be met for all the actions in this controller:
    allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')    
                 
    @expose('projectmanager.templates.items')
    def index(self):
        return dict(page='index')
        
    @expose('projectmanager.templates.items')
    def adminItem(self, faseid):                       
	session['idFaseItem'] = faseid
        session.save()        
        
        Globals.current_phase = DBSession.query(Fase).filter(Fase.id_fase == int(faseid)).one()
        
        idFaseItem = session.get('idFaseItem',None)
        '''q = DBSession.query(VersionItem)       
        q = q.join(['tipoItem', 'fase'])
        q = q.filter(Fase.id_fase==faseid)
        items = list(q)'''
        
	'''SELECT VI.id_version_item,VI.id_item,VI.id_estado,VI.id_tipo_item,VI.id_usuario_modifico,VI.nro_version_item, VI.observaciones, VI.fecha, VI.peso 
	FROM "VERSION_ITEM" VI 
	INNER JOIN (SELECT id_item as ID, MAX(id_version_item) as MAX_VERSION FROM "VERSION_ITEM" GROUP BY id_item) MAX 
	ON VI.id_item=MAX.ID AND VI.id_version_item=MAX.MAX_VERSION 
	INNER JOIN "TIPO_ITEM" AS TIP 
	ON VI.id_tipo_item = TIP.id_tipo_item 
	INNER JOIN "FASE" AS FAS 
	ON TIP.id_fase = FAS.id_fase 
	INNER JOIN "ESTADO" AS EST 
	ON EST.id_estado = VI.id_estado 
	WHERE FAS.id_fase=:idFase AND EST.nom_estado<>\'Eliminado\''''

        query = DBSession.query(VersionItem) 	        
        query = query.from_statement('SELECT VI.id_version_item,VI.id_item,VI.id_estado,VI.id_tipo_item,VI.id_usuario_modifico,VI.nro_version_item, VI.observaciones, VI.fecha, VI.peso FROM "VERSION_ITEM" VI INNER JOIN (SELECT id_item as ID, MAX(id_version_item) as MAX_VERSION FROM "VERSION_ITEM" GROUP BY id_item) MAX ON VI.id_item=MAX.ID AND VI.id_version_item=MAX.MAX_VERSION INNER JOIN "TIPO_ITEM" AS TIP ON VI.id_tipo_item = TIP.id_tipo_item INNER JOIN "FASE" AS FAS ON TIP.id_fase = FAS.id_fase INNER JOIN "ESTADO" AS EST ON EST.id_estado = VI.id_estado WHERE FAS.id_fase=:idFase AND EST.nom_estado<>\'Eliminado\'')
        query = query.params(idFase=idFaseItem)
        items = list(query)                

        return dict(page='Administrar Items', items=items)
        
    @expose('projectmanager.templates.newItem')
    def newItem(self, **kw):
	
	fase_id = kw['id_fase'] 
	
	listTipoItem = DBSession.query(TipoItem).filter(TipoItem.id_fase == fase_id).all()
	
	options=[]
	for itemEnviar in listTipoItem:
            options.append([itemEnviar.id_tipo_item,itemEnviar.nom_tipo_item])

        tmpl_context.form = create_new_item
        
        return dict(page='Nuevo Item', type_options = options)    	        
    
    @expose()
    def saveItem(self, **kw):
        unEstado = DBSession.query(Estado).filter_by(nom_estado="Inicial").one()
        unTipoItem = DBSession.query(TipoItem).filter_by(id_tipo_item=kw['tipoItem']).one()
        unTipoItem.cont_prefijo = unTipoItem.cont_prefijo + 1                
        DBSession.flush()
        lg_name=request.identity['repoze.who.userid']
        unUsuario = DBSession.query(Usuario).filter(Usuario.login_name==lg_name).one()
        
        unItem = Item()
        unItem.cod_item = str(unTipoItem.prefijo) + str(unTipoItem.cont_prefijo)
        
        aItemSelecionado = kw['tipoItem']
        unTipoItem_ = DBSession.query(TipoItem).filter(TipoItem.id_tipo_item == aItemSelecionado).one()
        unItem.nom_item = kw['nomItem']
        unItem.tipoItem = unTipoItem_          
        DBSession.add(unItem)

        

        nuevaVersionItem = VersionItem()
        nuevaVersionItem.item = unItem        
        nuevaVersionItem.nro_version_item = 0
        nuevaVersionItem.estado = unEstado
       # nuevaVersionItem.tipoItem = unTipoItem
        nuevaVersionItem.tipoItem = unTipoItem_         
        nuevaVersionItem.usuarioModifico = unUsuario
        nuevaVersionItem.fecha = "10/06/2011"
        nuevaVersionItem.observaciones = kw['observaciones']
        #unaVersionItem.peso = kw['peso']
        
        DBSession.add(nuevaVersionItem)  
        
        for atributo in DBSession.query(Atributo).filter_by(tipoItem=unTipoItem):
            nuevoAtributoItem = AtributoItem()
            nuevoAtributoItem.atributo = atributo
            nuevoAtributoItem.versionItem = nuevaVersionItem        
            nuevoAtributoItem.val_atributo = atributo.val_default
            DBSession.add(nuevoAtributoItem)   
      
        flash(_("Se ha creado un nuevo Item: %s") %kw['nomItem'],'info')
        redirect("atributosItem?id="+str(nuevaVersionItem.id_version_item))

    @expose('projectmanager.templates.atributosItem')
    def atributosItem(self, **kw):        
        #tmpl_context.form = atributos_item
        unaVersionItem = DBSession.query(VersionItem).filter(VersionItem.id_version_item==kw['id']).one()
        atributosItem = DBSession.query(AtributoItem).filter(AtributoItem.versionItem==unaVersionItem)                
        return dict(versionItem=unaVersionItem,atributosItem=atributosItem)            

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

