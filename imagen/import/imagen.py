# -*- coding: utf-8 -*-

"""Classes for importing data from Imagen XNAT server

Expects XML dumps for metadata and raw images and genetic data
Find additionnal data from FU2 processings

Only the information about F-maps or contrast is kept
"""

import logging
import os
from lxml import etree
import glob
import csv
import sys
import hashlib

from cubicweb.dataimport import RQLObjectStore
from cubicweb.dataimport import SQLGenObjectStore

from cubes.brainomics.importers.helpers import get_image_info

# XXX Other links/attributes

###############################################################################
### SOME GLOBALS ##############################################################
###############################################################################
# obsolete: use XPath and NAMESPACES instead
XNAT = '{http://nrg.wustl.edu/xnat}'
XSI = '{http://www.w3.org/2001/XMLSchema-instance}'
PSYTOOL = '{http://imagen.cea.fr/psytool}'
BEHAVIOURAL = '{http://imagen.cea.fr/behavioural}'
IMAGEN = '{http://imagen.cea.fr/imagen}'
FREESURFER = '{http://nrg.wustl.edu/fs}'
IMAGEN_fs = '{http://imagen.cea.fr/freesurfer}'

XNAT_TAGS_SUBJECT_INFOS = (
    'CANTAB',
    'CHILDHA',
    'CHILDRA',
    'Drugs',
    'Export',
    'Adolescent',
    'FMRI',
    'Series',
    'Guardian',
    'Medications',
    'PARENTRA',
    'PARENTSA',
    'Test',
)

##   1 !!! UNKNOWN EXPERIMENT ---> xnat:imageSessionData

XNAT_TAGS_SUBJECT_ADDITIONAL_INFOS = (
    'custom:cyclePhaseInfoData',
    'custom:sommeilData',
    'custom:bdnfData',
    'custom:oxyData',
    )

XNAT_TAGS_GENERIC_ASSESSMENT = (
    'dawba:clinicalRateData',
    'dawba:clinicalRate_fuData',
    'dawba:computerData',
    'dawba:computer_fuData',
    'dawba:youthData',
    'dawba:youth_fuData',
    'dawba:parent1Data',
    'dawba:parent1_fuData',
    'psytool:genData',
)
XNAT_TAGS_GENERIC_ASSESSMENT_RESOURCES_ONLY = (
    'imagen:rawPackageData',
)
XNAT_TAGS_NEUROIMAGING = (
    'xnat:mrSessionData',
)

XNAT_TAG_GENOMICS_SCORES = (
    'custom:per1_methylationData',
    'custom:oxtrGeneExpressionData',
    'custom:per2Data',
    'custom:per1_no13Data',
)

XNAT_TAGS_QUESTIONNAIRE = (
    'psytool:adsr_child_fuData',
    'psytool:audit_childData',
    'psytool:audit_child_fuData',
    'psytool:audit_parentData',
    'psytool:audit_parent_fuData',
    'psytool:audit_interview_fuData',
    'psytool:consent_fuData',
    'psytool:csi_child_fuData',
    'psytool:fbbhks_parent_fuData',
    'psytool:fu_reliabilityData',
    'psytool:fu_reliability_additionalData',
    'psytool:gateway_fu_parentData',
    'custom:iipData',
    'imagen:recruitmentInfosData',
    'imagen:imagenSubjectVariablesData',
    'psytool:espad_childData',
    'psytool:espad_child_fuData',
    'psytool:espad_parentData',
    'psytool:espad_parent_fuData',
    'psytool:espad_interview_fuData',
    'psytool:ctsData',
    'psytool:iri_child_fuData',
    'psytool:kirbyData',
    'psytool:kirby_fuData',
    'psytool:srs_parent_fuData',
    'psytool:stutt_parent_fuData',
    'psytool:leqData',
    'psytool:leq_fuData',
    'psytool:pbqData',
    'psytool:pdsData',
    'psytool:pds_fuData',
    'psytool:niData',
    'psytool:mast_parentData',
    'psytool:mast_parent_fuData',
    'psytool:neoffi_childData',
    'psytool:neoffi_child_fuData',
    'psytool:neoffi_parentData',
    'psytool:neoffi_parent_fuData',
    'psytool:pegboardData',
    'psytool:surpsData',
    'psytool:surps_fuData',
    'psytool:surps_parentData',
    'psytool:surps_parent_fuData',
    'psytool:tci_childData',
    'psytool:tci_child_fuData',
    'psytool:tci_parentData',
    'psytool:tci_parent_fuData',
    'psytool:tlfbData',
    'psytool:wiscData',
    'psytool:pbq_fuData',
    'custom:schizagenData',
    'custom:digitratioData',
    'custom:iat_cimhData',
    )

XNAT_TAGS_BEHAVIOURAL = (
    'psytool:srcData',
    'psytool:identData',
    'psytool:dotprobeData',
    'psytool:palp_v2Data',
    'behavioural:cantabTestsData',
)
XNAT_TAGS_SKIPPED = (
    'iteration',
    'language',
    'user_code_ident',
    'completed',
    'valid',
    'test_version',
    'trials',
    'imageSession_ID',
    'base_scan_type',
    'subject_ID',
    'ID',
    'project',
    'label',
    'type',
    '%stype' % XSI,
    'xsi:stype',
    'Task_type',
    'ratedate',
    'ratername',
    'relations'
)
CSV_DELIMITER = '\t'
PATHCHANGES = (('/data/xnat_private/archive/IMAGEN/arc001/processed/',
                '/neurospin/imagen/processed/'),
               ('/data/processed/',
                '/neurospin/imagen/processed/'),
               )

SCAN_TYPES = {'ADNI_MPRAGE': u'raw T1',
              'short_MPRAGE': u'raw T1',
              'behavioural:face_taskData': u'raw fMRI',
              'behavioural:gcaData': u'raw fMRI',
              'behavioural:mid_taskData': u'raw fMRI',
              'behavioural:recognition_taskData': u'raw fMRI',
              'behavioural:stop_signal_taskData': u'raw fMRI',
              'DTI': u'dti',
              'FLAIR': u'raw fMRI',
              'EPI_faces': u'raw fMRI',
              'EPI_global': u'raw fMRI',
              'EPI_rest': u'raw fMRI',
              'EPI_short_MID': u'raw fMRI',
              'EPI_stop_signal': u'raw fMRI',
              'T2': u'raw fMRI',
              'spm:betaData': u'preprocessed fMRI',
              'spm:beta_meanData': u'preprocessed fMRI',
              'spm:beta_mean_mvtroiData': u'preprocessed fMRI',
              'spm:cData': u'c map',
              'spm:conData': u'preprocessed fMRI',
              'spm:con_mvtroiData': u'preprocessed fMRI',
              'spm:essData': u'preprocessed fMRI',
              'spm:job_statsintraData': u'preprocessed fMRI',
              'spm:maskData': u'boolean mask',
              'spm:meanaData': u'preprocessed fMRI',
              'spm:meana_matData': u'preprocessed fMRI',
              'spm:mmprageData': u'preprocessed fMRI',
              'spm:mwcData': u'preprocessed fMRI',
              'spm:resmsData': u'preprocessed fMRI',
              'spm:rpl_aData': u'preprocessed fMRI',
              'spm:rp_txtData': u'preprocessed fMRI',
              'spm:rpvData': u'preprocessed fMRI',
              'spm:spmfData': u'preprocessed fMRI',
              'spm:spmtData': u'preprocessed fMRI',
              'spm:statsintra_mat_Data': u'preprocessed fMRI',
              'spm:wcData': u'preprocessed fMRI',
              'spm:weaData': u'preprocessed fMRI',
              'spm:weamaskData': u'preprocessed fMRI',
              'spm:wmmprageData': u'normalized T1',
              'spm:y_mprageData': u'normalized T1'}

