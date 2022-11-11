from preprocess.data_processer import DataProcesser

movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
clean_texts, clean_labels = movie_data.data_clean('process')
