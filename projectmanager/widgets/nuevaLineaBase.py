from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import MultipleSelectField
from tw.forms import TextArea
from tw.forms import PasswordField
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from formencode import *
    
class NuevaLineaBaseForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
 
        nombreLineaBase = TextField(label_text='Nombre de la Linea Base', 
                                validator=NotEmpty,
                                maxlength=20,
                                size=20,
                                help_text='Nombre de la Linea Base: Maximo 20 Caracteres',                              
                                )        
        
        descripcionLineaBase = TextArea(label_text='Descripcion',
                                validator=NotEmpty,
                                help_text='Breve Descripcion de la Linea Base: Maximo 200 Caracteres',
                                cols=40,
                                rows=5,
                                attrs={'maxlength':200})
        
        listaItem = MultipleSelectField(label_text='Lista de Items',                                
                                validator=ForEach(Int, if_missing=NoDefault),
                                help_text='Establece la lista de items. Para seleccionar varios items mantenga presionada la tecla CTRL mientras elige',)   
        
                     
  
creacion_nueva_lineaBase = NuevaLineaBaseForm("creacion_nueva_lineaBase", action='guardarLineaBase')
