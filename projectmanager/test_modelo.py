# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from sgp import model
from sgp.tests.models import ModelTest

class TestRol(ModelTest):
    """Unit test case for the ``Rol`` model."""
    klass = model.Rol
    attrs = dict(
        nombre = u"test_rol",
        descripcion = u"Descripcion de prueba",
        tipo=1
        )
    def test_obj_creation_nombre(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.nombre, u"test_rol")
        
    def test_obj_creation_descripcion(self):
        """El constructor debe setear la descripcion correctamente"""
        eq_(self.obj.descripcion, u"Descripcion de prueba")
        
    def test_obj_creation_tipo(self):
        """El constructor debe setear el tipo correctamente"""
        eq_(self.obj.tipo, 1)
        


class TestUser(ModelTest):
    """Unit test case for the ``Usuario`` model."""
    
    klass = model.Usuario
    attrs = dict(
        usuario = u"Cleodovina",
        nombre = u"Cleodovina",
        telefono = 123456,
        _password = u"admin"
        )

    def test_obj_creation_nombre(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.nombre, u"Cleodovina")

    def test_obj_creation_telefono(self):
        """El constructor debe setear el numero de telefono correctamente"""
        eq_(self.obj.telefono, 123456)

    def test_no_permissions_by_default(self):
        """El usuario se crea sin roles por defecto"""
        eq_(len(self.obj.roles), 0)



class TestPermiso(ModelTest):
    """Unit test case for the ``Permiso`` model."""
    
    klass = model.Permiso
    attrs = dict(
        nombre = u"test_permiso",
        descripcion = u"Permiso de prueba",
        tipo = 0
        )
    def test_obj_creation_nombre(self):
        """El constructor debe setear el nombre correctamente"""
        eq_(self.obj.nombre, u"test_permiso")
        
    def test_obj_creation_descripcion(self):
        """El constructor debe setear la descripcion correctamente"""
        eq_(self.obj.descripcion, u"Permiso de prueba")
        
    def test_obj_creation_tipo(self):
        """El constructor debe setear el tipo correctamente"""
        eq_(self.obj.tipo, 0)