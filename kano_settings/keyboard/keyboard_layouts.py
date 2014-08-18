#!/usr/bin/env python

# keyboard_layouts.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Country code mappings to keyboard model names, and keyboard variant names collected from
# Debian console-setup source package, version 1.88: http://packages.debian.org/source/wheezy/console-setup
# http://dev.kano.me/public/Keyboardnames.pl.txt
#
# Mapping of country names to keyboard layout codes,
# With additional names for natural country prompts (for example United Kingdom, England, UK, etc)

layouts = {
    'europe': {
        'Albania': 'al',
        'Andorra': 'ad',
        'Austria': 'at',
        'Belarus': 'by',
        'Belgium': 'be',
        'Bosnia': 'ba',
        'Herzegovina': 'ba',
        'Bulgaria': 'bg',
        'Croatia': 'hr',
        'Czech Republic': 'cz',
        'Denmark': 'dk',
        'Estonia': 'ee',
        'Faroe Islands': 'fo',
        'Finland': 'fi',
        'France': 'fr',
        'Germany': 'de',
        'Greece': 'gr',
        'Hungary': 'hu',
        'Iceland': 'is',
        'Italy': 'it',
        'Ireland': 'ie',
        'Latvia': 'lv',
        'Lithuania': 'lt',
        'Macedonia': 'mk',
        'Malta': 'mt',
        'Montenegro': 'me',
        'Netherlands': 'nl',
        'Norway': 'no',
        'Poland': 'pl',
        'Portugal': 'pt',
        'Romania': 'ro',
        'Russia': 'ru',
        'Serbia': 'rs',
        'Slovakia': 'sk',
        'Slovenia': 'si',
        'Spain': 'es',
        'Sweden': 'se',
        'Switzerland': 'ch',
        'Turkey': 'tr',
        'Ukraine': 'ua',
        'United Kingdom': 'gb',
    },
    'asia': {
        'Afghanistan': 'af',
        'Arabic': 'ara',
        'Armenia': 'am',
        'Azerbaijan': 'az',
        'Bangladesh': 'bd',
        'Bhutan': 'bt',
        'Cambodia': 'kh',
        'China': 'cn',
        'Georgia': 'ge',
        'India': 'in',
        'Iran': 'ir',
        'Iraq': 'iq',
        'Israel': 'il',
        'Japan': 'jp',
        'Kazakhstan': 'kz',
        'Kyrgyzstan': 'kg',
        'Korea': 'kr',
        'Laos': 'la',
        'Maldives': 'mv',
        'Mongolia': 'mn',
        'Myanmar': 'mm',
        'Nepal': 'np',
        'Pakistan': 'pk',
        'Philippines': 'ph',
        'Sri Lanka': 'lk',
        'Syria': 'sy',
        'Tajikistan': 'tj',
        'Thailand': 'th',
        'Turkmenistan': 'tm',
        'Uzbekistan': 'uz',
        'Vietnam': 'vn'
    },
    'africa': {
        'Botswana': 'bw',
        'Congo': 'cd',
        'Ethiopia': 'et',
        'Ghana': 'gh',
        'Guinea': 'gn',
        'Kenya': 'ke',
        'Mali': 'ml',
        'Morocco': 'ma',
        'Nigeria': 'ng',
        'Senegal': 'sn',
        'South Africa': 'za',
        'Tanzania': 'tz',
    },
    'america': {
        'Argentina': 'latam',
        'Bolivia': 'latam',
        'Brazil': 'br',
        'Canada': 'ca',
        'Chile': 'latam',
        'Colombia': 'latam',
        'Costa Rica': 'latam',
        'Cuba': 'latam',
        'Ecuador': 'latam',
        'El Salvador': 'latam',
        'Guatemala': 'latam',
        'Guayana': 'latam',
        'Haiti': 'latam',
        'Honduras': 'latam',
        'Mexico': 'latam',
        'Nicaragua': 'latam',
        'Panama': 'latam',
        'Paraguay': 'latam',
        'Peru': 'latam',
        'Puerto Rico': 'latam',
        'Republica Dominicana': 'latam',
        'Uruguay': 'latam',
        'United States': 'us',
        'Venezuela': 'latam',
    },
    'australia': {
        'Australia': 'gb',
        'Maori': 'mao',
    },
    'others': {
        'Braille': 'brai',
        'Esperanto': 'epo',
    }
}

