import os
import sys
import time
import datetime
import traceback
from glob import glob
from csv import reader
from cubicweb import dbapi

########################################################################
# Usage : python import_quest.py quest
# insert questionnaire(s) passed as argument quest into DB,
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

c = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin', password='admin')

#date is unused
t = time.gmtime()
date = datetime.date(t.tm_year, t.tm_mon, t.tm_mday).isoformat()[:10]

#Local cache variables
subjects = dict(c.cursor().execute('Any I, S WHERE S is Subject, S identifier I'))
QUESTIONS = dict(c.cursor().execute('Any I, X WHERE X is Question, X identifier I'))
QUESTION_POSSIBLE_ANSWERS = dict(c.cursor().execute('Any X, A WHERE X is Question, X possible_answers A'))


def main(argv):

    print len(argv)
    print argv[1]
    print date, c

    try:
        #if argv[1] is a file, call insert_quest method to insert this questionnary in DB
        file(argv[1])
        insert_quest(argv)
    except:
        #if argv[1] is not a file, it should be a directory containing csv questionnary files to be inserted in DB
        l = glob(os.path.join(argv[1], '*.csv'))
        for i in l:
            print i
            insert_quest(['import_quest.py', i])

    # Update all questions
    for eid, pa in QUESTION_POSSIBLE_ANSWERS.iteritems():
        #Escape \, " and ' in possible_answer value
        if pa and pa is not 'None':
            pa = pa.replace("\\", "\\\\")
            pa = pa.replace('"', '\\"')
            pa = pa.replace("'", "\\'")
            #debug
            print 'pa', pa, 'eid', eid
        c.cursor().execute("SET X possible_answers '%(pa)s' WHERE X eid %(eid)s" % {'eid': eid, 'pa': pa})
        c.commit()


