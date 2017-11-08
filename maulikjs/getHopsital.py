import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class getHospital(dml.Algorithm):
    contributor = 'maulikjs'
    reads = []
    writes = ['maulikjs.hospitals']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('maulikjs', 'maulikjs')

        url = 'https://data.boston.gov/export/622/208/6222085d-ee88-45c6-ae40-0c7464620d64.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("hospitals")
        repo.createCollection("hospitals")
        repo['maulikjs.hospitals'].insert_many(r)
        repo['maulikjs.hospitals'].metadata({'complete':True})
        print(repo['maulikjs.hospitals'].metadata())

       
        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
        Create the provenance document describing everything happening
        in this script. Each run of the script will generate a new
        document describing that invocation event.
        '''

    # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('maulikjs', 'maulikjs')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/maulikjs#') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/maulikjs#') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bos', 'https://data.boston.gov/export/622/208/')

        this_script = doc.agent('alg:getHospital', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bos:6222085d-ee88-45c6-ae40-0c7464620d64.json', {'prov:label':'Hospitals', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_prices = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        
        doc.wasAssociatedWith(get_prices, this_script)

        doc.usage(get_prices, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})
        
        prices = doc.entity('dat:hospitals', {prov.model.PROV_LABEL:'hospitals', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(prices, this_script)
        doc.wasGeneratedBy(prices, get_prices, endTime)
        doc.wasDerivedFrom(prices, resource, get_prices, get_prices, get_prices)

      
        repo.logout()
                  
        return doc

getHospital.execute()
doc = getHospital.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