FREESURFER_TYPES = ('fs:fsData',)


###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################


class ImagenException(Exception):
    """Errors encountered while parsing XML files"""

    def __init__(self, message, filename):
        Exception.__init__(self, message)
        self.filename = filename


def get_node_text(node, path, converter=None):
    """Function returning the text of the first node given a path."""
    _node = node.findall(path)
    if _node:
        info = _node[0].text
        if converter:
            try:
                return converter(info)
            except:
                return None
        return unicode(info)
    return None

def format_filepath(filepath):
    """Correctly change the path, according to some user-defined conversions
    """
    if not filepath:
        return None
    for old, new in PATHCHANGES:
        filepath = filepath.replace(old, new)
    return unicode(filepath)

def iterate_external_resources(store, experiment, study_eid):
    """Iterate over all the possible external resources (resouce/file)
    from an experiment node
    """
    added_files = set()
    for resource in experiment.findall('%(a)sresources/%(a)sresource' % {'a': XNAT}):
        filepath = format_filepath(resource.get('URI'))
        if filepath and filepath not in added_files:
            added_files.add(filepath)
            yield {'name': resource.get('label'), 'filepath': filepath, 'related_study': study_eid}
    # From Files
    for resource in experiment.findall('%(a)sFiles/%(a)sfile' % {'a': IMAGEN}):
        filepath = format_filepath(resource.get('file_name'))
        if filepath and filepath not in added_files:
            added_files.add(filepath)
            yield {'name': filepath, 'filepath': filepath, 'related_study': study_eid}

def iterate_investigators(node):
    """Iterate over the investigators of a node"""
    for assistant in node.findall('%sResearchAssistant' % IMAGEN):
        lastname = unicode(assistant.get('LastName'))
        # Cleanup lastname
        lastname = lastname.replace('-', '').strip()
        if lastname:
            yield {'identifier': lastname, 'lastname': lastname}

def iterate_score_value_infos(store, node, category, base_tag=XNAT):
    """Iterate possible score values over a node
    """
    scores = []
    try:
        node_name = node.tag.replace(base_tag, '')
    except AttributeError:
        return
    if node.text and node.text.strip():
        if node_name not in XNAT_TAGS_SKIPPED:
            scores.append((node_name, node.text.strip()))
    else:
        # Use attributes
        scores.extend((node_name + '_' + key, value) for key, value in node.items()
                      if key not in XNAT_TAGS_SKIPPED)
    for name, value in scores:
        yield build_score_value_infos(store, name, value, category)

def build_score_value_infos(store, name, value, category=u'various',
                            unit=None, possible_values=None):
    """Build score value infos from a name and a value
    """
    try:
        _value = float(value)
        _type = 'numerical'
    except:
        _type = 'string'
    if name in SCORE_DEFS:
        entity_eid = SCORE_DEFS[name]
    else:
        #print 'ScoreDefinition = ', name, category, _type, unit, possible_values
        entity = session.create_entity('ScoreDefinition', name=unicode(name),
                                     category=unicode(category), type=unicode(_type),
                                     unit=unicode(unit), possible_values=unicode(possible_values))
        #print 'entity = ', entity, entity.eid
        #scoredef = dict(session.execute('Any I, X WHERE X is ScoreDefinition, X name I'))
        #print 'scoredef = ', scoredef
        #session.flush()
        #session.commit()
        #scoredef = dict(session.execute('Any I, X WHERE X is ScoreDefinition, X name I'))
        #print 'scoredef = ', scoredef
        SCORE_DEFS[name] = entity.eid
        entity_eid = entity.eid
    attrs = {'definition': entity_eid}
    if _type == 'numerical':
        attrs['value'] = value
    else:
        # Truncate text
        if len(value)>=2040:
            attrs['text'] = unicode(value[:2040] + u'[...]')
        else:
            attrs['text'] = unicode(value)
    return attrs

def build_csv_external_resource(store, file_id, all_scores, study_eid):
    all_data = []
    all_keys = set()
    # Two steps to merge possibly different keys
    for data in all_scores:
        all_keys.update(data.keys())
        all_data.append(data)
    all_keys = sorted(list(all_keys))
    if all_data:
        # Only create file if some data exist
        filename = os.path.join(OUTPUT_FOLDER, file_id) + '.csv'
        fobj = open(filename, 'w')
        csvwriter = csv.writer(fobj, delimiter=CSV_DELIMITER)
        # Two steps to merge possibly different keys
        csvwriter.writerow(all_keys)
        for data in all_data:
            csvwriter.writerow([data.get(key) for key in all_keys])
        fobj.close()
#        fent_eid = store.create_entity('FileEntry', name=file_id,
#                                       filepath=format_filepath(filename)).eid
#        fset_eid = store.create_entity('FileSet', name=file_id,
#                                         format='csv',
#                                         related_study=study_eid).eid
#        store.relate(fset_eid, 'file_entries', fent_eid)                                 
#        return fset_eid
        ext_eid = store.create_entity('ExternalResource', name=file_id,
        filepath=format_filepath(filename),
        related_study=study_eid).eid
        return ext_eid
    return None


###############################################################################
### GENOMICS EXPERIMENT #######################################################
###############################################################################
def import_genomics_scores(store, tree, experiment, study_eid, subject_eid, center_eid):
    """Import genomics scores
    """
    # Create assessment
    measure_eid = import_generic_test_run(store, experiment, study_eid, subject_eid,
                                          _type=u'genomics')
    assessment_eid = create_assessment_for_experiment(store, experiment, None,
                                                      study_eid, subject_eid,
                                                      center_eid, measure_eid)
    # Create measure

###############################################################################
### NEUROIMAGING EXPERIMENT ###################################################
###############################################################################
def build_scan_map(tree, scan, experiment, psc):
    """Retrieve Scan attributes from an assessor and a scan

    Returns a map of Scan attributes, ready to be fed to the store
    """
    scan_id = unicode(scan.get('ID'))
    scan_type = unicode(scan.get('type'))
    for assessor_file in experiment.findall('%(a)sassessors/%(a)sassessor' % {'a': XNAT}):
        if assessor_file.get('type') == scan_type:
            _file = assessor_file.find('%(a)sout/%(a)sfile' % {'a': XNAT})
            break
    else:
        # No data file path
        print 'NO DATA FILEPATH FOR', scan_id, scan_type
        return
    if _file is None:
        return
    file_uri = format_filepath(_file.get('URI'))
    file_format = unicode(_file.get('format'))
    _type = SCAN_TYPES.get(scan_type, 'raw fMRI')
    identifier = file_uri
    index = identifier.find(psc)
    identifier = identifier[index:]
    attributes = {
        'identifier': '%(a)s_%(b)s'%{'a': scan_type, 'b': identifier}, # required attribute
        #'identifier': identifier,
        'label': scan_type, # required attribute ### infer from type?
        'type': unicode(_type), # required attribute
        'format': file_format,
        'filepath': file_uri, # required attribute
        'position_acquisition': int(scan_id),
    }
    return attributes

