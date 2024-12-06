from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Crear la aplicación Flask y la API Flask-RESTX
app = Flask(__name__)
api = Api(app, version="1.0", title="Consulta API",
          description="API para consultar tablas de diferentes bases de datos usando Flask-RESTX")

# Definir el modelo del payload para Swagger
query_model = api.model('Query', {
    'databases': fields.List(fields.String, required=True, description="Lista de nombres de las bases de datos"),
    'table': fields.String(required=True, description="Nombre de la tabla a consultar")
})

# Definir el endpoint
@api.route('/query')
class QueryEndpoint(Resource):
    @api.expect(query_model)
    def post(self):
        """
        Endpoint para consultar una tabla en múltiples bases de datos.
        """
        data = request.get_json()
        db_names = data.get('databases')
        table_name = data.get('table')

        if not db_names or not table_name:
            return {"error": "Se deben proporcionar 'databases' (lista) y 'table' en el payload"}, 400

        results = {}

        for db_name in db_names:
            try:
                # Conectar a la base de datos usando las variables de entorno
                connection = psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=db_name,
                    port=os.getenv("DB_PORT", 5432)
                )
                cursor = connection.cursor()

                # Ejecutar consulta
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                rows = cursor.fetchall()

                # Obtener los nombres de las columnas
                columns = [desc[0] for desc in cursor.description]

                # Transformar resultados en lista de diccionarios
                results[db_name] = [dict(zip(columns, row)) for row in rows]

                # Cerrar conexión
                cursor.close()
                connection.close()

            except Exception as ex:
                results[db_name] = {"error": f"Error al conectar o consultar la base de datos '{db_name}': {str(ex)}"}

        return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