def insert_quest(argv):
    for i in subjects:
        print i, subjects[i]

    i = argv[1].find('-')
    j = argv[1][i+1:].find('-')
    print argv[1][i+1:i+1+j]
    #try :
    #    c.cursor().execute('INSERT Study X: X name \'Imagen\', X data_filepath \'\', X description \'Imagen Study\'')
    #    print 'Imagen inserted'
    #except :
    #    c.rollback()
    #    print 'cannot insert Study Imagen'

    validated = False
    language = ''
    try:
        lignes = reader(open(argv[1]))
        first_ligne = lignes.next()
        #Child questionnaire have 12 columns, the last one ('Valid'), is not present for parent questionnaire
        if len(first_ligne) == 12:
            print first_ligne[11]
            if first_ligne[11] == 'Valid':
                validated = True
        first_ligne = lignes.next()
        #language is set here for the whole questionnaire
        language = first_ligne[2]
    #Just for more fun, some questionnaire are empty...
    except StopIteration:
        return
    questionnaire = argv[1][i+1:i+1+j]
    version = ''
    if questionnaire[-4:-1] == '_RC':
        version = questionnaire[-3:]
        questionnaire = questionnaire[:-4]
    if questionnaire[:5] == 'IMGN_':
        questionnaire = questionnaire[5:]
    print 'questionnaire = ', questionnaire
    print 'version = ', version
    try:
        req = ("INSERT Questionnaire Q: Q name '%(a)s', "
               "Q identifier '%(identifier)s', Q type '%(type)s', "
               "Q version '%(version)s', Q language '%(language)s', "
               "Q note_format 'text/html'"
               % {'questionnaire': questionnaire,
                  'identifier': questionnaire,
                  'type': questionnaire,
                  'version': version,
                  'language': language}
               )
        #print 'req = ', req
        res = c.cursor().execute(req)
        #print 'res = ', res
    except:
        c.rollback()
        print 'cannot insert Questionnaire %s' % argv[1][i+1:i+1+j]
    #city has to be read from filepath
    city = 'BERLIN'
    center = {
        'LONDON': 1, 'NOTTINGHAM': 2, 'DUBLIN': 3, 'BERLIN': 4,
        'HAMBURG': 5, 'MANNHEIM': 6, 'PARIS': 7, 'DRESDEN': 8,
    }
    center_id = center[city]

    lignes = reader(open(argv[1]))
    old_subject = None
    position = 0
    for l in lignes:
        subject = l[0]

        #the file may contain information for subjects who are not in DB
        if 'IMAGEN_%s' % subject[0:12] in subjects:
            print '%s' % subject[0:12]
            #if the current line concerns the same subject than the precedent one only increment the question position
            if subject == old_subject:
                position += 1
                #print position, 'Q : ',l[7],', Answer : ',l[8],', time : ',l[10]
            #else a new subject is treated and the question position index is reset to 0
            else:
                old_subject = subject
                position = 0
                #print '====='
                #print l
                #print subject

            #age_for_subject maybe one of those two following values
            if l[4] != '':
                #Completed Timestamp
                age = l[4]
            else:
                #Processed Timestamp
                age = l[5]
            if l[3] == 't':
                completed = 'True'
            else:
                completed = 'False'
            assesment_id = questionnaire + subject[0:12] + '_' + age
            questionnairerun_id = assesment_id + '_' + l[1]
            if age.isdigit():
                req = ("INSERT Assessment A, "
                       "QuestionnaireRun Q: A identifier '%(assesment)s', "
                       "A age_of_subject '%(age)s', "
                       "A timepoint 'FU2', "
                       "Q identifier '%(questionnairerun)s', "
                       "Q user_ident '%(subject)s', "
                       "Q iteration '%(iteration)s', "
                       "Q completed %(completed)s"
                       % {'assesment': assesment_id,
                          'age': age,
                          'questionnairerun': questionnairerun_id,
                          'subject': subject[13:14],
                          'completed': completed,
                          'iteration': l[1]}
                       )
            else:
                req = ("INSERT Assessment A, "
                       "QuestionnaireRun Q: A identifier '%(assesment)s', "
                       "A timepoint 'FU2', "
                       "Q identifier '%(questionnairerun)s', "
                       "Q user_ident '%(subject)s', "
                       "Q iteration '%(iteration)s', "
                       "Q completed %(completed)s"
                       % {'assesment': assesment_id,
                          'questionnairerun': questionnairerun_id,
                          'subject': subject[13:14],
                          'completed': completed,
                          'iteration': l[1]}
                       )
            #parent questionnaire have no field "Valid"
            if validated:
                valid = 'False'
                if l[11] == 't':
                    valid = 'True'
                req += ', Q valid ' + valid
            req = req + (", Q concerns S, Q instance_of X, "
                         "Q related_study Y Where S is Subject, "
                         "X is Questionnaire, Y is Study, "
                         "S identifier 'IMAGEN_%(subject)s', "
                         "X identifier '%(questionnaire)s', Y name 'Imagen'"
                         % {'subject': subject[0:12],
                            'questionnaire': questionnaire}
                         )
            #iteration field is read only once time from the first question of each subject's questionnaire expecting only one iteration value for a questionnaire
            try:
                print 'req = ', req
                res = c.cursor().execute(req)
                print 'res = ', res
            except:
                c.rollback()
                print 'cannot insert Assessment and QuestionnaireRun %(a)s%(b)s_%(c)s' % {'a': argv[1][i+1:i+1+j], 'b': subject[0:12], 'c': age}
            try:
                assesment_id = questionnaire + subject[0:12] + '_' + age
                req = ("SET A related_study S Where A is Assessment, "
                       "S is Study, S name 'Imagen', "
                       "A identifier '%(assesment)s'"
                       % {'assesment': assesment_id}
                       )
                c.cursor().execute(req)
                req = ("SET C holds A Where A is Assessment, "
                       "C is Center, C identifier '%(center)s', "
                       "A identifier '%(assesment)s'"
                       % {'assesment': assesment_id, 'center': center_id}
                       )
                c.cursor().execute(req)
                req = ("SET S concerned_by A Where A is Assessment, "
                       "S is Subject, S identifier 'IMAGEN_%(subject)s', "
                       "A identifier '%(assesment)s'"
                       % {'subject': subject[0:12], 'assesment': assesment_id}
                       )
                c.cursor().execute(req)
                questionnairerun_id = questionnaire + subject[0:12] + '_' + age + '_' + l[1]
                req = ("SET A generates Q Where A is Assessment, "
                       "Q is QuestionnaireRun, "
                       "A identifier '%(assesment)s', "
                       "Q identifier '%(questionnairerun)s'"
                       % {'assesment': assesment_id, 'questionnairerun': questionnairerun_id}
                       )
                c.cursor().execute(req)
            except:
                c.rollback()
                print 'cannot relate Assessment and QuestionnaireRun %(a)s%(b)s_%(c)s' % {'a': argv[1][i+1:i+1+j], 'b': subject[0:12], 'c': age}
            #print position, 'Q : ',l[7],', Answer : ',l[8],', time : ',l[10]
            try:
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
                        #This case should never happen. If it does the CSV file may be corrupted.
                        raise Exception('Uuuh? (...\x1e, \x1f are Record Seprator and Unit Separator...)')
                    possible_answers = unicode(value)
                    value = 0
                    _type = u'text'
                # Question
                identifier = l[7] + '_' + questionnaire
                if identifier in QUESTIONS:
                    question_eid = QUESTIONS[identifier]
                    # Update possible answer
                    if possible_answers:
                        old_possible_answers = (QUESTION_POSSIBLE_ANSWERS[question_eid] or u'').split(US)
                        if possible_answers not in old_possible_answers:
                            old_possible_answers += (possible_answers,)
                            QUESTION_POSSIBLE_ANSWERS[question_eid] = US.join(old_possible_answers)
                        value = old_possible_answers.index(possible_answers)
                    #print 'value',value
                else:
                    req = ("INSERT Question Q: Q identifier '%(question)s', "
                           "Q position '%(position)s', Q text '%(text)s', "
                           "Q type '%(type)s', "
                           "Q possible_answers '%(answers)s', "
                           "Q questionnaire X Where X is Questionnaire, "
                           "X identifier '%(questionnaire)s'"
                           % {'question': identifier,
                              'position': position,
                              'text': l[7],
                              'type': _type,
                              'answers': possible_answers,
                              'questionnaire': questionnaire}
                           )
                    question = c.cursor().execute(req)
                    #print 'question[0][0] = ',question[0][0], 'possible_answers = ', possible_answers
                    QUESTIONS[identifier] = question[0][0]
                    question_eid = question[0][0]
                    QUESTION_POSSIBLE_ANSWERS[question_eid] = possible_answers
                # Answer
                questionnaire_id = questionnaire + subject[0:12] + '_' + age + '_' + l[1]
                req = ("Any A, X Where A is Answer, X is QuestionnaireRun, "
                       "Q is Question, A question Q, "
                       "Q identifier '%(question)s', "
                       "A questionnaire_run X, "
                       "X identifier '%(questionnaire)s'"
                       % {'question': identifier, 'questionnaire': questionnaire_id}
                       )
                res = c.cursor().execute(req)
                if not res:
                    req = ("INSERT Answer A: A value '%(answer)s', A question Q, "
                           "A questionnaire_run X Where Q is Question, "
                           "X is QuestionnaireRun, "
                           "Q identifier '%(question)s', "
                           "X identifier '%(questionnaire)s'"
                           % {'answer': value,
                              'question': identifier,
                              'questionnaire': questionnaire_id})
                    c.cursor().execute(req)
            except Exception as e:
                c.rollback()
                print 'cannot insert Question %(q)s and Answer %(a)s' % {'q': l[7], 'a': l[8]}
                e_t, e_v, e_tb = sys.exc_info()
                print 'Exc', e_t, e_v
                traceback.print_tb(e_tb)
        #commit must be done here to avoid insertion of current question/answer be rollbacked by a next rollback() method call
        c.commit()

if __name__ == '__main__':
    main(sys.argv)
