# -*- coding: utf-8 -*-
import KBEngine
import copy
from KBEDebug import *

class Avatar(KBEngine.Entity):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		DEBUG_MSG("Avatar::__init__:%s." % (self.__dict__))

