#!/usr/bin/env python
#
#Copyright 2012 Steve Pennington
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys, argparse, os, json, subprocess, re

from ram import index

INDEX_PATH = '.ramindex'
RAMFILE_PATH = 'ramfile.json'

DEBUG = True

def debug(string):
    if (DEBUG):
        print string

class TerminalColors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

class RamArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.exit(2)

class SlaveConversion:

    def __init__(self, path=None, width=None, height=None):
        self.path = path
        self.width = width
        self.height = height

    def __str__(self):
        return str(self.path) + ' ' + str(self.width) + 'x' + str(self.height)

class ConversionTemplate:

    def __init__(self, name=None, slave_conversions=[]):
        self.name = name
        self.slave_conversions = slave_conversions

class UnboundArgException(Exception):
    pass

class InvalidConversionException(Exception):
    pass

class UnamedConversionException(InvalidConversionException):
    pass

class TemplateNotFoundException(InvalidConversionException):
    pass

class Conversion:

    def __init__(self, master=None, template=None, slaves=None, args={}):
        self.master = master
        self.template = template
        self.slaves = slaves
        self.args = args

def parse_templates(json_data):
    templates = {}
    for template_name in json_data:
        template_data = json_data[template_name]
        slave_conversions = parse_slaves(template_data['slaves'])
        templates[template_name] = ConversionTemplate(
            template_name, slave_conversions)
    return templates

def parse_conversions(json_data, templates):
    conversions = {}
    for conversion_data in json_data:
        template = None
        slaves = None
        master = None

        if 'master' in conversion_data:
            master = conversion_data['master']
        else:
            raise UnamedConversionException()

        if (type(master) != str and type(master) != unicode) or len(master) == 0:
            raise InvalidConversionException()

        if 'template' in conversion_data:
            template_name = conversion_data['template']
            if template_name in templates:
                template = templates[template_name]
            else:
                raise TemplateNotFoundException()

        if 'slaves' in conversion_data:
            slaves = parse_slaves(conversion_data['slaves'])
            if type(slaves) != list:
                raise InvalidConversionException()

        if template == None and slaves == None:
            raise InvalidConversionException()

        if master in conversions:
            raise InvalidConversionException()

        conversions[master] = Conversion(
                master=master,
                template=template,
                slaves=slaves,
                args=conversion_data)

    return conversions

def parse_slaves(json_data):
    slave_conversions = []
    for slave in json_data:
        slave_conversions.append(SlaveConversion(
                path=slave['path'],
                width=slave['width'],
                height=slave['height']
        ))
    return slave_conversions

def add(args):
    rows = []
    for f in args.files:
        relpath = os.path.relpath(f.name)
        if relpath.startswith('..'):
            print '%s is outside of ram managed folder' % relpath
        else:
            rows.append((relpath, 0))
        f.close()
    file_index = index.FileIndex(INDEX_PATH)
    file_index.add(rows)

def replace_args(val, args):
    matches = re.findall('\{(.+?)\}', val)
    for arg in matches:
        if arg in args:
            val = re.sub('{' + arg + '}', str(args[arg]), val)
        else:
            raise UnboundArgException()
    return val

def populate_template(template, args):
    slaves = []
    for slave in template.slave_conversions:
        slave.path = replace_args(slave.path, args)
        if type(slave.width) != int:
            slave.width = replace_args(slave.width, args)
            slave.width = eval(slave.width)
        if type(slave.height) != int:
            slave.height = replace_args(slave.height, args)
            slave.height = eval(slave.height)
        slaves.append(slave)
    return slaves

def do_conversions(conversion, verbose):
    if verbose:
        print 'converting %s' % conversion.master

    slaves = conversion.slaves
    if not slaves:
        slaves = []
    if conversion.template:
        slaves.extend(populate_template(conversion.template, conversion.args))

    for slave in slaves:
        if verbose:
            print '\t %s' % slave

        result = subprocess.call(
            ['convert',
             '-resize',
             '%sx%s' % (str(slave.width), str(slave.height)),
             str(conversion.master) + '[0]',
             str(slave.path)])
        if result != 0:
            if verbose:
                print '\t failed'
            else:
                print 'failed: %s --> %s' % (conversion.master, slave.path)
            return False

    return True

def convert(args):
    # 2-tuple of filename and modified time
    files_to_convert = []

    file_index = index.FileIndex(INDEX_PATH)
    for row in file_index.all():
        filename = row[0]
        timestamp = row[1]
        if os.path.exists(filename) and timestamp < os.path.getmtime(filename):
            files_to_convert.append((filename, os.path.getmtime(filename)))

    if not files_to_convert:
        print 'Nothing to convert.'
        print 'Maybe you need to add files with "ram add <file> ..."?'
    else:
        with open(RAMFILE_PATH, 'r') as ramfile:
            json_data = json.loads(ramfile.read())

        templates = {}
        conversions = {}
        if 'templates' in json_data:
            templates = parse_templates(json_data['templates'])
        if 'conversions' in json_data:
            conversions = parse_conversions(json_data['conversions'], templates)

        success_count = 0
        for f in files_to_convert:
            if f[0] not in conversions:
                print 'warning: no conversion stragegy found for %s' % f[0]
            else:
                success = do_conversions(conversions[f[0]], args.verbose)
                if success:
                    file_index.update(f[0], f[1])
                    success_count += 1

        print 'successfully converted %d master files' % success_count

