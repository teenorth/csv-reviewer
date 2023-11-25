from api import Api

app = Api.app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
