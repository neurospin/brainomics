# -*- coding: utf-8 -*-

import os
import os.path
import sys
import time
import datetime
import traceback
import csv
import logging

########################################################################
# Usage : cubicweb-ctl shell instance import_quest.py quest
# insert questionnaire(s) passed as argument quest into DB,
# instance should be started before lauching this script,
# quest might be a csv file or a directory containing csv files
#
# It connect via "ZMQ" to a CubicWeb DB, that should be started before
# It parse each line of the csv file passed as argument and insert the
# corresponding question/answer into DB by proceding as the following
# heuristic schema:
#
#       create_entity('Study') -> actually the only study used is Imagen
#       create_entity('Questionnaire')
#       create_entity('Device') -> useless
#       create_entity('Assessment')
#       create_entity('QuestionnaireRun',
#                     instance_of=questionnaire_eid,
#                     uses_device=device_eid)
#
#       If an entity identifier is already in DB, DB return an Error and
#       the connection is rolled back
#
#       add_relation(assessment_eid, 'related_study', study_eid)
#       add_relation(assessment_eid, 'generates', questionnairerun_eid)
#       add_relation(questionnairerun_eid, 'related_study', study_eid)
#       add_relation(questionnairerun_eid, 'concerns', subject_eid)
#
#       create_entity('Question', questionnaire=questionnaire_eid)
#       create_entity('Answer')
#
#       Before to insert a new answer, search in DB if current
#       questionnaireRun has already one answer for the corresponding
#       question, if so, consider it as the good one, don't insert the
#       value again
#
#


#date is unused
t = time.gmtime()
date = datetime.date(t.tm_year, t.tm_mon, t.tm_mday).isoformat()[:10]
count = 0

#cnx = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin',
#password='admin')

#Local cache variables
subjects = dict(
    session.execute('Any I, S WHERE S is Subject, S identifier I'))
QUESTIONS = dict(
    session.execute('Any I, X WHERE X is Question, X identifier I'))
QUESTION_POSSIBLE_ANSWERS = dict(session.execute(
    'Any X, A WHERE X is Question, X possible_answers A'))


def main(path, cnx):
    logging.basicConfig(filename='log.txt', level=logging.INFO)
    print path
    print 80 * '*'
    logging.info(date)
    logging.info(80 * '*')
    logging.info('count = %s' % count)

    print 80 * '*'
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if os.path.splitext(filename)[1] == '.csv':
                insert_questionnaire(os.path.join(path, filename), cnx)
    else:
        insert_questionnaire(path, cnx)

    # Update all questions
    for eid, pa in QUESTION_POSSIBLE_ANSWERS.iteritems():
        #Escape \, " and ' in possible_answer value
        if pa and pa is not 'None':
            pa = pa.replace("\\", "\\\\")
            pa = pa.replace('"', '\\"')
            pa = pa.replace("'", "\\'")
            #debug
            #print 'pa', pa, 'eid', eid
            req = ("SET X possible_answers '%(pa)s' WHERE X eid %(eid)s"
            % {'eid': eid, 'pa': pa})
            logging.info('req = %s' % req)
            res = session.execute(req)
            logging.info('res = %s' % res)
    logging.info(80 * '*')
    logging.info('%s QuestionnaireRun inserted' % count)
    print 80 * '*'
    print '%s QuestionnaireRun inserted' % count
    cnx.commit()


def create_entity_safe(entity_name, **entity):
    db_entity = None
    is_existe = False
    req = "Any X where X is %(a)s, X identifier '%(b)s'" % {
        'a': entity_name, 'b': entity['identifier']}
    #print 'req %s' % req
    res = session.execute(req)
    #print 'res %s' % res
    if res:
        is_existe = True
    if not is_existe:
        req = "INSERT %s E: " % entity_name
        for i in entity:
            if entity[i] == True or entity[i] == False:
                req = req + "E %(a)s %(b)s," % {
                    'a': i, 'b': entity[i]}
            else:
                req = req + "E %(a)s '%(b)s'," % {
                    'a': i, 'b': entity[i]}
        req = req[:-1]
        #print 'req %s' % req
        db_entity = session.execute(req)
        #print 'db_entity %s' % db_entity
    else:
        return None
    return db_entity


