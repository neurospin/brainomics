########################################################################
#
# Usage: python import_nifti.py path
# where path is a file or a directory containing .nii.gz nifti scan
# to be inserted into database, only file which match 0*.nii.gz are 
# stored
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
c = dbapi.connect('zmqpickle-tcp://127.0.0.1:8181', login='admin', password='admin')

psc_center_file='/neurospin/imagen/src/scripts/psc_tools/psc2_centre.csv'
psc_center={}
for i in reader(open(psc_center_file)):
    psc_center[i[0]]=i[1]
    
def main(argv):
    print argv[0], argv[1]
    try:
        file(argv[1])
        print 'argv[1] is a file'
        insert_nifti(argv)
    except:
		l = os.path.join(argv[1], '*/Session*/*/0*.nii.gz')
		print l
		l = glob(l)
		for i in l:
			insert_nifti(['import_nifti.py', i])

def insert_nifti(argv):
    print argv[1]
    cw_uri = os.path.abspath(argv[1])
    scan = cw_uri.split('/')[-2]
    identifier = cw_uri.split('/')[-1]
    identifier = identifier.replace('.nii.gz','')
    psc = cw_uri.split('/')[-4]
    identifier = 'IMAGEN_%(e)s_%(d)s'%{'e': scan, 'd': identifier}
    print 'PSC = ', psc
    print 'identifier = ', identifier
    print 'cw_uri = ', cw_uri
    label = cw_uri.split('/')[-1]
    print 'label = ', label
    print 'Device = ?'
    
    print 'MRIData :'
    print 'sequence = ', scan
    img = nib.load(cw_uri)
#    data = img.get_data()
#    shape_x = data.shape[0]
#    shape_y = data.shape[1]
#    shape_z = data.shape[2]
    hdr = img.get_header()
    raw = hdr.structarr
    shape = raw['dim'].tolist()
    shape_x = shape[0]
    shape_y = shape[1]
    shape_z = shape[2]
    print 'shape_xyz = ', shape_x, shape_y, shape_z
#    print 'data.shape = ', data.shape
    res_x = raw['pixdim'].tolist()[1]
    res_y = raw['pixdim'].tolist()[2]
    res_z = raw['pixdim'].tolist()[3]
    print 'voxel_res_xyz = ', res_x, res_y, res_z
    tr = raw['db_name'].tolist().split('TR:')[-1].split(' TE:')[0]
    te = raw['db_name'].tolist().split('TE:')[-1]
    print 'tr = ', tr, 'te = ', te
    
#    print data.size
#    print data.view
#    print 'hdr = ', hdr


    studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))
    
    print studies
    if 'Imagen' in studies:
        study_eid = studies['Imagen']
    print 'study_eid = ',study_eid
    if (study_eid==None):        
        try:
            c.cursor().execute('INSERT Study S: S name \'Imagen\', S data_filepath \'\', S description \'Imagen\'')
        except:
            c.rollback()
            print 'Can not insert Study'
        studies = dict(c.cursor().execute('Any N, S WHERE S is Study, S name N'))
        study_eid = studies['Imagen']

    t = time.gmtime()
    date = datetime.date(t.tm_year, t.tm_mon, t.tm_mday).isoformat()[:10]
    print date
    try:
        c.cursor().execute('''INSERT Assessment A: A identifier \'%(e)s\', A datetime \'%(b)s\', A timepoint \'FU2\',
        A related_study S, C holds A, X concerned_by A WHERE S is Study, C is Center, X is Subject, S name 'Imagen', C identifier \'%(d)s\', X identifier \'IMAGEN_%(a)s\''''
    %{'a': psc, 'b': date, 'd': psc_center[psc], 'e': identifier})
#        c.cursor().execute('''INSERT Protocol P: P identifier \'%(a)s\', P related_study S WHERE S is Study, S name \'FU2\''''%{'a': cw_protocol})
#        res = c.cursor().execute('''SET A protocols P Where A is Assessment, P is Protocol, P identifier \'%(a)s\', A identifier \'%(c)s_%(b)s\'
#        '''%{'a': cw_protocol, 'b': psc, 'c': scan})
        print 'Assessment inserted'
    except:
        c.rollback()
        print 'Can not insert Assessment'
        
    try:
        req = 'INSERT MRIData M, Scan S: M sequence \'%(a)s\''%{'a':scan}
        req = req + ', M shape_x %s'%shape_x
        req = req + ', M shape_y %s'%shape_y
        req = req + ', M shape_z %s'%shape_z
        req = req + ', M voxel_res_x %s'%res_x
        req = req + ', M voxel_res_y %s'%res_y
        req = req + ', M voxel_res_z %s'%res_z
#        req = req + ', M fov_x ' + 'None'
#        req = req + ', M fov_x ' + 'None'
        req = req + ', M tr %s'%tr
        req = req + ', M te %s'%te
#        print 'req = ', req
    
#        req_end = ''', S has_data M, S identifier \'%(d)s_%(a)s\', S label \'%(d)s\', S type \'%(b)s\', S format \'tar.gz\', S completed True, S valid True, 
#        S filepath \'%(c)s\', S related_study X WHERE X is Study, X name \'FU2\''''%{'a': psc,'b': cw_scan_type, 'c': cw_uri, 'd': scan}
        req_end = ''', S has_data M, S identifier \'%(d)s\', S label \'%(e)s\', S type \'%(b)s\', S format \'NIFTI COMPRESSED\', S completed True, S valid True, 
        S filepath \'%(c)s\', S related_study X WHERE X is Study, X name \'Imagen\''''%{'a': psc,'b': 'NIFTI', 'c': cw_uri, 'd': identifier, 'e': label}
        
        req = req + req_end
        print 'req = ', req
    
        c.cursor().execute(req)
    
        res = c.cursor().execute('''SET S concerns Y Where S is Scan, Y is Subject, S identifier \'%(a)s\', Y identifier \'IMAGEN_%(b)s\'
        '''%{'a': identifier, 'b': psc})
        #print 'res = ',res
#        res = c.cursor().execute('''SET S uses_device D Where S is Scan, D is Device, S identifier \'%(g)s_%(a)s\', D identifier \'%(c)s_%(d)s_%(e)s_%(f)s\'
#        '''%{'a': psc, 'b': cw_scanner_text,'c': cw_scanner_text, 'd': cw_scanner_manufacturer, 'e': cw_scanner_model, 'f': psc_center[psc], 'g': scan})
        #print 'res = ', res
        res = c.cursor().execute('''SET A generates S Where A is Assessment, S is Scan, S identifier \'%(a)s\', A identifier \'%(a)s\'
        '''%{'a': identifier})
        #print 'res = ',res
        print 'Scan inserted'
        c.commit()
    except Exception as e:
        c.rollback()
        print 'Can not insert Scan'
        e_t, e_v, e_tb = sys.exc_info()
        print 'Exc',e_t, e_v, e_tb
        traceback.print_tb(e_tb)
    #c.commit()

if __name__ == "__main__":
	main(sys.argv)
