class Locales(dict):
    LANGUAGES = {
        'en': _("English"),
        'de': _("German")
    }

    REGIONS = {
        'US': _("United States"),
        'GB': _("United Kingdom"),
        'DE': _("Germany")
    }

    def list_language_codes(self):
        return self.keys()

    def list_languages(self):
        return [self.LANGUAGES[lang] for lang in self.iterkeys()]

    def list_region_codes(self, lang=None, lang_code=None):
        if lang:
            lang_code = self.lang_to_lang_code(lang)

        return self[lang_code]

    def list_regions(self, lang=None, lang_code=None):
        return [
            self.REGIONS[region_code] for region_code
            in self.list_region_codes(lang=lang, lang_code=lang_code)
        ]

    @staticmethod
    def lang_to_lang_code(lang):
        for lang_code, _lang in Locales.LANGUAGES.iteritems():
            if lang == _lang:
                return lang_code

    @staticmethod
    def lang_code_to_lang(lang_code):
        return Locales.LANGUAGES[lang_code]

    @staticmethod
    def region_to_region_code(region):
        for region_code, _region in Locales.REGIONS.iteritems():
            if region == _region:
                return region_code

    @staticmethod
    def region_code_to_region(region_code):
        return Locales.REGIONS[region_code]

    @staticmethod
    def get_codes_from_locale_code(locale_code):
        return locale_code.split('_')

    @staticmethod
    def get_locale_code_from_codes(lang_code, region_code):
        return "{}_{}".format(lang_code, region_code)

    @staticmethod
    def get_locale_code_from_langs(lang, region):
        region_code = Locales.region_to_region_code(region)
        lang_code = Locales.lang_to_lang_code(lang)

        return Locales.get_locale_code_from_codes(lang_code, region_code)


SUPPORTED_LOCALES = Locales({
    'en': ['US', 'GB'],
    'de': ['DE']
})
