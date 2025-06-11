from flask import Flask, Response

app=Flask(__name__)
@app.route('/app/log',methods=['GET'])
def get_log():
    with open('/Users/nimalesh/Downloads/HPC/HPC.log', 'r') as file:
        log_content = file.read()
    return Response(log_content, mimetype='text/plain')
if __name__ == '__main__':
    app.run(debug=True)