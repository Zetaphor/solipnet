from flask import Flask, render_template, request
from urllib.parse import urlparse

from engine import *

app = Flask(__name__)
engine = SolinetEngine()

@app.route("/")
def index():
    return render_template("browser.html")

@app.route("/browse", defaults={'path': ''})
@app.route("/browse/<path:path>")
def browse(path):
    query = request.args.get('query', None)
    if query:
        print(f"query: {query}")
        results = engine.get_search(query)
        return render_template("search_results.html", results=results, query=query)
    elif path:
        if path == "_export":
            return engine.export_internet()
        else:
            parsed_path = urlparse("http://" + path)
            generated_page = engine.get_page(parsed_path.netloc, path=parsed_path.path)
            return generated_page
    else:
        return render_template("search_home.html")

if __name__ == "__main__":
    app.run()
    print(engine.export_internet())
