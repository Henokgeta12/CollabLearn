from CollabLearn.app import create_app
#from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    # Use socketio.run to run the Flask app with Socket.IO
    #socketio.run(app, debug=True)
    app.run(debug=True)
