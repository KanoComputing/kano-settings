class Filter(object):
    ALL = 'all'
    EDID_TEMPLATE='EDID={edid}'

    @classmethod
    def get_edid_filter(cls, edid):
        if not edid:
            return cls.ALL

        return cls.EDID_TEMPLATE.format(edid=edid)
