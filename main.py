from flask import Flask, jsonify
import sqlite3


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASII'] = False
    app.config['DEBAG'] = True


    def dp_connect(query):
        connection = sqlite3.connect('netflix.db')
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result


    @app.route('/movie/<title>')
    def search_by_title(title):
        query = f"""
            SELECT
                title
                , country
                , release_year
                , listed_in AS genre
                , description 
            FROM netflix
            WHERE title = '{title}'
            ORDER BY release_year DESC 
            LIMIT 1
        """
        response = dp_connect(query)[0]
        response_json = {
            'title': response[0],
            'country': response[1],
            'release_year': response[2],
            'genre': response[3],
            'description': response[4].strip(),
        }
        return jsonify(response_json)


    @app.route('/movie/<int:start>/to/<int:end>')
    def search_by_release_year(start, end):
        query = f"""
            SELECT
                title
                , release_year
            FROM netflix
            WHERE release_year BETWEEN {start} AND {end}
            LIMIT 100
        """
        response = dp_connect(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'release_year': film[1],
            })
        return jsonify(response_json)


    @app.route('/rating/<group>')
    def search_by_rating(group):
        levels = {
            'children': ['G'],
            'family': ['G', 'PG', 'PG-13'],
            'adult': ['R', 'NC-17']}
        if group in levels:
            level = '\", \"'.join(levels[group])
            level = f'\"{level}\"'
        else:
            return jsonify([])

        query = f"""
            SELECT
                title
                , rating
                , description
            FROM netflix
            WHERE rating IN ({level})
        """
        print(query)
        response = dp_connect(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'rating': film[1],
                'description': film[2].strip()
            })
        return jsonify(response_json)


    @app.route('//genre/<genre>')
    def search_by_genre(genre):
        query = f"""
            SELECT
                title
                , description
            FROM netflix
            WHERE listed_in LIKE '%{genre}%'
            ORDER BY release_year DESC 
            LIMIT 10
        """
        response = dp_connect(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1],
            })
        return jsonify(response_json)


    def get_actors(name1, name2):
        query = f"""
            SELECT
                "cast"
            FROM netflix
            WHERE "cast" LIKE '%{name1}%'
                AND "cast" LIKE '%{name2}%'

        """
        response = dp_connect(query)
        actors = []
        for cast in response:
            actors.extend(cast[0].split(', '))
        result = []
        for a in actors:
            if a not in [name1, name2]:
                if actors.count(a) > 2:
                    result.append(a)
        result = set(result)
        return result


    def get_films(type_film, release_year, genre):
        query = f"""
            SELECT
                title
                , description
                , "type"
            FROM netflix
            WHERE "type" = '{type_film}'
                AND "release_year" = '{release_year}'
                AND  listed_in LIKE '%{genre}%'

        """
        response = dp_connect(query)
        response_json = []
        for i in response:
            response_json.append({
                'title': i[0],
                'description': i[1],
                'type': i[2]
            })
        return response_json

    app.run(debug=True, port=7000)
    # print(get_films(type_film='Movie', release_year=2016, genre='Drama'))
    # print(get_actors(name1='Rose McIver', name2='Ben Lamb'))


if __name__ == '__main__':
    main()
