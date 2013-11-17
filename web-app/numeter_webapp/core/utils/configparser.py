from ConfigParser import RawConfigParser, NoOptionError


class Custom_ConfigParser(RawConfigParser):
    def get_d(self, section, option, default=None):
        if self.has_option(section, option):
            return self.get(section, option)
        elif default is None:
            raise ValueError('Missing option : %s - %s' % (section,option))
        return default

    def getint_d(self, section, option, default=None):
        if self.has_option(section, option):
            return self.getint(section, option)
        elif default is None:
            raise ValueError('Missing option : %s - %s' % (section,option))
        return default

    def getboolean_d(self, section, option, default=None):
        if self.has_option(section, option):
            return self.getboolean(section, option)
        elif default is None:
            raise ValueError('Missing option : %s - %s' % (section,option))
        return default

    def getobj_d(self, section, option, default=None):
        if self.has_option(section, option):
            return eval(self.get(section, option))
        elif default is None:
            raise ValueError('Missing option : %s - %s' % (section,option))
        return default