def build_scan_data_map(store, tree, scan):
    """Retrieve ScanData attributes from a scan

    Returns a map of ScanData attributes, ready to be fed to the store
    """
    root = tree.getroot()
    nsmap = root.nsmap
    scan_type = unicode(scan.get('%stype' % XSI).split(':')[-1])
    ### TODO fix below
    if scan_type == 'mrScanData':
        data_etype ='MRIData'
        scan_infos = {}
        path = 'xnat:parameters'
        find = scan.xpath(path, namespaces=nsmap)
        parameters = find[0]
        # MRIData
        for seq_name in ('sequence', 'scanSequence', 'seqVariant', 'acqType'):
            scan_infos.setdefault('sequence', []).append(get_node_text(parameters,
                                                                       '%s%s' % (XNAT, seq_name)))
        scan_infos['sequence'] = unicode('/'.join([s for s in scan_infos['sequence'] if s]))
        voxelres = parameters.findall('%svoxelRes' % XNAT)
        if voxelres:
            for axis in ('x', 'y', 'z'):
                scan_infos['voxel_res_%s' % axis] = float(voxelres[0].get(axis))
        fov = parameters.findall('%sfov' % XNAT)
        if fov:
            for axis in ('x', 'y'):
                scan_infos['fov_%s' % axis] = float(fov[0].get(axis))
        for attr in ('tr', 'te'):
            scan_infos['%s' % attr] = get_node_text(parameters, '%s%s' % (XNAT, attr), float)
    else:
        print 'Data type %s not implemented' % scan_type
        raise
    return store.create_entity(data_etype, **scan_infos).eid

def build_resource_scan_infos(resource, assessor, psc):
    """Build scan infos from an assessor and a resource
    """
    if unicode(assessor.get('base_scan_type')):
        label = u'%s_%s' % (unicode(assessor.get('base_scan_type')), assessor.get('%stype' % XSI))
    else:
        label = assessor.get('%stype' % XSI)
    identifier = format_filepath(resource.get('URI'))
    index = identifier.find(psc)
    identifier = identifier[index:]
    return {'format': unicode(resource.get('format')),
            'identifier': '%(a)s_%(b)s'%{'a':unicode(assessor.get('%stype' % XSI)), 'b': identifier},
            #'identifier': identifier,
            'label': label,
            'type': unicode(SCAN_TYPES.get(assessor.get('%stype' % XSI), 'raw fMRI')),
            'filepath': format_filepath(resource.get('URI'))}

def import_neuroimaging_raw_scan(store, tree, experiment, scan,
                                 assessment_eid, study_eid, subject_eid,
                                 center_eid, device_eid, center_id, psc):
    """Import a raw scan with all the related entities
    """
    # Classical case - Iterate over scans
    if not device_eid:
        device_eid = import_device(store, tree, experiment, center_eid, center_id)
    scan_infos = build_scan_map(tree, scan, experiment, psc)
    if not scan_infos:
        return
    scan_infos['concerns'] = subject_eid
    scan_infos['related_study'] = study_eid
    if device_eid:
        scan_infos['uses_device'] = device_eid
    # Add data
    scan_infos['has_data'] = build_scan_data_map(store, tree, scan)
    # Create entity
    if not scan_infos.get('label') or not scan_infos.get('filepath'):
        return
    #debug
    #print 'scan_infos', scan_infos
    #TOFIX quick workaround to fix the external_resource FileSet modifications
    #TOFIX  pop filepath for now so that the mapping will not raise an error
    #scan_infos.pop('filepath')
    scan_eid = store.create_entity('Scan', **scan_infos).eid
    store.relate(assessment_eid, 'generates', scan_eid, subjtype='Assessment')
    # Add external resource
    filepath = scan.findall('%sfile' % XNAT)[0]
    if format_filepath(filepath.get('URI')):
        ##### TOFIX not sure that this code is ever run
#        fent_eid = store.create_entity('FileEntry',
#                                        name=unicode(filepath.get('content')),
#                                        filepath=format_filepath(filepath.get('URI'))).eid
#        fset_eid = store.create_entity('FileSet',
#                                         name=unicode(filepath.get('content')),
#                                         format=filepath.get('format')).eid
        ext_eid = store.create_entity('ExternalResource', name=unicode(filepath.get('content')),
        filepath=format_filepath(filepath.get('URI')),
        related_study=study_eid).eid
#        store.relate(fset_eid, 'file_entries', fent_eid)
#        store.relate(scan_eid, 'external_resources', fset_eid)
        store.relate(scan_eid, 'external_resources', ext_eid)
#        store.relate(fset_eid, 'related_study', study_eid)
    return scan_infos['type'], scan_eid

def build_freesurfer_analysis(store, tree, assessor, study_eid, subject_eid):
    _type = u'Freesurfer'
    if _type in GENERIC_TESTS:
        test_eid = GENERIC_TESTS[_type]
    else:
        test = store.create_entity('GenericTest', identifier=_type,
                                   name=_type, type=_type)
        GENERIC_TESTS[_type] = test.eid
        test_eid = test.eid
    # GenericTestRun
    measure = store.create_entity('GenericTestRun',
                                  user_ident=u'child',
                                  identifier=unicode(assessor.get('ID')),
                                  instance_of=test_eid,
                                  related_study=study_eid,
                                  concerns=subject_eid)
    # Add files
    for extres_infos in iterate_external_resources(store, assessor, study_eid):
        if extres_infos.get('filepath'):
            #TOFIX quick workaround to fix the external_resource FileSet modifications
            #keep_filepath = extres_infos.pop('filepath')
            extres_infos['format'] = 'ascii'
