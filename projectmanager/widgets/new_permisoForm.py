from projectmanager.lib.app_globals import Globals
from sqlalchemy.orm.exc import NoResultFound
from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import CheckBoxList
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from projectmanager.model import DBSession, metadata
from projectmanager.model.roles import EntidadSistema
from projectmanager.model.roles import Privilegios
from projectmanager.model.roles import Permisos
from projectmanager.model.roles import Rol
import formencode
from formencode import *

class UniqueEntidad(formencode.FancyValidator):
    entidades=[]        
    def _to_python(self, value, state):
        rol = DBSession.query(Rol).filter(Rol.id_rol==Globals.current_rol.id_rol).one()        
        self.entidades=[]
        for permiso in rol.permisos:                        
            self.entidades.append(str(permiso.entidad.id_entidad))
       
        if value in self.entidades:
            raise formencode.Invalid(u'Ya se establecio un permiso para esta Entidad, favor seleccione otra o editela',\
                    value, state)
        return value    
        
class NewPermisoForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        
        options_Entidad=DBSession.query(EntidadSistema.id_entidad,EntidadSistema.nom_entidad).all()        
        options_Privilegios= DBSession.query(Privilegios.id_privilegio,Privilegios.nom_privilegio).all()
          
        entidad = SingleSelectField(label_text='Entidad',                                
                                help_text='Seleccione sobre que entidad/elemento desea establecer permisos',
                                options = options_Entidad,
                                validator=formencode.All(UniqueEntidad()))
        privilegios = CheckBoxList(label_text='Privilegios',                                 
                                help_text='Seleccione los privilegios que desea tener sobre la entidad seleccionada',                              
                                options = options_Privilegios)
       
create_new_permission = NewPermisoForm("create_new_permission", action='savePermiso')
