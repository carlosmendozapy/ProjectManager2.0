import sys
import tw.dynforms as twd
from sys import maxint
from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import HiddenField
from tw.forms import CheckBoxList
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

class NewAtributoForm(twd.HidingTableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    nclude_dynamic_js_calls = True
            
    class fields(WidgetsList):   
       tipo_dato_options = DBSession.query(TipoDatoAtributo.id_tipo_dato,TipoDatoAtributo.nom_tipo_dato).all()
        
       id_tipo= HiddenField()
          
       nom_atributo= TextField(label_text='Nombre Atributo', 
                              help_text='Nombre del atributo')        
        
       tipo_dato = twd.HidingSingleSelectField(label_text='Tipo de Dato',
                                    help_text='El tipo de dato del atributo',
                                    options= tipo_dato_options,
                                    validator=NotEmpty,
                                    mapping={
										1:['def_texto'],
										2:['def_numerico'],
										3:['def_fecha'],                                    
                                    })   
       
       subtitulo = CheckBoxList(label_text='Valor por Defecto:',options=[])
       
       def_numerico = TextField(label_text='Numerico',
                                validator=formencode.All(Int(min=(-sys.maxint-1), max=sys.maxint)),
                                help_text='Favor Escriba un valor por defecto')                  
                                    
       def_fecha = CalendarDatePicker(label_text='Fecha',
                                      date_format='%d/%m/%Y',
                                      validator=formencode.All(DateConverter(month_style='dd/mm/yyyy')),
                                      help_text='Favor escoja una fecha por defecto')
                                  
       def_texto = TextField(label_text='Texto',
                            attrs={'maxlength':255},                            
                            help_text='Favor Escriba un texto por defecto')
   
create_new_atributo = NewAtributoForm("create_new_atributo", action='saveAtributo')
