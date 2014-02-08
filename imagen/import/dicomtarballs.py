#!/usr/bin/python
# -*- coding: utf-8 -*-

########################################################################
#
# python dicomtarballs.py should insert all .tar.gz file contain in
# /neurospin/imagen/FU2/processed/dicomtarballs/*/*/*/*.gz and related
# to a present subject into database
#
########################################################################

import sys
import os
from os.path import sep, join, exists
from os import listdir
import re
import tempfile
import shutil
#import traceback
from csv import reader
from glob import glob
import dicom
import locale

import tarfile

from cubicweb import dbapi

psc_center_file = '/neurospin/imagen/src/scripts/psc_tools/psc2_centre.csv'
psc_center = {}
for i in reader(open(psc_center_file)):
    psc_center[i[0]] = i[1]
cw_project = 'IMAGEN'

c = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin', password='admin')


def parse_dicom(path, psc, scan):
    print '>>> path, psc, scan >>> ', path, psc, scan

    studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))

    centers = dict(c.cursor().execute('Any I, C WHERE C is Center, C identifier I'))

    subjects = dict(c.cursor().execute('Any I, S WHERE S is Subject, S identifier I'))

    subject_eid = None
    if 'IMAGEN_%(a)s' % {'a': psc} in subjects:
        subject_eid = subjects['IMAGEN_%(a)s' % {'a': psc}]
    if not subject_eid:
        return
    center_eid = centers[psc_center[psc]]

    date = None
    tarball = tarfile.open(path)
    file1 = tarball.extractfile('./1.dcm')
    dataset = dicom.read_file(file1)

    if (0x0020,0x0011) in dataset:
        cw_scan_id = dataset[0x0020,0x0011].value
        #cw_scan_type = None
        #scan.set('type', serie)
        cw_scan_type = scan
        #scan.set('type', dcm_header['0008']['103e'])
        #print 'Could not set scan type'
        cw_scanner_manufacturer = None
        if (0x0008, 0x0070) in dataset:
            cw_scanner_manufacturer = dataset[0x0008, 0x0070].value
        else:
            print 'Could not find scanner manufacturer in dicom header'
        cw_scanner_model = None
        if (0x0008,0x1090) in dataset:
            cw_scanner_model = dataset[0x0008,0x1090].value
        else:
            print 'Could not find scanner model in dicom header'
        cw_scanner_text = "None"
        if (0x0008,0x1010) in dataset:
            cw_scanner_text = dataset[0x0008,0x1010].value
        else:
            print 'Could not find scanner id in dicom header'
        cw_operator = None
        if (0x0008,0x1070) in dataset:
            cw_operator = dataset[0x0008,0x1070].value
        else:
            print 'Could not find operator name in dicom header'
        cw_uri = path.decode(locale.getpreferredencoding())

        cw_content = None
        if (0x0008,0x103e) in dataset:
            cw_content = dataset[0x0008,0x103e].value+'_RAW'
        else:
            print 'Could not find scan content type in dicom header'
        cw_voxelres_x = None
        cw_voxelres_y = None
        cw_voxelres_z = None
        try:
            resolution = dataset[0x0028,0x0030].value.split('\\')
            cw_voxelres_x = resolution[0]
            cw_voxelres_y = resolution[1]
            cw_voxelres_z = dataset[0x0018,0x0050].value
        except:
            print 'Could not find voxel resolution infos in dicom header'
        cw_fov_x = None
        cw_fov_y = None
        if (0x0028,0x0010) in dataset and (0x0028,0x0011) in dataset:
                cw_fov_x = dataset[0x0028,0x0010].value
                cw_fov_y = dataset[0x0028,0x0011].value
        else:
            print 'Could not find fov infos in dicom header'
        cw_tr = None
        if (0x0018,0x0080) in dataset:
            cw_tr = dataset[0x0018,0x0080].value
        else:
            print 'Could not find tr in dicom header'
        cw_te = None
        if (0x0018,0x0081) in dataset:
            cw_te = dataset[0x0018,0x0081].value
        else:
            print 'Could not find te in dicom header'
        cw_sequence = None
        if (0x0018,0x0024) in dataset:
            cw_sequence = dataset[0x0018,0x0024].value
        else:
            print 'Could not find sequence in dicom header'
        cw_scanTime = None
        if (0x0008,0x0031) in dataset:
            st = dataset[0x0008,0x0031].value
            cw_scanTime = st[0:2]+':'+st[2:4]+':'+st[4:6]
        else:
            print 'Could not find scan time in dicom header'
        cw_imageType = None
        if (0x0008,0x0008) in dataset:
            cw_imageType = dataset[0x0008,0x0008].value
        else:
            print 'Could not find image type in dicom header'
        cw_scanSequence = None
        if (0x0018,0x0020) in dataset:
            #dataset[0x0018,0x0020].value might be a list
            cw_scanSequence = '\\\\'.join(dataset[0x0018,0x0020].value)
        else:
            print 'Could not find scan sequence in dicom header'
        cw_seqVariant = None
        if (0x0018,0x0021) in dataset:
            cw_seqVariant = dataset[0x0018,0x0021].value
        else:
            print 'Could not find sequence variant in dicom header'
        cw_acqType = None
        if (0x0018,0x0023) in dataset:
            cw_acqType = dataset[0x0018,0x0023].value
        else:
            print 'Could not find acquisition type in dicom header'
        cw_protocol = None
        if (0x0018,0x1030) in dataset:
            cw_protocol = dataset[0x0018,0x1030].value
        else:
            print 'Could not find protocol in dicom header'
        #Default date
        scan_date = '1900-01-01'
        if (0x0008,0x0022) in dataset:
            scan_date = dataset[0x0008,0x0022].value
            if len(scan_date) == 8:
                scan_date = scan_date[:4] + '-' + scan_date[4:6] + '-' + scan_date[6:]
        else:
            print 'Warning : error while reading date from dicom header'
        date = scan_date
    else:
        if (0x0020,0x0011) not in dataset:
            print '(0020,0011) not in header'
        #2 deadcode lines
        else:
            print dataset[0x0020,0x0011].value
        print 'Could not set scan id from dicom tag ( 0020:0011 )'
    print "====="
    print [cw_project,
           # Scan
           cw_scan_id, cw_scan_type,
           # Device
           cw_scanner_manufacturer, cw_scanner_model, cw_scanner_text,
           cw_operator,
           cw_uri,
           cw_content,
           # MRIData
           cw_voxelres_x, cw_voxelres_y, cw_voxelres_z, cw_fov_x, cw_fov_y, cw_tr, cw_te, cw_sequence,
           cw_scanTime, cw_imageType, cw_scanSequence, cw_seqVariant, cw_acqType, cw_protocol, scan_date]

    study_eid = None
    if 'Imagen' in studies:
        study_eid = studies['Imagen']
    print 'study_eid = ', study_eid
    if study_eid is None:
        try:
            c.cursor().execute('INSERT Study S: S name \'Imagen\', S data_filepath \'\', S description \'Imagen study\'')
        except:
            c.rollback()
            print 'Can not insert Study'
        studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))
        study_eid = studies['Imagen']

    try:
        req = '''INSERT Assessment A: A identifier \'%(f)s_%(a)s\', A datetime \'%(b)s\', A timepoint \'FU2\',
        A related_study S, C holds A, X concerned_by A WHERE S is Study, C is Center, X is Subject, S name \'Imagen\', C identifier \'%(d)s\', X identifier \'IMAGEN_%(e)s\'
        ''' % {'a': psc, 'b': date, 'd': psc_center[psc], 'e': psc, 'f': scan}
        print 'req = ', req
        res = c.cursor().execute(req)
        print 'res = ', res
        res = c.cursor().execute('''INSERT Protocol P: P identifier \'%(a)s\', P related_study S WHERE S is Study, S name \'Imagen\''''
                                 % {'a': cw_protocol})
        res = c.cursor().execute('''SET A protocols P Where A is Assessment, P is Protocol, P identifier \'%(a)s\', A identifier \'%(c)s_%(b)s\''''
                                 % {'a': cw_protocol, 'b': psc, 'c': scan})
    except:
        c.rollback()
        print 'Can not insert Assessment'
    devices = dict(c.cursor().execute('Any N, D WHERE D is Device, D name N, D manufacturer \"%(b)s\", D model \"%(c)s\"'
                                      % {'b': cw_scanner_manufacturer, 'c': cw_scanner_model}))
    device = None
    if cw_scanner_text in devices:
        device = devices[cw_scanner_text]
    print 'device = ', device
    if device is None:
        try:
            # still yet serialnum = void
            req = '''INSERT Device D: D serialnum \'%(a)s_%(b)s_%(c)s_%(d)s\', D name \'%(a)s\', D manufacturer \'%(b)s\', D model \'%(c)s\',
            D hosted_by C WHERE C is Center, C identifier \'%(d)s\'''' % {'a': cw_scanner_text, 'b': cw_scanner_manufacturer, 'c': cw_scanner_model, 'd': psc_center[psc]}
            print 'req = ', req
            device = c.cursor().execute(req)
        except:
            c.rollback()
            print 'Can not insert Device'
    try:
        req = 'INSERT MRIData M, Scan S: M sequence \'%(a)s\'' % {'a': cw_scanSequence}
        if cw_voxelres_x is not None:
            req = req + ', M voxel_res_x ' + cw_voxelres_x
        if cw_voxelres_y is not None:
            req = req + ', M voxel_res_y ' + cw_voxelres_y
        if cw_voxelres_z is not None:
            req = req + ', M voxel_res_z ' % cw_voxelres_z
        if cw_fov_x is not None:
            req = req + ', M fov_x ' + cw_fov_x
        if cw_fov_y is not None:
            req = req + ', M fov_x ' + cw_fov_y
        if cw_tr is not None:
            req = req + ', M tr ' + cw_tr
        if cw_te is not None:
            req = req + ', M te ' + cw_te
        #print 'req = ', req

        req_end = ''', S has_data M, S identifier \'%(d)s_%(a)s\', S label \'%(d)s\', S type \'%(b)s\', S format \'tar.gz\',
        S filepath \'%(c)s\', S completed True, S valid True, S related_study X WHERE X is Study, X name \'Imagen\'
        ''' % {'a': psc, 'b': cw_scan_type, 'c': cw_uri, 'd': scan}

        req = req + req_end
        print 'req = ', req

        c.cursor().execute(req)

        ##### TOFIX not sure that this code is ever run
        #req = '''INSERT FileEntry F: F name \'%(a)s\', F filepath \'%(b)s\''''%{'a': scan, 'b': cw_uri}
        #res = c.cursor().execute(req)
        #fe_eid = res[0][0]
        #req = '''INSERT FileSet F: F name \'%(a)s\', F format \'%(b)s\''''%{'a': scan, 'b': 'DICOM COMPRESSED'}
        #res = c.cursor().execute(req)
        #fs_eid = res[0][0]
        #res = c.cursor().execute('''SET S file_entries E Where S is FileSet, E is FileEntry, S eid \'%(a)s\', E eid \'%(b)s\'
        #''' % {'a': fs_eid, 'b': fe_eid})
        #res = c.cursor().execute('''SET S external_resources F Where S is Scan, F is FileSet, S identifier \'%(a)s_%(b)s\', F eid \'%(c)s\'
        #''' % {'a': scan, 'b': psc, 'c': fs_eid})
        #res = c.cursor().execute('''SET F related_study S Where S is Study, F is FileSet, S name \'Imagen\', F eid \'%(a)s\'
        #''' % {'a': fs_eid})
        req = '''INSERT ExternalResource E: E name \'%(a)s\', E filepath \'%(b)s\', E related_study S Where S is Study, S name \'Imagen\'
        ''' % {'a': scan, 'b': cw_uri}
        res = c.cursor().execute(req)
        ext_eid = res[0][0]
        res = c.cursor().execute('''SET S external_resources E Where S is Scan, E is ExternalResource, S identifier \'%(a)s_%(b)s\', E eid \'%(c)s\'
        ''' % {'a': scan, 'b': psc, 'c': ext_eid})

        res = c.cursor().execute('''SET S concerns Y Where S is Scan, Y is Subject, S identifier \'%(c)s_%(a)s\', Y identifier \'IMAGEN_%(b)s\'
        ''' % {'a': psc, 'b': psc, 'c': scan})
        #print 'res = ', res
        res = c.cursor().execute('''SET S uses_device D Where S is Scan, D is Device, S identifier \'%(g)s_%(a)s\', D serialnum \'%(c)s_%(d)s_%(e)s_%(f)s\'
        ''' % {'a': psc, 'b': cw_scanner_text, 'c': cw_scanner_text, 'd': cw_scanner_manufacturer, 'e': cw_scanner_model, 'f': psc_center[psc], 'g': scan})
        print 'res = ', res
        res = c.cursor().execute('''SET A generates S Where A is Assessment, S is Scan, S identifier \'%(c)s_%(a)s\', A identifier \'%(c)s_%(b)s\'
        ''' % {'a': psc, 'b': psc, 'c': scan})
        print 'res = ', res
    except Exception as e:
        c.rollback()
        print 'Can not insert MRIData or Scan'
        e_t, e_v, e_tb = sys.exc_info()
        print 'Exc', e_t, e_v, e_tb
        traceback.print_tb(e_tb)
    c.commit()
    return [cw_project, cw_scan_id, cw_scan_type]


def main(argv):

    l = glob('/neurospin/imagen/FU2/processed/dicomtarballs/*/*/*/*.gz')
    for i in l:
        j = i.split('/')
        psc = j[-4]
        scan = j[-2]
        infos = parse_dicom(i, psc, scan)
        print 'infos = ',  infos

    #infos = parse_dicom()
    # dialogue avec la base CW
    # faire les create entities ....

    #c.commit()

if __name__ == '__main__':
    main(sys.argv)
