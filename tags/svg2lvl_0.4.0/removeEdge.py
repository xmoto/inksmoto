from xmotoExtension import XmotoExtension

class removeEdge(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--remove_up", type="string", dest="remove_up",
                                     help="if true, remove upper texture")
        self.OptionParser.add_option("--remove_down",  type="string", dest="remove_down",
                                     help="if true, remove down texture")

    def getLabelChanges(self):
        if self.options.remove_up == 'true' and self.label.has_key('edge'):
            if self.label['edge'].has_key('texture'):
                del self.label['edge']['texture']
        if self.options.remove_down == 'true' and self.label.has_key('edge'):
            if self.label['edge'].has_key('downtexture'):
                del self.label['edge']['downtexture']

        return []

e = removeEdge()
e.affect()
