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
from tw.forms import RadioButtonList
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
		
        mapy=dict()        
        for tipo in tipo_dato_options:
            if str(tipo.nom_tipo_dato) == 'texto':
                mapy[int(tipo.id_tipo_dato)] = ['def_texto']
            elif str(tipo.nom_tipo_dato) == 'numerico':
                mapy[int(tipo.id_tipo_dato)] = ['def_numerico']
            elif str(tipo.nom_tipo_dato) == 'fecha':
                mapy[int(tipo.id_tipo_dato)] = ['def_fecha']
                   
		id_tipo= HiddenField()
          
		nom_atributo= TextField(label_text='Nombre Atributo', 
                              help_text='Nombre del atributo',
                              validator=NotEmpty)        
        
		tipo_dato = twd.HidingRadioButtonList(label_text='Tipo de Dato',
                                    help_text='El tipo de dato del atributo',
                                    options= tipo_dato_options,                                    
                                    validator=NotEmpty(messages={'missing':'Por favor seleccione un Tipo de Dato'}),                                    
                                    mapping=mapy)       
                              
        def_numerico = TextField(label_text='Valor por Defecto',
                                validator=formencode.All(Int(min=(-sys.maxint-1), max=sys.maxint)),
                                help_text='Favor Escriba un valor por defecto')                  
                                    
        def_fecha = CalendarDatePicker(label_text='Valor por Defecto',
                                      date_format='%d/%m/%Y',
                                      validator=formencode.All(DateConverter(month_style='dd/mm/yyyy')),
                                      help_text='Favor escoja una fecha por defecto')
                                  
        def_texto = TextArea(label_text='Valor por Defecto', 
                            attrs={'maxlength':255},
                            cols=51,
                            rows=5,                            
                            help_text='Favor Escriba un texto por defecto')
                            
        save_as = RadioButtonList(label_text= 'Aplicar a Items',
                                  options=[(0,'Nuevos'),(1,'Nuevos y Existentes')],
                                  default=0,
                                  help_text='Seleccione la opcion de guardado')
   
create_new_atributo = NewAtributoForm("create_new_atributo", action='saveAtributo')
