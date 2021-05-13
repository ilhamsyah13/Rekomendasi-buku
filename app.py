import numpy as np
import pandas as pd
from flask import Flask, request, render_template, jsonify, json
from flask_sqlalchemy import SQLAlchemy  


app = Flask(__name__, template_folder='templates')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/drop_duplicate_books'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://etlyftgx:hPyv1Xfs78L0W6b5XkIPRxO3VDCukEuj@queenie.db.elephantsql.com:5432/etlyftgx'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db = SQLAlchemy(app) 
 
class mytable(db.Model):
    __tablename__ = 'mytable'
    book_id = db.Column(db.Integer, primary_key=True)
    original_title = db.Column(db.String(150))
    image_url = db.Column(db.String(150))
    def as_dict(self):
        return {'original_title': self.original_title}


#Dataset
books = pd.read_csv('Dataset/new_book.csv')
main_data = pd.read_csv('Dataset/final_data.csv')
final_book = pd.read_csv('Dataset/drop_duplicate_books.csv')


#variable for top10
C = main_data['average_rating'].mean()
m = main_data['ratings_count'].quantile(0.9)


# find title
main_data = main_data.reset_index()

final_dataset = main_data.pivot_table(index='user_id',columns='original_title',values='rating')
final_dataset = final_dataset.fillna(0)

title = [main_data['original_title'][i] for i in range(len(main_data['original_title']))]


def weighted_rating(x, m=m, C=C):
    v = x['ratings_count']
    R = x['average_rating']
    # IMDB Formula
    return (v/(v+m)) * R + (m/(v+m)) * C

def matching(title):
    match_books = final_book[final_book['original_title'].str.contains(title)]
    return match_books

def recommendation(title):
    find_books = final_dataset[title]
    corr_books = final_dataset.corrwith(find_books, method='pearson')
    corr_table = pd.DataFrame(corr_books, columns=['correlation'])
    corr_table.dropna(inplace=True)
    corr_summary = corr_table.join(books['ratings_count'])
    corr_summary = pd.merge(corr_table, books, on='original_title')
    corr_summary = corr_summary.sort_values('correlation', ascending = False)
    return corr_summary

def recommendTop():
    top_books = final_book.copy().loc[final_book['ratings_count'] >= m]
    top_books['score'] = top_books.apply(weighted_rating, axis=1)
    top_books = top_books.sort_values('score', ascending=False)
    top_books = top_books[['original_title', 'image_url']]
    return top_books


@app.route('/autocomplete')
def autocomplete():
    res = mytable.query.all()
    list_books = [r.as_dict() for r in res]
    return jsonify(list_books)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        recTop = recommendTop()
        titleTop = []
        image = []
        for i in range(len(recTop)):
            titleTop.append(recTop.iloc[i][0])
            image.append(recTop.iloc[i][1])
        return render_template('index.html', topTitle = titleTop, topImage = image)
            
    if request.method == 'POST':
        book_name = request.form['search-book']
        book_name = book_name.title()
        if book_name not in title:
            result_final = matching(book_name)
            names = []
            image = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][7])
                image.append(result_final.iloc[i][10])
            return render_template('no_result.html',books_names=names, search_name=book_name, recImage = image, len=len(result_final))
        else:
            result_final = recommendation(book_name)
            names = []
            name = final_book.loc[final_book['original_title'] == book_name, 'original_title'].values[0]
            authors = final_book.loc[final_book['original_title'] == book_name, 'authors'].values[0]
            rating = final_book.loc[final_book['original_title'] == book_name, 'average_rating'].values[0]
            isbn = final_book.loc[final_book['original_title'] == book_name, 'isbn'].values[0]
            year = final_book.loc[final_book['original_title'] == book_name, 'original_publication_year'].values[0]
            image = final_book.loc[final_book['original_title'] == book_name, 'image_url'].values[0]
            images = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                images.append(result_final.iloc[i][9])
            return render_template('result.html',books_names=names, search_name=book_name, author_names = authors, rating = rating, isbn = isbn, year= year, recImage = images, book_name=name, book_image = image)

@app.route('/link_book/<string:book_link>')
def link_book(book_link):
    book_name = book_link
    book_name = book_name.title()
    result_final = recommendation(book_name)
    names = []
    name = final_book.loc[final_book['original_title'] == book_name, 'original_title'].values[0]
    authors = final_book.loc[final_book['original_title'] == book_name, 'authors'].values[0]
    rating = final_book.loc[final_book['original_title'] == book_name, 'average_rating'].values[0]
    isbn = final_book.loc[final_book['original_title'] == book_name, 'isbn'].values[0]
    year = final_book.loc[final_book['original_title'] == book_name, 'original_publication_year'].values[0]
    image = final_book.loc[final_book['original_title'] == book_name, 'image_url'].values[0]
    images = []
    for i in range(len(result_final)):
        names.append(result_final.iloc[i][0])
        images.append(result_final.iloc[i][9])
    return render_template('result.html',books_names=names, search_name=book_name, author_names = authors,rating = rating, isbn = isbn, year= year, recImage = images, book_name=name, book_image = image )

@app.route('/all_books/<int:page_num>')
def all_books(page_num):
    all_books = mytable.query.paginate(per_page=15, page=page_num, error_out=True)
    return render_template('All_Books.html',all_books = all_books)

if __name__ == "__main__":
    app.run(debug=True)
