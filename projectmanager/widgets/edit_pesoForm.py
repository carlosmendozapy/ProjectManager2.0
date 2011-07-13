import sys
from sys import maxint
from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import HiddenField
from tw.forms.calendars import CalendarDatePicker
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from tw.forms.validators import FieldsMatch
import formencode
from formencode import *
from projectmanager.model import DBSession, metadata
from projectmanager.lib.app_globals import Globals
from projectmanager.model.proyecto import Fase
from projectmanager.model.entities import Estado
from projectmanager.model.entities import VersionItem
    
class EditPesoForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        help = 'Minimo=0, Maximo=100'
        id_atributo = HiddenField()     
        id_version_item = HiddenField()
        
        valor = TextField(label_text='Peso,',
                          validator=formencode.All(NotEmpty,
                                                   Int(min=0, max=100)),
                          help_text=help)
       
edit_atributo_peso = EditPesoForm("edit_atributo_peso", action='updateAtributoPeso')
