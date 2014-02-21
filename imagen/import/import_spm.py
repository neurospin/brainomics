########################################################################
#
# Usage: python import_spm.py
# insert various file contained in both following directories
# /neurospin/imagen/FU2/processed/spmpreproc
# /neurospin/imagen/FU2/processed/spmstatsintra
# into database
#
# NB: import_spm.py could not actually work properly the second
# launched time partly because ExternalResource have no unique field
#
########################################################################

import os
import sys
import time
import datetime
import traceback
import nibabel as nib
from glob import glob
from csv import reader
from cubicweb import dbapi
c = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin',
password='admin')

centers = dict(c.cursor().execute('''Any I, C WHERE C is Center,
C identifier I'''))
subjects = dict(c.cursor().execute('''Any I, S WHERE S is Subject,
S identifier I'''))
psc_center_file = '/neurospin/imagen/src/scripts/psc_tools/psc2_centre.csv'
psc_center = {}
for i in reader(open(psc_center_file)):
    psc_center[i[0]] = i[1]

PREPROC = '/neurospin/imagen/FU2/processed/spmpreproc/'
STATS = '/neurospin/imagen/FU2/processed/spmstatsintra/'


def main(argv):
    t = time.gmtime()
    date = datetime.date(
    t.tm_year, t.tm_mon, t.tm_mday).isoformat()[:10]
    print date
    #SPMPREPROC
    l = os.path.join(PREPROC, '*/Session*/*/*')
    print l
    l = glob(l)
    for i in l:
        print i
        psc = os.path.abspath(i).split('/')[-4]
        if 'IMAGEN_%s' % psc in subjects:
            print 'psc = %s' % psc
            cw_uri = os.path.abspath(i)
            scan = cw_uri.split('/')[-2]
            if i[-7:] == '.nii.gz':
                print 'Scan : %(a)s %(b)s %(c)s' % {'a': psc, 'b': cw_uri,
                'c': scan}
                insert_scan(psc, cw_uri, scan)
            else:
                print 'ExternalResource : %(a)s %(b)s' % {'a': psc,
                'b': cw_uri}
                insert_externalResource(psc, cw_uri)
    l = os.path.join(PREPROC, '*/mprage/*')
    print l
    l = glob(l)
    for i in l:
        print i
        psc = os.path.abspath(i).split('/')[-3]
        if 'IMAGEN_%s' % psc in subjects:
            print 'psc = %s' % psc
            cw_uri = os.path.abspath(i)
            scan = cw_uri.split('/')[-2]
            if i[-7:] == '.nii.gz':
                print 'Scan : %(a)s %(b)s %(c)s' % {'a': psc, 'b': cw_uri,
                'c': scan}
                insert_scan(psc, cw_uri, scan)
            else:
                print 'ExternalResource : %(a)s %(b)s' % {'a': psc,
                'b': cw_uri}
                insert_externalResource(psc, cw_uri)
    #SPMSTATSINTRA
    l = os.path.join(STATS, '*/Session*/*/*/*')
    print l
    l = glob(l)
    for i in l:
        print i
        psc = os.path.abspath(i).split('/')[-5]
        if 'IMAGEN_%s' % psc in subjects:
            print 'psc = %s' % psc
            cw_uri = os.path.abspath(i)
            scan = cw_uri.split('/')[-3]
            if i[-7:] == '.nii.gz':
                print 'Scan : %(a)s %(b)s %(c)s' % {'a': psc, 'b': cw_uri,
                'c': scan}
                insert_scan(psc, cw_uri, scan)
            else:
                print 'ExternalResource : %(a)s %(b)s' % {'a': psc,
                'b': cw_uri}
                insert_externalResource(psc, cw_uri)


