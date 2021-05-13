#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[4]:


combine_book_rating = pd.read_csv('../Dataset/main_data.csv')


# In[5]:


combine_book_rating.head(2)


# In[6]:


combine_book_rating['original_title'] = combine_book_rating['original_title'].str.strip()


# In[7]:


final_dataset = combine_book_rating.pivot_table(index='user_id',columns='original_title',values='rating')
print(final_dataset.shape)
final_dataset


# In[8]:


final_dataset.fillna(0)


# In[9]:


combine_book_rating.to_csv('pivot.csv',index=False)


# In[ ]:




