from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import getChannelID, getVideoList, GetComment, GetStats, GetSentiment
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/videos", methods=['GET'])
def getVideos():
    url = request.args.get('url')
    if url.split("/")[-1][0:2] == "UC":
        id = url.split("/")[-1]
    else:
        id = getChannelID(url.split("/")[-1])
        if id=="Error":
            print(1)
            return jsonify({"error" : "error"})
    videos, channel = getVideoList(id)
    if videos=="Error":
        return jsonify({"error" : "error"})
    return jsonify({"videos": videos, "channel":  channel})

@app.route("/comments", methods=['GET'])
def getComments():
    id = request.args.get('id')
    comments = GetComment(id)
    stats, description = GetStats(id)
    sentiments = GetSentiment(comments)
    sentiment_stats = {}
    sentiment_stats["Positive"] = sentiments.count("Positive")
    sentiment_stats["Negative"] = sentiments.count("Negative")
    sentiment_stats["Interogative"] = sentiments.count("Interogative")
    sentiment_stats["Imperative"] = sentiments.count("Imperative")
    sentiment_stats["Misc"] = sentiments.count("Misc.")
    sentiment_stats["Corrective"] = sentiments.count("Corrective")
    comments_sent = []
    for i in range(len(comments)):
        comment = {}
        comment["comment"] = comments[i]
        comment["sentiment"] = sentiments[i]
        comments_sent.append(comment)
        
    return jsonify({"comments": comments_sent, "stats": stats, "sentiment_stats": sentiment_stats, "description": description})

if __name__ == "__main__":
  app.run(debug=True)