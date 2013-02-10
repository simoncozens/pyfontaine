from __future__ import print_function
import csv
import os
import StringIO

from collections import OrderedDict

try:
    from unicodenames import unicodenames
    os.environ['UNAMES_INSTALLED'] = 'uname-installed'
except ImportError:
    pass


from fontaine.const import SUPPORT_LEVEL_FULL, SUPPORT_LEVEL_UNSUPPORTED
from fontaine.cmap import library
from fontaine.structures.dict2xml import dict2xml, dict2txt


def yesno(val):
    return 'yes' if val else 'no'


db = os.environ.get('UNAMES_DB') or os.path.join(os.path.dirname(__file__),
                                                 'charmaps', 'names.db',
                                                 'en.names-db')


def format(x):
    return u'U+%04x\x20\x20%s\x20\x20%s' % \
        (x, unichr(x), unicodenames(db).name(x) or '')


def unicodevalues_asstring(values):
    """ Return string with unicodenames if db defined """
    if os.environ.get('UNAMES_INSTALLED') \
            and not os.environ.get('DISABLE_UNAMES'):
        return map(lambda x: '%s' % format(x).strip(), values)
    return map(lambda x: u'U+%04x %s' % (x, unichr(x)), values)


extract_firstline = lambda text: \
    (text or '').replace('\r', '\n').split('\n')[0]


class Director(object):

    def construct_tree(self, fonts):

        tree = OrderedDict({'fonts': []})

        for font in fonts:
            F = OrderedDict()
            desc = OrderedDict()
            desc['commonName'] = font.common_name
            desc['subFamily'] = font.sub_family
            desc['style'] = font.style_flags
            desc['weight'] = font.weight
            desc['fixedWidth'] = yesno(font.is_fixed_width)
            desc['fixedSizes'] = yesno(font.has_fixed_sizes)
            desc['copyright'] = extract_firstline(font.copyright or '')
            desc['license'] = extract_firstline(font.license or '')
            desc['licenseUrl'] = font.license_url
            desc['version'] = font.version
            desc['vendor'] = extract_firstline(font.vendor or '')
            desc['vendorUrl'] = font.vendor_url
            desc['designer'] = font.designer
            desc['designerUrl'] = font.designer_url
            desc['glyphCount'] = font.glyph_num
            desc['characterCount'] = font.character_count
            for charmap, support_level, coverage, missing in font.get_orthographies():
                if support_level == SUPPORT_LEVEL_UNSUPPORTED:
                    continue
                if 'orthographies' not in desc:
                    desc['orthographies'] = []

                orth = OrderedDict({'orthography': OrderedDict()})
                orth['orthography']['commonName'] = charmap.common_name
                orth['orthography']['nativeName'] = charmap.native_name
                orth['orthography']['supportLevel'] = support_level

                if support_level != SUPPORT_LEVEL_FULL:
                    values = u'\n%s' % u'\n'.join(unicodevalues_asstring(missing))
                    orth['orthography']['percentCoverage'] = coverage
                    orth['orthography']['missingValues'] = values

                desc['orthographies'].append(orth)

            F['font'] = desc
            tree['fonts'].append(F)

        return tree


class Builder(object):

    @staticmethod
    def text_(tree):
        return dict2txt(tree, names=NAMES)

    @staticmethod
    def xml_(tree):
        return dict2xml({'report': tree})

    @staticmethod
    def json_(tree):
        pprint(tree)

    @staticmethod
    def csv_(fonts):
        data = StringIO.StringIO()
        doc = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        headers = ['Common Name']
        for subset in library.charmaps:
            headers.append(subset.common_name)
        doc.writerow(headers)

        for font in fonts:
            row = [font.common_name]
            for subset in library.charmaps:
                charmap, support_level, coverage, missing = font.get_othography_info(subset)
                row.append(str(coverage))
            doc.writerow(row)

        data.seek(0)
        return data.read()


NAMES = {
    'fonts': 'Fonts',
    'font': 'Font',
    'commonName': 'Common name',
    'nativeName': 'Common name',
    'subFamily': 'Sub family',
    'style': 'Style',
    'weight': 'Weight',
    'fixedWidth': 'Fixed width',
    'fixedSizes': 'Fixed sizes',
    'copyright': 'Copyright',
    'license': 'License',
    'licenseUrl': 'License url',
    'version': 'Version',
    'vendor': 'Vendor',
    'vendorUrl': 'Vendor url',
    'designer': 'Designer',
    'designerUrl': 'Designer url',
    'glyphCount': 'Glyph count',
    'characterCount': 'Character count',
    'orthographies': 'Orthographies',
    'orthography': 'Orthography',
    'supportLevel': 'Support level',
    'percentCoverage': 'Percent coverage',
    'missingValues': 'Missing values'
}


def pprint(obj, indent=''):
    if isinstance(obj, OrderedDict):
        length = len(obj.keys())
        if length == 1:
            pprint(obj[obj.keys()[0]], indent)
            return
        
        print("%s{" % indent)
        for i, key in enumerate(obj.keys()):
            comma = ', '
            if i + 1 == length:
                comma = ''
            if type(obj[key]) in [str, int, unicode]:
                value = unicode(obj[key]).replace('\n', ', ').strip(', ')
                value = value.replace('"', '\"')
                print("%s  %r: \"%s\"%s" % (indent, key, value, comma))
            else:
                print("%s  %r:" % (indent, key))
                pprint(obj[key], indent + '  ')
        print("%s}," % indent)
    elif isinstance(obj, list):
        print("%s[" % indent)
        for i, o in enumerate(obj):
            pprint(o, indent + '  ')
        print("%s]," % indent)
