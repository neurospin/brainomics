# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:29:44 2014

@author: jl237561
"""

import timeit
from brainomics.tools.cubicweb_tool import CubicWebTool
from brainomics.bioresource.scripts.import_subjets.parse_subjects import get_cng_center_assesement_genomic_measures
from brainomics.bioresource.scripts.import_subjets.parse_subjects import get_cng_center_assesements


class GeneticAssesement(CubicWebTool):
    # Default values
    _fields = {
        "Center": {"identifier": u"CNG",
                    "name": u"CNG",
                    "identifier": u"CNG",
                    "department": u"Essonne",
                    "city": u"Evry",
                    "country": u"France"},
        "GenomicPlatform": {"name": u"unknwon"},
        "GenomicMeasure": {"identifier": u"unknwon",
                           "type": u"unknwon",
                           "format": u"unknwon",
                           "filepath": u"unknwon",
                           "chip_serialnum ": 0,
                           "completed ": True,
                           "valid  ": True},
        "Subject": {"identifier": u"unknown",
                    "code_in_study": u"None",
                    "gender": u"unknown",
                    "date_of_birth": u"1900-01-01",
                    "handedness": u"unknown"},
        "Assessment": {"identifier": u"unknown",
                        "age_of_subject": 0},
    }

    _relations = {
        "Center": [],
        "GenomicPlatform": [],
        "GenomicMeasure": [("GenomicPlatform", "platform", True)],
        "Subject": [],
        "Assessment": [("Subject", "concerned_by", True),
                        ("Center", "holds", True),
                        ("GenomicMeasure", "generates", True)],
    }

    _rules = {
        "Center" : [(
                      [("Self","name"),],
                      "Any X WHERE X is Center, X {0} '{1}'"
                   )],
        "GenomicPlatform" : [(
                      [("Self","name"),],
                      "Any X WHERE X is GenomicPlatform, X {0} '{1}'"
                   )],
        "GenomicMeasure" : [(
                                [("Self","identifier"),],
                                "Any X WHERE X is GenomicMeasure, X {0} '{1}'"
                             ),
                             (
                                [("Self","filepath"),],
                                "Any X WHERE X is GenomicMeasure, X {0} '{1}'"
                             )
                             ],
        "Subject" : [(
                        [("Self","identifier"),],
                        "Any X WHERE X is Subject, X {0} '{1}'"
                     )],
        "Assessment" : [(
                        [("Self","identifier"),],
                        "Any X WHERE X is Assessment, X {0} '{1}'"
                        )],
    }

    def __init__(self, parser, *args, **kwargs) :
        """ Init class 
        """
        self.parser = parser
        # each item is a pair perent,childre: [(parameters, [children]),...]
        self.description = self.parser()
        super(GeneticAssesement, self).__init__(*args, **kwargs)


    def __call__(self):
        """ Execute the command.
        """
        tic = timeit.default_timer()
        self._fill_database()
        self._time = timeit.default_timer()-tic

    ##############
    # Members    
    ##############

    def _get_fields(self) :
        """ Get the entities used in the schema.
        """
        return self._fields

    def _get_relations(self) :
        """ Get the relations between entities.
        """
        return self._relations

    def _get_rules(self) :
        """ Get the unicity constraints used during the insertion.
        """
        return self._rules


    ##########################
    #          Requests
    ##########################

    def _fill_database(self) :
        """ Start the insertion.
        """
        parent_entities = {}
#        assessment = self.set_entity("Assessment",
#                                 parent_entities,
#                                 relations=self._relations["Assessment"],
#                                 **self._fields["Assessment"])
#        parent_entities["Assessment"] = assessment

        self._insert_entity(self.description, parent_entities,level=0)

        return 1

    def _insert_entity(self, description, parent_entities, level) :
        """ Add item.
        """
        for item,children in description :
            entity_name = item["entity_name"]
            item.pop("entity_name")
            entity_parameters = self._fields[entity_name]
            for key,value in item.items() :
                if key in entity_parameters.keys() :
                    entity_parameters[key] = value
            entity = self.set_entity(entity_name,
                                     parent_entities,
                                     relations = self._relations[entity_name],
                                     **entity_parameters)
            parent_entities[entity_name] = entity

            self._insert_entity(children,parent_entities,level + 1)


    def get_all_centers(self):
        rqt = "Any X WHERE X is Center"
        return self.send_request(rqt)

    def get_all_genomic_platforms(self):
        rqt = "Any X WHERE X is GenomicPlatform"
        return self.send_request(rqt)

    def get_all_genomic_measures(self):
        rqt = "Any X WHERE X is GenomicMeasure"
        return self.send_request(rqt)

    def get_all_subjects(self):
        rqt = "Any X WHERE X is Subject"
        return self.send_request(rqt)

    def get_all_assessments(self):
        rqt = "Any X WHERE X is Assessment"
        return self.send_request(rqt)

    centers = property(get_all_centers)
    genomic_platforms = property(get_all_genomic_platforms)
    genomic_measures = property(get_all_genomic_measures)
    subjects = property(get_all_subjects)
    assessments = property(get_all_assessments)

    def _get_time(self):
        return self._time

    time = property(_get_time)


def genetic_assesement_parser():
    root_path = "/neurospin/brainomics/2014_bioresource"
    genomic_measures = get_cng_center_assesement_genomic_measures(root_path)
    assesements = get_cng_center_assesements(genomic_measures)
    return assesements


if __name__ == "__main__":
    genetic_assesement = GeneticAssesement(
                                    parser=genetic_assesement_parser,
                                    instance="inst_bioresource2",
                                    login="admin",
                                    passwd="admin")
    genetic_assesement()
    description = genetic_assesement_parser()
