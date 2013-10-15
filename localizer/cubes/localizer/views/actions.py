# -*- coding: utf-8 -*-

from cubicweb.web.action import Action
from logilab.common.registry import yes

class LegalAction(Action):
    __regid__ = 'legal'
    __select__ = yes()

    category = 'footer'
    order = 3
    title = _('Legal')

    def url(self):
        return self._cw.build_url('doc/legal')


from cubicweb.web.views.actions import GotRhythmAction

def registration_callback(vreg):
    vreg.register(LegalAction)
    vreg.unregister(GotRhythmAction)
