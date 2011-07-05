from projectmanager.lib.app_globals import Globals
from sqlalchemy.orm.exc import NoResultFound
from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import HiddenField
from tw.forms import CheckBoxList
from tw.forms.validators import Int
from tw.forms.validators import NotEmpty
from tw.forms.validators import DateConverter
import formencode
from formencode import *
        
class AddPrivilegioForm(TableForm):

    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
            
    class fields(WidgetsList):   
        
        id_permiso = HiddenField()            
        privilegios = CheckBoxList(label_text='Privilegios',                                 
                                help_text='Seleccione los privilegios que desea agregar',
                                validator=formencode.All(NotEmpty))
       
add_privilegios = AddPrivilegioForm("add_privilegios", action='appendPrivilegio')
