import inspect
import os
import unittest

from six.moves import builtins # pylint: disable=import-error

from astroid.builder import AstroidBuilder
from astroid import nodes
from astroid import raw_building
from astroid import test_utils
from astroid import util


BUILTINS = builtins.__name__


class RawBuildingTC(unittest.TestCase):
    @test_utils.require_version(minver='3.0')
    def test_io_is__io(self):
        # _io module calls itself io. This leads
        # to cyclic dependencies when astroid tries to resolve
        # what io.BufferedReader is. The code that handles this
        # is in astroid.raw_building.imported_member, which verifies
        # the true name of the module.
        import _io

        module = raw_building.ast_from_object(_io, name='io')
        buffered_reader = module.getattr('BufferedReader')[0]
        self.assertEqual(buffered_reader.root().name, 'io')

    @unittest.skipUnless(util.JYTHON, 'Requires Jython')
    def test_open_is_inferred_correctly(self):
        # Lot of Jython builtins don't have a __module__ attribute.
        for name, _ in inspect.getmembers(builtins, predicate=inspect.isbuiltin):
            if name == 'print':
                continue
            node = test_utils.extract_node('{0} #@'.format(name))
            inferred = next(node.infer())
            self.assertIsInstance(inferred, nodes.FunctionDef, name)
            self.assertEqual(inferred.root().name, BUILTINS, name)



    # def test_ast_from_class(self):
    #     astroid = self.manager.ast_from_class(int)
    #     self.assertEqual(astroid.name, 'int')
    #     self.assertEqual(astroid.parent.frame().name, BUILTINS)

    #     astroid = self.manager.ast_from_class(object)
    #     self.assertEqual(astroid.name, 'object')
    #     self.assertEqual(astroid.parent.frame().name, BUILTINS)
    #     self.assertIn('__setattr__', astroid)

    # def test_ast_from_class_with_module(self):
    #     """check if the method works with the module name"""
    #     astroid = self.manager.ast_from_class(int, int.__module__)
    #     self.assertEqual(astroid.name, 'int')
    #     self.assertEqual(astroid.parent.frame().name, BUILTINS)

    #     astroid = self.manager.ast_from_class(object, object.__module__)
    #     self.assertEqual(astroid.name, 'object')
    #     self.assertEqual(astroid.parent.frame().name, BUILTINS)
    #     self.assertIn('__setattr__', astroid)

    # def test_ast_from_class_attr_error(self):
    #     """give a wrong class at the ast_from_class method"""
    #     self.assertRaises(exceptions.AstroidBuildingException,
    #                       self.manager.ast_from_class, None)


if __name__ == '__main__':
    unittest.main()