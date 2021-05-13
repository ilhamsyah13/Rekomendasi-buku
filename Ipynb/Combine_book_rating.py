import pandas as pd
import numpy as np


books=pd.read_csv('../Dataset/books.csv')
ratings=pd.read_csv('../Dataset/ratings.csv')





books.head()




books.isnull().sum()





books['isbn'].fillna('0', inplace = True)
books['original_title'].fillna('No Title', inplace = True)
books['original_publication_year'].fillna('0', inplace = True)





ratings.head()





books.columns



books = books.loc[:,['id','book_id','isbn','authors','original_publication_year','original_title','average_rating','ratings_count','image_url']]
books['original_publication_year'] = books['original_publication_year'].astype(int)





books.head()





books['original_title'] = books['original_title'].str.lower()





books['original_title'] = books['original_title'].str.strip()





combine_book_rating = pd.merge(ratings, books, on='book_id')
combine_book_rating.head(2)


# In[12]:


combine_book_rating['original_title'][1]


# In[13]:


combine_book_rating.to_csv('main_data.csv',index=False)


# In[ ]:




