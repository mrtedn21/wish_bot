create_wish_table_query = """
    CREATE TABLE wish(
       first_name VARCHAR(256),
       text VARCHAR(256),
       PRIMARY KEY(first_name, text)
    )"""

create_wish_with_index_view_query = """
    CREATE OR REPLACE VIEW wish_with_index AS
    SELECT
        first_name,
        text,
        ROW_NUMBER() OVER(PARTITION BY first_name ORDER BY text) AS rn
    FROM wish
    ORDER BY first_name, text;
"""
