# WikiLib
A library to access Wikipedia &amp; Wikidata APIs

# Examples

## Example 1 - Get content & first paragraph of page title "science"


    print("Hello, this is Wiki Core library!")
    root = get_data_by_title('science')
    text = get_page_content(root)
    print('page content: ', text)
    first_para = extract_first_sentence_baseline(text)
    print('first_para: ', first_para)
