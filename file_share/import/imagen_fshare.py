
import timeit
from cubicweb_tool import CubicWebTool
from parse_tool import parse_imagen_process_data


class Imagen(CubicWebTool) :
    """ Create the localizer database. Each item is a
    pair (entity, children).
    """

    _fields = {
        "Center" : {"name" : u"Neursospin","identifier" : u"Neursospin"},
        "Study" : {"name" : u"ImagenFU2_File_Share",
                   "data_filepath" : u"/neurospin/imagen/FU2/processed/ftp_mirror/"},
        "Subject": {"identifier": u"unknown", "code_in_study": u"None", "gender": u"unknown",
                    "date_of_birth": u"1900-01-01", "handedness": u"unknown"},
        "Assessment" : {"identifier": u"unknown", "age_for_assessment": 0},
        "ExternalResource": {"name": u"None", "filepath": u"None"}
    }

    _relations = {
        "Center" : [],
        "Study" : [],
        "Subject" : [],
        "Assessment" : [("Subject","concerned_by",True),
                        ("Center","holds",True), 
                        ("Study","related_study",False)],
        "ExternalResource" : [("Assessment","external_resources",True),
                              ("Study","related_study",False)],
    }

    _rules = {
        "Center" : [(
                      [("Self","name"),],
                      "Any X WHERE X is Center, X {0} '{1}'"
                   )],
        "Study" : [(
                      [("Self","name"),],
                      "Any X WHERE X is Study, X {0} '{1}'"
                   )],
        "Subject" : [(
                        [("Self","identifier"),],
                        "Any X WHERE X is Subject, X {0} '{1}'"
                     ),
                     (
                        [("Self","code_in_study"),],
                        "Any X WHERE X is Subject, X {0} '{1}'"
                     )],
        "Assessment" : [(
                           [("Subject","code_in_study"),("Self","identifier")],
                           "Any Y WHERE X is Subject, X concerned_by Y, X {0} '{1}', Y {2} '{3}'"
                        )],
        "ExternalResource" : [(
                    [("Subject","code_in_study"),("Assessment","identifier"),("Self","filepath")],
                    "Any Z WHERE X is Subject, X concerned_by Y, X {0} '{1}', \
                     Y external_resources Z, Y {2} '{3}', Z {4} '{5}'"
                  )],
    }

    def __init__(self, parser, *args, **kwargs) :
        """ Init class 
        """
        self.parser = parser
        # each item is a pair perent,childre: [(parameters, [children]),...]
        self.description = self.parser()
        super(Imagen, self).__init__(*args, **kwargs)


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
        center = self.set_entity("Center", 
                                 parent_entities, 
                                 relations = self._relations["Center"],
                                 **self._fields["Center"])
        parent_entities["Center"] = center
        study = self.set_entity("Study", 
                                parent_entities, 
                                relations = self._relations["Study"],
                                **self._fields["Study"])
        parent_entities["Study"] = study

        self._insert_entity(self.description,parent_entities,level=0)

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

            self._insert_entity(children,parent_entities,level+1)

        

    def get_all_centers(self) :
        rqt = "Any X WHERE X is Center"
        return self.send_request(rqt)

    def get_all_studies(self) :
        rqt = "Any X WHERE X is Study"
        return self.send_request(rqt)

    def get_all_subjects(self) :
        rqt = "Any X WHERE X is Subject"
        return self.send_request(rqt)

    def get_all_assessments(self) :
        rqt = "Any X WHERE X is Assessment"
        return self.send_request(rqt)

    def get_all_scans(self) :
        rqt = "Any X WHERE X is Scan"
        return self.send_request(rqt)

    def get_all_fsets(self) :
        rqt = "Any X WHERE X is FileSet"
        return self.send_request(rqt)

    def get_all_fentries(self) :
        rqt = "Any X WHERE X is FileEntries"
        return self.send_request(rqt)

    def _get_time(self):
        return self._time
       
    centers = property(get_all_centers)
    studies = property(get_all_studies)
    subjects = property(get_all_subjects)
    assessments = property(get_all_assessments)
    scans = property(get_all_scans)
    fsets = property(get_all_fsets)
    fentries = property(get_all_fentries)

    time = property(_get_time)

if __name__=="__main__" :

    imagen = Imagen(parser = parse_imagen_process_data,
                    instance = "nsap_imagen",
                    login = "admin",
                    passwd = "alpine")

    #imagen.create_schema()

    #print stop

    imagen()

    print imagen.time

    print imagen.centers
    print imagen.studies

    print stop
    print localizer.subjects
    print localizer.assessments
    print localizer.scans
    print localizer.fsets
    print localizer.fentries

  



