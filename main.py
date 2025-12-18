from web_page import create_web_page
from read_file import parse_sheet

if __name__ == "__main__":
    # Specify players
    players = ['Миша', 'Даня', 'Слава', 'Папа']

    df1, df2, df3, df4, df5, df6 = parse_sheet()
    create_web_page(df1, df2, df3, df4, df5, df6, players)
