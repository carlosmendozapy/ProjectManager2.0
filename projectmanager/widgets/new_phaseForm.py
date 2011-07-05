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
from projectmanager.lib.app_globals import Globals
from projectmanager.model import DBSession, metadata
from projectmanager.model.proyecto import Fase
from sqlalchemy import func


class UniquePhaseNumber(formencode.FancyValidator):                    
    
    phasenumber=[]        
    def _to_python(self, value, state):
        fases = DBSession.query(Fase).filter(Fase.id_proyecto==Globals.current_project.id_proyecto).all()
        phasenumber=[]
        for fase in fases:
            self.phasenumber.append(str(fase.nro_fase))        
        if value in self.phasenumber:            
            raise formencode.Invalid(u'Este numero de Fase ya existe',\
                    value, state)
        return value     
  
class NewPhaseForm(TableForm):
                
    hover_help = True
    show_errors = True   
    submit_text = 'Guardar'
    include_dynamic_js_calls = True
                
    class fields(WidgetsList):        
                
        nroPhase = TextField(label_text='Fase Numero',
                                maxlength=3,
                                size = 3,
                                help_text='Establece el orden entre Fases:0-999',
                                validator= formencode.All(Int(min=0,max=999), UniquePhaseNumber()))
        phaseName = TextField(label_text='Nombre de la Fase', 
                                maxlength=25,
                                size=25,
                                help_text='Nombre de la Fase: Maximo 25 Caracteres',                              
                                validator=NotEmpty)        
        descripcion = TextArea(label_text='Descripcion',
                                help_text='Breve Descripcion de la Fase: Maximo 200 Caracteres',
                                cols=40,
                                rows=5,
                                attrs={'maxlength':200},
                                validator=NotEmpty,)              
       
  
create_new_phase = NewPhaseForm("create_new_phase", action='savePhase')
