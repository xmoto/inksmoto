import logging, log

class Version:
    def __init__(self):
        # old version... (0.1.1)
        self.x = 0
        self.y = 1
        self.z = 1

        # TODO::get function2versions from the web
        self.functions2Versions = {"TouchBy":                      (0,3,0),
                                   "OnEnterBy":                    (0,3,0),
                                   "OnLeaveBy":                    (0,3,0),
                                   "OnSomersault":                 (0,2,1),
                                   "OnSomersaultBy":               (0,3,0),
                                   "OnWheel1Touchs":               (0,2,1),
                                   "OnWheel1TouchsBy":             (0,3,0),
                                   "IsAPlayerInZone":              (0,3,0),
                                   "SetAPlayerPosition":           (0,3,0),
                                   "GetAPlayerPosition":           (0,3,0),
                                   "MoveBlock":                    (0,2,0),
                                   "SetBlockCenter":               (0,2,0),
                                   "SetBlockPos":                  (0,2,0),
                                   "GetBlockPos":                  (0,2,0),
                                   "SetBlockRotation":             (0,2,0),
                                   "SetDynamicEntityRotation":     (0,2,0),
                                   "SetDynamicEntitySelfRotation": (0,2,0),
                                   "SetDynamicEntityTranslation":  (0,2,0),
                                   "SetDynamicEntityNone":         (0,2,0),
                                   "SetDynamicBlockRotation":      (0,2,0),
                                   "SetDynamicBlockSelfRotation":  (0,2,0),
                                   "SetDynamicBlockTranslation":   (0,2,0),
                                   "SetDynamicBlockNone":          (0,2,0),
                                   "CameraZoom":                   (0,2,0),
                                   "CameraMove":                   (0,2,0),
                                   "CameraRotate":                 (0,3,0),
                                   "CameraAdaptToGravity":         (0,3,0),
                                   "GetEntityRadius":              (0,2,0),
                                   "IsEntityTouched":              (0,2,0),
                                   "KillPlayer":                   (0,2,1),
                                   "KillAPlayer":                  (0,3,0),
                                   "KillEntity":                   (0,2,1),
                                   "WinPlayer":                    (0,2,1),
                                   "WinAPlayer":                   (0,2,1),
                                   "RemainingStrawberries":        (0,2,1),
                                   "NumberOfPlayers":              (0,3,0),
                                   "SetCameraRotationSpeed":       (0,4,2),
                                   "PlaySound":                    (0,4,2),
                                   "PlayMusic":                    (0,4,2),
                                   "StopMusic":                    (0,4,2),
                                   "AddPenaltyTime":               (0,5,0),
                                   "GetPlayerVelocity":            (0,5,0),
                                   "GetPlayerSpeed":               (0,5,0),
                                   "GetPlayerAngle":               (0,5,0)}

        self.params2Versions = {("physics",  "grip"):       (0,2,1),
                                ("size",     "width"):      (0,2,1),
                                ("size",     "height"):     (0,2,1),
                                ("position", "angle"):      (0,2,5),
                                ("position", "reversed"):   (0,2,5),
                                ("position", "physics"):    (0,5,0),
                                ("usetexture", "scale"):    (0,5,0),
                                ("physics",  "mass"):       (0,5,0),
                                ("physics",  "elasticity"): (0,5,0),
                                ("physics",  "friction"):   (0,5,0),
                                ("physics", "infinitemass"):(0,5,0)}

    def getXmotoRequiredVersion(self, options, rootLayer):
        # http://wiki.xmoto.tuxfamily.org/index.php?title=Others_tips_to_make_levels
        self.options = options
        if self.options.has_key('sky'):
            self.addVersion((0, 2, 5))
        if self.options['level']['tex'] != '':
            self.addVersion((0, 2, 5))
        if self.options['level'].has_key('music') and self.options['level']['music'] not in [None, '', 'None']:
            self.addVersion((0, 2, 5))
        if self.options.has_key('remplacement'):
            for key, value in self.options['remplacement'].iteritems():
                if value not in ['None', '', None]:
                    self.addVersion((0, 2, 5))
                    break
        if self.options.has_key('layer'):
            self.addVersion((0, 2, 7))
        
        if self.options['level']['lua'] not in [None, '']:
            self.addVersion((0,1,10))
            self.analyseScript(self.options['level']['lua'])

        self.analyseLevelElements(rootLayer)

        return (self.x, self.y, self.z)

    def analyseScript(self, scriptFilename):
        import re

        # every word can be a function, we test them all
        function  = re.compile(r'[a-zA-Z0-9]+')
        functions = {}

        f = open(scriptFilename)
        lines = f.readlines()
        f.close

        for line in lines:
            length = len(line)
            offset    = 0
            while True:
                m = function.search(line, offset)
                if m == None:
                    break
                if m:
                    if m.end() >= length:
                        break
                    # we use a dic instead of a set because sets are
                    # available only since python 2.4 (we need 2.3 compatibility for macosx)
                    functions[line[m.start():m.end()]] = ""
                    offset = m.end()

        for function in functions.iterkeys():
            if self.functions2Versions.has_key(function):
                version = self.functions2Versions[function]
                self.addVersion(version)

    def analyseLevelElements(self, layer):
        for child in layer.children:
            self.analyseLevelElements(child)

        for element in layer.elements:
            for namespace, params in element.elementInformations.iteritems():
                if type(params) == dict:
                    for paramKey in params.iterkeys():
                        if (namespace, paramKey) in self.params2Versions:
                            self.addVersion(self.params2Versions[(namespace, paramKey)])

    def addVersion(self, version):
        x,y,z = version
        if x > self.x:
            self.x = x
            self.y = y
            self.z = z
        elif x == self.x:
            if y > self.y:
                self.y = y
                self.z = z
            elif y == self.y:
                if z > self.z:
                    self.z = z

