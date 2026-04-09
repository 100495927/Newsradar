from mongo.Database import Database
import sys


def main() -> None:
    try:
        db = Database()
        l = db.col_rss_fuentes.lista_fuentes()
        if len(l) == 0:
            sys.exit(-1)
        for i in l:
            print(i)
    except:
        sys.exit(-1)


if __name__ == "__main__":
    main()
    sys.exit(0)