def help_cmd(args):
    if (args.command == 'init'):
        init_parser.print_help()
    elif (args.command == 'help'):
        help_parser.print_help()
    else:
        print 'no such command: ' + args.command

def init(args):
    if os.path.exists(INDEX_PATH):
        sys.stderr.write('folder already ram managed.\n')
        sys.exit(1)
    else:
        file_index = index.FileIndex(INDEX_PATH)
        file_index.init()
        print 'created ram index: %s' % os.path.abspath(INDEX_PATH)

def ls(args):
    file_index = index.FileIndex(INDEX_PATH)
    for row in file_index.all():
        print row

def status(args):
    file_index = index.FileIndex(INDEX_PATH)
    modified = []
    missing = []
    current = []
    for row in file_index.all():
        filename = row[0]
        mtime = row[1]
        if os.path.exists(filename):
            if os.path.getmtime(filename) == mtime:
                current.append(filename)
            else:
                modified.append(filename)
        else:
            missing.append(filename)
    print_status(current, modified, missing, args.all)

def print_status(current, modified, missing, show_current):
    if not current and not modified and not missing:
        print 'No files have been added.'
        print 'Maybe you need to add files with "ram add <file> ..."?'
    elif not modified and not missing and not show_current:
        print 'All files up to date'
    else:
        if current and show_current:
            print '# Up to date files:'
            for filename in current:
                print '#       %s%s%s' % (TerminalColors.GREEN,
                                          filename,
                                          TerminalColors.END)
        if modified:
            print '# Changed files:'
            print '#    (use "ram convert" to update files)'
            for filename in modified:
                print '#       %s%s%s' % (TerminalColors.YELLOW,
                                          filename,
                                          TerminalColors.END)
        if missing:
            print '# Deleted files:'
            print '#    (use "ram rm <file> ..." to remove files)'
            for filename in missing:
                print '#       %s%s%s' % (TerminalColors.RED,
                                          filename,
                                          TerminalColors.END)

def rm(args):
    file_index = index.FileIndex(INDEX_PATH)
    for filename in args.files:
        file_index.remove(filename)

parser = RamArgParser(
        prog='ram',
        add_help=False,
        epilog='See \'%(prog)s help <command>\' ' +
            'for more information on a specific command.')
subparsers = parser.add_subparsers(
        title="The ram commands are",
        metavar="<command>")

add_parser = subparsers.add_parser('add',
        description='add a file to the ram index',
        help='add a file to the ram index',
        add_help=False)
add_parser.add_argument('files',
        metavar='file',
        type=file,
        nargs='+',
        help='file to add',)
add_parser.set_defaults(func=add)

convert_parser = subparsers.add_parser('convert',
        description='convert assets',
        help='convert assets',
        add_help=False)
convert_parser.add_argument('-v', '--verbose',
        action='store_const',
        const=True,
        dest='verbose',
        metavar='verbose',
        help='print extra information',
        default=False)
convert_parser.set_defaults(func=convert)

help_parser = subparsers.add_parser('help',
        description='more information on a specific command',
        help='more information on a specific command',
        add_help=False)
help_parser.add_argument('command',
        type=str,
        metavar='<command>',
        help='command to get help for')
help_parser.set_defaults(func=help_cmd)

init_parser = subparsers.add_parser('init',
        description='initialize ram management for a folder',
        help='initialize ram management for a folder',
        add_help=False)
init_parser.set_defaults(func=init)

ls_parser = subparsers.add_parser('ls',
        description='list ram managed files',
        help='list ram managed files',
        add_help=False)
ls_parser.set_defaults(func=ls)

rm_parser = subparsers.add_parser('rm',
        description='remove a file from the ram index',
        help='remove a file from the ram index',
        add_help=False)
rm_parser.add_argument('files',
        metavar='file',
        type=str,
        nargs='+',
        help='file to remove',)
rm_parser.set_defaults(func=rm)

status_parser = subparsers.add_parser('status',
        description='show status of ram managed files',
        help='show status of ram managed files',
        add_help=False)
status_parser.add_argument('-a',
        action='store_const',
        const=True,
        dest='all',
        metavar='all',
        help='show all files',
        default=False)
status_parser.set_defaults(func=status)

def main():
    try:
        args = parser.parse_args()
    except IOError as e:
        print e.strerror + ': ' + e.filename
        exit(e.errno)

    try:
        args.func(args)
    except Exception as e:
        print 'fatal: %s' % e
