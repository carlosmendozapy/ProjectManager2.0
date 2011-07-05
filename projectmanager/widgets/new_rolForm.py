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
from formencode import *
    
class NewRolForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
           
        tipoRol = SingleSelectField(label_text='Tipo de Rol',                                
                                help_text='Establece el tipo de rol.',
                                validator=NotEmpty)
        nombreRol = TextField(label_text='Nombre del Rol', 
                                maxlength=20,
                                size=20,
                                help_text='Nombre del Rol: Maximo 20 Caracteres',                              
                                validator=NotEmpty)        
        descripcion = TextArea(label_text='Descripcion',
                                help_text='Breve Descripcion del Rol: Maximo 200 Caracteres',
                                cols=40,
                                rows=5,
                                attrs={'maxlength':200})                
        
  
create_new_rol = NewRolForm("create_new_rol", action='saveRol')
