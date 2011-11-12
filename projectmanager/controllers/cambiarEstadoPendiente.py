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


class cambiarEstadoPendienteController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    nro_lb_id = None

               
    @expose('projectmanager.templates.lineaBase.cambiarEstadoPendiente')
    def index(self, **kw):    
        
        self.nro_lb_id = kw['idlineaBase'] 
        print'entra aca'

        '''traer todas las versiones de items que pertenecen a la lineas base abierta'''
        lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == self.nro_lb_id).one()        
        itemlineabase = lineaBase.item
        
        Globals.lista_version_anterior = itemlineabase
        
        itemsAnteriores = []
        items=[]
        for item in itemlineabase:
            queryItem = DBSession.query(Item).filter(Item.id_item == item.id_item).one()
            items.append(queryItem)

        print 'pasa esto 1'
        
        versionItem=[]
        for item in items:
            max=0
            for item2 in item.VersionItem:
                if (item2.nro_version_item > max):
                    max = item2.nro_version_item
                    last_version = item2
            versionItem.append(last_version)
        
        print 'pasa esto 2'
        
        cambios=[]
        sinCambios=[]
        for item in itemlineabase:
            for item3 in versionItem:
                if((item.id_item == item3.id_item) and (item3.nro_version_item > item.nro_version_item)):
                    cambios.append(item3)
                    break
                if((item.id_item == item3.id_item) and(item3.nro_version_item == item.nro_version_item)):
                    sinCambios.append(item3)
                    break
                
        print 'pasa esto 3'

        for imprimir in cambios:
        
            print 'CAMBIOS GUARDADOS ' + imprimir.item.nom_item
        
        for imprimir in sinCambios:
        
            print 'sin CAMBIOS GUARDADOS ' + imprimir.item.nom_item
            print 'salio de aca'
            Globals.lista_actualizados = cambios
            Globals.lista_no_actualizados = sinCambios
         
        return dict(itemActualizados = cambios, itemAnteriores = sinCambios, idlineaBase = self.nro_lb_id) 
            
            
    @expose()
    def pendiente(self, **kw): 
        
        print 'vino a pendiente'
        nro_lb_id_ = kw['idlineaBase']
        print 'id_a_Cambiar'
        print nro_lb_id_
        
        
        
        estadoA = DBSession.query(Estado).filter(Estado.nom_estado == 'Aprobado').one()
        estadoItem = DBSession.query(Estado).filter(Estado.nom_estado == 'Confirmado').one()
        estadoP = DBSession.query(Estado).filter(Estado.nom_estado == 'Pendiente').one()
        lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == nro_lb_id_).one()       
        lineaBase.id_estado = estadoP.id_estado

        Globals.current_phase.id_estado = estadoP.id_estado


        lista=[]
        for i in lineaBase.item:
            lista.append(i)


        for element in lista:
            lineaBase.item.remove(element)
            DBSession.flush() 
        
        print 'hizo el remove??'

        
        listaGuardar = []
        
        for itemActualizado in Globals.lista_actualizados:
            itemSelect = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == itemActualizado.id_version_item).one()
            itemSelect.estado = estadoA
            listaGuardar.append(itemSelect)
            
        for itemNoActualizado in Globals.lista_no_actualizados:
            itemSelect1 = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == itemNoActualizado.id_version_item).one()
            itemSelect1.estado = estadoA
            listaGuardar.append(itemSelect1)
        
        for item in listaGuardar:
            itemSelect3 = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == item.id_version_item).one()
            if(itemSelect3.id_estado == estadoA.id_estado):
                lineaBase.item.append(itemSelect3)
        
        DBSession.add(lineaBase)
        DBSession.flush()     
        
        flash(_("LA LINEA BASE HA PASADO A UN ESTADO PENDIENTE DE APROBACION"))
        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))        
        
