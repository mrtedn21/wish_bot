from sqlalchemy import create_engine

create_wish_table_query = \
    'CREATE TABLE wish(' \
    '   first_name VARCHAR(256),' \
    '   text VARCHAR(256),' \
    '   PRIMARY KEY(first_name, text)' \
    ')'

engine = create_engine('postgresql+psycopg2://mrtedn:123@localhost/wish_db')

if __name__ == '__main__':
    engine.execute(create_wish_table_query)
