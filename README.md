# WikiLib
This is a library used to access Wikipedia &amp; Wikidata APIs where uou can get Wikipedia pages and Wikidata items.

## Dependencies
* Python >=3.6

## Wikipedia: Examples

### Example 1 - Get content & first paragraph of page title "science"


    print("Hello, this is Wiki Core library!")
    root = get_data_by_title('science')
    text = get_page_content(root)
    print('page content: ', text)
    first_para = extract_first_sentence_baseline(text)
    print('first_para: ', first_para)

## Wikidata: Examples

### Example 1 - Get Wikidata item information

    item = get_wikidata_item_by_id('Q123')
    print(item)
    ## Result
    ## {'wikidata_id': 'Q123', 'label': 'September', 'description': 'ninth month in the Julian and Gregorian calendars', 'instances': [['Q47018901', 'calendar month']], 'subclasses': [['Q18602249', 'month of the Gregorian calendar']], 'aliases': ['Sept', 'Sep', 'Sep.', '9. month', 'Sept.'], 'parts': [['Q11184', 'Julian calendar'], ['Q12138', 'Gregorian calendar'], ['Q1130275', 'Swedish calendar']]}
   
    item = get_wikidata_item_by_title('science')
    print(item)
    ## Result
    ## {'wikidata_id': 'Q336', 'label': 'science', 'description': 'systematic enterprise that builds and organizes knowledge, and the set of knowledge produced by this enterprise', 'instances': [['Q11862829', 'academic discipline'], ['Q1914636', 'activity']], 'subclasses': [['Q105948247', 'knowledge system']], 'parts': []}
