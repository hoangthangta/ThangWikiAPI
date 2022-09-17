# WikiLib
This is a library used to access Wikipedia &amp; Wikidata APIs where uou can get Wikipedia pages and Wikidata items.

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
   
    item = get_wikidata_item_by_title('science')
    print(item)
