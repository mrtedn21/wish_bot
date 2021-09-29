from sqlalchemy import create_engine

create_wish_table_query = 'CREATE TABLE wish(name VARCHAR(256))'

engine = create_engine('postgresql+psycopg2://mrtedn:123@localhost/wish_db')

if __name__ == '__main__':
    engine.execute(create_wish_table_query)
