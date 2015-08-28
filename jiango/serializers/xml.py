"""
XML serializer.
"""
from __future__ import absolute_import

import types
import datetime
from cStringIO import StringIO
from django.conf import settings
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from xml.sax import make_parser, ContentHandler

from .base import Serializer as BaseSerializer


_marker = object()

class struct( dict ):
    # used on import for easier value access
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            try:
                return self[unicode(key)]
            except:
                pass
            raise AttributeError( key )
        
    def __setattr__(self, key, value ):
        self[key]=value

def traverseStruct(path, data, get=False):
    last = data
    parts = path.split('.')
    parts = filter(None, parts)
    last_part = parts.pop(-1)
    
    for p in parts:
        if p == 'entry':
            last = last[-1]
        else:
            last = last[ p ]

    if get is False:
        return last, last_part

    if last_part == 'entry':
        return last
    else:
        return last[last_part]


class ImportReader(ContentHandler):
    _types = {
        u"string": str,
        u"unicode": unicode,
        u"int": int,
        u"float": float,
        u"bool": bool,
        u"dict": struct, #types.DictType,
        u"list": list,
        u"tuple": list,
        u"none": lambda x: None,
        #u"datetime": parseDate
        u"datetime": str
    }

    subnode_types = (types.ListType, types.DictType, types.TupleType, struct)

    def __init__(self):
        self.buf = []
        self.root = {}
        self.current_path = ''
        self.current_type = u'string'
        self.stack = []

    @classmethod
    def register_type(cls, type_name, converter):
        cls._types[type_name] = converter
    
    def getData(self):
        return self.root
    
    def startElement(self, element_name, attrs):
        d = {}
        for k, v in attrs.items():
            d[str(k)] = str(v)
        v_type = d.get('type')

        # everything in the new format should have a type code.

        self.current_path += ".%s" % element_name
        self.stack.append(v_type)

        if v_type is None:
            v_type = 'dict'

        factory = self._types[v_type]
        
        if factory in self.subnode_types:
            self.createData(self.current_path, v_type)

        if len(d) > 1: # has 'real' attributes
            assert d['type'] == 'dict'
            del d['type']
            path = self.current_path + ".attributes"
            self.createData(path, 'dict', d)
    
    def endElement(self, element_name):
        assert self.current_path.endswith(element_name), "%s %s" % (self.current_path, element_name)
        
        if self.buf and not self._types[self.stack[-1]] in self.subnode_types:
            data = "".join(self.buf)
            data = data.strip()
            self.createData(self.current_path, self.stack[-1], data)

        self.buf = []
        self.stack.pop(-1)
        
        if self.current_path.rfind('.') != -1:
            idx = self.current_path.rfind('.') 
            self.current_path = self.current_path[:idx]

    def characters(self , characters):
        self.buf.append(characters)
    
    def createData(self, path, type_code, data=_marker):
        factory = self._types[type_code]
        if data is not _marker:
            data = factory(data)
        else:
            data = factory()
        last, last_part = traverseStruct(path, self.root)
        if last_part == 'entry':
            last.append(data)
        else:
            last[last_part] = data


