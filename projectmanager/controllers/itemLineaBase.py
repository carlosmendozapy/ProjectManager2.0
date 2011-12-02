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
from projectmanager.lib.mypredicates import is_type
from projectmanager.lib.app_globals import Globals


# project specific imports
from projectmanager.lib.base import BaseController
from projectmanager.model import DBSession, metadata
from projectmanager.model.proyecto import Fase
from projectmanager.model.configuracion import LineaBase
from projectmanager.model.configuracion import NroLineaBase
from projectmanager.model.roles import Usuario
from projectmanager.model.entities import Estado, VersionItem, Item
from projectmanager.controllers.cambiarEstadoPendiente import cambiarEstadoPendienteController



class itemLineaBaseController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    nro_lb_id = None
    cambiarEstadoPendiente = cambiarEstadoPendienteController()
               
    @expose('projectmanager.templates.lineaBase.itemLineaBase')
    def index(self, **kw):        
      
        try:
            self.nro_lb_id = kw['id_nro_lb'] 
            float(self.nro_lb_id)

            lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == self.nro_lb_id).one()
            idlineaBase = lineaBase.id_nro_lb 

            estado = DBSession.query(Estado).filter(Estado.id_estado == lineaBase.id_estado).one()
            
            print 'pasa el query de items'
            itemList = lineaBase.item
            itemListEnviar = []
            print 'pasa2'
            
            
            for item in itemList:
                item_id = item.id_version_item
                itemEnviar = DBSession.query(VersionItem).filter(VersionItem.id_version_item == item_id).one()
                print 'ITEM DE  LA LINEA BASE ' + itemEnviar.item.nom_item
                itemListEnviar.append(itemEnviar)

            if (len(itemListEnviar) == 0):
                flash(_('ERROR DEL SISTEMA'),'info')
            
            band = 'ok'     
            
            print 'estado linea base ' + estado.nom_estado
            
            return dict(itemlineaBase = itemListEnviar, version = itemList, bandera=band, estado = estado.nom_estado, idlineaBase = idlineaBase ) 
            
        except:
            itemListEnviar = None
            band = "error"
            flash(_('PARAMETRO INCORRECTO'),'info')

            return dict(itemlineaBase = itemListEnviar, bandera=band, estado = 'NINGUNO')    
        
    @expose()
    def abrirLineaBase(self, **kw):

        print 'abrir linea base'


        lineaBase = kw['idlineaBase']   

        estadoD = DBSession.query(Estado).filter(Estado.nom_estado == 'En Desarrollo').one()
        Globals.current_phase.id_estado = estadoD.id_estado

        estadoA = DBSession.query(Estado).filter(Estado.nom_estado == 'Abierta').one()
        usuario = DBSession.query(Usuario).filter(Usuario.login_name == request.identity['repoze.who.userid']).one()
        nroLineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == lineaBase).one()
        
        
            
        aNroLineaBase = NroLineaBase()
        aNroLineaBase.id_linea_base = nroLineaBase.id_linea_base
        aNroLineaBase.nro_linea_base = nroLineaBase.nro_linea_base + 1 
        aNroLineaBase.id_estado = estadoA.id_estado   
        aNroLineaBase.id_usuario_aprobo = usuario.id_usuario  
        
        items = nroLineaBase.item  

        estadoC = DBSession.query(Estado).filter(Estado.nom_estado == 'Confirmado').one()
        for itemGuardar in items:       
            itemGuardar.estado = estadoC
            aNroLineaBase.item.append(itemGuardar)

        
        print 'ABRIR/NUEVA VERSION ID ' 
        print  aNroLineaBase.id_linea_base
        print 'ABRIR/NUEVA nro_linea_base '
        print aNroLineaBase.nro_linea_base
        print 'ABRIR/NUEVA id_estado '
        print aNroLineaBase.id_estado

        DBSession.add(aNroLineaBase)
        DBSession.flush() 
        
        flash(_("LA LINEA BASE HA SIDO ABIERTA"))
        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        
    @expose()
    def aprobar(self, **kw):  
        print '***************************************************************************************************************'
        print 'entro aca'
        lineaBase_id = kw['idlineaBase']   
        nroLineaBaseAprobar = DBSession.query(NroLineaBase).\
                              filter(NroLineaBase.id_nro_lb == lineaBase_id).one()
                              
        items = nroLineaBaseAprobar.item
        
        band = 1
        if (items == []):
            band = 0
            flash(_("ERROR!! NO SE PUEDE APROBAR UNA LINEA BASE SIN ITEMS"))
            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        else:
            
            estadoA = DBSession.query(Estado).filter(Estado.nom_estado == 'Aprobado').one()
            for itemEstado in nroLineaBaseAprobar.item:       
                itemEstado.estado = estadoA
            
            Globals.current_phase.id_estado = estadoA.id_estado
            nroLineaBaseAprobar.id_estado = estadoA.id_estado
            
            DBSession.add(nroLineaBaseAprobar)
            DBSession.flush()     
            
            flash(_("LA LINEA BASE HA SIDO APROBADA"))
            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        
            
    @expose()
    def rechazar(self, **kw):  
        lineaBase_id = kw['idlineaBase']   
        nroLineaBaseRechazar = DBSession.query(NroLineaBase).\
                              filter(NroLineaBase.id_nro_lb == lineaBase_id).one()
        lineaBaseId = DBSession.query(LineaBase).\
                              filter(LineaBase.id_linea_base == nroLineaBaseRechazar.id_linea_base).one()
        
        
        estado = DBSession.query(Estado).filter(Estado.nom_estado == 'Aprobado').one()
        
        anteriorNroLineaBase = DBSession.query(NroLineaBase).\
            filter(NroLineaBase.nro_linea_base == (nroLineaBaseRechazar.nro_linea_base - 1)).\
            filter(NroLineaBase.id_linea_base == lineaBaseId.id_linea_base).one()
        
        Globals.current_phase.id_estado = estado.id_estado
        nroLineaBaseRechazar.id_estado = estado.id_estado
        nroLineaBaseRechazar.nro_linea_base = nroLineaBaseRechazar.nro_linea_base - 1 
        
        
        listaAnterior = nroLineaBaseRechazar.item
        listaNueva = anteriorNroLineaBase.item
        
        lista=[]
        for i in listaAnterior:
            
            lista.append(i)


        for element in lista:
            nroLineaBaseRechazar.item.remove(element)
            DBSession.flush()
            
        for item in listaNueva:
            itemSelect3 = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == item.id_version_item).one()
            itemSelect3.estado = estado
            nroLineaBaseRechazar.item.append(itemSelect3)
        
        DBSession.add(nroLineaBaseRechazar)
        DBSession.flush()     
        
        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        
        
        flash(_("HA SIDO CREADA UNA NUEVA LINEA BASE"))
        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