#            extres_eid = store.create_entity('FileSet', **extres_infos).eid
#            fent_infos = {'filepath':keep_filepath, 'name':extres_infos.get('name')}
#            fent_eid = store.create_entity('FileEntry', **fent_infos).eid
#            store.relate(extres_eid , 'file_entries', fent_eid)
#            store.relate(measure.eid, 'external_resources', extres_eid)
#            store.relate(extres_eid, 'related_study', study_eid)
            ext_eid = store.create_entity('ExternalResource',name=unicode(extres_infos.get('name')), 
            filepath=extres_infos['filepath'], 
            related_study=study_eid).eid
            store.relate(measure.eid, 'external_resources', ext_eid)

    # Add scores - Volumetric
    volumetrics = assessor.find('%(fs)smeasures/%(fs)svolumetric' % {'fs': FREESURFER})
    if volumetrics is not None:
        for volumetric in volumetrics.getchildren():
            if volumetric.tag != '%sregions' % FREESURFER:
                name = volumetric.tag.split('}')[-1]
                value = volumetric.text.strip()
                if value and name:
                    attrs = build_score_value_infos(store, name, value, u'Freesurfer - Volumetric')
                    attrs['measure'] = measure.eid
                    score_eid = store.create_entity('ScoreValue', **attrs).eid
            else:
                # Regions
                for region in volumetric.getchildren():
                    name = region.get('name')
                    for region_score in region.getchildren():
                        if isinstance(region_score, etree._Comment):
                            continue
                        value = region_score.text.strip()
                        _name = '%s - %s' % (name, region_score.tag.split('}')[-1])
                        if value and _name:
                            attrs = build_score_value_infos(store, _name, value, u'Freesurfer - Volumetric')
                            attrs['measure'] = measure.eid
                            score_eid = store.create_entity('ScoreValue', **attrs).eid
    # Add scores - Surface
    surfaces = assessor.find('%(fs)smeasures/%(fs)ssurface' % {'fs': FREESURFER})
    if surfaces is not None:
        for hemisphere in surfaces.getchildren():
            for surface in hemisphere.getchildren():
                if isinstance(surface, etree._Comment):
                    continue
                if surface.tag != '%sregions' % FREESURFER:
                    name = hemisphere.get('name') + '_' + surface.tag.split('}')[-1]
                    value = surface.text.strip()
                    if value and name:
                        attrs = build_score_value_infos(store, name, value, u'Freesurfer - Surface')
                        attrs['measure'] = measure.eid
                        score_eid = store.create_entity('ScoreValue', **attrs).eid
                else:
                    # Regions
                    for region in surface.getchildren():
                        name = hemisphere.get('name') + '_' + region.get('name')
                        for region_score in region.getchildren():
                            if isinstance(region_score, etree._Comment):
                                continue
                            value = region_score.text.strip()
                            _name = '%s - %s' % (name, region_score.tag.split('}')[-1])
                            if value and _name:
                                attrs = build_score_value_infos(store, _name, value, u'Freesurfer - Surface')
                                attrs['measure'] = measure.eid
                                score_eid = store.create_entity('ScoreValue', **attrs).eid
    return measure.eid

def import_neuroimaging(store, tree, experiment, study_eid, subject_eid, center_eid, center_id, psc):
    """Import a neuroimaging assessment from an experiment node"""
    # Create assessment
    assessment_eid = create_assessment_for_experiment(store, experiment, None, #TODO: None->age?
                                                      study_eid, subject_eid, center_eid)
    # Create device
    device_eid = import_device(store, tree, experiment, center_eid, center_id)
    # Generate data from experiment
    seen_scan_types = {}
    for scan in experiment.findall('%(a)sscans/%(a)sscan' % {'a': XNAT}):
        # Create a scan with an external resource (raw data) and a filepath (nii file)
        data_scan = import_neuroimaging_raw_scan(store, tree, experiment, scan,
                                                 assessment_eid, study_eid, subject_eid,
                                                 center_eid, device_eid, center_id, psc)
        if data_scan:
            _type, eid = data_scan
            if _type and eid:
                seen_scan_types[_type] = eid
        else:
            _type, eid = None, None
    # Generate other scans (e.g. beta map) and measures (e.g. badrpData)
    all_scores = []
    for assessor in experiment.findall('%(a)sassessors/%(a)sassessor' % {'a': XNAT}):
        if assessor.get('type', None) in seen_scan_types:
            # This scan has already been related earlier
            continue
        if assessor.get('%stype' % XSI) in FREESURFER_TYPES:
            measure_eid = build_freesurfer_analysis(store, tree, assessor, study_eid, subject_eid)
            store.relate(assessment_eid, 'generates', measure_eid, subjtype='Assessment')
            continue
        resource = assessor.findall('%(a)sresources/%(a)sresource' % {'a': XNAT})
        if resource:
            # This is a scan file - Create it and relate it to a processing run
            assessor_scan_infos = build_resource_scan_infos(resource[0], assessor, psc)
            assessor_scan_infos['concerns'] = subject_eid
            if assessor.get('number'):
                assessor_scan_infos['position_acquisition'] = int(assessor.get('number'))
            if not assessor_scan_infos.get('label') or not assessor_scan_infos.get('filepath'):
                continue
            assessor_scan_infos['related_study'] = study_eid
            # MRI Data - Use get_image_info ?
            mri_eid = store.create_entity('MRIData').eid
            assessor_scan_infos['has_data'] = mri_eid
            #debug
            #print 'assessor_scan_infos', assessor_scan_infos
            #TOFIX quick workaround to fix the external_resource FileSet modifications
            #keep_filepath = assessor_scan_infos.pop('filepath')
            #print 'POP01 %s'%assessor_scan_infos['filepath']
            assessor_scan_eid = store.create_entity('Scan', **assessor_scan_infos).eid
            #TOFIX here use label to generate name
#            fset_eid = store.create_entity('FileSet', name=assessor_scan_infos.get('label'),
#                         format=assessor_scan_infos.get('format')).eid
#            fent_eid = store.create_entity('FileEntry', name=assessor_scan_infos.get('label'),
#                         filepath=keep_filepath).eid
#            store.relate(fset_eid, 'file_entries', fent_eid )
#            store.relate(assessor_scan_eid, 'external_resources', fset_eid)
            ext_eid = store.create_entity('ExternalResource', name=assessor_scan_infos.get('label'),
            filepath=assessor_scan_infos['filepath'],
            related_study=study_eid).eid
            store.relate(assessor_scan_eid, 'external_resources', ext_eid)
            store.relate(assessment_eid, 'generates', assessor_scan_eid, subjtype='Assessment')
        else:
            # This xml node only contains scores, e.g. badrpData
            scan_eid = seen_scan_types.get(assessor.get('base_scan_type', None))
            if scan_eid:
                # There is a scan related to the measure
                pass
            else:
                # There is no scan - Create a CSV file for the whole assessment
                scores = dict(assessor.items())
                if scores:
                    all_scores.append(scores)
        # XXX MISSING BEHAVIOURAL DATA, e.g. xsi:type="behavioural:face_taskData
    # Write the CSV scores
    if all_scores:
        _id = unicode(experiment.attrib['ID'])+'_'+'image_scores'
        extres_eid = build_csv_external_resource(store, _id, all_scores, study_eid)
        if extres_eid:
            store.relate(assessment_eid, 'external_resources', extres_eid)
            store.relate(extres_eid, 'related_study', study_eid)

    return assessment_eid


###############################################################################
### BEHAVIOURAL EXPERIMENT ####################################################
###############################################################################
def iterate_behavioural_trials(experiment, xml_ns):
    """Iterate over the trials of a behavioural experiment
    """
    for trial in experiment.findall('%(s)strials/%(s)strial' % {'s': xml_ns}):
        yield dict([(key, value) for key, value in trial.items()
                    if key not in XNAT_TAGS_SKIPPED or key == 'ID'])

