from argparse import ArgumentParser
import os.path
import sys
from lxml import etree
import xmltodict as xd
from zcl_classes import *


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'rb')  # return an open file handle


# read XML and validate against zcl_device.xsd
def read_validate_xml(file):
    fo = open('zcl_device.xsd', 'r')
    zcl_schema = fo.read()
    fo.close()

    schema_root = etree.XML(zcl_schema)
    schema = etree.XMLSchema(schema_root)
    xsd_parser = etree.XMLParser(schema=schema)

    try:
        root = etree.fromstring(file, xsd_parser)
        return root
    except etree.XMLSyntaxError as e:
        print(e)
        sys.exit()


# parse XML to Device object
def parse(root):
    if root.tag == 'device':
        return Device(parse(root[0]))
    elif root.tag == 'endpoint':
        in_clusters = None
        out_clusters = None
        for child in root:
            if child.tag == 'inClusters':
                in_clusters = parse(child)
            elif child.tag == 'outClusters':
                out_clusters = parse(child)
        return ZclEndpoint(id=root.attrib['id'], in_clusters=in_clusters, out_clusters=out_clusters)
    elif root.tag == 'cluster':
        attributes = None
        commands = None
        for child in root:
            if child.tag == 'attributes':
                attributes = parse(child)
            elif child.tag == 'commands':
                commands = parse(child)
        return ZclCluster(id=root.attrib['id'], name=root.attrib['name'], attributes=attributes, commands=commands)
    elif root.tag == 'attribute':
        return ZclAttribute(id=root.attrib['id'], name=root.attrib['name'], type=root.attrib['type'])
    elif root.tag == 'command':
        return ZclCommand(id=root.attrib['id'], name=root.attrib['name'], payload=parse(root[0]) if len(root) != 0 else None)
    elif root.tag == 'payload':
        return ZclPayload(name=root.attrib['name'], type=root.attrib['type'])
    elif root.tag in ('attributes', 'commands', 'endpoints', 'inClusters', 'outClusters'):
        children = []
        for child in root:
            children.append(parse(child))
        return children


def generate_sdt(device_obj, filename):
    namespace = "http://www.onem2m.org/xml/sdt/4.0"
    root = etree.Element('Domain', {"xmlns": namespace, "id": filename})
    devices = etree.SubElement(root, "Devices")
    if len(device_obj.endpoints) == 1:
        device = etree.SubElement(devices, "Device")
    else:
        device = etree.SubElement(devices, "Device")
        for endpoint in device_obj.endpoints:
            subdevice = etree.SubElement(device, "SubDevice", {"id": "Endpoint" + endpoint.id})
            modules = etree.SubElement(subdevice, "Modules")
            for cluster in endpoint.in_clusters:
                if cluster.id == '0x0000':
                    device_properties = etree.SubElement(subdevice, "Properties")
                    for attribute in cluster.attributes:
                        device_property = etree.SubElement(device_properties, "Property", {"name": attribute.name})
                        etree.SubElement(device_property, "SimpleType", {"type": attribute.type})
                else:
                    module = etree.SubElement(modules, "Module", {"name": cluster.name})
                    if len(cluster.attributes) != 0:
                        data_points = etree.SubElement(module, "DataPoints")
                        for attribute in cluster.attributes:
                            data_point = etree.SubElement(data_points, "DataPoint", {"name": attribute.name})
                            data_type = etree.SubElement(data_point, "DataType")
                            etree.SubElement(data_type, "SimpleType", {"type": attribute.type})
                    if len(cluster.commands) != 0:
                        actions = etree.SubElement(module, "Actions")
                        for command in cluster.commands:
                            action = etree.SubElement(module, "Action", {"name": command.name})
                            if command.payload is not None:
                                data_type = etree.SubElement(action, "DataType")
                                etree.SubElement(data_type, "SimpleType", {"type": command.payload.type})
                    extends = etree.SubElement(module, "extends", {"domain": filename, "class": cluster.name})


    s = etree.tostring(root, pretty_print=True)
    et = etree.ElementTree(root)
    et.write(filename + '.xml', pretty_print=True)


def write_to_file(filename, text):
    with open(filename, 'a') as the_file:
        the_file.write(text)


def main(argv):
    file_string = argv.filename.read()
    argv.filename.close()

    root = read_validate_xml(file_string)
    device = parse(root)

    generate_sdt(device, 'example.SDT')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                        help="file to be converted", metavar="FILE",
                        required=True, type=lambda x: is_valid_file(parser, x))
    main(parser.parse_args())
