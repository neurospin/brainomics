# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-brainomics views/forms/actions/components for web ui"""

from cubicweb.predicates import is_instance, yes
from cubicweb.view import EntityView
from cubicweb.web.views.primary import PrimaryView
from cubicweb.web.action import Action
from cubes.brainomics.views.startup import BrainomicsIndexView


###############################################################################
### CARD VIEW #################################################################
###############################################################################
class LocalizerIndexView(BrainomicsIndexView):

    def call(self, **kwargs):
        rset = self._cw.execute('Any X WHERE X is Card, X title %(t)s', {'t': 'index'})
        self.wview('primary', rset=rset)


class LocalizeCardView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('Card')

    def call(self, rset=None, **kwargs):
        rset = self.cw_rset or rset
        # Add links to content
        content = rset.get_entity(0, 0).content
        content = content % {'dataset-url': self._cw.build_url('dataset'),
                             'localizer-url': self._cw.build_url('localizer'),
                             'brainomics-url': self._cw.build_url('brainomics'),
                             'license-url': self._cw.build_url('license'),
                             'fmri-image': self._cw.data_url('index_fmri.jpg'),
                             'localizer-image': self._cw.data_url('localizer.jpg'),
                             'database-image': self._cw.data_url('database.png'),
                             'brainomics-image': self._cw.data_url('brainomics.jpg'),
                             # Brainomics content
                             'subject-image': self._cw.data_url('images/subject.png'),
                             'images-image': self._cw.data_url('images/images.png'),
                             'genetics-image': self._cw.data_url('images/genetics.png'),
                             'questionnaire-image': self._cw.data_url('images/questionnaire.png'),
                             'subject-url': self._cw.build_url(rql='Any X WHERE X is Subject'),
                             'images-url': self._cw.build_url(rql='Any X, XT, XL, XI, XF, XD '
                                                              'WHERE X is Scan, '
                                                              'X type XT, X label XL, X identifier XI, '
                                                              'X format XF, X description XD'),
                             'genetics-url': self._cw.build_url(rql='(Any X WHERE X is GenomicMeasure) '
                                                                'UNION (Any X WHERE X is GenericTestRun, '
                                                                'X instance_of T, T type "genomics")'),
                             'questionnaire-url': self._cw.build_url(rql='Any X, XI, XD '
                                                                     'WHERE X is QuestionnaireRun, '
                                                                     'X identifier XI, X datetime XD'),
                             }
        self.w(content)


###############################################################################
### ACTIONS ###################################################################
###############################################################################
class LicenseAction(Action):
    __regid__ = 'license'
    __select__ = yes()
    category = 'footer'
    order = 3
    title = _('License')

    def url(self):
        return self._cw.build_url('license')


class LegalAction(LicenseAction):
    __regid__ = 'legal'
    title = _('Legal')

    def url(self):
        return self._cw.build_url('legal')


class LocalizerAction(LicenseAction):
    __regid__ = 'localizer'
    title = _('Localizer dataset')

    def url(self):
        return self._cw.build_url('localizer')


class BrainomicsAction(LicenseAction):
    __regid__ = 'brainomics'
    title = _('Brainomics project')

    def url(self):
        return self._cw.build_url('brainomics')


class DatasetAction(LicenseAction):
    __regid__ = 'dataset'
    title = _('Access dataset')

    def url(self):
        return self._cw.build_url('dataset')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (LocalizerIndexView,))
    vreg.register_and_replace(LocalizerIndexView, BrainomicsIndexView)
    from cubicweb.web.views.actions import GotRhythmAction
    vreg.unregister(GotRhythmAction)
    from cubicweb.web.views.wdoc import HelpAction, AboutAction
    vreg.unregister(HelpAction)
    vreg.unregister(AboutAction)
