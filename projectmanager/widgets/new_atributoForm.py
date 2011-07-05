from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import HiddenField
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from tw.forms.validators import FieldsMatch
import formencode
from formencode import *
from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.entities import TipoDatoAtributo 

class FilteringSchema(Schema):
    filter_extra_fields = False
    allow_extra_fields = True
    ignore_key_missing = False
     
class NewAtributoForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        tipo_dato_options = DBSession.query(TipoDatoAtributo.id_tipo_dato,TipoDatoAtributo.nom_tipo_dato).all()
        
        id_tipo = HiddenField()   
        nom_atributo = TextField(label_text='Nombre Atributo', 
                              help_text='Nombre del atributo',                              
                              validator=NotEmpty)        
        
        tipo_dato = SingleSelectField(label_text='Tipo de Dato',
                                    help_text='El tipo de dato del atributo',
                                    options= tipo_dato_options,
                                    validator=NotEmpty)
      
create_new_atributo = NewAtributoForm("create_new_atributo", action='saveAtributo')
