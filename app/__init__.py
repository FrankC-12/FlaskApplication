from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import psycopg2
import os


# Crear la aplicación Flask y la API de Flask-RESTX
app = Flask(__name__)
api = Api(app, version="1.0", title="Consulta API",
          description="API para consultar tablas de diferentes bases de datos usando Flask-RESTX")

# Definir el modelo del payload para Swagger
query_model = api.model('Query', {
    'database': fields.String(required=True, description="Nombre de la base de datos"),
    'table': fields.String(required=True, description="Nombre de la tabla a consultar")
})

# Definir el endpoint
@api.route('/query')
class QueryEndpoint(Resource):
    @api.expect(query_model)  # Asociar el modelo con este endpoint
    def post(self):
        """
        Endpoint para consultar una tabla de una base de datos específica.
        El payload debe contener el nombre de la base de datos y el nombre de la tabla.
        """
        # Obtener datos del payload
        data = request.get_json()
        db_name = data.get('database')
        table_name = data.get('table')
        
        if not db_name or not table_name:
            return {"error": "Se deben proporcionar 'database' y 'table' en el payload"}, 400

        try:
            # Establecer la conexión con la base de datos
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "frank1203"),
                database=db_name
            )
            cursor = connection.cursor()

            # Ejecutar consulta
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]

            # Transformar los resultados en una lista de diccionarios
            results = [dict(zip(columns, row)) for row in rows]

            # Cerrar la conexión
            cursor.close()
            connection.close()

            return jsonify(results)

        except Exception as ex:
            return {"error": f"Error al conectar o ejecutar la consulta: {str(ex)}"}, 500


if __name__ == '__main__':
    app.run(debug=True)
