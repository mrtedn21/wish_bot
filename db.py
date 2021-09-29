from sqlalchemy import create_engine

create_wish_table_query = \
    'CREATE TABLE wish(' \
    '   username VARCHAR(256),' \
    '   text VARCHAR(256),' \
    '   PRIMARY KEY(text)' \
    ')'

engine = create_engine('postgresql+psycopg2://mrtedn:123@localhost/wish_db')

if __name__ == '__main__':
    engine.execute(create_wish_table_query)