def import_behavioural(store, tree, experiment, study_eid, subject_eid, center_eid):
    """Import a behavioural (as a type of psytool experiment)
    """
    # Create behavioural data
    behavioural_run_eid, behavioural_eid, age, psytool_type = import_pystool_experiment(store, tree,
                                                                          experiment,
                                                                          subject_eid,
                                                                          'Questionnaire',
                                                                          'QuestionnaireRun', study_eid)
    # Create questions/answers
    build_question_answer_infos(store, experiment, behavioural_eid, behavioural_run_eid, psytool_type)
    # Create trials file in a two steps procedure to merge possibly different keys
    _id = unicode(experiment.attrib['ID'])
    extres_eid = build_csv_external_resource(store, _id,
                                             iterate_behavioural_trials(experiment, PSYTOOL),
                                             study_eid)
    if extres_eid:
        store.relate(behavioural_run_eid, 'external_resources', extres_eid)
        store.relate(extres_eid, 'related_study', study_eid)

    # Files
    for extres_infos in iterate_external_resources(store, experiment, study_eid):
        if extres_infos.get('filepath'):
            #TOFIX quick workaround to fix the external_resource FileSet modifications
            #keep_filepath = extres_infos.pop('filepath')
            extres_infos['format'] = 'ascii'
#            extres_eid = store.create_entity('FileSet', **extres_infos).eid
#            fent_infos = {'filepath':keep_filepath, 'name':extres_infos.get('name')}
#            fent_eid = store.create_entity('FileEntry', **fent_infos).eid
#            store.relate(extres_eid , 'file_entries', fent_eid)
#            store.relate(behavioural_run_eid, 'external_resources', extres_eid)
#            store.relate(extres_eid, 'related_study', study_eid)
            ext_eid = store.create_entity('ExternalResource', name=unicode(extres_infos.get('name')),
            filepath=extres_infos['filepath'],
            related_study=study_eid).eid
            store.relate(behavioural_run_eid, 'external_resources', ext_eid)
    # Relate to an assessment
    assessment_eid = create_assessment_for_experiment(store, experiment, age,
                                                      study_eid, subject_eid, center_eid,
                                                      behavioural_run_eid)
    return behavioural_run_eid


###############################################################################
### QUESTIONNAIRE EXPERIMENT ##################################################
###############################################################################
def build_psytool_experiment(store, tree, experiment, etype):
    """Retrieve Experiment attributes from a Psytools experiment

    Discard all data relating to a specific experiment run, only keep
    metadata describing the experiment.

    Returns a map of Experiment attributes, ready to be fed to the store.
    """
    path = '@xsi:type'
    root = tree.getroot()
    nsmap = root.nsmap
    find = experiment.xpath(path, namespaces=nsmap)
    psytool_type = unicode(find[0].replace('psytool:', ''))
    simple_type = unicode(psytool_type.split('_')[0])
    path = 'psytool:test_version'
    find = experiment.xpath(path, namespaces=nsmap)
    version = unicode(find[0].text) if find else None
    path = 'psytool:language'
    find = experiment.xpath(path, namespaces=nsmap)
    language = unicode(find[0].text) if find else None
    if psytool_type in EXPERIMENTS:
        return EXPERIMENTS[psytool_type], psytool_type
    entity = store.create_entity(etype, identifier=psytool_type,
                                 name=psytool_type, type=simple_type,
                                 version=version, language=language)
    EXPERIMENTS[psytool_type] = entity.eid
    return entity.eid, psytool_type

def build_psytool_experiment_run(store, tree, experiment, etype_run, subject_eid, experiment_eid, study_eid):
    """Retrieve ExperimentRun attributes from a Psytools run

    Discard metadata describing the experiment, only keep date relating
    to a specific experiment run.

    Returns a map of ExperimentRun attributes, ready to be fed to the store.
    """
    path = '@ID'
    root = tree.getroot()
    nsmap = root.nsmap
    find = experiment.xpath(path, namespaces=nsmap)
    experiment_id = unicode(find[0])
    path = 'psytool:user_code_ident'
    find = experiment.xpath(path, namespaces=nsmap)
    user_ident = unicode(find[0].text) if find else u'unknown'
    path = 'psytool:iteration'
    find = experiment.xpath(path, namespaces=nsmap)
    iteration = int(find[0].text) if find else None
    path = 'psytool:completed'
    find = experiment.xpath(path, namespaces=nsmap)
    completed = bool(find[0].text) if find else None
    path = 'psytool:processed_age_for_test'
    find = experiment.xpath(path, namespaces=nsmap)
    if find:
        age = int(find[0].text)
    else:
        path = 'psytool:age_for_test'
        find = experiment.xpath(path, namespaces=nsmap)
        age = int(find[0].text) if find else None
    #identifier build to assume its unicity
    experiment_id =  '''%(a)s_%(b)s_%(c)s'''%{'a':experiment_id, 'b':age, 'c':iteration}
    experiment_id = experiment_id.upper()
    entity = store.create_entity(etype_run,
                               identifier=experiment_id,
                               iteration=iteration,
                               completed=completed,
                               user_ident=user_ident,
                               concerns=subject_eid,
                               instance_of=experiment_eid)
    store.relate(entity.eid, 'related_study', study_eid)
    return entity.eid, age

def import_pystool_experiment(store, tree, experiment, subject_eid, exp_etype, etype_run, study_eid):
    """Import all types of psytool experiments (questionnaire/behavioural)"""
    # Create experiment metadata - if not already created by a different
    # run of the same experiment
    experiment_eid, psytool_type = build_psytool_experiment(store, tree, experiment, exp_etype)
    # Create experiment data specific to this experiment run, relate to
    # experiment metadata
    # Retrieve the age of subject at the time of experiment
    experiment_run_eid, age = build_psytool_experiment_run(store, tree, experiment,
                                                           etype_run,
                                                           subject_eid,
                                                           experiment_eid,
                                                           study_eid)
    return experiment_run_eid, experiment_eid, age, psytool_type

def build_question_answer_infos(store, experiment, questionnaire_eid, questionnaire_run_eid, psytool_type):
    """Iterate over questions and answers for a questionnaire
    """
    _type = experiment.attrib['%stype' % XSI].replace('psytool:', '').split('_')[0]
    # Construct questions from children
    ind = 0
    data = [(child.tag.split('}')[-1], child.text) for child in experiment.getchildren()]
    # Construct questions from attributes
    data.extend(experiment.items())
    for key, value in data:
        if key not in XNAT_TAGS_SKIPPED:
            #Unit Separator
            US = '\x1f'
                
            try:
                value = float(value)
                possible_answers = None
                _type = u'numerical'
            except ValueError:
                # keep string as int, use possible_answers
                if value.find(US)>0:
                    raise Exception('Mais pourquoi ? (...\x1e, \x1f are Record Seprator and Unit Separator...)')
                possible_answers = unicode(value)
                value = 0
                _type = u'text'
            # Question
            identifier = '_'.join((key, psytool_type))
            if identifier in QUESTIONS:
                question_eid = QUESTIONS[identifier]
                # Update possible answer
                if possible_answers:
                    old_possible_answers = (QUESTION_POSSIBLE_ANSWERS[question_eid] or u'').split(US)
                    if possible_answers not in old_possible_answers:
                        old_possible_answers += (possible_answers,)
                        QUESTION_POSSIBLE_ANSWERS[question_eid] = US.join(old_possible_answers)
                    value = old_possible_answers.index(possible_answers)
            else:
                question = store.create_entity('Question', identifier=identifier,
                                               text=unicode(key), position=ind,
                                               type=_type,
                                               questionnaire=questionnaire_eid,
                                               possible_answers=possible_answers)
                QUESTIONS[identifier] = question.eid
                question_eid = question.eid
                QUESTION_POSSIBLE_ANSWERS[question_eid] = possible_answers
            # Answer
            answer = store.create_entity('Answer', value=value,
                                         questionnaire_run=questionnaire_run_eid,
                                         question=question_eid)
            ind += 1

