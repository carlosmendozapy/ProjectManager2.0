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


''' Controlador que permite cambiar el estado de una Linea Base Abierta
    a un estado Pendiente de Aprobacion '''
    
class cambiarEstadoPendienteController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    nro_lb_id = None

    '''Despliega la lista de items actualizados y no actualizados correspondientes
       a una linea base abierta para poder pasarlas a un estado pendiente de aprobacion
    '''
    @expose('projectmanager.templates.lineaBase.cambiarEstadoPendiente')
    def index(self, **kw):    
        
        self.nro_lb_id = kw['idlineaBase'] 
        print'entra aca'

        '''traer todas las versiones de items que pertenecen a la lineas base abierta'''
        lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == self.nro_lb_id).one()        
        itemlineabase = lineaBase.item
                
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
            
        return dict(itemActualizados = cambios, itemAnteriores = sinCambios, idlineaBase = self.nro_lb_id) 
            
    ''' La linea base pasa a un estado pendiente de aprobacion almacenando las nuevas versiones de item
        que pertenecen a la misma '''
    @expose()
    def pendiente(self, **kw): 
                
        self.nro_lb_id = kw['idlineaBase']

            
        '''traer todas las versiones de items que pertenecen a la linea base abierta'''
        lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == self.nro_lb_id).one()        
        itemlineabase = lineaBase.item
        
        estadoItem = DBSession.query(Estado).filter(Estado.nom_estado == 'Confirmado').one()
        estadoR = DBSession.query(Estado).filter(Estado.nom_estado == 'En Revision').one()
        estadoA = DBSession.query(Estado).filter(Estado.nom_estado == 'Aprobado').one()
        
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
                    if (item3.estado != estadoItem):
                        flash(_("ATENCION!! EXISTEN ITEMS DE LA FASE QUE AUN NO HAN SIDO CONFIRMADOS"),'warning')
                        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
                        
                    cambios.append(item3)
                    break
                if((item.id_item == item3.id_item) and(item3.nro_version_item == item.nro_version_item)):
                    if (item3.estado != estadoItem):
                        flash(_("ATENCION!! EXISTEN ITEMS DE LA FASE QUE AUN NO HAN SIDO CONFIRMADOS"),'warning')
                        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
                    sinCambios.append(item3)
                    break
                    
                    
                    
        listaGuardar = []            
        for itemActualizado in cambios:
            itemSelect = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == itemActualizado.id_version_item).one()
            #itemSelect.estado = estadoA
            listaGuardar.append(itemSelect)
            
        for itemNoActualizado in sinCambios:
            itemSelect1 = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == itemNoActualizado.id_version_item).one()
            #itemSelect1.estado = estadoA
            listaGuardar.append(itemSelect1)
        
        #Esta variable del tipo lista tendra todos los items relacionados a 'item'
        ListaItems = []  
        ListaIzq = []
        for itemP in listaGuardar:
            #El item modificado que se quiere volver a la LB
            item = DBSession.query(VersionItem).\
            filter(VersionItem.id_version_item==itemP.id_version_item).one()
            
            #Obtener la red de relaciones desde este item
            item.initGraph(item)
            #Obtenemos relaciones de la Izquierda
            ListaItems.extend(item.getRelacionesIzq(item.id_version_item))
            ListaIzq.extend(item.getRelacionesIzq(item.id_version_item))
            
            #Obtenemos relaciones de Abajo
            hijos=item.getHijos(item.id_version_item)        
            ListaItems.extend(item.getHijosNietos(hijos))
            
            #Obtenemos relaciones de la Derecha
            ListaItems.extend(item.getRelacionesDer(item.id_version_item))
            
            bandR = 0
            for test in ListaItems:
                itemRelacion = DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item == test.id_version_item).one()
                if (itemRelacion.estado == estadoR):
                    bandR = 1
        
                if (bandR == 1):
                    break
        
            if (bandR == 1):
                    break
        
        band = 1
        if (ListaItems == []):
            band = 0
            flash(_("ATENCION!! NO EXISTEN ITEMS","warning"))
            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        elif(bandR == 1):                
            flash(_("ATENCION!! EXISTEN ITEMS DE OTRAS FASES EN REVISION"),"warning")
            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))
        else:
            
            estadoP = DBSession.query(Estado).filter(Estado.nom_estado == 'Pendiente').one()
            lineaBase = DBSession.query(NroLineaBase).filter(NroLineaBase.id_nro_lb == self.nro_lb_id).one()       
            lineaBase.id_estado = estadoP.id_estado
            estadoE = DBSession.query(Estado).filter(Estado.nom_estado == 'Eliminado').one()
    
            faseList = DBSession.query(Fase).\
                filter(Fase.id_proyecto==Globals.current_project.id_proyecto).\
                order_by(Fase.nro_fase)
                            
            print '*******************************************************************************************************************************************'
            print faseList
                
            if(Globals.current_phase.nro_fase != faseList.first().nro_fase):     
                for item in ListaIzq:
                    if (len(item.NroLineaBase)>0 and item.estado != estadoA):
                        flash(_("ATENCION!! DEBE APROBAR PRIMERO LA LINEA BASE DE LA FASE ANTERIOR"),'warning')
                        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))              


            Globals.current_phase.id_estado = estadoP.id_estado

            lista=[]
            for i in lineaBase.item:
                lista.append(i)

            for element in lista:
                lineaBase.item.remove(element)
                DBSession.flush() 
            
            for item in listaGuardar:
                itemSelect3 = DBSession.query(VersionItem).\
                         filter(VersionItem.id_version_item == item.id_version_item).one()
                if(itemSelect3.estado == estadoItem):
                    itemSelect3.estado = estadoA 
                    lineaBase.item.append(itemSelect3)
            
            DBSession.add(lineaBase)
            DBSession.flush()     
        
            flash(_("LA LINEA BASE HA PASADO A UN ESTADO PENDIENTE DE APROBACION"))
            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))        
        
