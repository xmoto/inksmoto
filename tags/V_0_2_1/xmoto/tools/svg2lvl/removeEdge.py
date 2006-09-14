from xmotoExtension import XmotoExtension

class removeEdge(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getChanges(self):
        # previously not a block
        if self.dic.has_key('typeid'):
            self.dic.clear()

        if self.dic.has_key('edgeTexture'):
            del self.dic['edgeTexture']

        return []

    def getStyleChanges(self):
        changes = [('stroke', 'none')]
        if self.style['fill'] == 'none':
            changes.append(('fill', 'mediumaquamarine'))
        
        return changes

e = removeEdge()
e.affect()