def import_questionnaire(store, tree, experiment, study_eid, subject_eid, center_eid):
    """Import a questionnaire (as a type of psytool experiment)"""
    # Create questionnaire
    questionnaire_run_eid, questionnaire_eid, age, psytool_type = import_pystool_experiment(store, tree,
                                                                              experiment,
                                                                              subject_eid,
                                                                              'Questionnaire',
                                                                              'QuestionnaireRun', study_eid)
    # Create questions/answers
    build_question_answer_infos(store, experiment, questionnaire_eid, questionnaire_run_eid, psytool_type)
    # Create external resources
    for extres_infos in iterate_external_resources(store, experiment, study_eid):
        if extres_infos.get('filepath'):
            extres_eid = store.create_entity('ExternalResource', **extres_infos).eid
            store.relate(questionnaire_run_eid, 'external_resources', extres_eid)
            store.relate(extres_eid, 'related_study', study_eid)
    # Relate to an assessment
    assessment_eid = create_assessment_for_experiment(store, experiment, age,
                                                      study_eid, subject_eid, center_eid,
                                                      questionnaire_run_eid)
    # Files
    for extres_infos in iterate_external_resources(store, experiment, study_eid):
        if extres_infos.get('filepath'):
            extres_eid = store.create_entity('ExternalResource', **extres_infos).eid
            store.relate(questionnaire_run_eid, 'external_resources', extres_eid)
            store.relate(extres_eid, 'related_study', study_eid)
    return questionnaire_run_eid


###############################################################################
### GENERIC ASSESSMENT / EXPERIMENT ###########################################
###############################################################################
def import_generic_test_run(store, experiment, study_eid, subject_eid, _type=None):
    """Import a generic measure from an experiment node
    """
    # Create the GenericTest if it does not exist
    _type = unicode(experiment.get('%stype' % XSI)) if not _type else _type
    identifier = unicode(experiment.get('%stype' % XSI))
    if identifier in GENERIC_TESTS:
        test_eid = GENERIC_TESTS[identifier]
    else:
        test = store.create_entity('GenericTest', identifier=identifier,
                                   name=identifier, type=_type)
        GENERIC_TESTS[identifier] = test.eid
        test_eid = test.eid
    # Create the GenericTestRun
    measure = store.create_entity('GenericTestRun',
                                  user_ident=u'unknown',
                                  identifier=unicode(experiment.get('ID')),
                                  instance_of=test_eid,
                                  related_study=study_eid,
                                  concerns=subject_eid)
    # Add scores
    for score_value_infos in iterate_score_value_infos(store, experiment,
                                                       _type or u'generic'):
        score_value_infos['measure'] = measure.eid
        score_value_eid = store.create_entity('ScoreValue', **score_value_infos).eid
    return measure.eid

def create_assessment_for_experiment(store, experiment, age, study_eid,
                                     subject_eid, center_eid, measure_eid=None):
    """Create an assessment and required relations from and experiment

    Arguments:
    experiment -- XML node of the experiment
    age -- age of subject at the time of expriment
    study_eid -- identifier of the study this experiment is part of
    subject_eid -- identifier of the subject
    center_eid -- indentifier of the center where the expriment is conducted
    measure_eid -- ?

    Returns the identifier of the newly created Assessment
    """
    # Create an assessment
    experiment_id = unicode(experiment.get('ID'))
    #identifier build to assume its unicity
    experiment_id =  '''%(a)s_%(b)s'''%{'a':experiment_id, 'b':age}
    assessment_eid = store.create_entity('Assessment',
                                         identifier=experiment_id,
                                         #age_for_assessment=age,
                                         age_of_subject=age,
                                         timepoint=unicode('BL/FU1'),
                                         #protocols=unicode(experiment.get('%stype' % XSI)),
                                         related_study=study_eid).eid
    # Create relations
    protocol_eid = store.create_entity('Protocol',
                                         identifier=unicode(experiment.get('%stype' % XSI)),
                                         related_study=study_eid).eid
    store.relate(assessment_eid, 'protocols', protocol_eid)
    store.relate(subject_eid, 'concerned_by', assessment_eid)
    store.relate(center_eid, 'holds', assessment_eid)
    if measure_eid:
        store.relate(assessment_eid, 'generates', measure_eid, subjtype='Assessment')
    # Files
    for extres_infos in iterate_external_resources(store, experiment, study_eid):
        if extres_infos.get('filepath'):
            #TOFIX quick workaround to fix the external_resource FileSet modifications
            extres_infos['format'] = 'ascii'
            fent_infos = {'filepath':extres_infos.get('filepath'),
                          'name' : extres_infos.get('name')}
            #extres_infos.pop('filepath')
#            fset_eid = store.create_entity('FileSet', **extres_infos).eid
#            fent_eid = store.create_entity('FileEntry', **fent_infos).eid
#            store.relate(fset_eid, 'file_entries', fent_eid)
#            store.relate(assessment_eid, 'external_resources', fset_eid)
            ext_eid = store.create_entity('ExternalResource', name=unicode(extres_infos.get('name')),
            filepath=extres_infos.get('filepath'),
            related_study=study_eid).eid
            store.relate(assessment_eid, 'external_resources', ext_eid)
    # Investigators
    for investigator_infos in iterate_investigators(experiment):
        lastname = investigator_infos['lastname']
        if lastname in INVESTIGATORS:
            investigator_eid = INVESTIGATORS[lastname]
        else:
            investigator_eid = store.create_entity('Investigator', identifier=lastname,
                                                   lastname=lastname).eid
        store.relate(assessment_eid, 'conducted_by', investigator_eid)
    return assessment_eid

def import_quality_report(store, tree, experiment, study_eid, subject_eid, center_eid):
    """Import the quality report assessment from an experiment node
    """
    measure_eid = import_generic_test_run(store, experiment, study_eid, subject_eid)
    assessment_eid = create_assessment_for_experiment(store, experiment, None,  #TODO: None->age
                                                      study_eid, subject_eid,
                                                      center_eid, measure_eid)
    for _type in XNAT_TAGS_SUBJECT_INFOS:
        for child in experiment.findall('%s%s' % (IMAGEN, _type)):
            for score_value_infos in iterate_score_value_infos(store, child, u'qualityreport',
                                                               base_tag=IMAGEN):
                score_value_infos['measure'] = measure_eid
                score_value_eid = store.create_entity('ScoreValue', **score_value_infos).eid
    return assessment_eid

def import_generic_subject_assessments(store, tree, experiment, study_eid, subject_eid, center_eid):
    """Import generic assessments infos for various data of a subject,
    such as raw package, clinical rate, ... as Questionnaires
    """
    testrun_eid = import_questionnaire(store, tree, experiment, study_eid, subject_eid, center_eid)
    # Construct scores from relations - Multiples responses
    for relation in experiment.findall('%(p)srelations/%(p)srelation' % {'p': PSYTOOL}):
        # XXX More generic ? Missing information ?
        key = unicode(relation.get('relation'))
        value = unicode(relation.get('disorder'))
        if key != 'None' and value != 'None':
            score_value_infos = build_score_value_infos(store, key, value, category=u'relations')
            score_value_infos['measure'] = testrun_eid
            score_value_eid = store.create_entity('ScoreValue', **score_value_infos).eid
    return testrun_eid


