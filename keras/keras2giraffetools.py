# -*- coding: utf-8 -*-
import json
import re
import os
import pathlib
import inspect
from keras import backend as K
from math import sin, pi, floor

from docs.structure import EXCLUDE
from docs.structure import PAGES

keras_dir = pathlib.Path(__file__).resolve().parents[1]

TOOLBOX = 'Keras'

### Copied from .docs.autogen
def clean_module_name(name):
    if name.startswith('keras_applications'):
        name = name.replace('keras_applications', 'keras.applications')
    if name.startswith('keras_preprocessing'):
        name = name.replace('keras_preprocessing', 'keras.preprocessing')
    return name
    
    
### Modified from .docs.autogen
def get_function_signature(function, name):
    wrapped = getattr(function, '_original_function', None)
    if wrapped is None:
        signature = inspect.getargspec(function)
    else:
        signature = inspect.getargspec(wrapped)
    defaults = signature.defaults
    args = signature.args[1:]
    if defaults:
        kwargs = zip(args[-len(defaults):], defaults)
        args = args[:-len(defaults)]
    else:
        kwargs = []
        
        
    full_name = clean_module_name(function.__module__)
    sections = re.split(r'([a-z]*).(?P<section>[a-z]+)', full_name)
    sections = [i for i in sections if i] 

    ports = []
    
    ports.append({
        'name': '',
        'input': True,
        'output': False,
        'visible': True,
        'editable': True, 
        'code': []
    })
    
    i = 0
    for argument in args:
        ports.append({ 
         'name': str(argument),
         'input': False,
         'output': False,
         'visible': True,
         'editable': True,
         #'default': '',
         'code': [{
          'language': TOOLBOX,
          'argument': {
           'kwarg': False,
           'arg': i
          }
         }]
        })
        i += 1
        
    for argument, default in kwargs:
        if isinstance(default, str):
            default = '\'' + default + '\''
        if isinstance(default, tuple):
            default = "(" + ", ".join(map(str, default)) + ")"
        
        types = {
          type(True): "boolean",
          type(''): "string",
          type(1): "numeric",
          type(1.): "numeric",
          type(None): None
        }
        port = {
         'name': str(argument),
         'input': False,
         'output': False,
         'visible': False,
         'editable': True,
         'default': default,
         'code': [{
          'language': TOOLBOX,
          'argument': {
           'kwarg': True,
           'arg': False
          }
         }]
        }
        if type(default) in types:
            port['type'] = types[type(default)]

        ports.append(port)

    ports.append({
        'name': '',
        'input': False,
        'output': True,
        'visible': True,
        'editable': True,
        'code': []
    })
    
    return { 
     'name': name,
     'category': sections[-1],
     'toolbox': TOOLBOX,
     'code': [{
      'language': TOOLBOX,
      'argument': {
       'name': name,
       'import': 'from keras.layers import %s' % name
      }
     }],
     'web_url': 'https://keras.io/layers/%s/%s' % (sections[-1], name),
     'ports': ports
    }

    
### Copied from .docs.autogen
def read_page_data(page_data, type):
    assert type in ['classes', 'functions', 'methods']
    data = page_data.get(type, [])
    for module in page_data.get('all_module_{}'.format(type), []):
        module_data = []
        for name in dir(module):
            if name[0] == '_' or name in EXCLUDE:
                continue
            module_member = getattr(module, name)
            if (inspect.isclass(module_member) and type == 'classes' or
               inspect.isfunction(module_member) and type == 'functions'):
                instance = module_member
                if module.__name__ in instance.__module__:
                    if instance not in module_data:
                        module_data.append(instance)
        module_data.sort(key=lambda x: id(x))
        data += module_data
    return data


### Copied from .docs.autogen and modified
def get_class_signature(cls):
    try:
        class_signature = get_function_signature(cls.__init__, cls.__name__)
    except (TypeError, AttributeError):
        class_signature = {}
        print("{clean_module_name}.{cls_name}()".format(
            clean_module_name=cls.__module__,
            cls_name=cls.__name__
        ))
    return class_signature


def get_rainbow_color(index):
    r = floor(sin(pi * index + 0 * pi / 3) * 63) + 128;
    g = floor(sin(pi * index + 2 * pi / 3) * 63) + 128;
    b = floor(sin(pi * index + 4 * pi / 3) * 63) + 128;
    return '#%02x%02x%02x' % (r, g, b)

def insert_colours(sorted_nodes, colour_index, colour_spacing):
    sorted_nodes['colour'] = get_rainbow_color(colour_index)
    if 'categories' in sorted_nodes.keys() and sorted_nodes['categories']:
        colour_spacing /= len(sorted_nodes['categories'])
        for index, category in enumerate(sorted_nodes['categories']):
            insert_colours(category, colour_index + index * colour_spacing, colour_spacing)
            
### Copied from .docs.autogen and modified
def generate(sources_dir):
    
    if K.backend() != 'tensorflow':
        raise RuntimeError('The documentation must be built '
                           'with the TensorFlow backend because this '
                           'is the only backend with docstrings.')

    categories = []
    for page_data in PAGES:
        section = re.match(r'layers/(?P<name>[a-z]*).md',page_data['page'])

        if section:
            classes = read_page_data(page_data, 'classes')
            nodes = []
            for element in classes:
                if not isinstance(element, (list, tuple)):
                    element = (element, [])
                cls = element[0]
                signature = get_class_signature(cls)
                nodes.append(signature)
                
            categories.append({ 'name': section.group('name'), 'nodes': nodes })
        
    dictionary = { 'name': TOOLBOX, 'categories': categories } 
    insert_colours(dictionary, 0.0, 1.0)        

    with open('keras_nodes.json', 'w') as outfile:    
        json.dump({'toolboxes': [dictionary]}, outfile, sort_keys=False, indent=2)

if __name__ == '__main__':
    generate(os.path.join(str(keras_dir), 'docs', 'sources'))
    
    
 
    