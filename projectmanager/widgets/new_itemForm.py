from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms import CalendarDatePicker
from tw.forms import CheckBoxList
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
from projectmanager.model import DeclarativeBase, metadata, DBSession
from projectmanager.model.entities import Item
from projectmanager.lib.app_globals import Globals

class FilteringSchema(Schema):
    filter_extra_fields = False
    allow_extra_fields = True
    ignore_key_missing = False
    
class UniqueItemName(formencode.FancyValidator):
    itemnames=[]        
    def _to_python(self, value, state):
        items = DBSession.query(Item).filter(Item.tipoItem.has(id_fase = Globals.current_phase.id_fase)).all()
        for item in items:
            self.itemnames.append(item.nom_item)      
        if value in self.itemnames:
            raise formencode.Invalid(u'Este nombre de item ya existe, favor utilice otro',\
                    value, state)
        return value    
    
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
                                validator=formencode.All(NotEmpty,UniqueItemName))
        
        tipoItem = SingleSelectField(label_text='Tipo de Item',                                
                                validator=NotEmpty,
                                help_text='Establece a que tipo de item pertenecera')
        
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
        
        padres = CheckBoxList(label_text='Padres',
                              help_text='Establece los Padres del Item')
                              
        antecesor = CheckBoxList(label_text='Antecesor',                                 
                                 help_text='Establece el Antecesor del item. Si es la fase inicial no se necesita establecer un antecesor',
                                )
                       
  
create_new_item = NewItemForm("create_new_item", action='saveItem')
