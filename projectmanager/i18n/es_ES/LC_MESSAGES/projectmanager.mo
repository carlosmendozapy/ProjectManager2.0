��    �                    �	     �	     �	     
     
  3   0
  2   d
  H   �
  0   �
  x     �   �  S  I  �  �  $   �  �   �  
  �  R   �     �       
          &   "     I     c     r     t  i   �     �          )     D     _     k     �  '   �      �  .   �  -     !   J     l     �  �  �     ,     ;     N     a     q     }  2   �  ,   �     �  
                  )     2     8     K     e     }     �     �  !   �     �     �  �   �     �  -   �     �     �     �  7     =   H  $   �     �  
   �     �     �     �    �  +        3  Q   G  	   �     �  o   �  �   +     �     �     �  /     !   4     V     m  4   �     �     �     �     �     �               2  M   8  P   �  �   �  �  �  �   �"  �   n#  N   �#  
   E$  7   P$     �$      �$     �$     �$  '   �$  R   �$    =%     R&  �   X&  :   '  �   @'     (     (     ,(     5(  >   ;(  #   z(     �(     �(     �(  	   �(     �(     �(  �   �(    �)     �*     +     "+  ^  .+     �,     �,     �,      �,  	   �,     �,  K  �,     +.     3.     8.     H.     Z.    h.     v/     �/     �/  �  �/     >1     O1     \1     p1  3   �1  2   �1  H   �1  0   12  x   b2  �   �2  S  �3  �  �4  $   �6  �   7  
  �7  R   �8     K9     X9  
   _9     j9  &   s9     �9     �9     �9     �9  i   �9     N:     ^:     z:     �:     �:     �:     �:  '   �:      ;  .   >;  -   m;  !   �;     �;     �;  �  �;     }=     �=     �=     �=     �=     �=  2   �=  ,   >     F>  
   U>     `>     g>     z>     �>     �>     �>     �>     �>     �>     �>  !   ?     =?     B?  �   P?     �?  -   �?     (@     1@     G@  7   c@  =   �@  $   �@     �@  
   A     A     "A     )A    AA  +   ZB     �B  Q   �B  	   �B     �B  o   C  �   ~C     D     5D     QD  /   WD  !   �D     �D     �D  4   �D     E     E     (E     6E     IE     ZE     nE     �E  M   �E  P   �E  �   *F  �  $G  �   �I  �   �J  N   IK  
   �K  7   �K     �K      �K     L     L  '   L  R   =L    �L     �M  �   �M  :   XN  �   �N     gO     nO     O     �O  >   �O  #   �O     �O     �O     P  	   +P     5P     AP  �   MP    7Q     OR     ^R     uR  ^  �R     �S     �S     �S       T  	   !T     +T  K  2T     ~U     �U     �U     �U     �U    �U     �V     �V     �V   " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under About this page Administracion de Proyectos Administracion de Usuarios Administrador de Proyectos Administrar All objects from locals(): Another protected resource is Aqui el administrador maneja el sistema Aqui se administran los usuarios Architectural basics of a quickstart TG2 site. Authentication & Authorization in a TG2 site. Back to your Quickstart Home page Bienvenido a PyProject v1.0 Bienvenido, %s! But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Carlos Mendoza Code my data model Cristián Munizaga Desarrolladores Descripcion Design my URL structure Despliega Formulario de Administracion de Usuarios Despliega Formulario de Creacion de Proyecto Developing TG2 Diana Jara Editar Editar el Usuario: Eliminar Error Error has Occurred Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! Gracias por elegir PyProject v1.0 Home Identificador If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Ingresa al Sistema para acceder a tu proyecto Ingresar Join the TG Mail List Join the TG-Trunk Mail List Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Lo esperamos para su proxima sesion! Login Login Form More TG2 Documents Nombre Now try to visiting the Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Only for people with the "admin" permission Only for the editor Only managers are authorized to visit this method. You will need to log-in using: Password: Powered by TurboGears 2 PyProject is a open source front-to-back web projects
      administrator written in Python. Copyright (c) 2011 PyProject v1.0 es una herramienta de Administración de Proyectos desarrollada por alumnos
    de la Universidad Nacional de Asunción, Facultad Politécnica. Registrar Nuevo Usuario Reuse the web page elements Salir Sample Template, for looking at template locals Se ha creado un nuevo Proyecto %s Secure Controller here Solo para Administradores Solo para personas con permisos de  "Administracion" TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Tareas Administrativas The " The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). To change the comportement of this setup-app command you just need to edit the TurboGears URL. You will be challenged with a login/password form. Usuario Usuario y/o Password Incorrectos Usuario: Welcome What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. or password: managepass paster setup-app development.ini py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: to be able to access it. websetup.py with a password of Project-Id-Version: ProjectManager 0.1
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2011-05-19 11:18-0400
PO-Revision-Date: 2011-05-19 11:24-0400
Last-Translator: Carlos <carlosmendozapy@gmail.com>
Language-Team: es_ES <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.6
 " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under About this page Administracion de Proyectos Administracion de Usuarios Administrador de Proyectos Administrar All objects from locals(): Another protected resource is Aqui el administrador maneja el sistema Aqui se administran los usuarios Architectural basics of a quickstart TG2 site. Authentication & Authorization in a TG2 site. Back to your Quickstart Home page Bienvenido a PyProject v1.0 Bienvenido, %s! But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Carlos Mendoza Code my data model Cristián Munizaga Desarrolladores Descripcion Design my URL structure Despliega Formulario de Administracion de Usuarios Despliega Formulario de Creacion de Proyecto Developing TG2 Diana Jara Editar Editar el Usuario: Eliminar Error Ha ocurrido un Error Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! Gracias por elegir PyProject v1.0 Home Identificador If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Ingresa al Sistema para acceder a tu proyecto Ingresar Join the TG Mail List Join the TG-Trunk Mail List Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Lo esperamos para su proxima sesion! Login Login Form More TG2 Documents Nombre Now try to visiting the Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Only for people with the "admin" permission Only for the editor Only managers are authorized to visit this method. You will need to log-in using: Password: Powered by TurboGears 2 PyProject is a open source front-to-back web projects
      administrator written in Python. Copyright (c) 2011 PyProject v1.0 es una herramienta de Administración de Proyectos desarrollada por alumnos
    de la Universidad Nacional de Asunción, Facultad Politécnica. Registrar Nuevo Usuario Reuse the web page elements Salir Sample Template, for looking at template locals Se ha creado un nuevo Proyecto %s Secure Controller here Solo para Administradores Solo para personas con permisos de  "Administracion" TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Tareas Administrativas The " The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). To change the comportement of this setup-app command you just need to edit the TurboGears URL. You will be challenged with a login/password form. Usuario Usuario y/o Password Incorrectos Usuario: Welcome What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. or password: managepass paster setup-app development.ini py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: to be able to access it. websetup.py with a password of 