class ExportWriter(object):
    _values = {
        types.StringType: "dumpEntry",
        unicode: "dumpEntry",
        float: "dumpEntry",
        types.IntType: "dumpEntry",
        types.BooleanType: "dumpEntry",
        types.NoneType: "dumpEntry",
        datetime.datetime: "dumpEntry",        
        types.ListType: "dumpList",
        types.TupleType: "dumpList",
        types.DictType: "dumpDictionary",
    }
    
    _attrs = {
        types.StringType: "convertValue",
        unicode: "convertValue",
        types.IntType: "convertValue",
        float: "convertValue",
        types.BooleanType: "convertValue",
        types.NoneType: "convertValue",
        datetime.datetime: "convertValue"
    }
    
    _typecode = {
        types.StringType: u"string",
        unicode: u"unicode",
        float: u"float",
        types.IntType: u"int",
        types.BooleanType: u"bool",
        types.DictType:  u"dict",
        types.ListType: u"list",
        types.TupleType: u"tuple",
        types.NoneType: u"none",
        datetime.datetime: "datetime"
    }
    
    subnode_types = (types.ListType, types.DictType, types.TupleType)
    
    entry_key = u'entry'    
    attributes_key = u'attributes'
    
    def __init__(self, stream, encoding='utf-8'):
        """
        Set up a serializer object, which takes policies and outputs
        """
        logger = XMLGenerator(stream, encoding)
        self._logger = logger
        self._output = stream
        self._encoding = encoding
        self._logger.startDocument()
        self._stack = []
        self.startElementNS = self._logger.startElementNS
        self.endElementNS = self._logger.endElementNS
    
    @classmethod
    def register_type(cls, type, type_name, converter="convertValue", dumper="dumpEntry"):
        # converter can also be a callable
        cls._typecode[type] = type_name
        cls._attrs[type] = converter
        cls._values[type] = dumper
    
    def close(self):
        self._logger.endDocument()

    def getValueSerializer(self, v):
        v_type = type(v)
        serializer_name = self._values.get(v_type)
        if serializer_name is None:
            if serializer_name is None:
                raise ValueError("invalid type for serialization %r" % v_type)
        if not callable(serializer_name):
            method = getattr(self, serializer_name)
            assert isinstance(method, types.MethodType), "invalid handler for type %r" % v_type
        else:
            method = serializer_name
        return method

    def getAttrSerializer(self, v):
        v_type = type(v)
        serializer_name = self._attrs.get(v_type)
        if serializer_name is None:
            raise ValueError("invalid type for serialization %r" % v_type)
        method = getattr(self, serializer_name)
        assert isinstance(method, types.MethodType), "invalid handler for type %r" % v_type
        return method        

    def getTypeCode(self, v):
        return self._typecode[type(v)]
    
    def dumpDictionary(self, key, value):
        key = unicode(key)
        type_code = self.getTypeCode(value)
        attr_values = {(None, u'type'): type_code}
        attr_names  = {(None, u'type'): u'type'}

        for k, v in value.get(self.attributes_key, {}).items():
            k = unicode(k)
            assert not isinstance(v, self.subnode_types)
            serializer = self.getAttrSerializer(v)
            attr_values[(None, k)] = serializer(v)
            attr_names[(None, k)] = k
        
        attrs = AttributesNSImpl(attr_values, attr_names)
        self._logger.startElementNS((None, key), key, attrs)
        
        for k, v in value.items():
            if k == self.attributes_key:
                continue
            serializer = self.getValueSerializer(v)
            serializer(k, v)

        self._logger.endElementNS((None, key), key)
 
    def dumpList(self, key, value):
        type_code = self.getTypeCode(value)
        attrs = AttributesNSImpl({(None, u'type'): type_code},
                                  {(None, u'type'): u'type'})
        self._logger.startElementNS((None, key), key, attrs)

        for entry in value:
            serializer = self.getValueSerializer(entry)
            serializer(self.entry_key, entry)
        
        self._logger.endElementNS((None, key), key)

    def dumpEntry(self, key, value):
        key = unicode(key)
        type_code = self.getTypeCode(value)
        attrs = AttributesNSImpl({(None, u'type'): type_code},
                                  {(None, u'type'): u'type'})
        self._logger.startElementNS((None, key), key, attrs)
        serializer = self.getAttrSerializer(value)
        self._logger.characters(serializer(value))
        self._logger.endElementNS((None, key), key)

    def convertValue(self, value):
        return unicode(value)


class Serializer(BaseSerializer):
    """
    Convert a objects to XML.
    """
    content_type = 'text/xml'

    def serialization(self):
        xml = ExportWriter(self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET))
        xml.dumpDictionary('root', self.objects)
        xml.close()


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of XML data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    
    parser = make_parser()
    reader = ImportReader()
    parser.setContentHandler(reader)
    parser.parse(stream)
    
    return reader.getData()

