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
from formencode import *
    
class NewProjectForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
           
        projectName = TextField(label_text='Nombre del Proyecto', 
                                maxlength=25,
                                size=25,
                                help_text='Nombre del Proyecto: Maximo 25 Caracteres',                              
                                validator=NotEmpty)        
        descripcion = TextArea(label_text='Descripcion',
                                help_text='Breve Descripcion del objeto del Proyecto: Maximo 200 Caracteres',
                                cols=40,
                                rows=5,
                                attrs={'maxlength':200})                
  
create_new_project = NewProjectForm("create_new_project", action='saveProject')
