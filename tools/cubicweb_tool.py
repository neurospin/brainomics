
import os, sys
import copy
import timeit
import logging

from cubicweb.dataimport import SQLGenObjectStore
from cubicweb import cwconfig
from cubicweb.dbapi import in_memory_repo_cnx

import nsap.lib.base

import pygraphviz as pgv

class CubicWebTool(object) :
    """ Base class to fill cubicweb database.
    """

    def __init__(self,instance,login,passwd) :
        """ Init class parameters and connexiont to repo.
        """
        self._instance = instance
        self._login = login
        self._passwd = passwd
        self._time = None
  
        self.start_connection()

    def __del__(self) :
        """ Commit and delete object.
        """
        self.stop_connexion()

    ##############
    #   CubicWeb    
    ##############

    def start_connection(self) :
        """ Connextion to repo and store creation.
        """
        self._config = cwconfig.instance_configuration(self._instance)
        self._repo,self._cnx = in_memory_repo_cnx(self._config,login=self._login,
                                                  password=self._passwd)
        self._session = self._repo._get_session(self._cnx.sessionid)
        self._store = SQLGenObjectStore(self._session)

    def stop_connexion(self) :
        """ Close connexion to repo.
        """
        self._store.commit()
        self._session.commit()
        self._cnx.close()
        del self._store, self._session, self._repo, self._cnx, self._config

    def restore_connexion(self) :
        """ Restart the connexion to the repo and create a store
        """
        self.stop_connexion()
        self.start_connection()


    ##############
    # Members    
    ##############

    def send_request(self,request) :
        """ Submit a RQL request.
        """
        try :
            res = self._session.execute(request)
            logging.info(res.rql)
            logging.info(",".join([str(x) for x in res.rows]))
            return res
        except :
            self.restore_connexion()
            logging.info(sys.exc_info())
            return sys.exc_info()

    def _create_entity(self, entity_type, parameters) :
        """ Create a new element.
        """
        entity = self._store.create_entity(entity_type,**parameters)
        self._store.flush()
        return entity

    def check_rules(self, entity_name, entity_parameters, parent_entities) :
        """ Check rules before insertion
        """
        # init
        insert = True

        # check all rules that are defined for entity_name
        for tags,rql in self.rules[entity_name] :
            # first build expression parameters
            rql_parameters = []
            for entity_tag,relation_tag in tags :
                if entity_tag=="Self" :
                    rql_parameters.extend([relation_tag,entity_parameters[relation_tag]]) 
                else :
                    entity = parent_entities[entity_tag]
                    rql_parameters.extend([relation_tag,eval("entity."+relation_tag)]) 

            # then format expression 
            rql = rql.format(*rql_parameters)
            # send the check request
            query_res = self.send_request(rql)

            # finally assert that the entity do not exists
            if query_res.rowcount>0 :
                insert = False
                # return the entity and raise exeptioon if not unique
                if query_res.rowcount>1 :
                    raise Exception("the database is corrupted, please investigate")

                return (insert,query_res.get_entity(0,0))
                
        return (insert,None)
      
    def set_entity(self,entity_name,parent_entities,relations,**kwargs) :
        """ insert entity
        """
        entity_parameters = kwargs
        insert,entity = self.check_rules(entity_name,entity_parameters,
                                         parent_entities)

        if insert :
            # insert entity
            rqt_parameters = ["X {0} '{1}'".format(x,y) for x,y in entity_parameters.items()]
            rqt_parameters = ",".join(rqt_parameters)
            rqt = "INSERT {0} X: {1}".format(entity_name,rqt_parameters)

            print rqt

            query_res = self.send_request(rqt)
            entity = query_res.get_entity(0,0)

            # create relations
            for to_entity_name,rtype,invert in relations :
                to_entity = parent_entities[to_entity_name]
                if invert :
                    rqt = "SET X {0} Y WHERE X eid {1}, \
                           Y eid {2}".format(rtype,to_entity.eid,entity.eid)
                else :
                    rqt = "SET X {0} Y WHERE X eid {1}, \
                           Y eid {2}".format(rtype,entity.eid,to_entity.eid)
                print rqt
                query_res = self.send_request(rqt)
                print query_res

        return entity


    ##############
    #   Utils    
    ##############

    def create_schema(self, text_font="sans-serif", node_text_size=12) :
        """ Create Sub Graph
        """

        graph = pgv.AGraph(strict=False,directed=True,rankdir='LR',overlap=False)
        for entity,items in self.fields.iteritems() :

            t_labels = []
            for item in items.keys() :
                t_labels.append(item)

            graph.add_node(entity, style="filled", fillcolor='blue',
                           fontcolor="white", fontsize=node_text_size,
                           fontname=text_font,
                           label=entity + "|" + "|".join(t_labels),
                           shape='Mrecord')

        for entity, relations in self.relations.iteritems():
            for node, relation, direction in relations:
                if direction:
                    graph.add_edge(node, entity, label=relation)
                else:
                    graph.add_edge(entity, node, label=relation)


        # save figure
        folder = os.getcwd()
        if "CW_INSTANCES_DATA_DIR" in os.environ.keys() :
            folder = os.environ["CW_INSTANCES_DATA_DIR"]
        graph.draw(os.path.join(folder,"schema",self._instance+".png"), prog='dot')
        

    ##############
    # Properties #
    ##############

    def _get_fields(self) :
        raise NotImplementedError()

    def _get_relations(self) :
        raise NotImplementedError()

    def _get_rules(self) :
        raise NotImplementedError()
    
    rules = nsap.lib.base.LateBindingProperty(_get_rules)
    relations = nsap.lib.base.LateBindingProperty(_get_relations)
    fields = nsap.lib.base.LateBindingProperty(_get_fields)
        
