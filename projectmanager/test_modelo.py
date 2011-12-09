# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from projectmanager import model
from projectmanager.model.roles import Rol
from projectmanager.model.roles import Usuario
from projectmanager.model.roles import Permisos

class TestRol(Rol):
    """Unit test case for the ``Rol`` model."""
    klass = model.Rol
    attrs = dict(
        nom_rol = u"test_rol",
        des_rol = u"Descripcion de prueba",
        id_tipo_rol=u"uno"
        )
    def test_obj_creation_nombre(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.nom_rol, u"test_rol")
        
    def test_obj_creation_descripcion(self):
        """El constructor debe setear la descripcion correctamente"""
        eq_(self.obj.des_rol, u"Descripcion de prueba")
        
    def test_obj_creation_tipo(self):
        """El constructor debe setear el tipo correctamente"""
        eq_(self.obj.id_tipo_rol, u"uno")
        


class TestUser(Usuario):
    """Unit test case for the ``Usuario`` model."""
    
    klass = model.Usuario
    attrs = dict(
        nom_usuario = u"Cleodovina",
        login_name = u"Cleodovina",
        _password = u"admin"
        )

    def test_obj_creation_nombre(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.nom_usuario, u"Cleodovina")
   
    
class TestPermiso(Permisos):
    """Unit test case for the ``Permiso`` model."""
    
    klass = model.Permisos
    attrs = dict(
        id_permiso = 1,
        id_entidad_sistema= 1
        )
    def test_obj_creation_permiso(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.id_permiso, 1)
        
    def test_obj_creation_entidad(self):
        """El constructor debe setear la descripcion correctamente"""
        eq_(self.obj.id_entidad_sistema, 2)
        
    
