# -*- coding: utf-8 -*-
"""File Upload Controller"""

from tg import expose, flash, require, url, request, redirect, response
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from tg import session
from datetime import datetime
from projectmanager.lib.base import BaseController
from tg.controllers import CUSTOM_CONTENT_TYPE
from projectmanager.model import DBSession, metadata
#from fileupload.controllers.error import ErrorController
#from projectmanager.model.userfile import UserFile
from projectmanager.lib.app_globals import Globals
from projectmanager.model.entities import Atributo
from projectmanager.model.entities import AtributoArchivo
from projectmanager.model.entities import AtributoItem
from projectmanager.model.entities import VersionItem
from projectmanager.model.entities import Antecesor
from projectmanager.model.entities import Padre

from projectmanager.model.roles import Usuario
from sqlalchemy.orm.exc import NoResultFound

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
        
        aFile=[]
        if 'validate' in kw:
            flash(_('Favor seleccione un archivo'),'warning')
            aFile=None
            
        else:
            Globals.current_atributo = DBSession.query(AtributoItem).\
                filter(AtributoItem.id_atributo==int(kw['idAtributo'])).\
                filter(AtributoItem.id_version_item==int(kw['idVersionItem'])).\
                one()
            
            aFile = Globals.current_atributo.atributoArchivo
            
        return dict(current_file=aFile)
        
    @expose()
    def save(self, userfile):
        forbidden_files = [".js", ".htm", ".html", ".mp3"]
        for forbidden_file in forbidden_files:
            if not hasattr(userfile,'filename'):
                redirect('file_upload?validate=error')
            elif userfile.filename.find(forbidden_file) != -1:
                return redirect("/")
        
        versionItem = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item == Globals.\
                   current_item.id_version_item).one()
               
        filecontent = userfile.file.read()
        new_file = AtributoArchivo(filename=userfile.filename, filecontent=filecontent)        
        DBSession.add(new_file)
        
        atributo = DBSession.query(AtributoItem).\
            filter(AtributoItem.id_version_item==versionItem.id_version_item).\
            filter(AtributoItem.id_atributo == Globals.current_atributo.id_atributo).one()
                            
        atributo.atributoArchivo = new_file
               
       
        redirect("/item/atributosItem?id_version="+\
        str(versionItem.id_version_item) + ";frompage=item")
    
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