###############################################################################
### MEDICAL EXP DATA ##########################################################
###############################################################################
def import_center(store, tree):
    """Retrieve Center attributes
    The schema and other functions require a Center. If data is missing
    from the XML tree to build one, create it from scratch instead of
    bailing out.

    Returns a map of Center attributes, ready to be fed to the store.
    """
    root = tree.getroot()
    nsmap = root.nsmap
    # Center id
    path = '//xnat:experiment[@xsi:type="imagen:imagenSubjectVariablesData"]/@ImagingCentreID'
    find = root.xpath(path, namespaces=nsmap)
    identifier = unicode(find[0]) if find else u''
    if not identifier:
        return
    # Center city
    path = '//xnat:experiment[@xsi:type="imagen:imagenSubjectVariablesData"]/@ImagingCentreCity'
    find = root.xpath(path, namespaces=nsmap)
    if find and identifier:
        city = unicode(find[0])
    else:
        identifier = 0
        city = u'unknown'
    name = u'%s %s' % (identifier, city)
    if identifier in CENTERS:
        return CENTERS[identifier], identifier
    entity = store.create_entity('Center', identifier=identifier,
                                 name=name, city=city)
    CENTERS[identifier] = entity.eid
    return entity.eid, identifier

def import_study(store, tree, filepath):
    """Create Study attributes ex nihilo
    Imagen XML files lack the relevant information but it is
    straightforward to create one.

    Returns a map of Study attributes, ready to be fed to the store.
    """
    name = u'Imagen'
    if name in STUDIES:
        return STUDIES[name]
    entity = store.create_entity('Study', name=name,
                                 #uri are absolute filepath so study data_filepath prefix for all path should be set to ''
                                 data_filepath=u'',
                                 #data_filepath=filepath,
                                 description=u'Imagen XNAT data')
    STUDIES[name] = entity.eid
    return entity.eid

def import_subject(store, tree):
    """Retrieve Subject attributes

    XPath of relevant nodes in XML file:
    - xnat:Subject
    - xnat:Subject/xnat:demographics

    The schema and other functions require a Subject. If the XML tree is
    missing relevant data, bail out and throw an ImagenException because
    it wouldn't make sense to invent a Subject.

    Returns a map of Subject attributes, ready to be fed to the store.
    """
    # ID
    root = tree.getroot()
    nsmap = root.nsmap
    identifier = unicode(root.get('ID'))
    if not identifier:
        message = 'missing subject ID'
        logger.error('{0}: {1}'.format(tree.docinfo.URL, message))
        raise ImagenException(message, tree.docinfo.URL)
    if identifier in SUBJECTS:
        return SUBJECTS[identifier]
    # gender
    find = root.find('%(a)sdemographics/%(a)sgender' % {'a': XNAT})
    if find is not None:
        gender = find.text
        vocabulary = ('male', 'female', 'unknown')
        if gender in vocabulary:
            gender = unicode(gender)
        else:
            message = 'unexpected gender {0}'.format(gender)
            logger.warn('{0}: {1}'.format(tree.docinfo.URL, message))
            gender = u'unknown'
    else:
        message = 'missing gender'
        logger.warn('{0}: {1}'.format(tree.docinfo.URL, message))
        gender = u'unknown'
    # handedness
    find = root.find('%(a)sdemographics/%(a)shandedness' % {'a': XNAT})
    if find is not None:
        handedness = find.text
        vocabulary = ('right', 'left', 'ambidextrous', 'unknown')
        if handedness in vocabulary:
            handedness = unicode(handedness)
        else:
            message = 'unexpected handedness {0}'.format(handedness)
            logger.warn('{0}: {1}'.format(tree.docinfo.URL, message))
            handedness = u'unknown'
    else:
        message = 'missing handedness'
        logger.warn('{0}: {1}'.format(tree.docinfo.URL, message))
        handedness = u'unknown'
    #TOFIX quick workaround to fix the code_in_study modification
    #code_in_study = identifier.strip('IMAGEN_')
    #identifier = unicode(hashlib.sha1(identifier).hexdigest())
    # Create entity
    entity = store.create_entity('Subject', identifier=identifier,
                                 gender=gender, handedness=handedness)
                                 #,code_in_study=code_in_study)
    #res = session.execute('''INSERT Subject S: S identifier \'%(a)s\', S gender \'%(b)s\', S handedness \'%(c)s\'
    #'''%{'a': identifier, 'b': gender, 'c': handedness})
    SUBJECTS[identifier] = entity.eid
    #print 'res %s'%res[0][0]
    #SUBJECTS[identifier] = res[0][0]
    return entity.eid
    #return res[0][0]

def import_demographics(store, tree, subject_eid):
    """Import subject demographics (excluding gender and handedness)
    """
    demographics = tree.getroot().findall('%sdemographics' % XNAT)
    if not demographics:
        return
    for child in demographics[0].getchildren():
        if child.tag not in('%sgender' % XNAT, '%shandedness' % XNAT):
            for score_value_infos in iterate_score_value_infos(store, child, u'demographics'):
                score_value_eid = store.create_entity('ScoreValue', **score_value_infos).eid
                store.relate(subject_eid, 'related_infos', score_value_eid)

def import_subject_additional_infos(store, experiment, study_eid, subject_eid, center_eid):
    """Import subject additional infos (e.g. cyclePhaseInfo)
    """
    name = experiment.get('project', u'additional_infos')
    for score_value_infos in iterate_score_value_infos(store, experiment, name):
        score_value_eid = store.create_entity('ScoreValue', **score_value_infos).eid
        store.relate(subject_eid, 'related_infos', score_value_eid)


def import_device(store, tree, experiment, center_eid, center_id):
    """Retrieve Device attributes from an experiment

    Look for scanner nodes under the experiment node.

    Returns a map of Device attributes, ready to be fed to the store.
    """
    path = 'xnat:scanner'
    root = tree.getroot()
    nsmap = root.nsmap
    find = experiment.xpath(path, namespaces=nsmap)
    if find:
        name = unicode(find[0].text)
        if name == u'None':
            name = None
    else:
        return None
    path = 'xnat:scanner/@manufacturer'
    find = experiment.xpath(path, namespaces=nsmap)
    manufacturer = unicode(find[0]) if find else None
    if not name:
        name = manufacturer
    path = 'xnat:scanner/@model'
    find = experiment.xpath(path, namespaces=nsmap)
    model = unicode(find[0]) if find else None
    center_id = None
    centers = session.execute('Any C where C is Center')
    for c in centers.entities():
        if c.eid == center_eid:
            center_id = c.identifier
    #TOFIX No need to add an identifier field in Device entity
    #TOFIX this is a proposal using the serialnum instead
    # identifier='%(a)s_%(b)s_%(c)s_%(d)s'%{'a':name, 'b':manufacturer, 'c':model, 'd':center_id}
    # if identifier in DEVICES:
    #     return DEVICES[identifier]
    # entity = store.create_entity('Device', identifier=identifier, 
    #                             name=name,
    #                             manufacturer=manufacturer,
    #                             hosted_by=center_eid, model=model)
    # DEVICES[identifier] = entity.eid
    # return entity.eid
    #serialnum = unicode(hashlib.sha1('%(a)s_%(b)s_%(c)s_%(d)s'%{'a':name, 'b':manufacturer, 'c':model, 'd':center_id}).hexdigest())
    serialnum = unicode('%(a)s_%(b)s_%(c)s_%(d)s'%{'a':name, 'b':manufacturer, 'c':model, 'd':center_id})
    if serialnum in DEVICES:
        ret_eid = DEVICES[serialnum]
    else:
        entity = store.create_entity('Device', serialnum=serialnum, 
                                name=name,
                                manufacturer=manufacturer,
                                hosted_by=center_eid, model=model)
        DEVICES[serialnum] = entity.eid
        ret_eid = entity.eid
    return ret_eid
    


