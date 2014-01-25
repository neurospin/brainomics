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

from cubicweb.web.views.startup import IndexView
from cubes.brainomics.views.startup import BrainomicsIndexView

class NcbiIndexView(IndexView):

    def call(self, **kwargs):
        self.w(u'<div class="span12">')
        self.w(u'<div class="row-fluid">')
        
        url = self._cw.data_url('images/dbSNP.png')
        href = self._cw.build_url(rql='Any S WHERE S is Snp')
        self.w(u'<div class="span3"><h2>SNPs</h3><a href="%s"><img width="100" src="%s"/></a></div>'
               % (href, url))
               
        url = self._cw.data_url('images/eGene.png')
        href = self._cw.build_url(rql='Any G where G is Gene')
        self.w(u'<div class="span3"><h2>Gene</h3><a href="%s"><img width="100" src="%s"/></a></div>'
               % (href, url))
               
        url = self._cw.data_url('images/campaign.png')
        href = self._cw.build_url(rql='Any G where G is GenomicPlatform')
        self.w(u'<div class="span3"><h2>Platform</h3><a href="%s"><img width="100" src="%s"/></a></div>'
               % (href, url))
                              
        self.w(u'</div>')
        self.w(u'</div>')
        self.w(u'</div>')
        
        self.w(u'<div class="span12">')
        self.w(u'<div class="row-fluid">')
        
        url = self._cw.data_url('images/subjects.png')
        href = self._cw.build_url(rql='Any S WHERE S is Subject')
        self.w(u'<div class="span3"><h2>Subjects</h3><a href="%s"><img width="100" src="%s"/></a></div>'
               % (href, url))
               
        url = self._cw.data_url('images/campaign.png')
        href = self._cw.build_url(rql='(Any X WHERE X is GenomicMeasure')
        self.w(u'<div class="span3"><h2>Genotyping</h3><a href="%s"><img width="100" src="%s"/></a></div>'
               % (href, url))

        self.w(u'</div>')              
        self.w(u'</div>')
        self.w(u'</div>')        
        
        self.w(u'<div class="span12">')
        self.w(u'<div class="row-fluid">')
        for title in ('ncbi-index',):
            card = self._cw.execute('Any X WHERE X is Card, X title %(t)s', {'t': title})
            if card:
                self.w(card.get_entity(0,0).content)
        self.w(u'</div>')
        self.w(u'</div>')


def registration_callback(vreg):
    vreg.register_and_replace(NcbiIndexView, BrainomicsIndexView)
