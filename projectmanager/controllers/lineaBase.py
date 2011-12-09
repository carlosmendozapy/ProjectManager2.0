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


from projectmanager.widgets.nuevaLineaBase import creacion_nueva_lineaBase
from projectmanager.controllers.itemLineaBase import itemLineaBaseController

#from projectmanager.widgets.edit_projectForm import edit_project


class lineabaseController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = not_anonymous(msg='Debe Ingresar al Sistema para ver esta pagina')
    fase_id = None
    itemLineaBase = itemLineaBaseController()

    
               
    @expose('projectmanager.templates.lineaBase.lineaBase')
    def index(self, **kw):        
        
        try:
            self.fase_id = kw['id_fase'] 
            float(self.fase_id)
            
            listVersionLineasBase=[]
            lineabase_lista = DBSession.query(LineaBase).filter(LineaBase.id_fase == self.fase_id)

            #recorrer todas las lineas base de esa fase y guardar la ultima version de cada linea base
            for lineaBase in lineabase_lista: 
                max = 0
                for nroLb in lineaBase.NroLineaBase:
                    if(nroLb.nro_linea_base > max):
                        max = nroLb.nro_linea_base              
                        maxlb = nroLb
                print 'NROLINEABASE '+nroLb.lineaBase.nom_linea_base
                listVersionLineasBase.append(maxlb)

            for imprimir in listVersionLineasBase:
                print 'PARAMETRO A ENVIAR es ID' 
                print imprimir.id_nro_lb
                print 'PARAMETRO A ENVIAR Ees NOMBRE ' + imprimir.lineaBase.nom_linea_base
                print 'PARAMETRO A ENVIAR Ees DESCRIPCION ' + imprimir.lineaBase.descripcion

            if (len(listVersionLineasBase) == 0):
                flash(_('No se han encontrado Lineas bases'),'info')
            
            band = 'ok'     
            
            return dict(lineasBase = listVersionLineasBase, bandera=band) 
            
        except:
            listVersionLineasBase = None
            band = "error"
            flash(_('PARAMETRO INCORRECTO'),'info')

            return dict(lineasBase = listVersionLineasBase, bandera=band)    
            
               
    @expose('projectmanager.templates.lineaBase.nuevaLineaBase')
    def nuevaLineaBase(self, **kw):
        estado = DBSession.query(Estado).filter(Estado.nom_estado == 'Confirmado').one()
        estadoP = DBSession.query(Estado).filter(Estado.nom_estado == 'Pendiente').one()
        
        list_options = DBSession.query(VersionItem).\
        filter(VersionItem.id_fase == Globals.current_phase.id_fase).\
        filter(VersionItem.estado == estado).\
        filter(VersionItem.ultima_version == u'S').all()
        band=0
        options1 = []
        if (len(list_options) != 0):
            for op in list_options:
                    band=0
                    versionItem = DBSession.query(VersionItem).\
                                    filter(VersionItem.id_version_item == op.id_version_item).one()
                    LBases = versionItem.NroLineaBase
                    has_lb = False
                    
                    if len(LBases) > 0:
                        has_lb = True            
                        estado = None
                        for lb in LBases:
                            estado = lb.estado.nom_estado
                    if(len(LBases) == 0):
                        band = 1
                        options1.append(versionItem)
        
        
        if (len(list_options) != 0 and estado != 'Abierta' and estado != 'Pendiente'):
            options = []
            options2 = []
            for itemEnviar in list_options:
                #options.append([itemEnviar.id_version_item,itemEnviar.item.nom_item])
                options2.append(itemEnviar)
                        
            for itemP in options2:
                antecesores = itemP.Antecesores
                for antecesor in antecesores:
                    itemAntecesor = DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item==antecesor.id_version_item).one()
                                          
                    b=0
                    LBases = itemAntecesor.NroLineaBase
                    has_lb = False                        

                    if(len(LBases) == 0):
                        b = 1
                   
                    if (b == 0):
                        LBases.sort(cmp=None, key= lambda nrolb: nrolb.nro_linea_base, reverse=True)
                        maxlb = LBases[0]
                        if(maxlb.estado == estadoP):
                            flash(_("ATENCION!! DEBE APROBAR PRIMERO LA LINEA BASE DE LA FASE ANTERIOR"),'warning')
                            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))              
                
            for itemEnviar in list_options:
                options.append([itemEnviar.id_version_item,itemEnviar.item.nom_item])    
            
            tmpl_context.form = creacion_nueva_lineaBase
            return dict(page='Nueva Linea Base', type_options = options)                     
        elif (band == 1):
            for itemP in options1:
                antecesores = itemP.Antecesores
                for antecesor in antecesores:
                    itemAntecesor = DBSession.query(VersionItem).\
                        filter(VersionItem.id_version_item==antecesor.id_version_item).one()
                                          
                    b=0
                    LBases = itemAntecesor.NroLineaBase
                    has_lb = False                        

                    if(len(LBases) == 0):
                        b = 1
                   
                    if (b == 0):
                        LBases.sort(cmp=None, key= lambda nrolb: nrolb.nro_linea_base, reverse=True)
                        maxlb = LBases[0]
                        if(itemAntecesor.estado != estadoA and \
                        itemAntecesor.ultima_version == 'S' and \
                        itemAntecesor.estado.nom_estado != "Eliminado"):
                            
                            flash(_("ATENCION!! DEBE APROBAR PRIMERO LA LINEA BASE DE LA FASE ANTERIOR"),'warning')
                            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase))              
                   
                        if (maxlb.estado == estadoP):
                            flash(_("ATENCION!! DEBE APROBAR PRIMERO LA LINEA BASE DE LA FASE ANTERIOR"),'warning')
                            redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase)) 
                   
                    if(b == 1):
                        flash(_("ATENCION!! PRIMERO DEBE CREAR LA LINEA BASE DE LA FASE ANTERIOR"),'warning')
                        redirect("/lineaBase/index?id_fase="+str(Globals.current_phase.id_fase)) 
                   
                    
            tmpl_context.form = creacion_nueva_lineaBase
            return dict(page='Nueva Linea Base', type_options = options1)                     
        else:        
            flash(_("No existen items para una nueva Linea Base"),'warning')
            redirect("index?id_fase="+str(self.fase_id))
    
    @validate(creacion_nueva_lineaBase,error_handler=nuevaLineaBase)
    @expose()
    def guardarLineaBase(self, **kw):
        """
        Funcion que se encarga de guardar los datos introducidos en el formulario
        para la nueva linea base.
        """
        aLineaBase = LineaBase()
         
        fase = DBSession.query(Fase).filter(Fase.id_fase == self.fase_id).one()   
        usuario = DBSession.query(Usuario).filter(Usuario.login_name == request.identity['repoze.who.userid']).one()
        estado =DBSession.query(Estado).filter(Estado.nom_estado == 'Aprobado').one()


        aLineaBase.id_fase = fase.id_fase
        aLineaBase.nom_linea_base = kw['nombreLineaBase']
        aLineaBase.descripcion = kw['descripcionLineaBase']
        aItemsSelecionados = kw['listaItem']
    
        DBSession.add(aLineaBase) 
        DBSession.flush()    
        print aLineaBase.id_linea_base
        
        aNroLineaBase = NroLineaBase()
        aNroLineaBase.id_linea_base = aLineaBase.id_linea_base
        aNroLineaBase.nro_linea_base = 1
        aNroLineaBase.id_estado = estado.id_estado   
        aNroLineaBase.id_usuario_aprobo = usuario.id_usuario  
        
        for items1 in aItemsSelecionados:
              
            itemSelect = DBSession.query(VersionItem).filter(VersionItem.id_version_item ==items1).one()
            print itemSelect.observaciones
            itemSelect.id_estado = estado.id_estado
            aNroLineaBase.item.append(itemSelect)
              
        
        DBSession.add(aNroLineaBase)
        DBSession.flush() 
        flash(_("Se ha creado una nueva Linea Base: %s") %kw['nombreLineaBase'],'info')
        redirect("index?id_fase="+str(self.fase_id))
        
    @expose('projectmanager.templates.lineaBase.lineaBase')
    def search(self, **kw):
        word = '%'+kw['key']+'%'        
        
        listVersionLineasBase=[]
        lineabase_lista = DBSession.query(LineaBase).\
                          filter(LineaBase.id_fase == Globals.current_phase.id_fase).\
                          filter(LineaBase.nom_linea_base.like(word)).\
                          order_by(LineaBase.nom_linea_base)
        return dict(lineaBase=lineabase_lista)
        
        
    
