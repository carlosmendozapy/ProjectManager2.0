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
    
class NewItemForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
                   
        nomItem = TextField(label_text='Nombre del Item', 
                                maxlength=25,
                                size=25,
                                help_text='Nombre del Item: Maximo 25 Caracteres',                              
                                validator=NotEmpty)
        
        tipoItem = SingleSelectField(label_text='Lista de Tipo de Items',                                
                                validator=NotEmpty,
                                help_text='Establece la lista de tipo de items')
        
        peso = TextField(label_text='Complejidad',
                            maxlength=3,
                            size=3,
                            help_text='Peso o complejidad de realizar alguna modificacion a este item, escala[0-100]',
                            validator=formencode.All(NotEmpty,Int(min=0,max=100)))
	
        observaciones = TextArea(label_text='Observaciones', 
                                cols=40,
                                rows=5,
                                attrs={'maxlength':200},
                                help_text='Nombre del Item: Maximo 25 Caracteres')
        
                       
  
create_new_item = NewItemForm("create_new_item", action='saveItem')
