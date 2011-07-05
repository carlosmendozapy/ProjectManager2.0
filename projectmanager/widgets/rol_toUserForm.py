from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CheckBoxList
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import PasswordField
from tw.forms import HiddenField
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from tw.forms.validators import FieldsMatch
from formencode import *

class FilteringSchema(Schema):
    filter_extra_fields = False
    allow_extra_fields = True
    ignore_key_missing = False
    
class RolToUserForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):
          id_usuario = HiddenField()
          roles = CheckBoxList()
          
              
  
asignRol_to_user = RolToUserForm("asignRol_to_user", action='saveRolToUser')
