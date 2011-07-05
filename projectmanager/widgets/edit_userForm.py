from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import SingleSelectField
from tw.forms import TextField
from tw.forms import TextArea
from tw.forms import HiddenField
from tw.forms import PasswordField
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
from tw.forms.validators import FieldsMatch
import formencode
from formencode import *
from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.roles import Usuario
from projectmanager.lib.app_globals import Globals

class FilteringSchema(Schema):
    filter_extra_fields = False
    allow_extra_fields = True
    ignore_key_missing = False
    
class UniqueUserName(formencode.FancyValidator):
    usernames=[]        
    def _to_python(self, value, state):
        users = DBSession.query(Usuario).filter(Usuario.id_usuario != Globals.id_user_to_edit).all()
        for user in users:           
            self.usernames.append(user.login_name)      
        
        if value in self.usernames:
            raise formencode.Invalid(u'Este nombre de login ya existe, favor utilice otro',\
                    value, state)
        return value
        
class EditUserForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        
        id = HiddenField(validator=NotEmpty)
        userName = TextField(label_text='Nombre y Apellido', 
                              help_text='Nombre real del usuario',                              
                              validator=NotEmpty)        
        loginName = TextField(label_text='Nombre de usuario',
                            validator=formencode.All(NotEmpty,UniqueUserName()))                     
  
edit_user = EditUserForm("edit_user", action='updateUser')
