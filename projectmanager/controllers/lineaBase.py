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
        
        list_options = DBSession.query(VersionItem).\
        filter(VersionItem.id_fase == Globals.current_phase.id_fase).\
        filter(VersionItem.estado == estado).\
        filter(VersionItem.ultima_version == u'S').all()
		
        options =[]
        for itemEnviar in list_options:
            print '***************************************************************************'
            print 'LINEA BASE ITEMS ' + itemEnviar.item.nom_item
            options.append([itemEnviar.id_version_item,itemEnviar.item.nom_item])
			
        """
        listLineasBase =[]
        listItems =[]
        
        #TOdas las lineas base que pertenecen a la fase actual
        lb = DBSession.query(LineaBase).filter(LineaBase.id_fase == self.fase_id)
   
        
        #Todos los items que pertenecen a la fase actual
        item_list = DBSession.query(Item).join(['tipoItem', 'fase']).\
                    filter(Fase.id_fase == Globals.current_phase.id_fase).all()
        
        
        estado = DBSession.query(Estado).filter(Estado.nom_estado == 'Confirmado').one()
        '''TODAS LAS VERSIONES DE ITEM QEU EXISTAN EN UNA FASE'''        
        version_item_list = DBSession.query(VersionItem).join(['tipoItem', 'fase']).filter(Fase.id_fase==self.fase_id).all()

    
        #recorrer todas las lineas base de esa fase y guardar la ultima version de cada linea base
        for lineaBase in lb: 
            max = 0
            for nroLb in lineaBase.NroLineaBase:
                if(nroLb.nro_linea_base > max):
                    max = nroLb.nro_linea_base              
                    maxlb = nroLb
            print 'NROLINEABASE '+nroLb.lineaBase.nom_linea_base
            listLineasBase.append(maxlb)
            '''traer todas las versiones de items que pertenecen a la ultima version de 
                todas las lineas base aprobadas de esa fase'''
        for Ver_items in listLineasBase:
            item1 = Ver_items.item
            print 'pasa bien'
            for item2 in item1:
                listItems.append(item2)
            
                
        #recorrer todas las versiones item y traer la ultima version de cada item qeu pertenece a una fase
        versionItem = []
        for item in item_list:
            print 'nombre ITEM ' + item.nom_item
            '''Este primer for recorre la lista de items de la fase'''
            max = 0            
            for version_item in item.VersionItem:
                '''Este segundo for recorre la lista de VersionItem que hay en cada Item'''
                if (version_item.nro_version_item > max):
                    max = version_item.nro_version_item
                    last_version = version_item
            print 'Nom ultima version ' + last_version.item.nom_item
            versionItem.append(last_version)
       
        
        itemFactibles=[]
        for item in versionItem:
            band=0
            for item3 in listItems:
                band = 0
                if(item.id_version_item == item3.id_version_item): 
                    band = 1
                    break
            if(band == 0):
                if (item.id_estado == estado.id_estado ):
                    itemFactibles.append(item)
                    print 'item a mostrar '
                    print item.id_version_item
                else:
                    band = 0

        options=[]
        for itemEnviar in itemFactibles:
            if (itemEnviar.id_estado == estado.id_estado ):
                print 'LINEA BASE ITEMS ' + itemEnviar.item.nom_item
                options.append([itemEnviar.id_version_item,itemEnviar.item.nom_item])

        tam = len(itemFactibles)
        print 'TAMANHO'
        print tam
        
        tmpl_context.form = creacion_nueva_lineaBase
       
        
        #options = DBSession.query(item.id_tipo, TipoRol.nom_tipo_rol) 
        """
        tmpl_context.form = creacion_nueva_lineaBase
                 
        return dict(page='Nueva Linea Base', type_options = options)
    
    #ACA SE DEBE USAR TRANSACCION     
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
            aNroLineaBase.item.append(itemSelect)
              
        
        DBSession.add(aNroLineaBase)
        DBSession.flush() 
             
           
        flash(_("Se ha creado una nueva Linea Base: %s"))
        redirect("index?id_fase="+str(self.fase_id))
        
    @expose('projectmanager.templates.lineaBase.lineaBase')
    def search(self, **kw):
        word = '%'+kw['key']+'%'        
        
        listVersionLineasBase=[]
        lineabase_lista = DBSession.query(LineaBase).\
                          filter(LineaBase.id_fase == Globals.current_phase.id_fase)

        for lineaBase in lineabase_lista: 
            max = 0
            for nroLb in lineaBase.NroLineaBase:
                if(nroLb.nro_linea_base > max):
                    max = nroLb.nro_linea_base              
                    maxlb = nroLb
            print 'NROLINEABASE '+nroLb.lineaBase.nom_linea_base
            listVersionLineasBase.append(maxlb.lineaBase.nom_linea_base)
            
        return dict(lineasBase=listVersionLineasBase)

        
        
    
