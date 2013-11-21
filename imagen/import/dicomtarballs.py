#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#psc = '000002296749'
#psc = '000012029891'
psc_center_file='/neurospin/imagen/src/scripts/psc_tools/psc2_centre.csv'
psc_center={}
for i in reader(open(psc_center_file)):
    psc_center[i[0]]=i[1]
cw_project = 'IMAGEN'

c = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin', password='admin')



def parse_dicom(path, psc, scan):
    print '>>> path, psc, scan >>> ', path, psc, scan
    #path = '/neurospin/imagen/processed/dicomtarballs' \
    #   '/%s/SessionA/T2/T2.tar.gz'%psc
       
    tarball = tarfile.open(path)
    file1 =  tarball.extractfile('./1.dcm')

    dataset = dicom.read_file(file1)

    studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))

    centers = dict(c.cursor().execute('Any I, C WHERE C is Center, C identifier I'))

    subjects = dict(c.cursor().execute('Any I, S WHERE S is Subject, S identifier I'))
    center_eid = centers[psc_center[psc]]
    subject_eid = subjects['IMAGEN_%(a)s'%{'a' : psc}]
    if not subject_eid:
        return
    date = None

    if (0x0020,0x0011) in dataset:
        cw_scan_id = dataset[0x0020,0x0011].value # StudyDate
                
    if (0x0020,0x0011) in dataset:
        cw_scan_id = dataset[0x0020,0x0011].value
        cw_scan_type = None
        try:
            #scan.set('type', serie)
            cw_scan_type = serie
            #scan.set('type', dcm_header['0008']['103e'])
        except:
            print 'Could not set scan type'
        cw_scanner_manufacturer = None
        try:
            cw_scanner_manufacturer = dataset[0x0008, 0x0070].value
        except:
            print 'Could not find scanner manufacturer in dicom header'
        cw_scanner_model = None
        try:
            cw_scanner_model = dataset[0x0008,0x1090].value
        except:
            print 'Could not find scanner model in dicom header'
        cw_scanner_text = "None"
        try:
            cw_scanner_text = dataset[0x0008,0x1010].value
        except:
            print 'Could not find scanner id in dicom header'
        cw_operator = None
        try:
            cw_operator = dataset[0x0008,0x1070].value
        except:
            print 'Could not find operator name in dicom header'
        cw_uri = path.decode(locale.getpreferredencoding())
                
        cw_content = None
        try:
            cw_content = dataset[0x0008,0x103e].value+'_RAW'
        except:
            print 'Could not find scan content type in dicom header'  
        cw_voxelres_x = None
        cw_voxelres_y = None
        cw_voxelres_z = None
        try:
            resolution=dataset[0x0028,0x0030].value.split('\\')
            cw_voxelres_x = resolution[0]
            cw_voxelres_y = resolution[1]
            cw_voxelres_z = dataset[0x0018,0x0050].value
        except:
            print Warning('Could not find voxel resolution infos in dicom header')
        cw_fov_x = None
        cw_fov_y = None
        try:
            if dataset[0x0028,0X0010].value.isdigit() and dataset[0x0028,0x0011].value.isdigit():
                cw_fov_x = dataset[0x0028,0x0010].value
                cw_fov_y = dataset[0x0028,0x0011].value
        except:
            print Warning('Could not find fov infos in dicom header')
        cw_tr = None
        try:
            cw_tr = dataset[0x0018,0x0080].value
        except:
            print Warning('Could not find tr in dicom header')
        cw_te = None
        try:
            cw_te = dataset[0x0018,0x0081].value
        except:
            print Warning('Could not find te in dicom header')
        cw_sequence = None
        try:
            cw_sequence = dataset[0x0018,0x0024].value
        except:
            print Warning('Could not find sequence in dicom header')
        cw_scanTime = None
        try:
            if dataset[0x0008,0x0031]:
                st=dataset[0x0008,0x0031].value
                cw_scanTime = st[0:2]+':'+st[2:4]+':'+st[4:6]
        except:
            print Warning('Could not find scan time in dicom header')
        cw_imageType = None
        try:
            cw_imageType = dataset[0x0008,0x0008].value
        except:
            print Warning('Could not find image type in dicom header')
        cw_scanSequence = None
        try:
            #dataset[0x0018,0x0020].value might be a list
            cw_scanSequence = '\\\\'.join(dataset[0x0018,0x0020].value)
        except:
            print Warning('Could not find scan sequence in dicom header')
        cw_seqVariant = None
        try:
            cw_seqVariant = dataset[0x0018,0x0021].value
        except:
            print Warning('Could not find sequence variant in dicom header')
        cw_acqType = None
        try:
            cw_acqType = dataset[0x0018,0x0023].value
        except:
            print Warning('Could not find acquisition type in dicom header')
        cw_protocol = None
        try:
            cw_protocol = dataset[0x0018,0x1030].value
        except:
            print Warning('Could not find protocol in dicom header')
        scan_date = None
        try:
            scan_date = dataset[0x0008,0x0022].value
            if len(scan_date)==8:
                scan_date=scan_date[:4]+'-'+scan_date[4:6]+'-'+scan_date[6:]
                if not date:
                    date = scan_date
                else:
                    if scan_date != date:
                        print 'scans date mismatch : '+date+' and '+scan_date
        except:
            print 'Warning : error while reading date from dicom header'
    else:
        if (0x0020,0x0011) not in dataset:
            print '(0020,0011) not in header'
        #2 deadcode lines
        else:
            print dataset[0x0020,0x0011].value
        print 'Could not set scan id from dicom tag ( 0020:0011 )'
    print "====="
    print [
    cw_project, 
    #Scan
    cw_scan_id, cw_scan_type,
    #Device
    cw_scanner_manufacturer, cw_scanner_model, cw_scanner_text, 
    cw_operator, 
    cw_uri,
    cw_content, 
    #MRIData
    cw_voxelres_x, cw_voxelres_y, cw_voxelres_z, cw_fov_x, cw_fov_y, cw_tr, cw_te, cw_sequence ,
    cw_scanTime, cw_imageType, cw_scanSequence, cw_seqVariant, cw_acqType, cw_protocol, scan_date]
                
    #studies = dict(session.execute('Any N, S WHERE S is Study, S name N'))
    study_eid = None
    if 'FU2' in studies:
        study_eid = studies['FU2']
    print 'study_eid = ',study_eid
    if (study_eid==None):        
        try:
            c.cursor().execute('INSERT Study S: S name \'FU2\', S data_filepath \'\', S description \'Test Follow Up II\'')
        except:
            c.rollback()
            print 'Can not insert Study'
        studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))
        study_eid = studies['FU2']

    try:
        c.cursor().execute('''INSERT Assessment A: A identifier \'%(f)s_%(a)s\', A datetime \'%(b)s\',
    A related_study S, C holds A, X concerned_by A WHERE S is Study, C is Center, X is Subject, S name 'FU2', C identifier \'%(d)s\', X identifier \'IMAGEN_%(e)s\''''
    %{'a': psc, 'b': date, 'c': cw_protocol, 'd': psc_center[psc], 'e': psc, 'f': scan})
        c.cursor().execute('''INSERT Protocol P: P identifier \'%(a)s\', P related_study S WHERE S is Study, S name \'FU2\''''%{'a': cw_protocol})
        res = c.cursor().execute('''SET A protocols P Where A is Assessment, P is Protocol, P identifier \'%(a)s\', A identifier \'%(c)s_%(b)s\'
        '''%{'a': cw_protocol, 'b': psc, 'c': scan})
    except:
        c.rollback()
        print 'Can not insert Assessment'
    devices = dict(c.cursor().execute('Any N, D WHERE D is Device, D name N, D manufacturer \"%(b)s\", D model \"%(c)s\"'%{'b' : cw_scanner_manufacturer, 'c' : cw_scanner_model}))
    device = None
    if cw_scanner_text in devices:
        device = devices[cw_scanner_text]
    print 'device = ',device
    if (device==None):
        try:
            #still yet serialnum = void
            req = '''INSERT Device D: D identifier \'%(a)s_%(b)s_%(c)s_%(h)s\', D name \'%(a)s\', D manufacturer \'%(b)s\', D model \'%(c)s\', D modification_date \'%(f)s\', D creation_date \'%(g)s\', 
            D hosted_by C WHERE C is Center, C identifier \'%(h)s\'
            '''%{'a': cw_scanner_text, 'b': cw_scanner_manufacturer, 'c': cw_scanner_model, 'f': date, 'g': date, 'h': psc_center[psc]}
         
            device = c.cursor().execute(req) 
        except:
            c.rollback()
            print 'Can not insert Device'
    try:
        req = 'INSERT MRIData M, Scan S: M sequence \'%(a)s\''%{'a':cw_scanSequence}
        if cw_voxelres_x!=None:
            req = req + ', M voxel_res_x ' + cw_voxelres_x
        if cw_voxelres_y!=None:
            req = req + ', M voxel_res_y ' + cw_voxelres_y
        if cw_voxelres_z!=None:
            req = req + ', M voxel_res_z ' + cw_voxelres_z
        if cw_fov_x!=None:
            req = req + ', M fov_x ' + cw_fov_x
        if cw_fov_y!=None:
            req = req + ', M fov_x ' + cw_fov_y
        if cw_tr!=None:
            req = req + ', M tr %s'%cw_tr
        if cw_te!=None:
            req = req + ', M te %s'%cw_te
        #print 'req = ', req
    
        req_end = ''', S has_data M, S identifier \'%(d)s_%(a)s\', S label \'%(d)s\', S type \'%(b)s\', S format \'tar.gz\', S completed True, S valid True, 
        S filepath \'%(c)s\', S related_study X WHERE X is Study, X name \'FU2\''''%{'a': psc,'b': cw_scan_type, 'c': cw_uri, 'd': scan}
        
        req = req + req_end
        #print 'req = ', req
    
        c.cursor().execute(req)
    
        res = c.cursor().execute('''SET S concerns Y Where S is Scan, Y is Subject, S identifier \'%(c)s_%(a)s\', Y identifier \'IMAGEN_%(b)s\'
        '''%{'a': psc, 'b': psc, 'c': scan})
        #print 'res = ',res
        res = c.cursor().execute('''SET S uses_device D Where S is Scan, D is Device, S identifier \'%(g)s_%(a)s\', D identifier \'%(c)s_%(d)s_%(e)s_%(f)s\'
        '''%{'a': psc, 'b': cw_scanner_text,'c': cw_scanner_text, 'd': cw_scanner_manufacturer, 'e': cw_scanner_model, 'f': psc_center[psc], 'g': scan})
        #print 'res = ', res
        res = c.cursor().execute('''SET A generates S Where A is Assessment, S is Scan, S identifier \'%(c)s_%(a)s\', A identifier \'%(c)s_%(b)s\'
        '''%{'a': psc, 'b': psc, 'c': scan})
        #print 'res = ',res
    except Exception as e:
        c.rollback()
        print 'Can not insert MRIData or Scan'
        e_t, e_v, e_tb = sys.exc_info()
        print 'Exc',e_t, e_v, e_tb
        traceback.print_tb(e_tb)
    c.commit()
    return [cw_project, cw_scan_id, cw_scan_type]		            

