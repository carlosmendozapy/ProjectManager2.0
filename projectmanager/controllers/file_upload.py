# -*- coding: utf-8 -*-
"""File Upload Controller"""

from tg import expose, flash, require, url, request, redirect, response
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from tg import session

from projectmanager.lib.base import BaseController
from tg.controllers import CUSTOM_CONTENT_TYPE
from projectmanager.model import DBSession, metadata
#from fileupload.controllers.error import ErrorController
#from projectmanager.model.userfile import UserFile
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import AtributoArchivo
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import VersionItem

from repoze.what import predicates
from repoze.what.predicates import has_permission


__all__ = ['FileUploadController']


class FileUploadController(BaseController):
    """
    The root controller for the fileupload application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """    

    #error = ErrorController()

    """    allow_only = has_permission('admin',
                                msg=l_('Solo para personas con permisos de  "Administracion"'))"""    

    @expose('projectmanager.templates.file_upload')
    def file_upload(self, **kw):
        idAtributo = kw['idAtributo']
        idVersionItem = kw['idVersionItem']

        session['idAtributo'] = idAtributo
        session['idVersionItem'] = idVersionItem
        session.save()               

        q = DBSession.query(AtributoItem)
        q = q.from_statement('SELECT * FROM \"ATRIBUTO_ITEM\" WHERE id_atributo=:idAtributoArch AND id_version_item=:idVersionItemArch')
        q=  q.params(idAtributoArch=idAtributo)
        q=  q.params(idVersionItemArch=idVersionItem)        
        atributoItem = q.first()        

        current_files = DBSession.query(AtributoArchivo).filter(AtributoArchivo.id == atributoItem.id_archivo)
        return dict(current_files=current_files, idVersionItem=idVersionItem)
        
    @expose()
    def save(self, userfile):
        forbidden_files = [".js", ".htm", ".html", ".mp3"]
        for forbidden_file in forbidden_files:
            if userfile.filename.find(forbidden_file) != -1:
                return redirect("/")
        filecontent = userfile.file.read()
        new_file = AtributoArchivo(filename=userfile.filename, filecontent=filecontent)        
        DBSession.add(new_file)
        idAtributo = session.get('idAtributo',None)
        idVersionItem = session.get('idVersionItem',None)
        q = DBSession.query(AtributoItem)
        q = q.from_statement('SELECT * FROM \"ATRIBUTO_ITEM\" WHERE id_atributo=:idAtributoArch AND id_version_item=:idVersionItemArch')
        q=  q.params(idAtributoArch=idAtributo)
        q=  q.params(idVersionItemArch=idVersionItem)        
        atributoItem = q.first()        

	'''atributoItem = DBSession.query(AtributoItem).filter(AtributoItem.atributo.id_atributo == idAtributo).filter(AtributoItem.versionItem.id_version_item == idVersionItem)'''
        atributoItem.atributoArchivo = new_file
        DBSession.flush()
        #redirect("/file_upload/view/"+str(new_file.id))
        redirect("/item/atributosItem?id_version="+str(atributoItem.versionItem.id_version_item))
    
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def view(self, fileid):
        try:
            userfile = DBSession.query(AtributoArchivo).filter_by(id=fileid).one()
        except:
            redirect("/")
        content_types = {
            'display': {'.png': 'image/jpeg', '.jpeg':'image/jpeg', '.jpg':'image/jpeg', '.gif':'image/jpeg', '.txt': 'text/plain'},
            'download': {'.pdf':'application/pdf', '.zip':'application/zip', '.rar':'application/x-rar-compressed'}
        }
        for file_type in content_types['display']:
            if userfile.filename.endswith(file_type):
                response.headers["Content-Type"] = content_types['display'][file_type]
        for file_type in content_types['download']:
            if userfile.filename.endswith(file_type):
                response.headers["Content-Type"] = content_types['download'][file_type]
                response.headers["Content-Disposition"] = 'attachment; filename="'+userfile.filename+'"'
        if userfile.filename.find(".") == -1:
            response.headers["Content-Type"] = "text/plain"
        return userfile.filecontent
    
    @expose()
    def delete(self, fileid):
        try:
            userfile = DBSession.query(AtributoArchivo).filter_by(id=fileid).one()
        except:
            return redirect("/")
        DBSession.delete(userfile)
        return redirect("/")