###############################################################################
### MAIN IMPORTER FUNCTIONS ###################################################
###############################################################################
def import_imagen_file(store, xml_file, filepath):
    # Read XML file, get the root element, parse using XPath
    tree = etree.parse(xml_file)
    root = tree.getroot()
    nsmap = root.nsmap
    # Center
    center_eid, center_id = import_center(store, tree)
    # Study
    study_eid = import_study(store, tree, filepath)
    # Subject
    subject_eid = import_subject(store, tree)
    store.relate(subject_eid, 'related_studies', study_eid)
    # Import assessments
    import_demographics(store, tree, subject_eid)
    # Import experiments
    path = '/xnat:Subject/xnat:experiments/xnat:experiment'
    find = root.xpath(path, namespaces=nsmap)
    for experiment in find:
        find = experiment.xpath('@xsi:type', namespaces=nsmap)
        experiment_type = find[0]
        if experiment_type == 'imagen:qualityReportData':
            assessment_eid = import_quality_report(store, tree, experiment,
                                                   study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAGS_SUBJECT_ADDITIONAL_INFOS:
            assessment_eid = import_subject_additional_infos(store, experiment,
                                                             study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAGS_GENERIC_ASSESSMENT_RESOURCES_ONLY:
            assessment_eid = create_assessment_for_experiment(store, experiment, None,
                                                              study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAGS_GENERIC_ASSESSMENT:
            testrun_eid = import_generic_subject_assessments(store, tree, experiment,
                                                             study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAGS_QUESTIONNAIRE:
            measure_eid = import_questionnaire(store, tree, experiment,
                                               study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAGS_NEUROIMAGING:
            #psc=os.path.split(os.path.split(os.path.split(os.path.split(os.path.abspath(xml_file))[0])[0])[0])[1]
            psc = rescue_psc_from_xml_file_path(xml_file)
            #debug
            #print 'psc = ', psc
            assessment_eid = import_neuroimaging(store, tree, experiment,
                                                 study_eid, subject_eid, center_eid, center_id, psc)
        elif experiment_type in XNAT_TAGS_BEHAVIOURAL:
            measure_eid = import_behavioural(store, tree, experiment,
                                             study_eid, subject_eid, center_eid)
        elif experiment_type in XNAT_TAG_GENOMICS_SCORES:
            measure_eid = import_genomics_scores(store, tree, experiment,
                                                 study_eid, subject_eid, center_eid)
        else:
            print '!!! UNKNOWN EXPERIMENT --->', experiment_type
            continue

def rescue_psc_from_xml_file_path(xml_file):
    psc = os.path.split(os.path.abspath(xml_file))[1]
    psc = psc.replace('IMAGEN_', '')
    psc = psc.replace('.xml', '')
    return psc
###############################################################################
### ENTITIES/RELATIONS CACHE ##################################################
###############################################################################
SUBJECTS = dict(session.execute('Any I, X WHERE X is Subject, X identifier I'))
CENTERS = dict(session.execute('Any I, X WHERE X is Center, X identifier I'))
#TOFIX Temporary proposal for the present importer : use of serial num
#DEVICES = dict(session.execute('Any I, X WHERE X is Device, X identifier I'))
DEVICES = dict(session.execute('Any I, X WHERE X is Device, X serialnum I'))
STUDIES = dict(session.execute('Any I, X WHERE X is Study, X name I'))
GENERIC_TESTS = dict(session.execute('Any I, X WHERE X is GenericTest, X identifier I'))
SCORE_DEFS = dict(session.execute('Any I, X WHERE X is ScoreDefinition, X name I'))
INVESTIGATORS = dict(session.execute('Any I, X WHERE X is Investigator, X identifier I'))
EXPERIMENTS = dict(session.execute('Any I, X WHERE X is IN (Questionnaire, GenericTest), X identifier I'))
QUESTIONS = dict(session.execute('Any I, X WHERE X is Question, X identifier I'))
QUESTION_POSSIBLE_ANSWERS = dict(session.execute('Any X, A WHERE X is Question, X possible_answers A'))
REGIONS = dict(session.execute('Any I, X WHERE X is AnatomicalRegion, X name I'))
PROCESSING_RUNS = dict(session.execute('Any I, X WHERE X is ProcessingRun, X name I'))
RELATED_PROCESSING = set([(e[0], e[1]) for e in session.execute('Any X, Y WHERE X related_processing Y')])
OUTPUT_FOLDER = None


###############################################################################
### RUN THE IMPORTER ##########################################################
###############################################################################
if __name__ == '__main__':
    # Logging
    logger = logging.getLogger('imagen')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    # Create store
    path = sys.argv[-2]
    OUTPUT_FOLDER = sys.argv[-1]
    store = SQLGenObjectStore(session)
    #store = RQLObjectStore(session)
    if (type(store) is SQLGenObjectStore):
        STORE_FLUSH = True
    else:
        STORE_FLUSH = False
    
    for ind, xml_file in enumerate(glob.iglob(os.path.join(path, '*.xml'))):
        print 80*'*'
        print 'Processing', xml_file
        try:
            import_imagen_file(store, xml_file, path)
        except ImagenException:
            # typically XML files with imagen:Imagen_subject
            # instead of xnat:Subject
            continue
        if ind and ind % 10 == 0:
            print 80*'*'
            print 80*'*'
            print 'FLUSHING !'
            store.flush()
            print 80*'*'
            print 80*'*'
    # Update all questions
    for eid, pa in QUESTION_POSSIBLE_ANSWERS.iteritems():
        store.rql('SET X possible_answers %(pa)s WHERE X eid %(e)s',
                  {'e': eid, 'pa': pa})
        if STORE_FLUSH:
            store.flush()
    if STORE_FLUSH:
        store.flush()
    store.commit()
    # Update gender - Take gender from the QR
    rset = rql('Any S, V WHERE SD is ScoreDefinition, SD category %(c)s, SD name %(n)s, SV definition SD, '
               'SV measure M, M concerns S, SV text V',
               {'n': 'Adolescent_Gender', 'c': 'qualityreport'})
    for seid, g in rset:
        if g.lower() in ('male', 'female'):
            session.execute('SET X gender %(g)s WHERE X eid %(e)s', {'e': seid, 'g': g.lower()})
    session.commit()