variants = {

    'af': [
        ('OLPC Dari', 'olpc-fa'),
        ('OLPC Pashto', 'olpc-ps'),
        ('OLPC Southern Uzbek', 'olpc-uz'),
        ('Pashto', 'ps'),
        ('Southern Uzbek', 'uz')
    ],
    'am': [
        ('Alternative Eastern', 'eastern-alt'),
        ('Alternative Phonetic', 'phonetic-alt'),
        ('Eastern', 'eastern'),
        ('Phonetic', 'phonetic'),
        ('Western', 'western')
    ],
    'ara': [
        ('Buckwalter', 'buckwalter'),
        ('azerty', 'azerty'),
        ('azerty/digits', 'azerty_digits'),
        ('digits', 'digits'),
        ('qwerty', 'qwerty'),
        ('qwerty/digits', 'qwerty_digits')
    ],
    'at': [
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'az': [
        ('Cyrillic', 'cyrillic')
    ],
    'ba': [
        ('US keyboard with Bosnian digraphs', 'unicodeus'),
        ('US keyboard with Bosnian letters', 'us'),
        ('Use Bosnian digraphs', 'unicode'),
        ('Use guillemets for quotes', 'alternatequotes')
    ],
    'bd': [
        ('Probhat', 'probhat')
    ],
    'be': [
        ('Alternative', 'oss'),
        ('Alternative, Sun dead keys', 'oss_sundeadkeys'),
        ('Alternative, latin-9 only', 'oss_latin9'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('ISO Alternate', 'iso-alternate'),
        ('Sun dead keys', 'sundeadkeys'),
        ('Wang model 724 azerty', 'wang')
    ],
    'bg': [
        ('New phonetic', 'bas_phonetic'),
        ('Traditional phonetic', 'phonetic')
    ],
    'br': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Nativo', 'nativo'),
        ('Nativo for Esperanto', 'nativo-epo'),
        ('Nativo for USA keyboards', 'nativo-us')
    ],
    'brai': [
        ('Left hand', 'left_hand'),
        ('Right hand', 'right_hand')
    ],
    'by': [
        ('Latin', 'latin'),
        ('Legacy', 'legacy'),
    ],
    'ca': [
        ('English', 'eng'),
        ('French (legacy)', 'fr-legacy'),
        ('French Dvorak', 'fr-dvorak'),
        ('Inuktitut', 'ike'),
        ('Ktunaxa', 'kut'),
        ('Multilingual', 'multix'),
        ('Multilingual, first part', 'multi'),
        ('Multilingual, second part', 'multi-2gr'),
        ('Secwepemctsin', 'shs')
    ],
    'ch': [
        ('French', 'fr'),
        ('French (Macintosh)', 'fr_mac'),
        ('French, Sun dead keys', 'fr_sundeadkeys'),
        ('French, eliminate dead keys', 'fr_nodeadkeys'),
        ('German (Macintosh)', 'de_mac'),
        ('German, Sun dead keys', 'de_sundeadkeys'),
        ('German, eliminate dead keys', 'de_nodeadkeys'),
        ('Legacy', 'legacy')
    ],
    'cn': [
        ('Tibetan', 'tib'),
        ('Tibetan (with ASCII numerals)', 'tib_asciinum'),
        ('Uyghur', 'uig')
    ],
    'cz': [
        ('UCW layout (accented letters only)', 'ucw'),
        ('US Dvorak with CZ UCW support', 'dvorak-ucw'),
        ('With <\|> key', 'bksl'),
        ('qwerty', 'qwerty'),
        ('qwerty, extended Backslash', 'qwerty_bksl')
    ],
    'de': [
        ('Dead acute', 'deadacute'),
        ('Dead grave acute', 'deadgraveacute'),
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Lower Sorbian', 'dsb'),
        ('Lower Sorbian (qwertz)', 'dsb_qwertz'),
        ('Macintosh', 'mac'),
        ('Macintosh, eliminate dead keys', 'mac_nodeadkeys'),
        ('Neo 2', 'neo'),
        ('Romanian keyboard with German letters', 'ro'),
        ('Romanian keyboard with German letters, eliminate dead keys', 'ro_nodeadkeys'),
        ('Russian phonetic', 'ru'),
        ('Sun dead keys', 'sundeadkeys'),
        ('qwerty', 'qwerty')
    ],
    'dk': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Macintosh, eliminate dead keys', 'mac_nodeadkeys')
    ],
    'ee': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('US keyboard with Estonian letters', 'us')
    ],
    'epo': [
        ('displaced semicolon and quote (obsolete)', 'legacy')
    ],
    'es': [
        ('Asturian variant with bottom-dot H and bottom-dot L', 'ast'),
        ('Catalan variant with middle-dot L', 'cat'),
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Include dead tilde', 'deadtilde'),
        ('Macintosh', 'mac'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'fi': [
        ('Classic', 'classic'),
        ('Classic, eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Northern Saami', 'smi')
    ],
    'fo': [
        ('Eliminate dead keys', 'nodeadkeys')
    ],
    'fr': [
        ('(Legacy) Alternative', 'latin9'),
        ('(Legacy) Alternative, Sun dead keys', 'latin9_sundeadkeys'),
        ('(Legacy) Alternative, eliminate dead keys', 'latin9_nodeadkeys'),
        ('Alternative', 'oss'),
        ('Alternative, Sun dead keys', 'oss_sundeadkeys'),
        ('Alternative, eliminate dead keys', 'oss_nodeadkeys'),
        ('Alternative, latin-9 only', 'oss_latin9'),
        ('Bepo, ergonomic, Dvorak way', 'bepo'),
        ('Bepo, ergonomic, Dvorak way, latin-9 only', 'bepo_latin9'),
        ('Breton', 'bre'),
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Georgian AZERTY Tskapo', 'geo'),
        ('Macintosh', 'mac'),
        ('Occitan', 'oci'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'gb': [
        ('Colemak', 'colemak'),
        ('Dvorak', 'dvorak'),
        ('Dvorak (UK Punctuation)', 'dvorakukp'),
        ('Extended - Winkeys', 'extd'),
        ('International (with dead keys)', 'intl'),
        ('Macintosh', 'mac'),
        ('Macintosh (International)', 'mac_intl')
    ],
    'ge': [
        ('Ergonomic', 'ergonomic'),
        ('MESS', 'mess'),
        ('Ossetian', 'os'),
        ('Russian', 'ru')
    ],
    'gh': [
        ('Akan', 'akan'),
        ('Avatime', 'avn'),
        ('Ewe', 'ewe'),
        ('Fula', 'fula'),
        ('GILLBT', 'gillbt'),
        ('Ga', 'ga'),
        ('Hausa', 'hausa'),
        ('Multilingual', 'generic')
    ],
    'gr': [
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Extended', 'extended'),
        ('Polytonic', 'polytonic'),
        ('Simple', 'simple')
    ],
    'hr': [
        ('US keyboard with Croatian digraphs', 'unicodeus'),
        ('US keyboard with Croatian letters', 'us'),
        ('Use Croatian digraphs', 'unicode'),
        ('Use guillemets for quotes', 'alternatequotes')
    ],
    'hu': [
        ('101/qwerty/comma/Dead keys', '101_qwerty_comma_dead'),
        ('101/qwerty/comma/Eliminate dead keys', '101_qwerty_comma_nodead'),
        ('101/qwerty/dot/Dead keys', '101_qwerty_dot_dead'),
        ('101/qwerty/dot/Eliminate dead keys', '101_qwerty_dot_nodead'),
        ('101/qwertz/comma/Dead keys', '101_qwertz_comma_dead'),
        ('101/qwertz/comma/Eliminate dead keys', '101_qwertz_comma_nodead'),
        ('101/qwertz/dot/Dead keys', '101_qwertz_dot_dead'),
        ('101/qwertz/dot/Eliminate dead keys', '101_qwertz_dot_nodead'),
        ('102/qwerty/comma/Dead keys', '102_qwerty_comma_dead'),
        ('102/qwerty/comma/Eliminate dead keys', '102_qwerty_comma_nodead'),
        ('102/qwerty/dot/Dead keys', '102_qwerty_dot_dead'),
        ('102/qwerty/dot/Eliminate dead keys', '102_qwerty_dot_nodead'),
        ('102/qwertz/comma/Dead keys', '102_qwertz_comma_dead'),
        ('102/qwertz/comma/Eliminate dead keys', '102_qwertz_comma_nodead'),
        ('102/qwertz/dot/Dead keys', '102_qwertz_dot_dead'),
        ('102/qwertz/dot/Eliminate dead keys', '102_qwertz_dot_nodead'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Standard', 'standard'),
        ('qwerty', 'qwerty')
    ],
    'ie': [
        ('CloGaelach', 'CloGaelach'),
        ('Ogham', 'ogam'),
        ('Ogham IS434', 'ogam_is434'),
        ('UnicodeExpert', 'UnicodeExpert')
    ],
    'il': [
        ('Biblical Hebrew (Tiro)', 'biblical'),
        ('Phonetic', 'phonetic'),
        ('lyx', 'lyx')
    ],
    'in': [
        ('Bengali', 'ben'),
        ('Bengali Probhat', 'ben_probhat'),
        ('English with RupeeSign', 'eng'),
        ('Gujarati', 'guj'),
        ('Gurmukhi', 'guru'),
        ('Gurmukhi Jhelum', 'jhelum'),
        ('Hindi Bolnagri', 'bolnagri'),
        ('Hindi Wx', 'hin-wx'),
        ('Kannada', 'kan'),
        ('Malayalam', 'mal'),
        ('Malayalam Lalitha', 'mal_lalitha'),
        ('Oriya', 'ori'),
        ('Tamil', 'tam'),
        ('Tamil Keyboard with Numerals', 'tam_keyboard_with_numerals'),
        ('Tamil TAB Typewriter', 'tam_TAB'),
        ('Tamil TSCII Typewriter', 'tam_TSCII'),
        ('Tamil Unicode', 'tam_unicode'),
        ('Telugu', 'tel'),
        ('Urdu, Alternative phonetic', 'urd-phonetic3'),
        ('Urdu, Phonetic', 'urd-phonetic'),
        ('Urdu, Winkeys', 'urd-winkeys')
    ],
    'iq': [
        ('Kurdish, (F)', 'ku_f'),
        ('Kurdish, Arabic-Latin', 'ku_ara'),
        ('Kurdish, Latin Alt-Q', 'ku_alt'),
        ('Kurdish, Latin Q', 'ku')
    ],
    'ir': [
        ('Kurdish, (F)', 'ku_f'),
        ('Kurdish, Arabic-Latin', 'ku_ara'),
        ('Kurdish, Latin Alt-Q', 'ku_alt'),
        ('Kurdish, Latin Q', 'ku'),
        ('Persian, with Persian Keypad', 'pes_keypad')
    ],
    'is': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Sun dead keys', 'Sundeadkeys')
    ],
    'it': [
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Georgian', 'geo'),
        ('Macintosh', 'mac'),
        ('US keyboard with Italian letters', 'us')
    ],
    'jp': [
        ('Kana', 'kana'),
        ('Kana 86', 'kana86'),
        ('Macintosh', 'mac'),
        ('OADG 109A', 'OADG109A')
    ],
    'ke': [
        ('Kikuyu', 'kik')
    ],
    'kg': [
        ('Phonetic', 'phonetic')
    ],
    'kr': [
        ('101/104 key Compatible', 'kr104')
    ],
    'kz': [
        ('Kazakh with Russian', 'kazrus'),
        ('Russian with Kazakh', 'ruskaz')
    ],
    'latam': [
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Include dead tilde', 'deadtilde'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'lk': [
        ('Tamil TAB Typewriter', 'tam_TAB'),
        ('Tamil Unicode', 'tam_unicode')
    ],
    'lt': [
        ('IBM (LST 1205-92)', 'ibm'),
        ('LEKP', 'lekp'),
        ('LEKPa', 'lekpa'),
        ('Standard', 'std'),
        ('US keyboard with Lithuanian letters', 'us')
    ],
    'lv': [
        ('Apostrophe () variant', 'apostrophe'),
        ('F-letter (F) variant', 'fkey'),
        ('Tilde (~) variant', 'tilde')
    ],
    'ma': [
        ('French', 'french'),
        ('Tifinagh', 'tifinagh'),
        ('Tifinagh alternative', 'tifinagh-alt'),
        ('Tifinagh alternative phonetic', 'tifinagh-alt-phonetic'),
        ('Tifinagh extended', 'tifinagh-extended'),
        ('Tifinagh extended phonetic', 'tifinagh-extended-phonetic'),
        ('Tifinagh phonetic', 'tifinagh-phonetic')
    ],
    'me': [
        ('Cyrillic', 'cyrillic'),
        ('Cyrillic with guillemets', 'cyrillicalternatequotes'),
        ('Cyrillic, Z and ZHE swapped', 'cyrillicyz'),
        ('Latin qwerty', 'latinyz'),
        ('Latin unicode', 'latinunicode'),
        ('Latin unicode qwerty', 'latinunicodeyz'),
        ('Latin with guillemets', 'latinalternatequotes')
    ],
    'mk': [
        ('Eliminate dead keys', 'nodeadkeys')
    ],
    'ml': [
        ('English (USA International)', 'us-intl'),
        ('English (USA Macintosh)', 'us-mac'),
        ('Francais (France Alternative)', 'fr-oss'),
    ],
    'mt': [
        ('Maltese keyboard with US layout', 'us')
    ],
    'ng': [
        ('Hausa', 'hausa'),
        ('Igbo', 'igbo'),
        ('Yoruba', 'yoruba')
    ],
    'nl': [
        ('Macintosh', 'mac'),
        ('Standard', 'std'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'no': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Macintosh, eliminate dead keys', 'mac_nodeadkeys'),
        ('Northern Saami', 'smi'),
        ('Northern Saami, eliminate dead keys', 'smi_nodeadkeys')
    ],
    'ph': [
        ('Capewell-Dvorak (Baybayin)', 'capewell-dvorak-bay'),
        ('Capewell-Dvorak (Latin)', 'capewell-dvorak'),
        ('Capewell-QWERF 2006 (Baybayin)', 'capewell-qwerf2k6-bay'),
        ('Capewell-QWERF 2006 (Latin)', 'capewell-qwerf2k6'),
        ('Colemak (Baybayin)', 'colemak-bay'),
        ('Colemak (Latin)', 'colemak'),
        ('Dvorak (Baybayin)', 'dvorak-bay'),
        ('Dvorak (Latin)', 'dvorak'),
        ('QWERTY (Baybayin)', 'qwerty-bay')
    ],
    'pk': [
        ('Arabic', 'ara'),
        ('CRULP', 'urd-crulp'),
        ('NLA', 'urd-nla'),
        ('Sindhi', 'snd')
    ],
    'pl': [
        ('Dvorak', 'dvorak'),
        ('Dvorak, Polish quotes on key 1', 'dvorak_altquotes'),
        ('Dvorak, Polish quotes on quotemark key', 'dvorak_quotes'),
        ('Kashubian', 'csb'),
        ('Programmer Dvorak', 'dvp'),
        ('Russian phonetic Dvorak', 'ru_phonetic_dvorak'),
        ('qwertz', 'qwertz')
    ],
    'pt': [
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Macintosh, Sun dead keys', 'mac_sundeadkeys'),
        ('Macintosh, eliminate dead keys', 'mac_nodeadkeys'),
        ('Nativo', 'nativo'),
        ('Nativo for Esperanto', 'nativo-epo'),
        ('Nativo for USA keyboards', 'nativo-us'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'ro': [
        ('Cedilla', 'cedilla'),
        ('Crimean Tatar (Dobruca-1 Q)', 'crh_dobruca1'),
        ('Crimean Tatar (Dobruca-2 Q)', 'crh_dobruca2'),
        ('Crimean Tatar (Turkish Alt-Q)', 'crh_alt'),
        ('Crimean Tatar (Turkish F)', 'crh_f'),
        ('Standard', 'std'),
        ('Standard (Cedilla)', 'std_cedilla'),
        ('Winkeys', 'winkeys')
    ],
    'rs': [
        ('Latin', 'latin'),
        ('Latin Unicode', 'latinunicode'),
        ('Latin Unicode qwerty', 'latinunicodeyz'),
        ('Latin qwerty', 'latinyz'),
        ('Latin with guillemets', 'latinalternatequotes'),
        ('Pannonian Rusyn Homophonic', 'rue'),
        ('With guillemets', 'alternatequotes'),
        ('Z and ZHE swapped', 'yz')
    ],
    'ru': [
        ('Bashkirian', 'bak'),
        ('Chuvash', 'cv'),
        ('Chuvash Latin', 'cv_latin'),
        ('DOS', 'dos'),
        ('Kalmyk', 'xal'),
        ('Komi', 'kom'),
        ('Legacy', 'legacy'),
        ('Mari', 'chm'),
        ('Ossetian, Winkeys', 'os_winkeys'),
        ('Ossetian, legacy', 'os_legacy'),
        ('Phonetic', 'phonetic'),
        ('Phonetic Winkeys', 'phonetic_winkeys'),
        ('Serbian', 'srp'),
        ('Tatar', 'tt'),
        ('Typewriter', 'typewriter'),
        ('Typewriter, legacy', 'typewriter-legacy'),
        ('Udmurt', 'udm'),
        ('Yakut', 'sah')
    ],
    'se': [
        ('Dvorak', 'dvorak'),
        ('Eliminate dead keys', 'nodeadkeys'),
        ('Macintosh', 'mac'),
        ('Northern Saami', 'smi'),
        ('Russian phonetic', 'rus'),
        ('Russian phonetic, eliminate dead keys', 'rus_nodeadkeys'),
        ('Svdvorak', 'svdvorak')
    ],
    'si': [
        ('US keyboard with Slovenian letters', 'us'),
        ('Use guillemets for quotes', 'alternatequotes')
    ],
    'sk': [
        ('Extended Backslash', 'bksl'),
        ('qwerty', 'qwerty'),
        ('qwerty, extended Backslash', 'qwerty_bksl')
    ],
    'sy': [
        ('Kurdish, (F)', 'ku_f'),
        ('Kurdish, Latin Alt-Q', 'ku_alt'),
        ('Kurdish, Latin Q', 'ku'),
        ('Syriac', 'syc'),
        ('Syriac phonetic', 'syc_phonetic')
    ],
    'th': [
        ('Pattachote', 'pat'),
        ('TIS-820.2538', 'tis')
    ],
    'tj': [
        ('Legacy', 'legacy')
    ],
    'tm': [
        ('Alt-Q', 'alt')
    ],
    'tr': [
        ('(F)', 'f'),
        ('Alt-Q', 'alt'),
        ('Crimean Tatar (Turkish Alt-Q)', 'crh_alt'),
        ('Crimean Tatar (Turkish F)', 'crh_f'),
        ('Crimean Tatar (Turkish Q)', 'crh'),
        ('International (with dead keys)', 'intl'),
        ('Kurdish, (F)', 'ku_f'),
        ('Kurdish, Latin Alt-Q', 'ku_alt'),
        ('Kurdish, Latin Q', 'ku'),
        ('Sun dead keys', 'sundeadkeys')
    ],
    'ua': [
        ('Crimean Tatar (Turkish Alt-Q)', 'crh_alt'),
        ('Crimean Tatar (Turkish F)', 'crh_f'),
        ('Crimean Tatar (Turkish Q)', 'crh'),
        ('Homophonic', 'homophonic'),
        ('Legacy', 'legacy'),
        ('Phonetic', 'phonetic'),
        ('Standard RSTU', 'rstu'),
        ('Standard RSTU on Russian layout', 'rstu_ru'),
        ('Typewriter', 'typewriter'),
        ('Winkeys', 'winkeys')
    ],

    'us': [
        ('Alternative international', 'alt-intl'),
        ('Cherokee', 'chr'),
        ('Classic Dvorak', 'dvorak-classic'),
        ('Colemak', 'colemak'),
        ('Dvorak', 'dvorak'),
        ('Dvorak alternative international (no dead keys)', 'dvorak-alt-intl'),
        ('Dvorak international (with dead keys)', 'dvorak-intl'),
        ('International (AltGr dead keys)', 'altgr-intl'),
        ('International (with dead keys)', 'intl'),
        ('Layout toggle on multiply/divide key', 'olpc2'),
        ('Left handed Dvorak', 'dvorak-l'),
        ('Macintosh', 'mac'),
        ('Programmer Dvorak', 'dvp'),
        ('Right handed Dvorak', 'dvorak-r'),
        ('Russian phonetic', 'rus'),
        ('Serbo-Croatian', 'hbs'),
        ('With EuroSign on 5', 'euro')
    ],
    'uz': [
        ('Crimean Tatar (Turkish Alt-Q)', 'crh_alt'),
        ('Crimean Tatar (Turkish F)', 'crh_f'),
        ('Crimean Tatar (Turkish Q)', 'crh'),
        ('Latin', 'latin')
    ]

}