#main
def main(argv):
    #psc is the 4th argument if this script is called with: cubicweb-ctl shell "instanceName" ./import_dicom.py "psc"
    #psc = sys.argv[1]
    #print len(sys.argv)

    #subjectID = psc#listOfFiles[i][k:k+12]
    #subjects = dict(session.execute('Any I, S WHERE S is Subject, S identifier I'))
    #print subjects['IMAGEN_%(a)s'%{'a' : subjectID}]
    #psc = subjects['IMAGEN_%(a)s'%{'a' : subjectID}]
    
    #f = os.path.join(os.getcwd(),listOfFiles[i])
    #print 'file = ',f
    
    #TOBEDONE
    l = glob('/neurospin/imagen/FU2/processed/dicomtarballs/000000106601/*/*/*.gz')
    for i in l:
        j = i.split('/')
        psc = j[5]
        scan = j[7]
        infos = parse_dicom(i, psc, scan)
        print 'infos = ',  infos
    
    l = glob('/neurospin/imagen/FU2/processed/dicomtarballs/000002296749/*/*/*.gz')
    for i in l:
        j = i.split('/')
        psc = j[5]
        scan = j[7]
        infos = parse_dicom(i, psc, scan)
        print 'infos = ',  infos
    
    l = glob('/neurospin/imagen/FU2/processed/dicomtarballs/000003726191/*/*/*.gz')
    for i in l:
        j = i.split('/')
        psc = j[5]
        scan = j[7]
        infos = parse_dicom(i, psc, scan)
        print 'infos = ',  infos
    
    #infos = parse_dicom()
    # dialogue avec la base CW
    # faire les create entities ....

    #c.commit()
    
if __name__ == '__main__':
    main(sys.argv)