def insert_questionnaire(filename, cnx):
    #for i in subjects:
    #    print i, subjects[i]
    global count
    i = filename.find('-')
    j = filename[i + 1:].find('-')
    logging.info(filename[i + 1:i + 1 + j])
    #try :
    #    session.execute('''INSERT Study X: X name \'Imagen\',
    #        X data_filepath \'\', X description \'Imagen Study\'''')
    #    print 'Imagen inserted'
    #except :
    #    cnx.rollback()
    #    print 'cannot insert Study Imagen'

    validated = False
    language = ''
    try:
        with open(filename) as csvfile:
            lignes = csv.reader(csvfile)
            first_ligne = lignes.next()
            #Child questionnaire have 12 columns, the last one
            #('Valid'), is not present for parent questionnaire
            if len(first_ligne) == 12:
                #print first_ligne[11]
                if first_ligne[11] == 'Valid':
                    validated = True
            first_ligne = lignes.next()
            #language is set here for the whole questionnaire
            language = first_ligne[2]
    #Just for more fun, some questionnaire are empty...
    except StopIteration:
        return
    questionnaire = filename[i + 1:i + 1 + j]
    version = ''
    if questionnaire[-4:-1] == '_RC':
        version = questionnaire[-3:]
        questionnaire = questionnaire[:-4]
    if questionnaire[:5] == 'IMGN_':
        questionnaire = questionnaire[5:]
    #print 'questionnaire = ', questionnaire
    #print 'version = ', version
    quest = {}
    quest['name'] = unicode(questionnaire)
    quest['identifier'] = unicode(questionnaire)
    quest['type'] = unicode(questionnaire)
    quest['version'] = unicode(version)
    quest['language'] = unicode(language)
    res = create_entity_safe('Questionnaire', **quest)
        #print 'req = ', req
        #res = session.execute(req)
        #print 'res = ', res
    if not res:
        logging.info(
            'cannot insert Questionnaire %s' % filename[i + 1:i + 1 + j])
    else:
        logging.info('Questionnaire %s inserted' % filename[i + 1:i + 1 + j])
        #city has to be read from filepath
        city = 'BERLIN'
        center = {
            'LONDON': 1, 'NOTTINGHAM': 2, 'DUBLIN': 3, 'BERLIN': 4,
            'HAMBURG': 5, 'MANNHEIM': 6, 'PARIS': 7, 'DRESDEN': 8,
        }
        center_id = center[city]

        csvfile = open(filename)
        lignes = csv.reader(csvfile)
        old_subject = None
        old_iter = None
        position = 0
        for l in lignes:
            subject = l[0]
            iteration = l[1]

            #the file may contain information for subjects who are not in DB
            if 'IMAGEN_%s' % subject[0:12] in subjects:
                #print '%s' % subject[0:12]
                #age_for_subject maybe one of those two following values
                if l[4] != '':
                    #Completed Timestamp
                    age = l[4]
                else:
                    #Processed Timestamp
                    age = l[5]
                if l[3] == 't':
                    completed = True
                else:
                    completed = False
                #if the current line concerns the same subject than the
                #precedent one only increment the question position
                if subject == old_subject and iteration == old_iter:
                    position += 1
                    #print position, 'Q : ',l[7],', Answer : ',l[8],',
                    # time : ',l[10]
                #else a new subject is treated and the question position
                #index is reset to 0
                else:
                    count = count + 1
                    old_subject = subject
                    old_iter = iteration
                    position = 0
                    #print '====='
                    #print l
                    #print subject

                    assessment_id = unicode(
                    questionnaire + subject[0:12] + '_' + age + '_'
                    + iteration)
                    questionnairerun_id = assessment_id
                    quest = {}
                    quest['identifier'] = unicode(questionnairerun_id)
                    quest['user_ident'] = unicode(subject[13:14])
                    quest['iteration'] = unicode(iteration)
                    quest['completed'] = completed
                    #parent questionnaire have no field "Valid"
                    if validated:
                        valid = False
                        if l[11] == 't':
                            valid = True
                        quest['valid'] = valid
                    logging.debug('create QuestionnaireRun')
                    res_quest = create_entity_safe('QuestionnaireRun', **quest)
                    logging.debug('res %s' % res_quest)
                    print 'End create QuestionnaireRun'
                    if not res_quest:
                        logging.info(
                        'cannot insert QuestionnaireRun %(a)s%(b)s_%(c)s' % {
                        'a': filename[i + 1:i + 1 + j], 'b': subject[0:12],
                        'c': age})
                    else:
                        asses = {}
                        if age.isdigit():
                            asses['age_of_subject'] = age
                        asses['identifier'] = assessment_id
                        asses['timepoint'] = u'FU2'
                        logging.debug('create Assessment')
                        res_asses = create_entity_safe('Assessment', **asses)
                        logging.debug('res %s' % res_asses)
                        logging.debug('End create Assessment')
                        if not res_asses:
                            logging.debug('''cannot insert Assessment for
                            QuestionnaireRun %(a)s%(b)s_%(c)s''' % {
                            'a': filename[i + 1:i + 1 + j], 'b': subject[0:12],
                            'c': age})
                        else:
                            #print 'relate Assessment and QuestionnaireRun'
                            subject_id = 'IMAGEN_%(subject)s' % {
                                'subject': subject[0:12]}
                            req = (
                            "SET Q concerns S Where Q is QuestionnaireRun, "
                                   "S is Subject, S identifier '%(subject)s', "
                                   "Q identifier '%(questionnaire)s'"
                                   % {'subject': subject_id,
                                   'questionnaire': questionnairerun_id}
                                   )
                            res = session.execute(req)
                            #print 'res1 %s' % res
                            req = ("SET Q related_study S Where Q is "
                                   "QuestionnaireRun,"
                                   " S is Study, S name 'Imagen', "
                                   "Q identifier '%(quest)s'"
                                   % {'quest': questionnairerun_id}
                                   )
                            res = session.execute(req)
                            #print 'res2 %s' % res
                            req = (
                            "SET Q instance_of X Where Q is QuestionnaireRun, "
                                   "X is Questionnaire, "
                                   "Q identifier '%(quest)s',"
                                   "X identifier '%(questionnaire)s'"
                                   % {'quest': questionnairerun_id,
                                   'questionnaire': questionnaire}
                                   )
                            res = session.execute(req)
                            #print 'res3 %s' % res
                            req = (
                            "SET A related_study S Where A is Assessment, "
                                   "S is Study, S name 'Imagen', "
                                   "A identifier '%(assessment)s'"
                                   % {'assessment': assessment_id}
                                   )
                            res = session.execute(req)
                            #print 'res4 %s' % res
                            req = ("SET C holds A Where A is Assessment, "
                                   "C is Center, C identifier '%(center)s', "
                                   "A identifier '%(assessment)s'"
                                   % {'assessment': assessment_id,
                                   'center': center_id}
                                   )
                            res = session.execute(req)
                            #print 'res5 %s' % res
                            req = (
                            "SET S concerned_by A Where A is Assessment, "
                            "S is Subject, S identifier 'IMAGEN_%(subject)s', "
                                   "A identifier '%(assessment)s'"
                                   % {'subject': subject[0:12],
                                   'assessment': assessment_id}
                                   )
                            res = session.execute(req)
                            #print 'res6 %s' % res
                            questionnairerun_id = questionnaire + subject[0:12]
                            + '_' + age + '_' + iteration
                            req = ("SET A generates Q Where A is Assessment, "
                                   "Q is QuestionnaireRun, "
                                   "A identifier '%(assessment)s', "
                                   "Q identifier '%(questionnairerun)s'"
                                   % {'assessment': assessment_id,
                                   'questionnairerun': questionnairerun_id}
                                   )
                            res = session.execute(req)
                            #print 'res7 %s' % res
                            #print 'End relate Assessment and QuestionnaireRun'
                    #    print '''cannot relate Assessment and
                    #QuestionnaireRun %(a)s%(b)s_%(c)s''' % {
                    #'a': filename[i+1:i+1+j], 'b': subject[0:12], 'c': age}
                #print position, 'Q : ',l[7],', Answer : ',l[8],',
                #time : ',l[10]
                #Unit Separator
                US = '\x1f'

                value = l[8]
                try:
                    value = float(value)
                    possible_answers = None
                    _type = u'numerical'
                except ValueError:
                    # keep string as int, use possible_answers
                    if value.find(US) >= 0:
                        #This case should never happen.
                        #If it does the CSV file may be corrupted.
                        raise Exception(
                        '''Uuuh? (...\x1e, \x1f are Record Seprator
                        and Unit Separator...)''')
                    #Escape \, " and ' in possible_answer value
                    value = value.replace("\\", "\\\\")
                    value = value.replace('"', '\\"')
                    value = value.replace("'", "\\'")
                    possible_answers = unicode(value)
                    value = 0
                    _type = u'text'
                # Question
                identifier = l[7] + '_' + questionnaire
                if identifier in QUESTIONS:
                    question_eid = QUESTIONS[identifier]
                    # Update possible answer
                    if possible_answers:
                        old_possible_answers = (
                        QUESTION_POSSIBLE_ANSWERS[question_eid] or u''
                        ).split(US)
                        if possible_answers not in old_possible_answers:
                            old_possible_answers += (possible_answers,)
                            QUESTION_POSSIBLE_ANSWERS[
                            question_eid] = US.join(old_possible_answers)
                        value = old_possible_answers.index(possible_answers)
                    #print 'value',value
                else:
                    quest = {}
                    quest['identifier'] = unicode(identifier)
                    quest['position'] = unicode(position)
                    quest['text'] = unicode(l[7])
                    quest['type'] = unicode(_type)
                    quest['possible_answers'] = unicode(possible_answers)
                    question = create_entity_safe('Question', **quest)
                    if question:
                        req = ("SET Q questionnaire X Where Q is Question, "
                        "X is Questionnaire, X identifier "
                        "'%(questionnaire)s', "
                        "Q identifier '%(question)s'"
                        % {'questionnaire': questionnaire,
                        'question': identifier}
                        )
                        session.execute(req)

                        #print 'question = %s'% question
                        #print 'question[0] = %s'% question[0]
                        #print 'question[0][0] = %s'% question[0][0]
                        #print 'question.eid = %s'% question.eid
                        #print 'possible_answers = ', possible_answers
                        QUESTIONS[identifier] = question[0][0]
                        question_eid = question[0][0]
                        QUESTION_POSSIBLE_ANSWERS[question_eid] =
                        possible_answers
                # Answer
                questionnaire_id = questionnaire + subject[0:12] + '_'
                + age + '_' + l[1]
                req = ("Any A, X Where A is Answer, X is QuestionnaireRun, "
                       "Q is Question, A question Q, "
                       "Q identifier '%(question)s', "
                       "A questionnaire_run X, "
                       "X identifier '%(questionnaire)s'"
                       % {'question': identifier,
                       'questionnaire': questionnaire_id}
                       )
                res = session.execute(req)
                if not res:
                    req = ("INSERT Answer A: A value '%(answer)s', "
                           "A question Q, "
                           "A questionnaire_run X Where Q is Question, "
                           "X is QuestionnaireRun, "
                           "Q identifier '%(question)s', "
                           "X identifier '%(questionnaire)s'"
                           % {'answer': value,
                              'question': identifier,
                              'questionnaire': questionnaire_id})
                    session.execute(req)
                    #print 'Answer %s inserted' % value
                #except Exception as e:
                #    session.rollback()
                #    print 'cannot insert Question %(q)s and Answer %(a)s' % {
                #    'q': l[7], 'a': l[8]}
                #    e_t, e_v, e_tb = sys.exc_info()
                #    print 'Exc', e_t, e_v
                #    traceback.print_tb(e_tb)
                #print 'End of line'
                #commit must be done here to avoid insertion of current
                #question/answer be rollbacked by a next rollback() method call
                if (count % 100 == 0):
                    session.commit()
                    session.set_cnxset()
                    logging.info(80 * '*')
                    logging.info(
                    'already %s QuestionnaireRun inserted' % count)
                    print 80 * '*'
                    print 'already %s QuestionnaireRun inserted' % count
    logging.info('End of csv file')
    csvfile.close()


if __name__ == '__main__':

    main(sys.argv[-1], cnx)
