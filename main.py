import wikipedia
from Tkinter import *
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from os import walk

def write_page_content(main_page, directory):

    print('Beginning writing page contents to disk...')
    wikipedia.set_rate_limiting(True)

    try:
        print('Retrieving and writing {}'.format(main_page.title))
        # get the links for the wikipedia page
        links = main_page.links
        # encode unicode links
        links = [link.encode('utf-8') for link in links]
        
        # write the contents of the main page (if file doesn't already exist)
        if not os.path.exists('./' + main_page.title + '.txt'):            
            with open(main_page.title + '.txt', 'w') as f:
                f.write(main_page.content.encode('utf-8'))
        
        # get content for all of the links
        for link in links:            
            # get the page and title
            print('Getting {} page'.format(link))
            link_page = wikipedia.page(title=link, auto_suggest=False)
            link_title = link_page.title
            
            #write the page contents to a file (if file doesn't already exist)
            if not os.path.exists('./' + link_title + '.txt'):
                with open(link_title + '.txt', 'w') as f:
                    print('Writing {}'.format(link_title))
                    f.write(link_page.content.encode('utf-8'))
        # endfor
        
        print('Done writing contents of pages')
        return
        
    except wikipedia.exceptions.WikipediaException as e:
        print(e)

def main():
    
    try:
        
        main_page = wikipedia.page(title='fallout 4')
        page_title = main_page.title.encode('utf-8')
        
        # directory to write wikipedia page contents
        directory = page_title + '_pages'
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
            write_page_content(main_page, directory)
        else:
            os.chdir(directory)
        
        text_files = []
        for (dirpath, dirnames, filenames) in walk('.'):
            text_files.extend(filenames)
            break
        
        text_files.remove(page_title + '.txt')
        text_files.insert(0, page_title + '.txt')
    
        # perform tfidf transformation
        documents = [open(f) for f in text_files]
        tfidf = TfidfVectorizer(input='file').fit_transform(documents)
        pairwise_similarity = (tfidf * tfidf.T).A
        
        # we only need the documents similar to the given page (first row)
        similarities = pairwise_similarity[0]
        
        # combine files and similarity values into list of (file, similarity) tuples
        page_sim = zip(text_files, similarities)
        # if the similarity is 1, it is the same page, so don't include it
        page_sim = [item for item in page_sim if item[1] < 1]
        
        top_page_sim = sorted(page_sim, key=lambda x: x[1], reverse=True)[:10]
        
        for idx, (page, sim) in enumerate(top_page_sim):
            page_name = page[:len(page) - 4]
            print('Result #{}'.format(idx + 1))
            print('Page: {0}\tLink: https://en.wikipedia.org/wiki/{0}\tsimilarity: {1}'.format(page_name, sim))        
        
    except wikipedia.exceptions.WikipediaException as e:
        print(e)
        return
    
if __name__ == '__main__':
    main()