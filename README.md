## search_engine

Our implementation of a search engine using `Elasticsearch`, `elasticsearch-py` and `Flask`.

## Installation

```
git pull https://github.com/amosbastian/search_engine.git

# Do this wherever your elasticsearch implementation is
./bin/elasticsearch

# From the main folder, go to where all our Python files are and create XML and JSON folder
cd app/views
mkdir XML
mkdir JSON

# Add the XML files to the XML folder and create your JSON files
python xml_to_json.py

# Then you want to add the created JSON files to our Elasticsearch telegraaf index
python populate_database.py

# Everything has been added to our index, so now we can search!
cd ..
python run.py
```

Get your favourite browser and go to `localhost:5555` and you should be able to search!
