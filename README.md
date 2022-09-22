# ThangWikiAPI
This is a library used to access Wikipedia &amp; Wikidata APIs where you can get Wikipedia pages and Wikidata items. For details, please check the code!

## Dependencies
* Python >= 3.6
* spaCy >= 3.x.x

## Wikipedia: Examples

### Example 1 - Get content & first paragraph of page title "science"

Arguments: get_data_by_title(title, data_format = 'xml', language = 'en', timeout = 30)

    print("Hello, this is Wiki Core library!")
    root = get_data_by_title('science', language = 'en')
    text = get_page_content(root)
    print('page content: ', text)
    first_para = extract_first_sentence_baseline(text)
    print('first_para: ', first_para)

## Wikidata: Examples

### Example 1 - Get Wikidata item information

    item = get_wikidata_item_by_id('Q123')
    print(item)
    ## {'wikidata_id': 'Q123', 'label': 'September', 'description': 'ninth month in the Julian and Gregorian calendars', 'instances': [['Q47018901', 'calendar month']], 'subclasses': [['Q18602249', 'month of the Gregorian calendar']], 'aliases': ['Sept', 'Sep', 'Sep.', '9. month', 'Sept.'], 'parts': [['Q11184', 'Julian calendar'], ['Q12138', 'Gregorian calendar'], ['Q1130275', 'Swedish calendar']]}
   
    item = get_wikidata_item_by_title('science')
    print(item)
    ## {'wikidata_id': 'Q336', 'label': 'science', 'description': 'systematic enterprise that builds and organizes knowledge, and the set of knowledge produced by this enterprise', 'instances': [['Q11862829', 'academic discipline'], ['Q1914636', 'activity']], 'subclasses': [['Q105948247', 'knowledge system']], 'parts': []}

## Example 2 - Search Wikidata
    results = search_wikidata('science')
    print('results: ', results)
    ## results:  [{'wikidata_id': 'P2579', 'title': 'Property:P2579', 'label': 'studied by', 'datatype': 'wikibase-item', 'object_type': 'property'}, {'wikidata_id': 'P10376', 'title': 'Property:P10376', 'label': 'ScienceDirect topic ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P8694', 'title': 'Property:P8694', 'label': 'Science Museum Group ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P9268', 'title': 'Property:P9268', 'label': 'Science Magazine author ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P4389', 'title': 'Property:P4389', 'label': 'Science Museum people ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P7709', 'title': 'Property:P7709', 'label': 'ScienceOpen author ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P5064', 'title': 'Property:P5064', 'label': 'World of Physics identifier', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P8504', 'title': 'Property:P8504', 'label': 'Science Fiction Awards Database author ID', 'datatype': 'external-id', 'object_type': 'property'}, {'wikidata_id': 'P7710', 'title': 'Property:P7710', 'label': 'ScienceOpen publication ID', 'datatype': 'external-id', 'object_type': 'property'}]
