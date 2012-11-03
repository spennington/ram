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

import unittest
from ram import commands
import json

class TestParsing(unittest.TestCase):

    def test_template_parse(self):
        data = """
            {
                "templates": {
                    "android": {
                        "slaves": [
                            {
                                "path": "res/drawable-ldpi/$name",
                                "width": "$basewidth * 0.75",
                                "height": "$baseheight * 0.75"
                            },
                            {
                                "path": "res/drawable-mdpi/$name",
                                "width": "$basewidth",
                                "height": "$baseheight"
                            },
                            {
                                "path": "res/drawable-hdpi/$name",
                                "width": "$basewidth * 1.5",
                                "height": "$baseheight * 1.5"
                            },
                            {
                                "path": "res/drawable-xhdpi/$name",
                                "width": "$basewidth * 2",
                                "height": "$baseheight * 2"
                            }
                        ]
                    },
                    "ios": {
                        "slaves": [
                            {
                                "path": "Images/$name",
                                "width": "$basewidth",
                                "height": "$baseheight"
                            },
                            {
                                "path": "Images/$name@2x",
                                "width": "$basewidth",
                                "height": "$baseheight"
                            }
                        ]
                    }
                },
                "conversions": []
            }
        """
        parsed_data = json.loads(data)
        templates = commands.parse_templates(parsed_data['templates'])
        self.assertEqual(2, len(templates))
        
        android_template = templates['android']
        self.assertEqual(4, len(android_template.slave_conversions))

        ios_template = templates['ios']
        self.assertEqual(2, len(ios_template.slave_conversions))

    def test_conversion_parse(self):
        data = """
            {
                "templates": {
                    "android": {
                        "slaves": [
                            {
                                "path": "res/drawable-ldpi/{name}",
                                "width": "{basewidth} * 0.75",
                                "height": "{baseheight} * 0.75"
                            },
                            {
                                "path": "res/drawable-mdpi/{name}",
                                "width": "{basewidth}",
                                "height": "{baseheight}"
                            },
                            {
                                "path": "res/drawable-hdpi/{name}",
                                "width": "{basewidth} * 1.5",
                                "height": "{baseheight} * 1.5"
                            },
                            {
                                "path": "res/drawable-xhdpi/{name}",
                                "width": "{basewidth} * 2",
                                "height": "{baseheight} * 2"
                            }
                        ]
                    }
                },
               "conversions": [
                  {
                     "master":"file.png",
                     "template": "android",
                     "name": "image.png",
                     "basewidth": 100,
                     "baseheight": 200
                  },
                  {
                     "master":"file2.png",
                     "slaves":[
                        {
                           "path":"res/layout-ldpi/image.png",
                           "width":75,
                           "height":75
                        },
                        {
                           "path":"res/layout-mdpi/image.png",
                           "width":100,
                           "height":100
                        },
                        {
                           "path":"res/layout-hdpi/image.png",
                           "width":150,
                           "height":150
                        },
                        {
                           "path":"res/layout-xhdpi/image.png",
                           "width":200,
                           "height":200
                        }
                     ]
                  }
               ]
            }
        """
        parsed_data = json.loads(data)
        templates = commands.parse_templates(parsed_data['templates'])
        conversions = commands.parse_conversions(parsed_data['conversions'], templates)

        self.assertEqual(2, len(conversions))
        self.assertEqual('image.png', conversions['file.png'].args['name'])
        self.assertEqual(100, conversions['file.png'].args['basewidth'])
        self.assertEqual(200, conversions['file.png'].args['baseheight'])

    def test_conversion_parse_template_not_found(self):
        data = """
            {
                "templates": {
                    "android": {
                        "slaves": [
                            {
                                "path": "res/drawable-ldpi/@name",
                                "width": "@basewidth * 0.75",
                                "height": "@baseheight * 0.75"
                            },
                            {
                                "path": "res/drawable-mdpi/@name",
                                "width": "@basewidth",
                                "height": "@baseheight"
                            },
                            {
                                "path": "res/drawable-hdpi/@name",
                                "width": "@basewidth * 1.5",
                                "height": "@baseheight * 1.5"
                            },
                            {
                                "path": "res/drawable-xhdpi/@name",
                                "width": "@basewidth * 2",
                                "height": "@baseheight * 2"
                            }
                        ]
                    }
                },
               "conversions": [
                  {
                     "master":"file.png",
                     "template": "GARBAGE",
                     "name": "image.png",
                     "basewidth": 100,
                     "baseheight": 200
                  },
                  {
                     "master":"file2.png",
                     "slaves":[
                        {
                           "path":"res/layout-ldpi/image.png",
                           "width":75,
                           "height":75
                        },
                        {
                           "path":"res/layout-mdpi/image.png",
                           "width":100,
                           "height":100
                        },
                        {
                           "path":"res/layout-hdpi/image.png",
                           "width":150,
                           "height":150
                        },
                        {
                           "path":"res/layout-xhdpi/image.png",
                           "width":200,
                           "height":200
                        }
                     ]
                  }
               ]
            }
        """
        parsed_data = json.loads(data)
        templates = commands.parse_templates(parsed_data['templates'])
        self.assertRaises(commands.TemplateNotFoundException, commands.parse_conversions, parsed_data['conversions'], templates)

    def test_conversion_parse_template_missing(self):
        data = """
            {
                "templates": {
                    "android": {
                        "slaves": [
                            {
                                "path": "res/drawable-ldpi/@name",
                                "width": "@basewidth * 0.75",
                                "height": "@baseheight * 0.75"
                            },
                            {
                                "path": "res/drawable-mdpi/@name",
                                "width": "@basewidth",
                                "height": "@baseheight"
                            },
                            {
                                "path": "res/drawable-hdpi/@name",
                                "width": "@basewidth * 1.5",
                                "height": "@baseheight * 1.5"
                            },
                            {
                                "path": "res/drawable-xhdpi/@name",
                                "width": "@basewidth * 2",
                                "height": "@baseheight * 2"
                            }
                        ]
                    }
                },
               "conversions": [
                  {
                     "master":"file.png",
                     "name": "image.png",
                     "basewidth": 100,
                     "baseheight": 200
                  },
                  {
                     "master":"file2.png",
                     "slaves":[
                        {
                           "path":"res/layout-ldpi/image.png",
                           "width":75,
                           "height":75
                        },
                        {
                           "path":"res/layout-mdpi/image.png",
                           "width":100,
                           "height":100
                        },
                        {
                           "path":"res/layout-hdpi/image.png",
                           "width":150,
                           "height":150
                        },
                        {
                           "path":"res/layout-xhdpi/image.png",
                           "width":200,
                           "height":200
                        }
                     ]
                  }
               ]
            }
        """
        parsed_data = json.loads(data)
        templates = commands.parse_templates(parsed_data['templates'])
        self.assertRaises(commands.InvalidConversionException, commands.parse_conversions, parsed_data['conversions'], templates)

    def test_conversion_parse_master_missing(self):
        data = """
            {
                "templates": {
                    "android": {
                        "slaves": [
                            {
                                "path": "res/drawable-ldpi/@name",
                                "width": "@basewidth * 0.75",
                                "height": "@baseheight * 0.75"
                            },
                            {
                                "path": "res/drawable-mdpi/@name",
                                "width": "@basewidth",
                                "height": "@baseheight"
                            },
                            {
                                "path": "res/drawable-hdpi/@name",
                                "width": "@basewidth * 1.5",
                                "height": "@baseheight * 1.5"
                            },
                            {
                                "path": "res/drawable-xhdpi/@name",
                                "width": "@basewidth * 2",
                                "height": "@baseheight * 2"
                            }
                        ]
                    }
                },
               "conversions": [
                  {
                     "template": "android",
                     "name": "image.png",
                     "basewidth": 100,
                     "baseheight": 200
                  },
                  {
                     "master":"file2.png",
                     "slaves":[
                        {
                           "path":"res/layout-ldpi/image.png",
                           "width":75,
                           "height":75
                        },
                        {
                           "path":"res/layout-mdpi/image.png",
                           "width":100,
                           "height":100
                        },
                        {
                           "path":"res/layout-hdpi/image.png",
                           "width":150,
                           "height":150
                        },
                        {
                           "path":"res/layout-xhdpi/image.png",
                           "width":200,
                           "height":200
                        }
                     ]
                  }
               ]
            }
        """
        parsed_data = json.loads(data)
        templates = commands.parse_templates(parsed_data['templates'])
        self.assertRaises(commands.InvalidConversionException, commands.parse_conversions, parsed_data['conversions'], templates)

    def test_replace_args(self):
        val = '{baseheight} * 2'
        args = {'baseheight': 10}
        self.assertEqual('10 * 2', commands.replace_args(val, args))

        val = '{baseheight} * 2 * {baseheight}'
        args = {'baseheight': 10}
        self.assertEqual('10 * 2 * 10', commands.replace_args(val, args))

        val = '{baseheight} * 2 * {basewidth}'
        args = {'baseheight': 10, 'basewidth': '20'}
        self.assertEqual('10 * 2 * 20', commands.replace_args(val, args))


if __name__ == '__main__':
    unittest.main()