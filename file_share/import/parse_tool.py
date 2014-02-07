
import os, csv, glob, sys
from collections import defaultdict
import datetime




def parse_imagen_process_data(do_database=True) :

    # parameters
    process_folder = "/neurospin/imagen/FU2/processed/ftp_mirror/"

    # nifti folder
    nifti_zip = glob.glob(process_folder+"nifti/*/BehaviouralData.zip")
    nifti_zip.extend(glob.glob(process_folder+"nifti/*/*/*.zip"))

    # spmpreproc folder
    spmpreproc_zip = glob.glob(process_folder+"spmpreproc/*/*/*.zip")

    # spmstatsintra folder
    spmstatsintra_zip = glob.glob(process_folder+"spmstatsintra/*/*/*.zip")

    # create dataset
    dataset = defaultdict(dict)
    for zip_to_treat in [nifti_zip, spmpreproc_zip, spmstatsintra_zip]:
        for zip_item in zip_to_treat:
            uid = zip_item.split("/")[7]
            if uid not in dataset.keys():
                dataset[uid] = {}
            processing_name = zip_item.split("/")[6]
            if processing_name not in dataset[uid].keys():
                dataset[uid][processing_name] = []
            dataset[uid][processing_name].append(zip_item)

    # generate database description
    if do_database :
        return generate_description(dataset)
    else :
        return dataset

#date = datetime.datetime.fromtimestamp(os.path.getctime(zip_item))
#date = str(date)
#date = date.split(" ")[0]

def generate_description(dict_description_object) :

    result = []
    for key,value in dict_description_object.items() :
        if isinstance(value,dict) :
            sub_result = generate_description(value)
            if len(sub_result)>0 :
                parameters = {"identifier": key, "code_in_study": key,
                              "entity_name" : "Subject"}
                result.append((parameters, sub_result))

        else :
            items = []
            for item in value :
                parameters = {"name" : "imagenFU2_processing_{0}".format( 
                              os.path.splitext(os.path.split(item)[1])[0]),
                              "filepath" : item, "entity_name" : "ExternalResource"}
                #print key
                items.append((parameters, []))
            if len(items)>0 :
                parameters = {"identifier": key, "entity_name" : "Assessment"}
                result.append((parameters, items))

    return result


if __name__=="__main__" :
    dataset = parse_imagen_process_data(False)
    print dataset[dataset.keys()[0]]["spmstatsintra"]
    parse_imagen_process_data()
    for item in parse_imagen_process_data():
        print item, "\n"