def insert_scan(psc, cw_uri, scan):
    identifier = cw_uri.split('/')[-1]
    identifier = identifier.replace('.nii.gz', '')
    identifier = 'IMAGEN_%(e)s_%(d)s' % {'e': scan, 'd': identifier}
    label = cw_uri.split('/')[-1]
    print 'MRIData :'
    print 'sequence = ', scan
    img = nib.load(cw_uri)
    hdr = img.get_header()
    #print hdr
    raw = hdr.structarr
    shape = raw['dim'].tolist()
    shape_x = shape[0]
    shape_y = shape[1]
    shape_z = shape[2]
    print 'shape_xyz = ', shape_x, shape_y, shape_z
    res_x = raw['pixdim'].tolist()[1]
    res_y = raw['pixdim'].tolist()[2]
    res_z = raw['pixdim'].tolist()[3]
    print 'voxel_res_xyz = ', res_x, res_y, res_z
    tr = raw['db_name'].tolist().split('TR:')[-1].split(' TE:')[0]
    te = raw['db_name'].tolist().split('TE:')[-1]
    print 'tr = ', tr, 'te = ', te

    studies = dict(c.cursor().execute('''Any N, S WHERE S is Study,
    S name N'''))
    study_eid = studies['Imagen']

    try:
        print 'a,e = %(a)s %(e)s' % {'a': psc, 'e': identifier}
        print psc_center[psc]
        req = '''INSERT Assessment A: A identifier \'%(e)s\',
        A timepoint \'FU2\', A related_study S, C holds A,
        X concerned_by A WHERE S is Study, C is Center,
        X is Subject, S name 'Imagen', C identifier \'%(d)s\',
        X identifier \'IMAGEN_%(a)s\'
        ''' % {'a': psc, 'd': psc_center[psc], 'e': identifier}
        print 'req = ', req
        c.cursor().execute(req)
        print 'Assessment inserted'
    except:
        c.rollback()
        print 'Can not insert Assessment'

    try:
        req = '''INSERT MRIData M, Scan S: M sequence \'%(a)s\'
        ''' % {'a': scan}
        req = req + ', M shape_x %s' % shape_x
        req = req + ', M shape_y %s' % shape_y
        req = req + ', M shape_z %s' % shape_z
        req = req + ', M voxel_res_x %s' % res_x
        req = req + ', M voxel_res_y %s' % res_y
        req = req + ', M voxel_res_z %s' % res_z
        if tr:
            req = req + ', M tr %s' % tr
        if te:
            req = req + ', M te %s' % te
        #print 'req = ', req
        req_end = ''', S has_data M, S identifier \'%(d)s\',
        S label \'%(e)s\', S type \'NIFTI\',
        S format \'NIFTI COMPRESSED\',
        S completed True, S valid True, S filepath \'%(c)s\',
        S related_study X WHERE X is Study, X name \'Imagen\'
        ''' % {'a': psc, 'c': cw_uri, 'd': identifier, 'e': label}

        req = req + req_end
        print 'req = ', req

        c.cursor().execute(req)

        res = c.cursor().execute(
        '''SET S concerns Y Where S is Scan,
        Y is Subject, S identifier \'%(a)s\',
        Y identifier \'IMAGEN_%(b)s\'
        ''' % {'a': identifier, 'b': psc})
        #print 'res = ', res
        res = c.cursor().execute(
        '''SET A generates S Where A is Assessment, S is Scan,
        S identifier \'%(a)s\', A identifier \'%(a)s\'
        ''' % {'a': identifier})
        #print 'res = ',res
        print 'Scan inserted'
        c.commit()
    except Exception as e:
        c.rollback()
        print 'Can not insert Scan'
        e_t, e_v, e_tb = sys.exc_info()
        print 'Exc', e_t, e_v, e_tb
        traceback.print_tb(e_tb)


def insert_externalResource(psc, cw_uri):
    identifier = cw_uri.split('/')[-1]
#    identifier = identifier.replace('.nii.gz', '')
#    identifier = 'IMAGEN_%(a)s' % {'a': identifier}
    studies = dict(c.cursor().execute('''Any N, S WHERE S is Study,
    S name N'''))
    study_eid = studies['Imagen']

    try:
        print 'a,e = %(a)s %(e)s' % {'a': psc, 'e': identifier}
        print psc_center[psc]
        req = '''INSERT Assessment A: A identifier \'%(e)s\',
        A timepoint \'FU2\', A related_study S, C holds A,
        X concerned_by A WHERE S is Study, C is Center, X is Subject,
        S name \'Imagen\', C identifier \'%(d)s\',
        X identifier \'IMAGEN_%(a)s\'
        ''' % {'a': psc, 'd': psc_center[psc], 'e': identifier}
        print 'req = ', req
        c.cursor().execute(req)
        print 'Assessment inserted'
    except:
        c.rollback()
        print 'Can not insert Assessment'

    try:
        print 'cw_uri2 = %(a)s %(c)s' % {'a': cw_uri.split('/')[-1],
        'c': cw_uri}
        req = '''INSERT ExternalResource E: E name \'%(a)s\',
        E filepath \'%(c)s\', E related_study X WHERE X is Study,
        X name \'Imagen\'
        ''' % {'a': cw_uri.split('/')[-1], 'c': cw_uri}
        #print 'req = ', req

        c.cursor().execute(req)

        res = c.cursor().execute(
        '''SET A external_resources E Where A is Assessment,
        E is ExternalResource, A identifier \'%(a)s\',
        E filepath \'%(b)s\'
        ''' % {'a': identifier, 'b': cw_uri})
        #print 'res = ', res
        print 'ExternalResource inserted'
        c.commit()
    except Exception as e:
        c.rollback()
        print 'Can not insert ExternalResource'
        e_t, e_v, e_tb = sys.exc_info()
        print 'Exc', e_t, e_v, e_tb
        traceback.print_tb(e_tb)

if __name__ == "__main__":
    main(sys.argv)
