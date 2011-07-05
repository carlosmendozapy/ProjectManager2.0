from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import PasswordField
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from tw.forms.validators import FieldsMatch
import formencode
from formencode import *
from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.roles import Usuario
from projectmanager.model.entities import TipoItem
from projectmanager.model.proyecto import Fase
from projectmanager.lib.app_globals import Globals

class FilteringSchema(Schema):
    filter_extra_fields = False
    allow_extra_fields = True
    ignore_key_missing = False
    
class UniqueTypeName(formencode.FancyValidator):
    tiponames=[]        
    def _to_python(self, value, state):
        tiponames=[]
        fase = DBSession.query(Fase).\
			filter(Fase.id_fase==Globals.current_phase.id_fase).one()
			
        tipos=DBSession.query(TipoItem).\
			filter(TipoItem.fase==fase).all()
        for tipo in tipos:
            self.tiponames.append(tipo.nom_tipo_item)      
        if value in self.tiponames:
            raise formencode.Invalid(u'Este nombre de Tipo de Item ya existe, favor utilice otro',\
                    value, state)
        return value    
    
class NewTipoItemForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        
        nom_tipo = TextField(label_text='Nombre Tipo de Item', 
                              help_text='Nombre del Tipo de Item',                              
                              validator=formencode.All(NotEmpty,UniqueTypeName()))         
  
create_new_tipoItem = NewTipoItemForm("create_new_tipoItem", action='saveTipoItem')
